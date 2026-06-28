"""12-factor fitness function for keyboard layout evolution.

Pure-tensor GPU batch evaluation — evaluates entire populations in one call
with zero Python loops in the hot path.
"""
import math
import numpy as np
from collections import OrderedDict

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from representation import (
    Position, Shortcut, KEY_GROUPS,
    FINGER_MAP, THUMB_HAND, LEFT_COLS, RIGHT_COLS,
    KNOWN_KEY_NAMES, LAYER_ACCESS, build_layer_to_positions,
    discover_dynamic_groups, is_universal_shortcut,
    is_frozen_l0_position, is_l0_thumb_worthy_shortcut,
    shortcut_matches_group,
)
from layer_access import HARD_INVALID_FITNESS, LayerAccessAnalyzer


class FitnessEvaluator:
    def __init__(self, positions, shortcut_pool, config, usage_stats=None,
                 conjunction_pairs=None, device="cpu", current_genome=None,
                 canonical=None):
        self.positions = positions
        self.pool = shortcut_pool
        self.canonical = canonical
        self.config = config
        self.weights = config.get("weights", {})
        self.usage_stats = usage_stats or {}
        self.conjunction_pairs = conjunction_pairs or {}
        self.device = device
        self.exact_gpu_scoring = bool(config.get("exact_gpu_scoring", config.get("exact_gpu_adjacency", False)))
        self.n_positions = len(positions)
        self.n_shortcuts = len(shortcut_pool)
        self.layer_positions = build_layer_to_positions(positions)
        self.current_genome = np.array(current_genome, dtype=np.int32) if current_genome is not None else None
        self.access_analyzer = LayerAccessAnalyzer(canonical, positions, shortcut_pool) if canonical else None

        self.dynamic_groups = discover_dynamic_groups(
            self.conjunction_pairs, self.usage_stats, self.pool, threshold=0.3
        )
        self.all_protected_groups = [g for g in KEY_GROUPS if g.get("protected")] + self.dynamic_groups

        self._precompute_numpy()
        if HAS_TORCH and device != "cpu":
            self._build_gpu_tensors()

    def _precompute_numpy(self):
        N = self.n_positions
        S = self.n_shortcuts

        self.effort_arr = np.array([p.effort for p in self.positions], dtype=np.float32)

        # Pad index S as "empty" sentinel
        self.importance_arr = np.zeros(S + 1, dtype=np.float32)
        self.raw_importance_arr = np.zeros(S + 1, dtype=np.float32)
        for s in self.pool:
            self.importance_arr[s.sid] = s.importance
            self.raw_importance_arr[s.sid] = s.importance

        # Clipboard parity: Ctrl+Z/X are as fundamental as Ctrl+C/V but score
        # lower in the pipeline (9 vs 10). Boost to match so they compete for
        # prime positions equally.
        clipboard_max = 0.0
        for s in self.pool:
            if s.keys in ('Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X'):
                clipboard_max = max(clipboard_max, self.importance_arr[s.sid])
        if clipboard_max > 0:
            for s in self.pool:
                if s.keys in ('Ctrl+Z', 'Ctrl+X'):
                    self.importance_arr[s.sid] = max(self.importance_arr[s.sid], clipboard_max)

        self.usage_boost = np.ones(S + 1, dtype=np.float32)
        shortcuts_usage = self.usage_stats.get("shortcuts", {})
        for s in self.pool:
            count = shortcuts_usage.get(s.keys, {}).get("count", 0)
            per_day = shortcuts_usage.get(s.keys, {}).get("per_day", 0)
            if count > 0:
                self.usage_boost[s.sid] = 1.0 + math.log(1 + count)
                if per_day >= 3:
                    self.importance_arr[s.sid] = max(self.importance_arr[s.sid], 9.0)
                elif count >= 2:
                    self.importance_arr[s.sid] = max(self.importance_arr[s.sid], 7.0)

        # Per-layer usage multiplier: how much a shortcut is actually used on
        # each layer. Defaults to 1.0 (neutral). When usage_stats contains
        # "by_layer_shortcut" data (keys -> {layer -> count}), shortcuts that
        # are never used on a given layer get a low multiplier, making
        # duplicates on unused layers expensive. This penalizes pointless
        # cross-layer duplication while preserving duplicates the user relies on.
        unique_layers = sorted(set(p.layer for p in self.positions))
        n_layers = max(unique_layers) + 1 if unique_layers else 0
        self.layer_usage_mult = np.ones((S + 1, n_layers), dtype=np.float32)
        sid_by_keys = {s.keys: s.sid for s in self.pool}
        by_layer_shortcut = dict(self.usage_stats.get("by_layer_shortcut", {}))
        # Merge mouse_by_layer into by_layer_shortcut so mouse buttons get
        # per-layer usage multipliers just like keyboard shortcuts
        for btn, layer_counts in self.usage_stats.get("mouse_by_layer", {}).items():
            if btn not in by_layer_shortcut:
                by_layer_shortcut[btn] = {}
            for lyr, cnt in layer_counts.items():
                by_layer_shortcut[btn][str(lyr)] = by_layer_shortcut[btn].get(str(lyr), 0) + cnt
        for keys, layer_counts in by_layer_shortcut.items():
            sid = sid_by_keys.get(keys)
            if sid is None:
                continue
            total = sum(layer_counts.values())
            if total < 3:
                continue
            for layer in unique_layers:
                lcount = layer_counts.get(str(layer), 0)
                if lcount == 0 and total >= 5:
                    # Never used on this layer despite decent total usage —
                    # strong signal the duplicate is unnecessary
                    self.layer_usage_mult[sid, layer] = 0.3
                elif total > 0:
                    ratio = lcount / total
                    # Scale: 0% usage -> 0.3x, 50%+ -> 1.0x
                    self.layer_usage_mult[sid, layer] = max(0.3, min(1.0, 0.3 + ratio * 1.4))

        # Mouse button usage boost from mouse_by_layer
        mouse_by_layer = self.usage_stats.get("mouse_by_layer", {})
        for s in self.pool:
            if s.keys in mouse_by_layer:
                total_clicks = sum(mouse_by_layer[s.keys].values())
                if total_clicks > 0:
                    self.usage_boost[s.sid] = max(
                        self.usage_boost[s.sid], 1.0 + math.log(1 + total_clicks)
                    )
                    if total_clicks >= 3:
                        self.importance_arr[s.sid] = max(self.importance_arr[s.sid], 9.0)

        # Scroll toggle key boost from scroll_total
        scroll_total = self.usage_stats.get("scroll_total", 0)
        if scroll_total > 0:
            for s in self.pool:
                if "scroll" in s.keys.lower() or (
                    hasattr(s, "action") and "scroll" in getattr(s, "action", "").lower()
                ):
                    self.usage_boost[s.sid] = max(
                        self.usage_boost[s.sid], 1.0 + math.log(1 + scroll_total)
                    )
                    self.importance_arr[s.sid] = max(self.importance_arr[s.sid], 9.0)

        # Layer switch key boost from layer_switch_activations
        layer_activations = self.usage_stats.get("layer_switch_activations", {})
        for s in self.pool:
            if s.keys.startswith("coach_") and s.keys.endswith("_hold"):
                layer_match = s.keys.replace("coach_l", "").replace("_hold", "")
                act_count = layer_activations.get(layer_match, 0)
                if act_count > 0:
                    self.usage_boost[s.sid] = max(
                        self.usage_boost[s.sid], 1.0 + math.log(1 + act_count)
                    )
                    if act_count >= 10:
                        self.importance_arr[s.sid] = max(self.importance_arr[s.sid], 9.0)

        # Blind spot importance boost: shortcuts the user SHOULD use but doesn't
        blind_spots = self.usage_stats.get("blind_spots", [])
        self.blind_spot_boost = np.zeros(S + 1, dtype=np.float32)
        blind_lookup = {(b["app"], b["keys"]): b["blind_spot_score"] for b in blind_spots}
        for s in self.pool:
            score = blind_lookup.get((s.app, s.keys), 0.0)
            if score > 0:
                # Boost importance by up to 30% for high blind-spot shortcuts
                boost = min(0.3, score / 30.0)
                self.importance_arr[s.sid] *= (1.0 + boost)
                self.blind_spot_boost[s.sid] = boost

        self._build_layer_switch_costs()
        self._build_layer_util_boost()

        self.finger_arr = np.array([
            list(FINGER_MAP.values()).index(p.finger) if p.finger in FINGER_MAP.values() else -1
            for p in self.positions
        ], dtype=np.int32)
        self.hand_arr = np.array([0 if p.hand == "left" else 1 for p in self.positions], dtype=np.int32)
        self.layer_arr = np.array([p.layer for p in self.positions], dtype=np.int32)
        self.is_thumb_arr = np.array([p.is_thumb for p in self.positions], dtype=np.bool_)
        self.x_arr = np.array([p.x for p in self.positions], dtype=np.int32)
        self.y_arr = np.array([p.y for p in self.positions], dtype=np.int32)

        self.app_ids = {}
        self.app_sets = {}
        for s in self.pool:
            self.app_ids[s.sid] = s.app
            self.app_sets[s.sid] = set(s.apps) if s.apps else {s.app}

        self._build_conjunction_data()
        self._build_distance_matrix()

        self.toggled_layers = {
            layer for layer, info in LAYER_ACCESS.items()
            if info.get("method") == "toggled"
        }
        self.exit_required_layers = {
            layer for layer, info in LAYER_ACCESS.items()
            if info.get("method") in ("toggled", "locked", "momentary_or_locked")
        }
        if self.access_analyzer is not None:
            self.exit_required_layers = set(self.access_analyzer.exit_required_layers)
        self.momentary_layers = {
            layer for layer, info in LAYER_ACCESS.items()
            if "momentary" in info.get("method", "")
        }
        self.pure_momentary_layers = {
            layer for layer, info in LAYER_ACCESS.items()
            if info.get("method") == "momentary"
        }
        self._classify_mouse_layers()
        self._build_thumb_busy_penalty()
        self._build_layer_importance_multipliers()
        self.base_accessible_sids = self._find_base_accessible()
        self._build_zmk_compat()
        self._build_layer_context_mask()
        self._build_thumb_vectors()
        self._build_original_dupe_exempt()
        self._build_mouse_protection()
        self._build_toggled_layer_effort()
        self._build_toggled_base_requirement()
        self._build_l0_only_base_keys()
        self._build_frozen_l0_duplicate_data()
        self._build_structural_capability_data()
        self._build_app_coherence_data()
        self._build_mouse_accessibility_data()
        self._build_relationship_awareness_data()
        self._build_layer_demand()
        self._build_l0_open_position_data()

    def _build_layer_switch_costs(self):
        unique_layers = sorted(set(p.layer for p in self.positions))
        n_layers = max(unique_layers) + 1 if unique_layers else 0
        self.layer_switch_cost_matrix = np.zeros((n_layers, n_layers), dtype=np.float32)
        for a in range(n_layers):
            for b in range(n_layers):
                if a == b:
                    continue
                a_acc = LAYER_ACCESS.get(a, {})
                b_acc = LAYER_ACCESS.get(b, {})
                a_method = a_acc.get("method", "")
                b_method = b_acc.get("method", "")
                if a == 0 or b == 0:
                    other = b_method if a == 0 else a_method
                    if other.startswith("momentary"):
                        self.layer_switch_cost_matrix[a, b] = 1.0
                    elif other == "toggled":
                        self.layer_switch_cost_matrix[a, b] = 2.0
                    else:
                        self.layer_switch_cost_matrix[a, b] = 1.5
                elif a_method.startswith("momentary") and b_method.startswith("momentary"):
                    a_thumb = a_acc.get("thumb")
                    b_thumb = b_acc.get("thumb")
                    if a_thumb == b_thumb:
                        self.layer_switch_cost_matrix[a, b] = 2.0
                    else:
                        self.layer_switch_cost_matrix[a, b] = 1.5
                elif a_method.startswith("momentary") or b_method.startswith("momentary"):
                    self.layer_switch_cost_matrix[a, b] = 2.5
                else:
                    self.layer_switch_cost_matrix[a, b] = 3.0

    def _build_layer_util_boost(self):
        layer_sessions = self.usage_stats.get("layer_sessions", {})
        unique_layers = sorted(set(p.layer for p in self.positions))
        n_layers = max(unique_layers) + 1 if unique_layers else 0
        layer_util = np.ones(n_layers, dtype=np.float32)
        for layer_str, session_data in layer_sessions.items():
            layer = int(layer_str)
            if layer >= n_layers:
                continue
            count = session_data.get("count", 0)
            avg_duration = session_data.get("avg_duration_ms", 0)
            if count >= 2:
                util = math.log(1 + count) * (1 + math.log(1 + avg_duration / 1000.0))
                layer_util[layer] = min(2.0, 1.0 + util * 0.1)
        self.layer_util_arr = np.array([layer_util[p.layer] if p.layer < n_layers else 1.0
                                        for p in self.positions], dtype=np.float32)

    def _find_base_accessible(self):
        """Shortcuts reachable on Layer 0 without any layer activation.
        L0 has: letters, numbers, punctuation, Ctrl, Shift, Alt, Enter,
        Tab, Escape, Delete, Space. L0 does NOT have: F-keys, arrow keys,
        Home/End/PgUp/PgDn, Insert, PrintScreen, or Win/Super key."""
        # Keys physically present on L0
        l0_keys = set('abcdefghijklmnopqrstuvwxyz')
        l0_keys.update(set('0123456789'))
        l0_mods = {'ctrl', 'shift', 'alt'}  # no Win/Super on L0
        l0_special = {'Delete', 'Escape', 'Enter', 'Tab', 'Space'}

        base = set()
        for s in self.pool:
            k = s.keys
            # Parse the shortcut to check all parts are on L0
            parts = k.replace('+', ' ').split()
            mods_needed = set()
            base_key = parts[-1] if parts else k

            for p in parts[:-1]:
                mods_needed.add(p.lower())

            # Check: are all required modifiers on L0?
            if not mods_needed.issubset(l0_mods):
                continue  # e.g. Win+X — Win not on L0

            # Check: is the base key on L0?
            if base_key.lower() in l0_keys:
                base.add(s.sid)
            elif base_key in l0_special:
                base.add(s.sid)
            # F-keys, arrows, Home/End/PgUp/PgDn — NOT on L0

        return base

    def _shortcut_complexity(self, sid):
        """Effort multiplier for pressing a shortcut on L0.
        1 key = 1.0, 2 keys (Ctrl+C) = 1.0, 3 keys (Ctrl+Shift+K) = 1.8,
        4+ keys = 2.5+. Reflects the physical and cognitive difficulty of
        holding multiple modifiers simultaneously."""
        s = self.pool[sid]
        parts = s.keys.replace('+', ' ').split()
        n = len(parts)
        if n <= 2:
            return 1.0
        elif n == 3:
            return 1.8
        else:
            return 2.5

    def _build_conjunction_data(self):
        sid_lookup = {s.keys: s.sid for s in self.pool}
        self.conj_pairs = []
        for pair_key, weight in self.conjunction_pairs.items():
            parts = pair_key.split("|")
            if len(parts) != 2:
                continue
            sid_a = sid_lookup.get(parts[0])
            sid_b = sid_lookup.get(parts[1])
            if sid_a is not None and sid_b is not None:
                self.conj_pairs.append((sid_a, sid_b, weight))

        if self.conj_pairs:
            self.conj_sid_a = np.array([c[0] for c in self.conj_pairs], dtype=np.int64)
            self.conj_sid_b = np.array([c[1] for c in self.conj_pairs], dtype=np.int64)
            self.conj_weight = np.array([c[2] for c in self.conj_pairs], dtype=np.float32)
        else:
            self.conj_sid_a = np.array([], dtype=np.int64)
            self.conj_sid_b = np.array([], dtype=np.int64)
            self.conj_weight = np.array([], dtype=np.float32)

    def _add_relation_pair(self, relation_weights, sid_a, sid_b, weight):
        if sid_a is None or sid_b is None or sid_a == sid_b or weight <= 0:
            return
        a, b = sorted((int(sid_a), int(sid_b)))
        relation_weights[(a, b)] = max(float(weight), relation_weights.get((a, b), 0.0))

    def _static_group_sids(self, group):
        return [s.sid for s in self.pool if shortcut_matches_group(s, group)]

    def _build_relationship_awareness_data(self):
        """Pairs of controls that should be spatially coherent, not hard-locked.

        This is broader than key groups. Mouse buttons are very strong
        relations, clipboard/arrows are strong workflow relations, and observed
        conjunction pairs add softer usage-derived relations.
        """
        relation_weights = {}

        for sid_a, sid_b, weight in self.conj_pairs:
            if sid_a == sid_b:
                continue
            # Usage/conjunction weights can be very large; compress them so
            # observed habits inform layout without overwhelming hard quality.
            self._add_relation_pair(
                relation_weights, sid_a, sid_b,
                min(8.0, 1.5 * math.log1p(float(weight))),
            )

        group_weights = {
            "arrows": 12.0,
            "win_directions": 8.0,
            "clipboard": 10.0,
            "f_keys_low": 2.0,
            "f_keys_high": 2.0,
        }
        for group in KEY_GROUPS:
            base_weight = group_weights.get(group.get("name"))
            if not base_weight:
                continue
            members = self._static_group_sids(group)
            for ia in range(len(members)):
                for ib in range(ia + 1, len(members)):
                    self._add_relation_pair(relation_weights, members[ia], members[ib], base_weight)

        mouse_edges = {
            ("1", "2"): 22.0,
            ("1", "3"): 16.0,
            ("2", "3"): 14.0,
            ("2", "4"): 6.0,
            ("1", "5"): 6.0,
            ("4", "5"): 4.0,
        }
        for (a, b), weight in mouse_edges.items():
            self._add_relation_pair(
                relation_weights,
                self.mouse_button_sids.get(a),
                self.mouse_button_sids.get(b),
                weight,
            )

        self.relationship_pairs = [
            (a, b, w) for (a, b), w in sorted(relation_weights.items())
        ]
        if self.relationship_pairs:
            self.relationship_sid_a = np.array([p[0] for p in self.relationship_pairs], dtype=np.int64)
            self.relationship_sid_b = np.array([p[1] for p in self.relationship_pairs], dtype=np.int64)
            self.relationship_weight = np.array([p[2] for p in self.relationship_pairs], dtype=np.float32)
        else:
            self.relationship_sid_a = np.array([], dtype=np.int64)
            self.relationship_sid_b = np.array([], dtype=np.int64)
            self.relationship_weight = np.array([], dtype=np.float32)

    def _build_distance_matrix(self):
        n = self.n_positions
        self.dist_matrix = np.full((n, n), 99.0, dtype=np.float32)
        for i in range(n):
            for j in range(i, n):
                pi, pj = self.positions[i], self.positions[j]
                if pi.layer != pj.layer:
                    continue
                if (pi.x in LEFT_COLS) != (pj.x in LEFT_COLS):
                    continue
                d = abs(pi.x - pj.x) + abs(pi.y - pj.y)
                self.dist_matrix[i, j] = d
                self.dist_matrix[j, i] = d

    def _build_zmk_compat(self):
        self.zmk_incompat = set()
        self.zmk_incompat_arr = np.zeros(self.n_shortcuts + 1, dtype=np.float32)
        for s in self.pool:
            if s.zmk_parameter and s.zmk_parameter.startswith("Keyboard "):
                if s.zmk_parameter not in KNOWN_KEY_NAMES:
                    self.zmk_incompat.add(s.sid)
                    self.zmk_incompat_arr[s.sid] = 1.0

    def _build_layer_context_mask(self):
        """No-op: layer context emerges from app-coherence reward, not violations."""
        pass

    def _build_app_coherence_data(self):
        """Precompute per-shortcut app sets for the app-coherence reward.
        Shortcuts sharing an app on the same layer get a bonus, naturally
        creating layer themes without a hardcoded layer-app context table."""
        self.shortcut_app_sets = {}
        self.shortcut_primary_app = {}
        for s in self.pool:
            if s.category == "base_key":
                continue
            apps = set(s.apps) if s.apps else {s.app}
            self.shortcut_app_sets[s.sid] = apps
            self.shortcut_primary_app[s.sid] = s.app if s.app in apps else sorted(apps)[0]

    def _build_mouse_accessibility_data(self):
        """Precompute mouse button SIDs and ideal L2 left-hand positions for
        the mouse accessibility reward. MB1/2/3 get strong reward for being
        on L2, left hand, low effort, and grouped together."""
        import re
        self.mouse_button_sids = {}  # maps mb number to sid
        for s in self.pool:
            mb_match = re.search(r"select:mb([1-5])", s.keys.lower())
            if mb_match:
                mb_num = mb_match.group(1)
                self.mouse_button_sids[mb_num] = s.sid
        self.mouse_button_required_sids = set(self.mouse_button_sids.values())
        self.mouse_left_low_effort = {}
        for i, p in enumerate(self.positions):
            if p.layer in self.left_hand_mouse_layers and p.hand == "left" and p.effort <= 3:
                self.mouse_left_low_effort.setdefault(p.layer, []).append(i)

    def _build_layer_demand(self):
        """Compute demand per layer dynamically from usage data.

        NOT hardcoded to layer-app mappings. Layer demand comes from:
        1. layer_sessions: how often the user actually activates each layer
        2. shortcut usage: aggregate importance * usage_boost of shortcuts
           actually placed on each layer (computed per-genome in _layer_demand_penalty)
        3. app_time_seconds: mapped to app IDs for per-shortcut weighting

        This builds the app_demand lookup; per-layer demand is computed dynamically
        from the genome in _layer_demand_for_genome()."""
        PROCESS_TO_APP = {
            "claude.exe": "browser",
            "msedge.exe": "browser",
            "chrome.exe": "browser",
            "firefox.exe": "browser",
            "code.exe": "vscode",
            "windowsterminal.exe": "terminal",
            "explorer.exe": "explorer",
            "searchhost.exe": "windows",
            "taskmgr.exe": "windows",
            "teams.exe": "teams",
            "msteams.exe": "teams",
            "outlook.exe": "outlook",
            "excel.exe": "excel",
            "winword.exe": "word",
            "powerpnt.exe": "powerpoint",
            "discord.exe": "discord",
        }

        app_time = self.usage_stats.get("app_time_seconds", {})
        self.app_demand = {}
        for proc, secs in app_time.items():
            app_id = PROCESS_TO_APP.get(proc.lower(), proc.lower().replace(".exe", ""))
            self.app_demand[app_id] = self.app_demand.get(app_id, 0.0) + secs
        total_time = sum(self.app_demand.values()) or 1.0
        self.app_demand_frac = {app: t / total_time for app, t in self.app_demand.items()}

        self.layer_session_counts = {}
        layer_sessions = self.usage_stats.get("layer_sessions", {})
        session_total = sum(ls.get("count", 0) for ls in layer_sessions.values()) or 1.0
        for layer_str, ls in layer_sessions.items():
            self.layer_session_counts[int(layer_str)] = ls.get("count", 0) / session_total

        # Precompute per-shortcut app demand weight
        self.shortcut_app_demand = np.zeros(self.n_shortcuts + 1, dtype=np.float32)
        for s in self.pool:
            apps = set(s.apps) if s.apps else {s.app}
            demand = sum(self.app_demand_frac.get(a, 0.0) for a in apps)
            self.shortcut_app_demand[s.sid] = demand

        # Placeholder: _layer_demand_for_genome computes per-genome
        self.layer_demand = {}

    def _build_l0_open_position_data(self):
        """Mark mutable L0 thumb positions as premium slots.

        L0 thumbs are the highest-value positions: direct access, thumb
        reachable, no layer switch needed. They should hold structural keys:
        coach holds, mouse buttons, layer switches, modifiers, spacebar-tier
        controls. Raw content keys (arrows, F-keys, punctuation) do not
        belong here even if they have high importance.
        """
        N = self.n_positions
        S = self.n_shortcuts
        self.l0_open_pos_arr = np.zeros(N, dtype=np.float32)
        for i, pos in enumerate(self.positions):
            if pos.layer == 0 and pos.is_thumb and not is_frozen_l0_position(pos):
                self.l0_open_pos_arr[i] = 1.0

        # SIDs that are "L0 thumb worthy" — structural/access keys
        self.l0_thumb_worthy = np.zeros(S + 1, dtype=np.float32)
        for s in self.pool:
            if is_l0_thumb_worthy_shortcut(s):
                self.l0_thumb_worthy[s.sid] = 1.0

    def _layer_demand_for_genome(self, genome):
        """Compute per-layer demand from a specific genome's shortcut placement.

        Each layer's demand = sum of (importance * usage_boost * app_demand)
        for all shortcuts placed on it, normalized. Layers with many important,
        frequently-used, high-app-demand shortcuts get high demand."""
        layer_scores = {}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            layer = self.positions[i].layer
            if layer == 0:
                continue
            score = (self.importance_arr[sid] *
                     self.usage_boost[sid] *
                     max(self.shortcut_app_demand[sid], 0.1))
            layer_scores[layer] = layer_scores.get(layer, 0.0) + score

        # Add session-based demand (what the user actually uses)
        for layer, session_frac in self.layer_session_counts.items():
            layer_scores[layer] = layer_scores.get(layer, 0.0) + session_frac * 50.0

        # Normalize to 0-1 range
        max_score = max(layer_scores.values()) if layer_scores else 1.0
        if max_score <= 0:
            max_score = 1.0
        return {layer: score / max_score for layer, score in layer_scores.items()}

    def _classify_mouse_layers(self):
        """Classify layers by mouse-mode capability from LAYER_ACCESS properties.

        Left-hand mouse layers: left-thumb momentary — right hand free for trackball.
        Synthetic mouse layers: toggled OR left-thumb momentary — right hand near
        keyboard AND trackball, one-handed browsing.
        Right-thumb momentary: BAD for mouse — right thumb holds layer key,
        blocking trackball use.
        """
        self.left_hand_mouse_layers = set()
        self.right_thumb_momentary_layers = set()
        for layer, info in LAYER_ACCESS.items():
            method = info.get("method", "")
            thumb = info.get("thumb")
            if thumb == "left" and "momentary" in method:
                self.left_hand_mouse_layers.add(layer)
            if thumb == "right" and "momentary" in method:
                self.right_thumb_momentary_layers.add(layer)
        self.synthetic_mouse_layers = self.left_hand_mouse_layers | self.toggled_layers
        self.any_mouse_layers = self.left_hand_mouse_layers | self.synthetic_mouse_layers

    def _build_thumb_busy_penalty(self):
        """Extra effort for thumb-cluster keys on momentary layers where the
        same-hand thumb is busy holding the layer key.

        Penalty tiers:
        - Same x-column as hold key: +5.0 (physically the same key, impossible)
        - Same hand, different column: +2.0 (awkward but reachable)
        - momentary_or_locked layers (L2): half penalty (user often toggles)
        """
        # Derive hold key x-column from current genome: find where coach_l*_hold sits on L0
        hold_key_x = {}
        layer_hold_names = {1: 'coach_l1_hold', 2: 'coach_l2_hold',
                            3: 'coach_l3_hold', 4: 'coach_l4_hold'}
        if self.current_genome is not None:
            for i, pos in enumerate(self.positions):
                if pos.layer != 0 or not pos.is_thumb:
                    continue
                sid = self.current_genome[i]
                if sid < 0:
                    continue
                key_name = self.pool[sid].keys
                for layer_num, hold_name in layer_hold_names.items():
                    if key_name == f'_base_{hold_name}':
                        hold_key_x[layer_num] = pos.x

        N = self.n_positions
        self.thumb_busy_extra = np.zeros(N, dtype=np.float32)
        for i, pos in enumerate(self.positions):
            if not pos.is_thumb:
                continue
            access = LAYER_ACCESS.get(pos.layer)
            if not access or access["method"] not in ("momentary", "momentary_or_locked"):
                continue
            thumb_hand = access.get("thumb")
            if thumb_hand is None:
                continue
            pos_hand = THUMB_HAND.get(pos.x)
            if pos_hand != thumb_hand:
                continue
            hx = hold_key_x.get(pos.layer)
            if hx is not None and pos.x == hx:
                penalty = 5.0  # same physical key as hold
            else:
                penalty = 2.0  # adjacent thumb, awkward
            if access["method"] == "momentary_or_locked":
                penalty *= 0.5  # user often locks L2
            self.thumb_busy_extra[i] = penalty

    def _build_layer_importance_multipliers(self):
        """Per-position importance multiplier based on layer mouse capability.
        Left-hand mouse layers: left hand does everything while right hand is
        on trackball. Left-hand shortcuts get 2.5x, right-hand 0.5x.
        Synthetic mouse layers: both hands available, no bias (1.0x)."""
        N = self.n_positions
        self.layer_imp_mult = np.ones(N, dtype=np.float32)
        mouse_bonus_w = self.weights.get("mouse_layer_bonus", 5.0)
        for i, pos in enumerate(self.positions):
            if pos.layer in self.left_hand_mouse_layers:
                if pos.hand == "left":
                    self.layer_imp_mult[i] = 2.5
                else:
                    self.layer_imp_mult[i] = 0.5

    def _build_original_dupe_exempt(self):
        """Track same-layer (layer, sid) pairs that are intentionally duplicated.
        The reference genome is the baseline for normal and scratch runs, so
        duplicates already present there should not make the seed look broken.
        Only duplicates introduced beyond this baseline are violations."""
        self.original_layer_sid_counts = {}
        if self.current_genome is not None:
            from collections import Counter
            for layer in set(p.layer for p in self.positions):
                layer_sids = []
                for i, sid in enumerate(self.current_genome):
                    if sid >= 0 and self.positions[i].layer == layer:
                        layer_sids.append(int(sid))
                counts = Counter(layer_sids)
                for sid, cnt in counts.items():
                    if cnt > 1:
                        self.original_layer_sid_counts[(layer, sid)] = cnt

    def _build_mouse_protection(self):
        """Identify mouse button and clipboard positions on mouse-capable layers.
        These resist displacement to preserve one-handed mouse mode."""
        self.mouse_protected_sids = set()
        self.mouse_protected_positions = set()
        if self.current_genome is None:
            return
        for i, sid in enumerate(self.current_genome):
            if sid < 0 or self.positions[i].layer not in self.any_mouse_layers:
                continue
            s = self.pool[sid]
            is_mouse_button = 'select:mb' in s.keys
            is_clipboard = s.keys in ('Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X', 'Ctrl+A')
            if is_mouse_button or is_clipboard:
                self.mouse_protected_sids.add(sid)
                self.mouse_protected_positions.add(i)

    def _build_toggled_layer_effort(self):
        """Add extra effort cost for toggled layers (L5, L9, L10).
        Toggled layers cost 3 keypresses for isolated use (toggle on, press, toggle off).
        Momentary layers cost 0 extra (thumb hold is already modeled)."""
        N = self.n_positions
        self.toggled_layer_extra = np.zeros(N, dtype=np.float32)
        for i, pos in enumerate(self.positions):
            access = LAYER_ACCESS.get(pos.layer)
            if access and access["method"] == "toggled":
                self.toggled_layer_extra[i] = 1.0  # +1.0 on top of existing effort

    def _build_toggled_base_requirement(self):
        """Precompute: for each exit-required layer, which positions exist and
        which SIDs are coach_base/coach_recover_base (return-to-L0 keys)."""
        self.toggled_layer_indices = {}
        self.coach_base_sids = set()
        for s in self.pool:
            if s.keys in ('_base_coach_base', '_base_coach_recover_base', '_base_coach_travel_off'):
                self.coach_base_sids.add(s.sid)
        for layer in self.exit_required_layers:
            indices = [i for i, p in enumerate(self.positions)
                       if p.layer == layer]
            if indices:
                self.toggled_layer_indices[layer] = indices

    def _build_structural_capability_data(self):
        """Capability target/mode arrays used for structural duplicate scoring."""
        from layer_access import shortcut_capability
        S = self.n_shortcuts
        self.struct_cap_target_arr = np.full(S + 1, -1, dtype=np.int32)
        self.struct_cap_mode_arr = np.full(S + 1, -1, dtype=np.int32)
        self.struct_cap_mode_ids = {}
        probe_pos = self.positions[0] if self.positions else Position(
            gene_idx=0, layer=0, x=0, y=0, coord="0:0",
            effort=0.0, hand="left", finger="pinky", is_thumb=False,
        )
        for s in self.pool:
            cap = shortcut_capability(s, probe_pos)
            if not cap:
                continue
            mode_id = self.struct_cap_mode_ids.setdefault(cap.mode, len(self.struct_cap_mode_ids))
            self.struct_cap_target_arr[s.sid] = cap.target
            self.struct_cap_mode_arr[s.sid] = mode_id
        self.struct_exit_to_base_mode_id = self.struct_cap_mode_ids.get("exit_to_base", -1)

    def _capability_sid_set(self):
        """SIDs that express layer-access capability and may legitimately repeat."""
        if hasattr(self, "_cap_sid_set"):
            return self._cap_sid_set
        from layer_access import shortcut_capability
        self._cap_sid_set = set()
        probe_pos = self.positions[0] if self.positions else Position(
            gene_idx=0, layer=0, x=0, y=0, coord="0:0",
            effort=0.0, hand="left", finger="pinky", is_thumb=False,
        )
        for s in self.pool:
            if shortcut_capability(s, probe_pos):
                self._cap_sid_set.add(s.sid)
        return self._cap_sid_set

    def _build_frozen_l0_duplicate_data(self):
        """Precompute frozen L0 SIDs that should not be duplicated elsewhere.

        Frozen positions are determined by physical keyboard layout, not by
        key names. The main grid (y=0-3) and two specific thumb positions
        are frozen. All other L0 thumb positions are mutable — the optimizer
        decides what goes there via importance scores.
        """
        self.frozen_l0_sids = set()
        S = self.n_shortcuts
        self.frozen_l0_sid_arr = np.zeros(S + 1, dtype=np.float32)
        self.capability_sid_arr = np.zeros(S + 1, dtype=np.float32)
        self.frozen_l0_source_pos_arr = np.zeros(self.n_positions, dtype=np.float32)
        capability_sids = self._capability_sid_set()
        for sid in capability_sids:
            self.capability_sid_arr[sid] = 1.0
        if self.current_genome is None:
            return

        for i, sid in enumerate(self.current_genome):
            if sid < 0 or not is_frozen_l0_position(self.positions[i]):
                continue
            if int(sid) in capability_sids:
                continue
            self.frozen_l0_sids.add(int(sid))
            self.frozen_l0_source_pos_arr[i] = 1.0

        for sid in self.frozen_l0_sids:
            self.frozen_l0_sid_arr[sid] = 1.0

    # Base keys that only make sense on L0 — letters, numbers, basic punctuation.
    # These produce a character when pressed and serve no purpose on layers.
    _L0_ONLY_PATTERNS = {
        '_base_a', '_base_b', '_base_c', '_base_d', '_base_e', '_base_f',
        '_base_g', '_base_h', '_base_i', '_base_j', '_base_k', '_base_l',
        '_base_m', '_base_n', '_base_o', '_base_p', '_base_q', '_base_r',
        '_base_s', '_base_t', '_base_u', '_base_v', '_base_w', '_base_x',
        '_base_y', '_base_z',
        '_base_1', '_base_2', '_base_3', '_base_4', '_base_5',
        '_base_6', '_base_7', '_base_8', '_base_9', '_base_0',
        '_base_comma', '_base_period', '_base_semicolon',
        '_base_forwardslash', '_base_backslash',
        '_base_left brace', '_base_left apos',
    }

    def _build_l0_only_base_keys(self):
        """Mark base keys that only belong on L0 (letters, numbers, punctuation).
        Defined by key identity, not current placement."""
        self.l0_only_sids = set()
        for s in self.pool:
            if s.keys in self._L0_ONLY_PATTERNS:
                self.l0_only_sids.add(s.sid)
        S = self.n_shortcuts
        self.l0_only_arr = np.zeros(S + 1, dtype=np.float32)
        for sid in self.l0_only_sids:
            self.l0_only_arr[sid] = 1.0

    def _build_thumb_vectors(self):
        """Per-position weights for thumb scoring.

        On momentary layers, the hold-thumb is busy but the opposite thumb is
        completely free. Free-thumb positions are extremely valuable — they're
        the easiest keys to press while holding a layer. Empty free-thumb
        positions are wasted prime real estate and get a heavy penalty."""
        N = self.n_positions
        self.thumb_filled_weight = np.zeros(N, dtype=np.float32)
        self.thumb_empty_weight = np.zeros(N, dtype=np.float32)
        for i, pos in enumerate(self.positions):
            if not pos.is_thumb:
                continue
            if pos.layer in self.toggled_layers:
                self.thumb_filled_weight[i] = 3.0
                self.thumb_empty_weight[i] = -1.0
            elif pos.layer in self.momentary_layers:
                access = LAYER_ACCESS.get(pos.layer)
                hold_thumb = access.get("thumb") if access else None
                if hold_thumb and pos.hand != hold_thumb:
                    # Free thumb — opposite hand from hold. Very high value.
                    self.thumb_filled_weight[i] = 5.0
                    self.thumb_empty_weight[i] = -4.0  # heavy penalty for empty
                else:
                    # Busy thumb — same hand as hold. Still worth filling if reachable.
                    self.thumb_filled_weight[i] = 1.0
                    self.thumb_empty_weight[i] = -0.5

    # =========================================================================
    # GPU BATCH EVALUATION — pure tensor, no Python loops in hot path
    # =========================================================================

    def _build_gpu_tensors(self):
        d = self.device
        S = self.n_shortcuts
        N = self.n_positions

        self.t_effort = torch.tensor(self.effort_arr, device=d)
        self.t_importance = torch.tensor(self.importance_arr, device=d)
        self.t_raw_importance = torch.tensor(self.raw_importance_arr, device=d)
        self.t_usage_boost = torch.tensor(self.usage_boost, device=d)
        self.t_finger = torch.tensor(self.finger_arr, device=d, dtype=torch.long)
        finger_ext = np.append(self.finger_arr, -1)
        self.t_finger_ext = torch.tensor(finger_ext, device=d, dtype=torch.long)
        self.t_hand = torch.tensor(self.hand_arr, device=d, dtype=torch.long)
        self.t_layer = torch.tensor(self.layer_arr, device=d, dtype=torch.long)
        layer_ext = np.append(self.layer_arr, 0)
        self.t_layer_ext = torch.tensor(layer_ext, device=d, dtype=torch.long)
        self.t_is_thumb = torch.tensor(self.is_thumb_arr, device=d)
        self.t_x_arr = torch.tensor(self.x_arr, device=d, dtype=torch.long)
        self.t_y_arr = torch.tensor(self.y_arr, device=d, dtype=torch.long)
        self.t_dist_matrix = torch.tensor(self.dist_matrix, device=d)
        self.t_zmk_incompat = torch.tensor(self.zmk_incompat_arr, device=d)
        self.t_pos_idx = torch.arange(N, device=d)
        self.t_batch_arange_cache = {}
        self.gpu_sid_occurrence_slots = int(self.config.get("gpu_sid_occurrence_slots", 24))

        # App coherence GPU data: stable primary app ID per shortcut
        unique_apps = sorted(set(self.shortcut_primary_app.values()))
        app_to_id = {app: i for i, app in enumerate(unique_apps)}
        self._n_unique_apps = len(unique_apps)
        primary_app_arr = np.full(S + 1, -1, dtype=np.int64)
        for sid, app in self.shortcut_primary_app.items():
            primary_app_arr[sid] = app_to_id[app]
        self.t_primary_app_id = torch.tensor(primary_app_arr, device=d, dtype=torch.long)
        self.t_thumb_filled_w = torch.tensor(self.thumb_filled_weight, device=d)
        self.t_thumb_empty_w = torch.tensor(self.thumb_empty_weight, device=d)
        self.t_layer_imp_mult = torch.tensor(self.layer_imp_mult, device=d)
        self.t_thumb_busy_extra = torch.tensor(self.thumb_busy_extra, device=d)
        self.t_toggled_extra = torch.tensor(self.toggled_layer_extra, device=d)

        # Mouse/clipboard protection mask for GPU learning curve
        mouse_prot = np.zeros(N, dtype=np.float32)
        for idx in self.mouse_protected_positions:
            mouse_prot[idx] = 1.0
        self.t_mouse_protected = torch.tensor(mouse_prot, device=d)
        layer_type_bonus = np.full(N, 1.5, dtype=np.float32)
        for i, p in enumerate(self.positions):
            if p.layer in self.toggled_layers:
                layer_type_bonus[i] = 2.5
        self.t_cl_position_weight = torch.tensor(layer_type_bonus, device=d)

        # 3-tier shortcut tier multipliers for GPU learning curve
        # tier_mult[sid]: 0.3 for simple L0-accessible, 1.0 for complex L0-accessible, 1.5 for layer-only
        tier_mult = np.ones(S + 1, dtype=np.float32)
        for s in self.pool:
            if s.sid in self.base_accessible_sids and self._shortcut_complexity(s.sid) <= 1.0:
                tier_mult[s.sid] = 0.3
            elif s.sid not in self.base_accessible_sids:
                tier_mult[s.sid] = 1.5
        self.t_tier_mult = torch.tensor(tier_mult, device=d)

        # For momentary redundancy: mask of complex (3+ key) base-accessible shortcuts
        complex_base = np.zeros(S + 1, dtype=np.float32)
        for s in self.pool:
            if s.sid in self.base_accessible_sids and self._shortcut_complexity(s.sid) >= 1.8:
                complex_base[s.sid] = 1.0
        self.t_complex_base = torch.tensor(complex_base, device=d)

        base_return = np.zeros(S + 1, dtype=np.float32)
        for sid in self.coach_base_sids:
            base_return[sid] = 1.0
        self.t_base_return_sid = torch.tensor(base_return, device=d)

        # Complexity discount per shortcut (S+1 sentinel)
        complexity_arr = np.ones(S + 1, dtype=np.float32)
        for s in self.pool:
            complexity_arr[s.sid] = 1.0 / self._shortcut_complexity(s.sid)
        self.t_complexity_discount = torch.tensor(complexity_arr, device=d)

        # Base key mask for learning curve scaling on non-L0 layers
        is_base_key = np.zeros(S + 1, dtype=np.float32)
        for s in self.pool:
            if s.category == 'base_key':
                is_base_key[s.sid] = 1.0
        self.t_is_base_key = torch.tensor(is_base_key, device=d)

        # L0-only base keys: letters/numbers that should never appear on non-L0 layers
        self.t_l0_only = torch.tensor(self.l0_only_arr, device=d)
        self.t_frozen_l0_sid = torch.tensor(self.frozen_l0_sid_arr, device=d)
        self.t_capability_sid = torch.tensor(self.capability_sid_arr, device=d)
        self.t_frozen_l0_source_pos = torch.tensor(self.frozen_l0_source_pos_arr, device=d)
        self.t_l0_open_pos = torch.tensor(self.l0_open_pos_arr, device=d)
        self.t_l0_thumb_worthy = torch.tensor(self.l0_thumb_worthy, device=d)
        self.t_struct_cap_target = torch.tensor(self.struct_cap_target_arr, device=d, dtype=torch.long)
        self.t_struct_cap_mode = torch.tensor(self.struct_cap_mode_arr, device=d, dtype=torch.long)
        mouse_related = np.zeros(S + 1, dtype=np.float32)
        for s in self.pool:
            if (s.app in ("windows",) and
                any(kw in s.action.lower() for kw in ("click", "scroll", "mouse", "drag", "snap", "move"))):
                mouse_related[s.sid] = 1.0
        self.t_mouse_related = torch.tensor(mouse_related, device=d)

        # Layer switch cost matrix and layer utilization
        self.t_layer_switch_cost = torch.tensor(self.layer_switch_cost_matrix, device=d)
        self.t_layer_util = torch.tensor(self.layer_util_arr, device=d)
        self.t_layer_usage_mult = torch.tensor(self.layer_usage_mult, device=d)
        self.t_shortcut_app_demand = torch.tensor(self.shortcut_app_demand, device=d)

        # Conjunction pair tensors
        if len(self.conj_pairs) > 0:
            self.t_conj_sid_a = torch.tensor(self.conj_sid_a, device=d, dtype=torch.long)
            self.t_conj_sid_b = torch.tensor(self.conj_sid_b, device=d, dtype=torch.long)
            self.t_conj_weight = torch.tensor(self.conj_weight, device=d)

        # Proximity matrix: prox[i,j] = max(0, 1 - dist*0.2), 0 where dist=99
        prox = np.maximum(0, 1.0 - self.dist_matrix * 0.2)
        prox[self.dist_matrix >= 99] = 0
        self.t_prox_matrix = torch.tensor(prox, device=d)

        # Hand alternation bonus matrix
        hand_bonus = np.zeros((N, N), dtype=np.float32)
        for i in range(N):
            for j in range(N):
                if self.hand_arr[i] != self.hand_arr[j] and self.dist_matrix[i, j] < 99:
                    hand_bonus[i, j] = 0.3
        self.t_hand_bonus = torch.tensor(hand_bonus, device=d)
        self.t_adj_matrix = self.t_prox_matrix + self.t_hand_bonus  # (N, N)
        self.t_adj_ext = torch.zeros(N + 1, N + 1, device=d)
        self.t_adj_ext[:N, :N] = self.t_adj_matrix
        group_neighbor = np.zeros((N, N), dtype=np.float32)
        group_manhattan = np.zeros((N, N), dtype=np.float32)
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                manhattan = abs(self.x_arr[i] - self.x_arr[j]) + abs(self.y_arr[i] - self.y_arr[j])
                group_manhattan[i, j] = manhattan
                if (self.layer_arr[i] == self.layer_arr[j] and
                    self.hand_arr[i] == self.hand_arr[j] and
                    abs(self.x_arr[i] - self.x_arr[j]) <= 1 and
                    abs(self.y_arr[i] - self.y_arr[j]) <= 1):
                    group_neighbor[i, j] = 1.0
        self.t_group_neighbor = torch.tensor(group_neighbor, device=d)
        self.t_group_manhattan = torch.tensor(group_manhattan, device=d)
        self.t_upper_tri = torch.triu(torch.ones(N, N, device=d, dtype=torch.bool), diagonal=1)

        if self.current_genome is not None:
            cur = np.array(self.current_genome, dtype=np.int64)
            cur_sentinel = cur.copy()
            cur_sentinel[cur_sentinel < 0] = S
            self.t_current_genome = torch.tensor(cur, device=d, dtype=torch.long)
            self.t_current_sids = torch.tensor(cur_sentinel, device=d, dtype=torch.long)
            self.t_current_assigned = self.t_current_genome >= 0
            self.t_current_count = self.t_current_assigned.sum().float()
        else:
            self.t_current_genome = None
            self.t_current_sids = None
            self.t_current_assigned = None
            self.t_current_count = None

        self.t_very_high_imp_sids = torch.tensor(
            [s.sid for s in self.pool if s.importance >= 9.0], device=d, dtype=torch.long
        )
        self.t_high_imp_sids = torch.tensor(
            [s.sid for s in self.pool if 3.0 <= s.importance < 9.0], device=d, dtype=torch.long
        )
        self.t_med_imp_sids = torch.tensor(
            [s.sid for s in self.pool if 1.0 <= s.importance < 3.0], device=d, dtype=torch.long
        )
        self.t_base_accessible_sids = torch.tensor(
            sorted(self.base_accessible_sids), device=d, dtype=torch.long
        )
        self.t_coach_base_sids = torch.tensor(
            sorted(self.coach_base_sids), device=d, dtype=torch.long
        )
        self.t_clipboard_sids = {
            clip_key: torch.tensor([s.sid for s in self.pool if s.keys == clip_key], device=d, dtype=torch.long)
            for clip_key in ['Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X']
        }
        self.t_nav_utility_sids = torch.tensor(
            [s.sid for s in self.pool if s.keys in {'Ctrl+A', 'Ctrl+W', 'Ctrl+Y', 'Escape', 'Enter', 'Tab', 'Delete'}],
            device=d,
            dtype=torch.long,
        )
        self.t_critical_mb_sids = torch.tensor(
            [
                self.mouse_button_sids[mb_num]
                for mb_num in ('1', '2', '3')
                if self.mouse_button_sids.get(mb_num) is not None
            ],
            device=d,
            dtype=torch.long,
        )
        self.t_all_mouse_button_sids = torch.tensor(
            sorted(self.mouse_button_required_sids), device=d, dtype=torch.long
        )
        self.t_relationship_sid_a = torch.tensor(self.relationship_sid_a, device=d, dtype=torch.long)
        self.t_relationship_sid_b = torch.tensor(self.relationship_sid_b, device=d, dtype=torch.long)
        self.t_relationship_weight = torch.tensor(self.relationship_weight, device=d)
        self.t_toggled_layer_indices = {
            layer: torch.tensor(layer_idxs, device=d, dtype=torch.long)
            for layer, layer_idxs in self.toggled_layer_indices.items()
        }

        # One-hot encoding: onehot[sid, pos] = positions where sid could appear
        # For batch: genome_onehot[batch, sid, pos] built at eval time
        self.n_fingers_unique = int(max(self.finger_arr.max() + 1, 1))

        # Unique layers for duplicate detection
        self.unique_layers = sorted(set(p.layer for p in self.positions))
        layer_masks = {}
        for l in self.unique_layers:
            layer_masks[l] = torch.tensor(self.layer_arr == l, device=d, dtype=torch.bool)
        self.t_layer_masks = layer_masks
        self.t_momentary_mask = torch.zeros(N, device=d, dtype=torch.bool)
        for l in self.momentary_layers:
            if l in layer_masks:
                self.t_momentary_mask |= layer_masks[l]
        self.t_toggled_mask = torch.zeros(N, device=d, dtype=torch.bool)
        for l in self.toggled_layers:
            if l in layer_masks:
                self.t_toggled_mask |= layer_masks[l]
        self.t_pure_momentary_mask = torch.zeros(N, device=d, dtype=torch.bool)
        for l in self.pure_momentary_layers:
            if l in layer_masks:
                self.t_pure_momentary_mask |= layer_masks[l]

        self.t_is_left_mouse_layer = torch.zeros(N, device=d, dtype=torch.bool)
        for l in self.left_hand_mouse_layers:
            if l in layer_masks:
                self.t_is_left_mouse_layer |= layer_masks[l]
        self.t_is_synthetic_mouse = torch.zeros(N, device=d, dtype=torch.bool)
        for l in self.synthetic_mouse_layers:
            if l in layer_masks:
                self.t_is_synthetic_mouse |= layer_masks[l]
        self.t_is_right_thumb_mom = torch.zeros(N, device=d, dtype=torch.bool)
        for l in self.right_thumb_momentary_layers:
            if l in layer_masks:
                self.t_is_right_thumb_mom |= layer_masks[l]
        self.t_is_any_mouse_layer = self.t_is_left_mouse_layer | self.t_is_synthetic_mouse

        # Original duplicate exemption per (layer, sid)
        self.t_original_dupe_counts = {}
        for (layer, sid), cnt in self.original_layer_sid_counts.items():
            self.t_original_dupe_counts[(layer, sid)] = cnt

        # Precompute group SIDs for GPU group-split and placement checking.
        # Group split uses all declared groups; placement reward mirrors CPU and
        # uses only protected static groups plus dynamic groups.
        self._gpu_group_sids = []
        self._gpu_placement_group_sids = []
        for group in list(KEY_GROUPS) + self.dynamic_groups:
            if "behaviors" in group:
                continue
            if group.get("dynamic", False):
                group_sids = list(group.get("sids", []))
                expected_size = len(group_sids)
            else:
                group_sids = []
                for s in self.pool:
                    if shortcut_matches_group(s, group):
                        group_sids.append(s.sid)
                expected_size = len(group.get("params", []))
            if len(group_sids) >= 2:
                is_spatial = group.get("name", "") in ("arrows",)
                item = (
                    torch.tensor(group_sids, device=d, dtype=torch.long),
                    is_spatial,
                    float(group.get("weight", 1.0)),
                    float(expected_size),
                )
                self._gpu_group_sids.append(item)
                if group.get("protected") or group.get("dynamic", False):
                    self._gpu_placement_group_sids.append(item)

    @torch.no_grad()
    def _sid_position_slots_gpu(self, t_g):
        """Return (positions, counts) where positions[b, sid, k] stores up to K
        placements for each SID. Uses extra VRAM to keep adjacency exact for
        duplicated shortcuts without constructing a B x S x N one-hot tensor."""
        B, N = t_g.shape
        S = self.n_shortcuts
        K = self.gpu_sid_occurrence_slots
        d = self.device
        counts = torch.zeros(B, S + 1, device=d, dtype=torch.long)
        slots = torch.full((B, S + 1, K), N, device=d, dtype=torch.long)
        batch_idx = self.t_batch_arange_cache.get(B)
        if batch_idx is None:
            batch_idx = torch.arange(B, device=d, dtype=torch.long)
            self.t_batch_arange_cache[B] = batch_idx
        flat = slots.view(-1)
        for pos in range(N):
            sid = t_g[:, pos]
            occ = counts.gather(1, sid.unsqueeze(1)).squeeze(1)
            valid = (sid < S) & (occ < K)
            if valid.any():
                offsets = ((batch_idx[valid] * (S + 1) + sid[valid]) * K + occ[valid])
                flat[offsets] = pos
            counts.scatter_add_(1, sid.unsqueeze(1), torch.ones(B, 1, device=d, dtype=torch.long))
        slots[:, S, :] = N
        counts[:, S] = 0
        return slots, counts

    @torch.no_grad()
    def evaluate_batch_gpu(self, genomes_list, prebuilt_np=None):
        """Evaluate entire population on GPU. Returns list of (effort, -adj, viol).

        If prebuilt_np is provided (int32 ndarray, -1 for empty), skips the
        expensive list-of-lists → numpy conversion."""
        if prebuilt_np is not None:
            B = prebuilt_np.shape[0]
        else:
            B = len(genomes_list)
        N = self.n_positions
        S = self.n_shortcuts
        d = self.device

        # Convert genomes: -1 → S (sentinel for empty), stale SIDs → S for
        # safe tensor indexing. Rows with stale SIDs are hard-invalidated below.
        if prebuilt_np is not None:
            raw_np = prebuilt_np.astype(np.int64)
        else:
            raw_np = np.array(genomes_list, dtype=np.int64)
        invalid_sid_rows = ((raw_np < -1) | (raw_np >= S)).any(axis=1)
        g_np = raw_np.copy()
        g_np[g_np < 0] = S
        g_np[g_np > S] = S
        t_g = torch.tensor(g_np, device=d, dtype=torch.long)  # (B, N)
        assigned = (t_g < S)  # (B, N) bool
        assigned_f = assigned.float()
        sid_slots = sid_counts = None
        if self.exact_gpu_scoring:
            sid_slots, sid_counts = self._sid_position_slots_gpu(t_g)

        # ── EFFORT ──
        imp = self.t_importance[t_g]        # (B, N)
        usage = self.t_usage_boost[t_g]     # (B, N)
        eff = (self.t_effort + self.t_thumb_busy_extra + self.t_toggled_extra).unsqueeze(0)  # (1, N)
        layer_mult = self.t_layer_imp_mult.unsqueeze(0)  # (1, N)
        # Quadratic effort scaling for important shortcuts: e^1.5 for imp>=7, e^2 for imp>=9
        eff_scaled = torch.where(imp >= 9.0, eff ** 2.0,
                     torch.where(imp >= 7.0, eff ** 1.5, eff))
        layer_util = self.t_layer_util.unsqueeze(0)  # (1, N)
        weighted = eff_scaled * imp * usage * layer_mult * layer_util * assigned_f
        effort_raw = weighted.sum(dim=1) * self.weights.get("effort", 1.0)

        # Finger balance: load per finger via scatter_add
        finger_ids = self.t_finger.unsqueeze(0).expand(B, -1)  # (B, N)
        finger_loads = torch.zeros(B, self.n_fingers_unique, device=d)
        finger_loads.scatter_add_(1, finger_ids, imp * assigned_f)
        fb_mean = finger_loads.mean(dim=1, keepdim=True)
        finger_balance = ((finger_loads - fb_mean) ** 2).mean(dim=1).sqrt() * self.weights.get("finger_balance", 0.8)

        # Same-finger penalty: for each conjunction pair, check if both sids
        # are placed on the same finger. Use sid->position lookup table.
        sfp = torch.zeros(B, device=d)
        if len(self.conj_pairs) > 0:
            if self.exact_gpu_scoring:
                CHUNK = 500
                for start in range(0, len(self.conj_pairs), CHUNK):
                    end = min(start + CHUNK, len(self.conj_pairs))
                    ca = self.t_conj_sid_a[start:end]
                    cb = self.t_conj_sid_b[start:end]
                    cw = self.t_conj_weight[start:end]
                    pa = sid_slots[:, ca, :]
                    pb = sid_slots[:, cb, :]
                    pair_valid = (pa < N).unsqueeze(3) & (pb < N).unsqueeze(2)
                    fa = self.t_finger_ext[pa].unsqueeze(3)
                    fb = self.t_finger_ext[pb].unsqueeze(2)
                    la = self.t_layer_ext[pa].unsqueeze(3)
                    lb = self.t_layer_ext[pb].unsqueeze(2)
                    not_self_pair = (ca != cb).unsqueeze(0).unsqueeze(2).unsqueeze(3)
                    same = pair_valid & not_self_pair & (fa == fb) & (fa >= 0) & (la == lb)
                    pair_penalty = same.float().sum(dim=(2, 3)) * cw.unsqueeze(0) * 0.5
                    sfp += pair_penalty.sum(dim=1)
            else:
                sid_finger = torch.full((B, S + 1), -1, device=d, dtype=torch.long)
                sid_layer = torch.full((B, S + 1), -1, device=d, dtype=torch.long)
                sid_finger.scatter_(1, t_g, self.t_finger.unsqueeze(0).expand(B, -1))
                sid_layer.scatter_(1, t_g, self.t_layer.unsqueeze(0).expand(B, -1))
                sid_finger[:, S] = -1
                sid_layer[:, S] = -1
                CHUNK = 500
                for start in range(0, len(self.conj_pairs), CHUNK):
                    end = min(start + CHUNK, len(self.conj_pairs))
                    ca = self.t_conj_sid_a[start:end]
                    cb = self.t_conj_sid_b[start:end]
                    cw = self.t_conj_weight[start:end]
                    fa = sid_finger.gather(1, ca.unsqueeze(0).expand(B, -1))
                    fb = sid_finger.gather(1, cb.unsqueeze(0).expand(B, -1))
                    la = sid_layer.gather(1, ca.unsqueeze(0).expand(B, -1))
                    lb = sid_layer.gather(1, cb.unsqueeze(0).expand(B, -1))
                    not_self_pair = (ca != cb).unsqueeze(0)
                    same = ((fa == fb) & not_self_pair & (fa >= 0) & (la == lb) & (la >= 0)).float()
                    sfp += (same * cw.unsqueeze(0) * 0.5).sum(dim=1)

        sfp *= self.weights.get("same_finger_penalty", 2.0)

        # Hard floor: penalize genomes that removed too many assignments
        unassign_effort = torch.zeros(B, device=d)
        if self.t_current_genome is not None:
            cur_t_e = self.t_current_genome
            cur_count = self.t_current_count
            now_count = assigned.sum(dim=1).float()
            min_ratio = 0.85
            below_floor = (now_count < cur_count * min_ratio).float()
            # Catastrophic penalty for going below floor
            unassign_effort += below_floor * 50000.0
            # Proportional penalty folded into effort for any removal
            cur_assigned_e = self.t_current_assigned
            now_empty_e = ~assigned
            removed_e = cur_assigned_e.unsqueeze(0) & now_empty_e
            cur_imp_e = self.t_importance[self.t_current_sids]
            unassign_effort += (removed_e.float() * (2.0 + cur_imp_e.unsqueeze(0).pow(2) * 1.0)).sum(dim=1)

        # Learning curve: penalize changes from current layout
        lc = torch.zeros(B, device=d)
        if self.t_current_genome is not None:
            cur_t_lc = self.t_current_genome
            cur_sids_lc = self.t_current_sids
            cur_imp_lc = self.t_importance[cur_sids_lc]  # (N,)
            changed = (t_g != cur_t_lc.unsqueeze(0))  # (B, N)
            cur_had = self.t_current_assigned.unsqueeze(0)  # (1, N)
            now_has = assigned  # (B, N)
            # Swaps: both had and have something, but different
            swapped = changed & cur_had & now_has  # (B, N)
            imp_sq = cur_imp_lc.unsqueeze(0).pow(2)
            swap_cost = (1.0 + cur_imp_lc.unsqueeze(0) * 0.5 + imp_sq * 0.01) * swapped.float()
            # L2 mouse/clipboard protection
            swap_cost += (cur_imp_lc.unsqueeze(0) * 100.0) * (swapped.float() * self.t_mouse_protected.unsqueeze(0))
            # 3-tier multiplier (skip on mouse layers — all keys there are important)
            is_mouse = self.t_is_any_mouse_layer.unsqueeze(0).float()
            tier_per_pos = self.t_tier_mult[cur_sids_lc].unsqueeze(0)  # (1, N)
            tier_adjusted = torch.where(is_mouse > 0, torch.ones_like(tier_per_pos), tier_per_pos)
            swap_cost *= tier_adjusted
            # Base keys on non-L0 layers get 0.5× learning curve
            is_l0 = (self.t_layer == 0).unsqueeze(0)  # (1, N)
            is_base = self.t_is_base_key[cur_sids_lc].unsqueeze(0)  # (1, N)
            base_on_layer = (~is_l0).float() * is_base * swapped.float()
            swap_cost *= (1.0 - base_on_layer * 0.5)  # multiply by 0.5 where base_on_layer
            # Nearby displacement discount: if old sid moved to nearby same-layer pos, 80% off
            # Skip L0 (touch typing muscle memory) and L2 protected positions (mouse buttons)
            pos_idx = self.t_pos_idx.unsqueeze(0).expand(B, -1)
            old_sids_exp = cur_sids_lc.unsqueeze(0).expand(B, -1).long()  # (B, N)
            if self.exact_gpu_scoring:
                new_slots_of_old = sid_slots.gather(
                    1,
                    old_sids_exp.unsqueeze(2).expand(-1, -1, self.gpu_sid_occurrence_slots),
                )  # (B, N, K)
                slot_valid = new_slots_of_old < N
                new_pos_clamp = new_slots_of_old.clamp(max=N-1)
                same_layer_slots = (self.t_layer[new_pos_clamp] == self.t_layer.unsqueeze(0).unsqueeze(2)) & slot_valid
                manhattan = (self.t_x_arr[new_pos_clamp] - self.t_x_arr.unsqueeze(0).unsqueeze(2)).abs() + \
                            (self.t_y_arr[new_pos_clamp] - self.t_y_arr.unsqueeze(0).unsqueeze(2)).abs()
                not_self = (new_slots_of_old != pos_idx.unsqueeze(2))
                nearby_any = (same_layer_slots & (manhattan <= 3) & not_self).any(dim=2)
            else:
                sid_pos_lc = torch.full((B, S + 1), N, device=d, dtype=torch.long)
                sid_pos_lc.scatter_(1, t_g, pos_idx)
                new_pos_of_old = sid_pos_lc.gather(1, old_sids_exp)
                new_pos_clamp = new_pos_of_old.clamp(max=N-1)
                same_layer_near = (self.t_layer[new_pos_clamp] == self.t_layer.unsqueeze(0)) & (new_pos_of_old < N)
                manhattan = (self.t_x_arr[new_pos_clamp] - self.t_x_arr.unsqueeze(0)).abs() + \
                            (self.t_y_arr[new_pos_clamp] - self.t_y_arr.unsqueeze(0)).abs()
                not_self = (new_pos_of_old != pos_idx)
                nearby_any = same_layer_near & (manhattan <= 3) & not_self
            not_l0 = (~is_l0).float()  # (1, N)
            not_mouse_prot = (1.0 - self.t_mouse_protected.unsqueeze(0))  # (1, N)
            nearby_discount = (nearby_any & swapped).float()
            nearby_discount *= not_l0 * not_mouse_prot
            swap_cost *= (1.0 - nearby_discount * 0.8)  # multiply by 0.2 where nearby
            # Removals: had something, now empty
            removed_lc = changed & cur_had & ~now_has
            remove_cost = (3.0 + cur_imp_lc.unsqueeze(0) * 1.0 + imp_sq * 0.02) * removed_lc.float()
            remove_cost += (cur_imp_lc.unsqueeze(0) * 150.0) * (removed_lc.float() * self.t_mouse_protected.unsqueeze(0))
            # Additions: was empty, now has something
            added = changed & ~cur_had & now_has
            add_cost = 0.3 * added.float()
            lc = (swap_cost + remove_cost + add_cost).sum(dim=1)
        lc *= self.weights.get("learning_curve", 0.5)

        # Placement reward: placing important shortcuts reduces net effort
        layer_for_pos = self.t_layer.unsqueeze(0).expand(B, -1)
        layer_usage_for_pos = self.t_layer_usage_mult[t_g, layer_for_pos]
        placement_reward = (imp * assigned_f * 8.0 * layer_usage_for_pos).sum(dim=1)
        pw_weight = float(self.weights.get("position_waste", 5.0))
        prime_mask = (self.t_effort <= 1.5).unsqueeze(0).float()
        position_waste = (
            (6.0 - imp).clamp(min=0).pow(2) *
            (2.0 - self.t_effort.unsqueeze(0)).clamp(min=0) *
            pw_weight *
            assigned_f
        ).sum(dim=1)
        # Empty prime positions (eff<=1.5) are worse than any filled position
        # when unplaced shortcuts exist. Penalize empty prime positions.
        empty_prime = prime_mask * (1.0 - assigned_f) * (self.t_layer.unsqueeze(0) > 0).float()
        position_waste += (empty_prime * 30.0 * pw_weight).sum(dim=1)
        eff_over = (eff - 2.0).clamp(min=0)
        extreme_mult = 1.0 + (eff_over >= 3.0).float() * 2.0
        high_imp_misplacement = (
            (imp >= 8.0).float() *
            eff_over.pow(2) * extreme_mult *
            imp *
            float(self.weights.get("high_importance_misplacement", 1.5)) *
            assigned_f
        ).sum(dim=1)
        importance_alignment = (
            (imp - 4.0).clamp(min=0) *
            (4.0 - eff).clamp(min=0) *
            float(self.weights.get("importance_effort_alignment", 2.5)) *
            assigned_f
        ).sum(dim=1)
        effort_total = (
            effort_raw + position_waste + high_imp_misplacement +
            finger_balance + sfp + unassign_effort + lc -
            placement_reward - importance_alignment
        )

        # ── ADJACENCY ──
        # For each conjunction pair (a,b,w): look up where a and b are placed,
        # then index into the adjacency matrix. Uses sid->position lookup.
        adj_scores = torch.zeros(B, device=d)
        if len(self.conj_pairs) > 0:
            if self.exact_gpu_scoring:
                CHUNK = int(self.config.get("gpu_adjacency_chunk", 32))
                for start in range(0, len(self.conj_pairs), CHUNK):
                    end = min(start + CHUNK, len(self.conj_pairs))
                    ca = self.t_conj_sid_a[start:end]
                    cb = self.t_conj_sid_b[start:end]
                    cw = self.t_conj_weight[start:end]
                    pa = sid_slots[:, ca, :]  # (B, C, K)
                    pb = sid_slots[:, cb, :]  # (B, C, K)
                    pair_valid = (pa < N).unsqueeze(3) & (pb < N).unsqueeze(2)
                    adj_pair_vals = self.t_adj_ext[
                        pa.unsqueeze(3).expand(-1, -1, -1, pb.shape[2]),
                        pb.unsqueeze(2).expand(-1, -1, pa.shape[2], -1),
                    ]
                    adj_pair_vals = torch.where(pair_valid, adj_pair_vals, torch.zeros_like(adj_pair_vals))
                    adj_vals = adj_pair_vals.amax(dim=(2, 3))  # CPU best_prox

                    layer_switch_w = self.weights.get("layer_switch_penalty", 0.5)
                    if layer_switch_w > 0:
                        la = self.t_layer_ext[pa].unsqueeze(3).expand(-1, -1, -1, pb.shape[2])
                        lb = self.t_layer_ext[pb].unsqueeze(2).expand(-1, -1, pa.shape[2], -1)
                        switch_pair = self.t_layer_switch_cost[la, lb]
                        switch_pair = torch.where(
                            pair_valid,
                            switch_pair,
                            torch.full_like(switch_pair, 1_000_000.0),
                        )
                        min_switch = switch_pair.amin(dim=(2, 3))
                        both_placed = (sid_counts[:, ca] > 0) & (sid_counts[:, cb] > 0)
                        switch_penalty = (adj_vals == 0) & both_placed
                        adj_vals = adj_vals - switch_penalty.float() * min_switch * layer_switch_w

                    adj_scores += (adj_vals * cw.unsqueeze(0)).sum(dim=1)
            else:
                sid_pos = torch.full((B, S + 1), N, device=d, dtype=torch.long)
                sid_pos.scatter_(1, t_g, self.t_pos_idx.unsqueeze(0).expand(B, -1))
                sid_pos[:, S] = N
                CHUNK = 500
                for start in range(0, len(self.conj_pairs), CHUNK):
                    end = min(start + CHUNK, len(self.conj_pairs))
                    ca = self.t_conj_sid_a[start:end]
                    cb = self.t_conj_sid_b[start:end]
                    cw = self.t_conj_weight[start:end]
                    pa = sid_pos.gather(1, ca.unsqueeze(0).expand(B, -1))
                    pb = sid_pos.gather(1, cb.unsqueeze(0).expand(B, -1))
                    adj_vals = self.t_adj_ext[pa.reshape(-1), pb.reshape(-1)].reshape(B, -1)

                    layer_switch_w = self.weights.get("layer_switch_penalty", 0.5)
                    if layer_switch_w > 0:
                        la = self.t_layer_ext[pa]
                        lb = self.t_layer_ext[pb]
                        switch_cost = self.t_layer_switch_cost[la.reshape(-1), lb.reshape(-1)].reshape(B, -1)
                        both_placed = ((pa < N) & (pb < N)).float()
                        adj_vals = adj_vals - ((adj_vals == 0).float() * both_placed * switch_cost * layer_switch_w)

                    adj_scores += (adj_vals * cw.unsqueeze(0)).sum(dim=1)

        # Thumb utilization
        thumb_filled = assigned_f * self.t_thumb_filled_w.unsqueeze(0)
        thumb_empty = (1.0 - assigned_f) * self.t_thumb_empty_w.unsqueeze(0)
        thumb_util = thumb_filled.sum(dim=1) + thumb_empty.sum(dim=1)

        # Cross-layer consistency: reward same sid at same physical position across layers
        # Uses scatter_reduce to find min/max coord per SID without per-SID loops
        cl_bonus = torch.zeros(B, device=d)
        coord_ids = self.t_x_arr * 100 + self.t_y_arr
        safe_g = t_g.clamp(min=0, max=S)
        coord_f = (coord_ids.unsqueeze(0).float() + 1.0) * assigned_f  # +1 so 0,0 coord != unassigned

        # Per-SID count, min coord, max coord via scatter_reduce
        sid_count_cl = torch.zeros(B, S + 1, device=d)
        sid_count_cl.scatter_add_(1, safe_g, assigned_f)
        sid_coord_min = torch.full((B, S + 1), 99999.0, device=d)
        sid_coord_min.scatter_reduce_(1, safe_g, torch.where(assigned, coord_f, torch.tensor(99999.0, device=d)), reduce="amin", include_self=True)
        sid_coord_max = torch.full((B, S + 1), -1.0, device=d)
        sid_coord_max.scatter_reduce_(1, safe_g, torch.where(assigned, coord_f, torch.tensor(-1.0, device=d)), reduce="amax", include_self=True)
        # Per-SID max position weight
        sid_pw = torch.zeros(B, S + 1, device=d)
        sid_pw.scatter_reduce_(1, safe_g, (self.t_cl_position_weight.unsqueeze(0) * assigned_f), reduce="amax", include_self=True)

        multi = (sid_count_cl[:, :S] >= 2)
        same_coord = (sid_coord_min[:, :S] == sid_coord_max[:, :S]) & multi
        # Weight by shortcut importance: high-importance cross-layer consistency
        # (e.g. Ctrl+C at same position across layers) is much more valuable
        imp_per_sid = self.t_importance[:S].unsqueeze(0).clamp(min=1.0) * 0.5
        cl_bonus = (same_coord.float() * sid_count_cl[:, :S] * sid_pw[:, :S] * imp_per_sid).sum(dim=1)

        # Trackball proximity: right-hand keys on synthetic mouse layers
        # get bonus (right hand near keyboard AND trackball). Left-hand mouse
        # layers get no right-hand bonus (right hand is on trackball, not keyboard).
        tb_bonus = torch.zeros(B, device=d)
        synth_right_mask = self.t_is_synthetic_mouse.unsqueeze(0) & (self.t_hand.unsqueeze(0) == 1) & assigned
        tb_bonus = (synth_right_mask.float() * imp * 0.2).sum(dim=1)
        right_non_mouse = (self.t_hand.unsqueeze(0) == 1) & \
                          (~self.t_is_any_mouse_layer).unsqueeze(0) & \
                          (self.t_y_arr.unsqueeze(0) >= 2) & \
                          (self.t_mouse_related[t_g] > 0) & assigned
        tb_bonus += (right_non_mouse.float() * imp * 0.1).sum(dim=1)

        # App coherence: reward shortcuts sharing primary app on same layer
        ac_bonus = torch.zeros(B, device=d)
        if hasattr(self, 't_primary_app_id'):
            app_ids_per_pos = self.t_primary_app_id[t_g]  # (B, N)
            n_apps = self._n_unique_apps
            # Encode (layer, app) as single index for scatter_add
            layer_app_idx = self.t_layer.unsqueeze(0) * n_apps + app_ids_per_pos.clamp(min=0)  # (B, N)
            n_la = len(self.unique_layers) * n_apps + n_apps
            valid_app = (app_ids_per_pos >= 0) & assigned
            # Count per (layer, app)
            la_count = torch.zeros(B, n_la, device=d)
            la_count.scatter_add_(1, layer_app_idx, valid_app.float())
            # Importance sum per (layer, app)
            la_imp = torch.zeros(B, n_la, device=d)
            la_imp.scatter_add_(1, layer_app_idx, (imp * valid_app.float()))
            # Reward clusters of 2+
            has_cluster = (la_count >= 2).float()
            avg_imp = la_imp / la_count.clamp(min=1)
            ac_bonus = (has_cluster * la_count * avg_imp * 0.3).sum(dim=1)

        # Mouse accessibility: reward functional mouse modes
        # Left-hand mode: left-thumb momentary, right hand on trackball
        # Synthetic mode: toggled or left-momentary, right hand near keyboard+trackball
        ma_bonus = torch.zeros(B, device=d)
        mb_weights = {'1': 2.0, '2': 1.5, '3': 1.0, '4': 0.3, '5': 0.3}
        is_lhm = self.t_is_left_mouse_layer.unsqueeze(0)
        is_synth = self.t_is_synthetic_mouse.unsqueeze(0)
        is_right_mom = self.t_is_right_thumb_mom.unsqueeze(0)
        is_left = (self.t_hand.unsqueeze(0) == 0)
        low_eff = (self.t_effort <= 2).unsqueeze(0)
        med_eff = ((self.t_effort > 2) & (self.t_effort <= 3)).unsqueeze(0)

        lhm_mb_count = torch.zeros(B, device=d)
        for mb_num, mb_w in mb_weights.items():
            mb_sid = self.mouse_button_sids.get(mb_num)
            if mb_sid is None:
                if mb_num in ('1', '2', '3'):
                    ma_bonus -= torch.full((B,), 40.0 * mb_w, device=d)
                continue
            mb_mask = (t_g == mb_sid) & assigned
            has_any = mb_mask.any(dim=1).float()
            on_lhm = mb_mask & is_lhm
            on_lhm_left = on_lhm & is_left
            on_lhm_right = on_lhm & ~is_left

            if mb_num in ('1', '2', '3'):
                ma_bonus -= (1.0 - has_any) * 40.0 * mb_w
                lhm_mb_count += on_lhm.any(dim=1).float()
                # Penalty: MB1-3 on left-mouse-layer right hand (can't reach during trackball)
                ma_bonus -= on_lhm_right.any(dim=1).float() * 60.0 * mb_w
                # Penalty: MB1-3 on right-thumb momentary (blocks trackball)
                on_rtm = mb_mask & is_right_mom
                ma_bonus -= on_rtm.any(dim=1).float() * 500.0 * mb_w

            # Left-hand mouse mode: best placement per button
            left_score = (on_lhm_left.float() * (14.0 * mb_w) +
                          (on_lhm_left & low_eff).float() * (4.0 * mb_w) +
                          (on_lhm_left & med_eff).float() * (2.0 * mb_w))
            right_score = on_lhm_right.float() * (1.0 * mb_w)
            best_lhm = torch.maximum(left_score, right_score).max(dim=1).values
            ma_bonus += best_lhm

            # Synthetic mouse mode: MB on any synthetic-capable layer
            on_synth = mb_mask & is_synth
            on_synth_right = on_synth & ~is_left
            on_synth_left = on_synth & is_left
            synth_score = (on_synth_right.float() * (10.0 * mb_w) +
                           on_synth_left.float() * (6.0 * mb_w) +
                           (on_synth & low_eff).float() * (3.0 * mb_w))
            ma_bonus += synth_score.max(dim=1).values

        if self.exact_gpu_scoring and self.t_critical_mb_sids.numel() > 0:
            crit_slots = sid_slots[:, self.t_critical_mb_sids, :].reshape(B, -1)
            crit_valid = crit_slots < N
            crit_slots_clamped = crit_slots.clamp(max=N - 1)
            crit_layers = self.t_layer_ext[crit_slots]
            crit_left_mouse = self.t_is_left_mouse_layer[crit_slots_clamped] & (self.t_hand[crit_slots_clamped] == 0) & crit_valid
            crit_dist = self.t_group_manhattan[crit_slots_clamped.unsqueeze(2), crit_slots_clamped.unsqueeze(1)]
            crit_pair_valid = crit_valid.unsqueeze(2) & crit_valid.unsqueeze(1) & \
                              torch.triu(torch.ones(crit_slots.shape[1], crit_slots.shape[1], device=d, dtype=torch.bool), diagonal=1).unsqueeze(0)
            best_left_mouse_layer_count = torch.zeros(B, device=d)
            for layer_id in self.unique_layers:
                lm = crit_valid & (crit_layers == layer_id)
                n_layer = lm.sum(dim=1).float()
                ma_bonus += (n_layer >= 3).float() * 15.0
                ma_bonus += ((n_layer >= 2) & (n_layer < 3)).float() * 5.0
                left_lm = lm & crit_left_mouse
                n_left_lm = left_lm.sum(dim=1).float()
                best_left_mouse_layer_count = torch.maximum(best_left_mouse_layer_count, n_left_lm)
                ma_bonus += (n_left_lm >= 3).float() * 90.0
                ma_bonus += ((n_left_lm >= 2) & (n_left_lm < 3)).float() * 20.0
                pair_mask = lm.unsqueeze(2) & lm.unsqueeze(1) & crit_pair_valid
                close2 = pair_mask & (crit_dist <= 2)
                close3 = pair_mask & (crit_dist > 2) & (crit_dist <= 3)
                ma_bonus += close2.sum(dim=(1, 2)).float() * 4.0
                ma_bonus += close3.sum(dim=(1, 2)).float() * 2.0
            ma_bonus -= (3.0 - best_left_mouse_layer_count).clamp(min=0) * 25.0
        elif not self.exact_gpu_scoring:
            ma_bonus += (lhm_mb_count >= 3).float() * 15.0
            ma_bonus += ((lhm_mb_count >= 2) & (lhm_mb_count < 3)).float() * 5.0
            best_left_mouse_layer_count = torch.zeros(B, device=d)
            for layer_id in self.unique_layers:
                layer_left = self.t_layer_masks[layer_id].unsqueeze(0) & is_lhm & is_left & assigned
                n_left_lm = torch.zeros(B, device=d)
                for mb_num in ('1', '2', '3'):
                    mb_sid = self.mouse_button_sids.get(mb_num)
                    if mb_sid is not None:
                        n_left_lm += ((t_g == mb_sid) & layer_left).any(dim=1).float()
                best_left_mouse_layer_count = torch.maximum(best_left_mouse_layer_count, n_left_lm)
            ma_bonus += (best_left_mouse_layer_count >= 3).float() * 90.0
            ma_bonus += ((best_left_mouse_layer_count >= 2) & (best_left_mouse_layer_count < 3)).float() * 20.0
            ma_bonus -= (3.0 - best_left_mouse_layer_count).clamp(min=0) * 25.0

        # Left-hand mouse layer fill bonus
        lhm_left_filled = (assigned & is_lhm & is_left).float().sum(dim=1)
        ma_bonus += lhm_left_filled.clamp(max=15) * 1.5

        # Synthetic mouse layer fill bonus
        synth_filled = (assigned & is_synth).float().sum(dim=1)
        ma_bonus += synth_filled.clamp(max=10) * 1.0

        # Clipboard on left-hand mouse layers (left hand)
        for clip_key in ['Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X']:
            clip_sids = self.t_clipboard_sids.get(clip_key)
            if clip_sids is not None and clip_sids.numel() > 0:
                clip_mask = (t_g == clip_sids[0]) & assigned & is_lhm & is_left
                ma_bonus += clip_mask.any(dim=1).float() * 6.0

        clipboard_keys = [self.t_clipboard_sids[k][0] for k in ['Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X']
                          if self.t_clipboard_sids[k].numel() > 0]
        if clipboard_keys:
            clip_t = torch.stack(clipboard_keys)
            lhm_left_sids = t_g.masked_fill(~(assigned & is_lhm & is_left), S)
            clipboard_present = (lhm_left_sids.unsqueeze(2) == clip_t.unsqueeze(0).unsqueeze(0)).any(dim=1)
            ma_bonus += (clipboard_present.sum(dim=1) >= 3).float() * 8.0

        # Nav utility on left-hand mouse layers and synthetic mouse layers
        if self.t_nav_utility_sids.numel() > 0:
            lhm_left_sids = t_g.masked_fill(~(assigned & is_lhm & is_left), S)
            nav_present_lhm = (lhm_left_sids.unsqueeze(2) == self.t_nav_utility_sids.unsqueeze(0).unsqueeze(0)).any(dim=1)
            ma_bonus += nav_present_lhm.sum(dim=1).float() * 4.0
            synth_sids = t_g.masked_fill(~(assigned & is_synth), S)
            nav_present_synth = (synth_sids.unsqueeze(2) == self.t_nav_utility_sids.unsqueeze(0).unsqueeze(0)).any(dim=1)
            ma_bonus += nav_present_synth.sum(dim=1).float() * 2.0

        # Group placement reward: GPU approximation of _group_placement_score.
        gp_bonus = torch.zeros(B, device=d)
        if hasattr(self, '_gpu_placement_group_sids') and self._gpu_placement_group_sids:
            for group_t, _is_spatial, _group_weight, _expected_size in self._gpu_placement_group_sids:
                member_mask = torch.zeros(B, N, device=d, dtype=torch.bool)
                for gs in group_t:
                    member_mask |= (t_g == gs.item())
                member_count = member_mask.sum(dim=1).float()
                enough = member_count >= 2
                if not enough.any():
                    continue
                effort_sum = (member_mask.float() * self.t_effort.unsqueeze(0)).sum(dim=1)
                avg_effort = effort_sum / member_count.clamp(min=1)
                masked_imp = torch.where(member_mask, imp, torch.zeros_like(imp))
                max_imp = masked_imp.max(dim=1).values
                masked_usage = torch.where(member_mask, usage, torch.zeros_like(usage))
                max_usage = masked_usage.max(dim=1).values
                effort_quality = (1.0 - avg_effort / 8.0).clamp(min=0)
                gp_bonus += torch.where(enough, effort_quality * max_imp * max_usage * member_count, torch.zeros_like(gp_bonus))

        relation_bonus = torch.zeros(B, device=d)
        if self.t_relationship_sid_a.numel() > 0:
            sid_pos_rel = torch.full((B, S + 1), -1, device=d, dtype=torch.long)
            pos_idx_rel = self.t_pos_idx.unsqueeze(0).expand(B, -1)
            sid_pos_rel.scatter_reduce_(1, t_g, pos_idx_rel, reduce="amax", include_self=True)
            ca = self.t_relationship_sid_a
            cb = self.t_relationship_sid_b
            rw = self.t_relationship_weight
            pa = sid_pos_rel.gather(1, ca.unsqueeze(0).expand(B, -1))
            pb = sid_pos_rel.gather(1, cb.unsqueeze(0).expand(B, -1))
            valid = (pa >= 0) & (pb >= 0)
            pa_c = pa.clamp(min=0, max=N - 1)
            pb_c = pb.clamp(min=0, max=N - 1)
            same_layer = valid & (self.t_layer[pa_c] == self.t_layer[pb_c])
            same_hand = same_layer & (self.t_hand[pa_c] == self.t_hand[pb_c])
            dist = (self.t_x_arr[pa_c] - self.t_x_arr[pb_c]).abs() + \
                   (self.t_y_arr[pa_c] - self.t_y_arr[pb_c]).abs()
            layer_switch = self.t_layer_switch_cost[self.t_layer[pa_c], self.t_layer[pb_c]]
            near_reward = same_hand.float() * (5.0 - dist.float()).clamp(min=0) * 1.6 * rw.unsqueeze(0)
            split_hand_penalty = (same_layer & ~same_hand).float() * 3.0 * rw.unsqueeze(0)
            split_layer_penalty = (valid & ~same_layer).float() * (4.0 + layer_switch) * rw.unsqueeze(0)
            relation_bonus = (near_reward - split_hand_penalty - split_layer_penalty).sum(dim=1)

        adj_total = adj_scores * self.weights.get("adjacency", 1.5) + \
                    thumb_util * self.weights.get("thumb_utilization", 3.0) + \
                    cl_bonus * self.weights.get("cross_layer_consistency", 2.0) + \
                    tb_bonus * self.weights.get("trackball_proximity", 1.5) + \
                    gp_bonus * self.weights.get("group_placement", 2.0) + \
                    ac_bonus * self.weights.get("app_coherence", 3.0) + \
                    relation_bonus * self.weights.get("relationship_awareness", 1.0) + \
                    ma_bonus * self.weights.get("mouse_accessibility", 5.0)

        # ── VIOLATIONS ──
        # ZMK compat
        zmk_viol = (self.t_zmk_incompat[t_g] * assigned_f).sum(dim=1)

        # Duplicates per layer (importance-weighted, exempting original layout duplicates)
        dupe_viol = torch.zeros(B, device=d)
        for l in self.unique_layers:
            lmask = self.t_layer_masks[l].unsqueeze(0) & assigned  # (B, N)
            layer_sids = t_g.clone()
            layer_sids[~lmask] = S  # sentinel

            # Count occurrences per sid on this layer: (B, S+1)
            sid_counts = torch.zeros(B, S + 1, device=d)
            sid_counts.scatter_add_(1, layer_sids, torch.ones(B, N, device=d))

            # Allowed count per sid: 1 normally, or original count if intentionally duplicated
            allowed = torch.ones(S + 1, device=d)
            for (el, esid), ecnt in self.t_original_dupe_counts.items():
                if el == l:
                    allowed[esid] = ecnt

            # Excess = count - allowed; only penalize new duplicates beyond original
            excess = (sid_counts - allowed.unsqueeze(0)).clamp(min=0)  # (B, S+1)
            excess[:, S] = 0  # sentinel
            dupe_imp = self.t_importance[:S+1]
            dupe_penalty = excess * (1.0 + dupe_imp.unsqueeze(0).pow(2) * 0.5)
            dupe_viol += dupe_penalty.sum(dim=1)

        # Unassignment penalty: quadratic importance scaling
        unassign_viol = torch.zeros(B, device=d)
        if self.t_current_genome is not None:
            cur_assigned = self.t_current_assigned
            now_empty = ~assigned
            removed = cur_assigned.unsqueeze(0) & now_empty  # (B, N)
            cur_imp = self.t_importance[self.t_current_sids]
            unassign_viol = (removed.float() * (5.0 + cur_imp.unsqueeze(0).pow(2) * 2.0)).sum(dim=1)

        # Group-split violations: spatial split + group integrity (partial groups)
        group_split_viol = torch.zeros(B, device=d)
        if hasattr(self, '_gpu_group_sids') and self._gpu_group_sids:
            for group_t, is_spatial, group_weight, expected_size in self._gpu_group_sids:
                member_mask = torch.zeros(B, N, device=d, dtype=torch.bool)
                for gs in group_t:
                    member_mask |= (t_g == gs.item())
                member_count = member_mask.sum(dim=1).float()
                has_members = member_count >= 2
                if not has_members.any():
                    continue
                masked_imp = torch.where(member_mask, imp, torch.zeros_like(imp))
                max_imp = masked_imp.max(dim=1).values
                imp_scale = torch.maximum(torch.ones_like(max_imp), max_imp / 3.0)

                if not self.exact_gpu_scoring:
                    if is_spatial:
                        left_members = (member_mask & (self.t_hand.unsqueeze(0) == 0)).sum(dim=1).float()
                        right_members = member_count - left_members
                        both_hands = (left_members > 0) & (right_members > 0)
                        group_split_viol += both_hands.float() * member_count * 5.0 * group_weight * imp_scale

                    best_layer_count = torch.zeros(B, device=d)
                    for layer_id in self.unique_layers:
                        lm = self.t_layer_masks[layer_id].unsqueeze(0) & member_mask
                        layer_count = lm.sum(dim=1).float()
                        best_layer_count = torch.maximum(best_layer_count, layer_count)
                    missing = (expected_size - best_layer_count).clamp(min=0)
                    group_split_viol += has_members.float() * missing * missing * 5.0 * group_weight * imp_scale
                    complete = (best_layer_count >= expected_size).float()
                    group_split_viol -= complete * expected_size * 3.0 * group_weight
                    continue

                # Group integrity: find best CPU-equivalent cluster. Spatial
                # groups cluster by layer+hand; other groups cluster by layer.
                best_layer_count = torch.zeros(B, device=d)
                for layer_id in self.unique_layers:
                    lm = self.t_layer_masks[layer_id].unsqueeze(0) & member_mask
                    layer_count = lm.sum(dim=1).float()
                    if is_spatial:
                        for hand_id in (0, 1):
                            hand_count = (lm & (self.t_hand.unsqueeze(0) == hand_id)).sum(dim=1).float()
                            best_layer_count = torch.maximum(best_layer_count, hand_count)
                    else:
                        best_layer_count = torch.maximum(best_layer_count, layer_count)

                # Partial group penalty: quadratic for missing members.
                missing = (expected_size - best_layer_count).clamp(min=0)
                group_split_viol += has_members.float() * missing * missing * 5.0 * group_weight * imp_scale

                for layer_id in self.unique_layers:
                    lm = self.t_layer_masks[layer_id].unsqueeze(0) & member_mask
                    layer_count = lm.sum(dim=1).float()
                    layer_has_group = layer_count >= 2
                    if not layer_has_group.any():
                        continue
                    layer_imp = torch.where(lm, imp, torch.zeros_like(imp)).max(dim=1).values
                    layer_imp_scale = torch.maximum(torch.ones_like(layer_imp), layer_imp / 3.0)

                    if is_spatial:
                        left_count = (lm & (self.t_hand.unsqueeze(0) == 0)).sum(dim=1).float()
                        right_count = layer_count - left_count
                        both_hands = (left_count > 0) & (right_count > 0)
                        group_split_viol += both_hands.float() * layer_count * 5.0 * group_weight * layer_imp_scale

                    neighbor_counts = lm.float() @ self.t_group_neighbor
                    isolated = lm & (neighbor_counts <= 0)
                    isolated_count = torch.zeros(B, device=d)
                    for hand_id in (0, 1):
                        same_hand = lm & (self.t_hand.unsqueeze(0) == hand_id)
                        hand_count = same_hand.sum(dim=1)
                        isolated_count += (isolated & same_hand & (hand_count.unsqueeze(1) >= 2)).sum(dim=1).float()
                    group_split_viol += isolated_count * group_weight * layer_imp_scale

                    same_hand_all = ((lm & (self.t_hand.unsqueeze(0) == 0)).sum(dim=1).eq(layer_count)) | \
                                    ((lm & (self.t_hand.unsqueeze(0) == 1)).sum(dim=1).eq(layer_count))
                    exact_size = layer_count.eq(expected_size) & (expected_size >= 2)
                    pair_dist = torch.where(
                        lm.unsqueeze(1) & lm.unsqueeze(2),
                        self.t_group_manhattan.unsqueeze(0),
                        torch.zeros(1, device=d),
                    )
                    max_dist = pair_dist.amax(dim=(1, 2))
                    complete = exact_size & same_hand_all & (max_dist <= expected_size)
                    group_split_viol -= complete.float() * expected_size * 3.0 * group_weight

        # Missing important shortcuts penalty — use scatter to check presence
        missing_viol = torch.zeros(B, device=d)
        # Build per-SID presence: count > 0 means present
        safe_g_m = t_g.clamp(min=0, max=S)
        sid_present = torch.zeros(B, S + 1, device=d, dtype=torch.bool)
        sid_present.scatter_(1, safe_g_m, assigned)
        if self.t_very_high_imp_sids.numel() > 0:
            vh_t = self.t_very_high_imp_sids
            vh_imp = self.t_raw_importance[vh_t]
            present_vh = sid_present[:, vh_t]
            missing_viol += ((~present_vh).float() * (vh_imp * vh_imp).unsqueeze(0) * 2.0).sum(dim=1)
        if self.t_high_imp_sids.numel() > 0:
            hi_t = self.t_high_imp_sids
            hi_imp = self.t_raw_importance[hi_t]
            present_hi = sid_present[:, hi_t]
            missing_viol += ((~present_hi).float() * (hi_imp * hi_imp).unsqueeze(0) * 0.5).sum(dim=1)
        if self.t_med_imp_sids.numel() > 0:
            med_t = self.t_med_imp_sids
            med_imp = self.t_raw_importance[med_t]
            present_m = sid_present[:, med_t]
            missing_viol += ((~present_m).float() * med_imp.unsqueeze(0) * 0.5).sum(dim=1)
        if self.t_all_mouse_button_sids.numel() > 0:
            mb_t = self.t_all_mouse_button_sids
            mb_imp = self.t_importance[mb_t].clamp(min=10.0)
            present_mb = sid_present[:, mb_t]
            missing_viol += ((~present_mb).float() * mb_imp.unsqueeze(0).pow(2) * 20.0).sum(dim=1)

        # Momentary redundancy: penalize base-accessible shortcuts on momentary layers
        # Complexity-aware: 3-key combos get reduced penalty (justified on layers)
        COGNITIVE_SWITCH_COST = 1.5
        base_sids = self.t_base_accessible_sids
        if base_sids.numel() > 0:
            is_base_accessible = (t_g.unsqueeze(2) == base_sids.unsqueeze(0).unsqueeze(0)).any(dim=2)
        else:
            is_base_accessible = torch.zeros(B, N, device=d, dtype=torch.bool)
        is_complex = (self.t_complex_base[t_g] > 0)  # 3+ key combos: skip redundancy penalty
        redundant = assigned & self.t_momentary_mask.unsqueeze(0) & is_base_accessible & ~is_complex
        eff_over = (self.t_effort.unsqueeze(0) - COGNITIVE_SWITCH_COST).clamp(min=0) * 0.3 + 1.0
        eff_under = torch.full_like(eff_over, 0.5)
        per_pos = torch.where(self.t_effort.unsqueeze(0) >= COGNITIVE_SWITCH_COST, eff_over, eff_under)
        complexity_disc = self.t_complexity_discount[t_g]  # (B, N)
        redundancy_viol = (redundant.float() * per_pos * complexity_disc).sum(dim=1)
        base_return_on_momentary = (
            assigned &
            self.t_pure_momentary_mask.unsqueeze(0) &
            (self.t_base_return_sid[t_g] > 0)
        )
        redundancy_viol += (base_return_on_momentary.float() * (10.0 + imp)).sum(dim=1)

        # Cross-layer duplicate: penalize shortcuts on 3+ layers
        # For each unique layer, create a per-sid presence mask, then count layers per sid
        cross_dupe_viol = torch.zeros(B, device=d)
        unique_layers = sorted(set(int(x) for x in self.layer_arr))
        if len(unique_layers) > 1:
            # (B, N) -> per-layer presence: for each sid, is it on this layer?
            # Encode as: for each layer, which sids are present (B, S)
            sid_layer_count = torch.zeros(B, S, device=d)
            for layer_id in unique_layers:
                if layer_id not in self.t_layer_masks:
                    continue
                lmask = self.t_layer_masks[layer_id].unsqueeze(0) & assigned  # (B, N)
                sids_on_layer = t_g.clone()
                sids_on_layer[~lmask] = S  # sentinel
                present = torch.zeros(B, S + 1, device=d)
                present.scatter_(1, sids_on_layer.clamp(max=S), 1.0)
                sid_layer_count += present[:, :S]
            sid_layer_count = sid_layer_count * (1.0 - self.t_capability_sid[:S].unsqueeze(0))
            # Penalize sids on 2+ layers — lighter for 2, escalating for 3+
            imp_s = self.t_importance[:S].unsqueeze(0)
            waste_factor = (10.0 - imp_s).clamp(min=1.0)
            # 2-layer: linear penalty (low-importance dupes waste space)
            on_two = (sid_layer_count == 2)
            cross_dupe_viol = (on_two.float() * waste_factor * 0.3).sum(dim=1)
            # 3+ layers: escalating quadratic
            excess = (sid_layer_count - 2).clamp(min=0)
            cross_dupe_viol += (excess.pow(2) * waste_factor).sum(dim=1)

        # Structural duplicate pressure: capability keys are exempt from
        # ordinary shortcut duplicate penalties, but floods of equivalent
        # layer switches on the same source layer or to the same target still
        # waste positions.
        structural_dupe_viol = torch.zeros(B, device=d)
        cap_target = self.t_struct_cap_target[t_g]
        cap_mode = self.t_struct_cap_mode[t_g]
        target_ids = [int(x) for x in np.unique(self.struct_cap_target_arr[:S]) if int(x) >= 0]
        mode_ids = [int(x) for x in np.unique(self.struct_cap_mode_arr[:S]) if int(x) >= 0]
        if target_ids and mode_ids:
            for layer_id in unique_layers:
                source_mask = self.t_layer_masks[layer_id].unsqueeze(0) & assigned
                for target_id in target_ids:
                    for mode_id in mode_ids:
                        group_mask = source_mask & (cap_target == target_id) & (cap_mode == mode_id)
                        count = group_mask.sum(dim=1).float()
                        excess = (count - 2.0).clamp(min=0.0)
                        structural_dupe_viol += excess.pow(2) * 10.0
            for target_id in target_ids:
                for mode_id in mode_ids:
                    if mode_id == getattr(self, "struct_exit_to_base_mode_id", -1):
                        continue
                    group_mask = assigned & (cap_target == target_id) & (cap_mode == mode_id)
                    count = group_mask.sum(dim=1).float()
                    excess = (count - 3.0).clamp(min=0.0)
                    structural_dupe_viol += excess.pow(2) * 10.0

        # Trackball workflow: MB1-3 and clipboard must be usable by the left
        # hand while the right hand stays on the trackball.
        mouse_workflow_viol = torch.zeros(B, device=d)
        if self.t_critical_mb_sids.numel() > 0:
            best_mb_count = torch.zeros(B, device=d)
            for layer_id in self.left_hand_mouse_layers:
                if layer_id not in self.t_layer_masks:
                    continue
                layer_left = self.t_layer_masks[layer_id].unsqueeze(0) & (self.t_hand.unsqueeze(0) == 0) & assigned
                count = torch.zeros(B, device=d)
                for mb_sid in self.t_critical_mb_sids:
                    count += ((t_g == mb_sid.item()) & layer_left).any(dim=1).float()
                best_mb_count = torch.maximum(best_mb_count, count)
            mouse_workflow_viol += (3.0 - best_mb_count).clamp(min=0).pow(2) * 300.0

        clipboard_keys = [
            self.t_clipboard_sids[k][0]
            for k in ['Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X']
            if self.t_clipboard_sids[k].numel() > 0
        ]
        if clipboard_keys:
            best_clip_count = torch.zeros(B, device=d)
            for layer_id in self.left_hand_mouse_layers:
                if layer_id not in self.t_layer_masks:
                    continue
                layer_left = self.t_layer_masks[layer_id].unsqueeze(0) & (self.t_hand.unsqueeze(0) == 0) & assigned
                count = torch.zeros(B, device=d)
                for clip_sid in clipboard_keys:
                    count += ((t_g == clip_sid.item()) & layer_left).any(dim=1).float()
                best_clip_count = torch.maximum(best_clip_count, count)
            mouse_workflow_viol += (3.0 - best_clip_count).clamp(min=0).pow(2) * 80.0

        # Layer redundancy: penalize pairs where the same app dominates both layers.
        # Mixed layers are allowed; this targets "four VS Code layers" style collapse.
        layer_redund_viol = torch.zeros(B, device=d)
        app_ids_by_pos = self.t_primary_app_id[t_g]  # -1 for base/sentinel
        profile_layers = [l for l in unique_layers if l not in (0, 7) and l in self.t_layer_masks]
        if self._n_unique_apps > 0 and len(profile_layers) > 1:
            dominant_apps = {}
            dominant_ratios = {}
            layer_totals = {}
            for layer_id in profile_layers:
                lmask = self.t_layer_masks[layer_id].unsqueeze(0) & assigned & (app_ids_by_pos >= 0)
                total = lmask.sum(dim=1).float()
                layer_totals[layer_id] = total
                app_counts = torch.zeros(B, self._n_unique_apps, device=d)
                safe_apps = app_ids_by_pos.clamp(min=0)
                app_counts.scatter_add_(1, safe_apps, lmask.float())
                top_counts, top_apps = app_counts.max(dim=1)
                dominant_apps[layer_id] = top_apps
                dominant_ratios[layer_id] = top_counts / total.clamp(min=1.0)

            for idx, la in enumerate(profile_layers):
                for lb in profile_layers[idx + 1:]:
                    same_app = dominant_apps[la] == dominant_apps[lb]
                    dominant = (dominant_ratios[la] > 0.7) & (dominant_ratios[lb] > 0.7)
                    enough_content = (layer_totals[la] >= 4) & (layer_totals[lb] >= 4)
                    excess = torch.minimum(dominant_ratios[la], dominant_ratios[lb]) - 0.7
                    pair_strength = (excess.clamp(min=0) * 10.0).pow(2)
                    pair_size = torch.minimum(layer_totals[la], layer_totals[lb]).clamp(max=12.0)
                    layer_redund_viol += (same_app & dominant & enough_content).float() * pair_strength * pair_size

        dupe_weight = self.weights.get("duplicate", 10.0)
        group_split_weight = self.weights.get("group_split", 50.0)
        viol_total = \
                     zmk_viol * self.weights.get("zmk_compatibility", 20.0) + \
                     dupe_viol * dupe_weight + \
                     unassign_viol * self.weights.get("unassignment", 15.0) + \
                     missing_viol * self.weights.get("missing_important", 15.0) + \
                     group_split_viol * group_split_weight + \
                     redundancy_viol * self.weights.get("momentary_redundancy", 5.0) + \
                     cross_dupe_viol * self.weights.get("cross_layer_duplicate", 8.0) + \
                     structural_dupe_viol * self.weights.get("structural_duplicate", 10.0) + \
                     mouse_workflow_viol * self.weights.get("violations", 10.0) + \
                     layer_redund_viol * self.weights.get("layer_redundancy", 12.0)

        # Toggled layer base requirement: penalize toggled layers without coach_base anywhere
        toggled_base_viol = torch.zeros(B, device=d)
        if self.toggled_layer_indices and self.t_coach_base_sids.numel() > 0:
            base_sids = self.t_coach_base_sids
            for layer, lidx in self.t_toggled_layer_indices.items():
                layer_sids = t_g[:, lidx]
                has_base = (layer_sids.unsqueeze(2) == base_sids.unsqueeze(0).unsqueeze(0)).any(dim=2).any(dim=1)
                toggled_base_viol += (~has_base).float() * 5000.0
        viol_total += toggled_base_viol * self.weights.get("violations", 10.0)

        # L0-only base key displacement: letters/numbers on non-L0 layers
        l0_only_flags = self.t_l0_only[t_g]  # (B, N) — 1.0 if L0-only key
        not_l0_layer = (self.t_layer != 0).unsqueeze(0).float()  # (1, N)
        displaced = l0_only_flags * not_l0_layer * assigned_f
        l0_displace_viol = (displaced * (50.0 + imp * 2.0)).sum(dim=1)
        viol_total += l0_displace_viol * self.weights.get("violations", 10.0)

        # Frozen-L0 duplicates: keys already present in locked L0 should not
        # occupy any mutable position, including open L0 thumb slots.
        duplicate_candidate_pos = (1.0 - self.t_frozen_l0_source_pos).unsqueeze(0)
        frozen_l0_dupes = self.t_frozen_l0_sid[t_g] * assigned_f * duplicate_candidate_pos
        frozen_l0_dupe_viol = (frozen_l0_dupes * (50.0 + imp * 5.0)).sum(dim=1)
        viol_total += frozen_l0_dupe_viol * self.weights.get("violations", 10.0)

        # L0 open position premium: L0 mutable thumbs are for structural keys
        # (coach holds, mouse buttons, modifiers, layer switches). Content keys
        # (arrows, F-keys, shortcuts) do not belong here regardless of importance.
        l0_open = self.t_l0_open_pos.unsqueeze(0)  # (1, N)
        worthy = self.t_l0_thumb_worthy[t_g]  # (B, N) — 1.0 if key belongs on L0 thumb
        unworthy_on_open = l0_open * assigned_f * (1.0 - worthy)
        l0_open_viol = (unworthy_on_open * 2500.0).sum(dim=1)
        empty_l0_open = l0_open * (1.0 - assigned_f)
        l0_open_viol += (empty_l0_open * 500.0).sum(dim=1)
        viol_total += l0_open_viol * self.weights.get("violations", 10.0)

        e = effort_total.cpu().numpy()
        a = adj_total.cpu().numpy()
        v = viol_total.cpu().numpy()
        if self.access_analyzer:
            self._batch_access_penalties(genomes_list, prebuilt_np, t_g, imp, usage, assigned, e, a, v, B, N, S, d)
        if invalid_sid_rows.any():
            e[invalid_sid_rows] = HARD_INVALID_FITNESS
            a[invalid_sid_rows] = 0.0
            v[invalid_sid_rows] = HARD_INVALID_FITNESS
        valid_for_coupling = (e < HARD_INVALID_FITNESS) & (v < HARD_INVALID_FITNESS)
        e = np.where((v > 10000) & valid_for_coupling, e + v * 0.5, e)
        # Build result list using numpy column stacking for speed
        result_arr = np.column_stack([e, -a, v])
        return [tuple(row) for row in result_arr]

    def _batch_access_penalties(self, genomes_list, prebuilt_np, t_g, imp, usage, assigned, e, a, v, B, N, S, d):
        """Cached layer access validation + fully GPU-vectorized penalties."""
        if not hasattr(self, '_t_is_cap_sid'):
            self._init_capability_cache()

        analyzer = self.access_analyzer
        cache = self._validation_cache

        # Build compact cache keys: only capability placements affect layer
        # access, so cache the sorted (position, sid) pairs instead of a full
        # 559-position masked genome.
        cap_mask_gpu = self._t_is_cap_sid[t_g.clamp(min=0, max=S)]
        cap_mask_gpu = cap_mask_gpu & (t_g >= 0) & (t_g < S)
        cap_mask_np = cap_mask_gpu.cpu().numpy()
        sid_np = t_g.cpu().numpy().astype(np.int16, copy=False)
        cap_keys = []
        fixed_fp = self._fixed_capability_fingerprint
        for row in range(B):
            pos_idx = np.flatnonzero(cap_mask_np[row]).astype(np.int16, copy=False)
            if pos_idx.size == 0:
                cap_keys.append(fixed_fp)
                continue
            pairs = np.column_stack((pos_idx, sid_np[row, pos_idx])).astype(np.int16, copy=False)
            cap_keys.append(fixed_fp + pairs.tobytes())

        # For validate() calls: get genome as list from either source
        def _get_genome_list(idx):
            if genomes_list is not None:
                return genomes_list[idx]
            row = prebuilt_np[idx]
            return row.tolist()

        # Validate with cache
        validations = [None] * B
        unique_keys = {}
        hits = 0
        for i, key in enumerate(cap_keys):
            if key in cache:
                validations[i] = cache[key]
                cache.move_to_end(key)
                hits += 1
            elif key in unique_keys:
                unique_keys[key].append(i)
            else:
                unique_keys[key] = [i]

        for key, indices in unique_keys.items():
            val = analyzer.validate(_get_genome_list(indices[0]))
            cache[key] = val
            cache.move_to_end(key)
            for i in indices:
                validations[i] = val

        self._last_cache_hits = hits
        self._last_cache_misses = len(unique_keys)

        self._trim_validation_cache()

        # Build cost/depth matrices
        n_lm = int(self.layer_arr.max()) + 1
        invalid_mask = np.zeros(B, dtype=bool)
        cost_matrix = np.zeros((B, n_lm), dtype=np.float32)
        depth_matrix = np.full((B, n_lm), 99.0, dtype=np.float32)

        for i, val in enumerate(validations):
            if not val.valid:
                invalid_mask[i] = True
                continue
            cached_arrays = getattr(val, "_optimizer_arrays", None)
            if cached_arrays is None:
                cv = np.zeros(n_lm, dtype=np.float32)
                dv = np.full(n_lm, 99.0, dtype=np.float32)
                for layer, c in val.access_costs.items():
                    if layer < n_lm:
                        cv[layer] = c
                depths = val.access_depths or {}
                for layer, dep in depths.items():
                    if layer < n_lm:
                        dv[layer] = dep
                cached_arrays = (cv, dv)
                try:
                    val._optimizer_arrays = cached_arrays
                except Exception:
                    pass
            cost_matrix[i], depth_matrix[i] = cached_arrays

        e[invalid_mask] = HARD_INVALID_FITNESS
        a[invalid_mask] = 0.0
        v[invalid_mask] = HARD_INVALID_FITNESS

        valid_mask = ~invalid_mask
        if not valid_mask.any():
            return

        t_cost = torch.tensor(cost_matrix, device=d)

        # GPU vectorized access effort: access_cost[layer] * importance * usage
        lae_w = self.weights.get("layer_access_effort", 1.0)
        access_cost_per_pos = t_cost[:, self.t_layer]
        access_effort = (access_cost_per_pos * imp * usage * assigned.float()).sum(dim=1) * lae_w
        ae_np = access_effort.cpu().numpy()
        e[valid_mask] += ae_np[valid_mask]

        # GPU vectorized layer demand penalty — single scatter_add, no per-layer loop
        ld_w = self.weights.get("layer_demand", 2.0)
        if ld_w > 0:
            app_demand = self.t_shortcut_app_demand[t_g].clamp(min=0.1)
            per_pos_score = imp * usage * app_demand * assigned.float()
            # Zero out L0 positions (CPU skips layer 0)
            per_pos_score = per_pos_score * (self.t_layer != 0).unsqueeze(0).float()
            # scatter_add by layer: accumulate per-position scores into per-layer totals
            layer_idx = self.t_layer.unsqueeze(0).expand(B, -1)
            layer_demand = torch.zeros(B, n_lm, device=d)
            layer_demand.scatter_add_(1, layer_idx, per_pos_score)

            # Add session demand
            if hasattr(self, 'layer_session_counts'):
                for layer, frac in self.layer_session_counts.items():
                    if 0 < layer < n_lm:
                        layer_demand[:, layer] += frac * 50.0

            max_demand = layer_demand.max(dim=1, keepdim=True).values.clamp(min=1.0)
            layer_demand_norm = layer_demand / max_demand

            t_depth = torch.tensor(depth_matrix, device=d)
            depth_mult = torch.where(t_depth <= 1, torch.tensor(0.5, device=d),
                         torch.where(t_depth <= 2, torch.tensor(3.0, device=d),
                                     torch.tensor(10.0, device=d)))

            required_mask = torch.zeros(n_lm, device=d)
            if validations[0] is not None and validations[0].valid:
                for l in validations[0].required_layers:
                    if l < n_lm:
                        required_mask[l] = 1.0

            demand_penalty = (layer_demand_norm * t_cost * depth_mult * required_mask.unsqueeze(0)).sum(dim=1) * ld_w
            dp_np = demand_penalty.cpu().numpy()
            e[valid_mask] += dp_np[valid_mask]

    def _init_capability_cache(self):
        """Precompute which SIDs affect layer access."""
        import torch as _torch
        from layer_access import shortcut_capability
        self._cap_sid_set = set()
        for s in self.pool:
            for p in self.positions[:1]:
                cap = shortcut_capability(s, p)
                if cap:
                    self._cap_sid_set.add(s.sid)
                    break
        self._cap_sid_array = np.array(sorted(self._cap_sid_set), dtype=np.int32)
        self._validation_cache = OrderedDict()
        fixed_caps = []
        if self.access_analyzer is not None:
            for cap in self.access_analyzer.fixed_capabilities:
                fixed_caps.append((cap.source, cap.target, cap.mode, cap.coord, cap.fixed))
        fixed_payload = repr(sorted(fixed_caps)).encode("utf-8")
        self._fixed_capability_fingerprint = fixed_payload + b"|"
        # GPU tensor for fast cap-SID membership
        d = self.device
        is_cap = _torch.zeros(self.n_shortcuts + 1, dtype=_torch.bool, device=d)
        for sid in self._cap_sid_set:
            is_cap[sid] = True
        self._t_is_cap_sid = is_cap
        cap_pos = np.zeros(self.n_positions, dtype=bool)
        if self.current_genome is not None:
            for i, sid in enumerate(self.current_genome):
                if sid >= 0 and int(sid) in self._cap_sid_set:
                    cap_pos[i] = True
        self._t_cap_pos_idx = _torch.tensor(np.flatnonzero(cap_pos), device=d, dtype=_torch.long)

    def _capability_cache_key_for_genome(self, genome):
        if not hasattr(self, "_t_is_cap_sid"):
            self._init_capability_cache()
        pairs = [
            (int(i), int(sid))
            for i, sid in enumerate(genome)
            if 0 <= int(sid) < self.n_shortcuts and int(sid) in self._cap_sid_set
        ]
        if not pairs:
            return self._fixed_capability_fingerprint
        arr = np.array(pairs, dtype=np.int16)
        return self._fixed_capability_fingerprint + arr.tobytes()

    def _trim_validation_cache(self):
        if not hasattr(self, "_validation_cache"):
            return
        max_cache_entries = int(self.config.get("validation_cache_max_entries", 10000))
        while len(self._validation_cache) > max_cache_entries:
            self._validation_cache.popitem(last=False)

    # =========================================================================
    # SINGLE-GENOME CPU EVALUATION (used for QD, final breakdown)
    # =========================================================================

    def _has_invalid_sids(self, genome):
        g = np.asarray(genome)
        return bool(((g < -1) | (g >= self.n_shortcuts)).any())

    def evaluate(self, genome):
        genome = np.array(genome, dtype=np.int32)
        if self._has_invalid_sids(genome):
            return (HARD_INVALID_FITNESS, 0.0, HARD_INVALID_FITNESS)
        validation = self._layer_access_validation(genome)
        if validation is not None and not validation.valid:
            return (HARD_INVALID_FITNESS, 0.0, HARD_INVALID_FITNESS)
        obj1 = self._effort_score(genome)
        obj2 = self._adjacency_score(genome)
        obj3 = self._violation_score(genome)
        if obj3 > 10000:
            obj1 += obj3 * 0.5
        return (obj1, -obj2, obj3)

    def evaluate_full(self, genome):
        genome = np.array(genome, dtype=np.int32)
        invalid_sids = self._has_invalid_sids(genome)
        if invalid_sids:
            return {
                "effort": HARD_INVALID_FITNESS,
                "adjacency": 0.0,
                "violations": HARD_INVALID_FITNESS,
                "layer_access_valid": 0.0,
                "layer_exit_valid": 0.0,
                "layer_access_cost": HARD_INVALID_FITNESS,
                "layer_access_errors": "Genome contains stale/out-of-range SID",
                "sid_valid": 0.0,
            }
        validation = self._layer_access_validation(genome)
        access_valid = validation.layer_access_valid if validation else 1.0
        exit_valid = validation.layer_exit_valid if validation else 1.0
        access_cost = validation.total_access_cost if validation else 0.0
        return {
            "effort": self._effort_score(genome),
            "adjacency": self._adjacency_score(genome),
            "violations": self._violation_score(genome),
            "violation_breakdown": self.violation_breakdown(genome),
            "layer_access_valid": access_valid,
            "layer_exit_valid": exit_valid,
            "layer_access_cost": access_cost,
            "layer_access_errors": "; ".join(validation.errors) if validation and validation.errors else "",
            "layer_demand_penalty": self._layer_demand_penalty(genome, validation),
            "layer_demand": dict(self.layer_demand) if hasattr(self, 'layer_demand') else {},
            "per_layer_access_costs": dict(validation.access_costs) if validation else {},
            "per_layer_depth": dict(self.access_analyzer.access_depth(genome)) if self.access_analyzer else {},
            "finger_balance": self._finger_balance(genome),
            "same_finger_penalty": self._same_finger_penalty(genome),
            "thumb_utilization": self._thumb_utilization(genome),
            "cross_layer_consistency": self._cross_layer_consistency(genome),
            "trackball_proximity": self._trackball_proximity(genome),
            "learning_curve": self._learning_curve(genome),
            "zmk_compatibility": self._zmk_compatibility(genome),
            "unassignment_penalty": self._unassignment_penalty(genome),
        }

    def behavior_descriptors(self, genome):
        genome = np.array(genome, dtype=np.int32)
        return (self._app_balance(genome), self._thumb_util_ratio(genome))

    def _layer_demand_penalty(self, genome, validation=None):
        """Penalize high-demand layers with expensive access.

        Layer demand is computed dynamically from the genome: each layer's demand
        = aggregate importance * usage * app_demand of shortcuts placed on it.
        High-demand layers should have direct (depth=1) access from base.
        Nested access (depth>=2) for high-demand layers is expensive.
        Low-demand layers tolerate nesting."""
        if not self.access_analyzer:
            return 0.0
        if validation is None:
            validation = self.access_analyzer.validate(genome)
        if not validation.valid:
            return HARD_INVALID_FITNESS

        layer_demand = self._layer_demand_for_genome(genome)
        self.layer_demand = layer_demand  # cache for evaluate_full

        depths = self.access_analyzer.access_depth(genome)
        penalty = 0.0
        for layer in validation.required_layers:
            demand = layer_demand.get(layer, 0.0)
            depth = depths.get(layer, 99)
            access_cost = validation.access_costs.get(layer, HARD_INVALID_FITNESS)
            if depth <= 1:
                penalty += demand * access_cost * 0.5
            elif depth == 2:
                penalty += demand * access_cost * 3.0
            else:
                penalty += demand * access_cost * 10.0
        return float(penalty * self.weights.get("layer_demand", 2.0))

    def _layer_access_validation(self, genome):
        if not self.access_analyzer:
            return None
        return self.access_analyzer.validate(genome)

    def _layer_access_effort_penalty(self, genome, validation=None):
        if not self.access_analyzer:
            return 0.0
        if validation is None:
            validation = self.access_analyzer.validate(genome)
        if not validation.valid:
            return HARD_INVALID_FITNESS
        penalty = 0.0
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            layer = self.positions[i].layer
            access_cost = validation.access_costs.get(layer, HARD_INVALID_FITNESS)
            if access_cost >= HARD_INVALID_FITNESS:
                return HARD_INVALID_FITNESS
            penalty += access_cost * self.importance_arr[sid] * self.usage_boost[sid]
        return float(penalty * self.weights.get("layer_access_effort", 1.0))

    def _effort_score(self, genome):
        if self._has_invalid_sids(genome):
            return HARD_INVALID_FITNESS
        validation = self._layer_access_validation(genome)
        if validation is not None and not validation.valid:
            return HARD_INVALID_FITNESS
        w = self.weights.get("effort", 1.0)
        mask = genome >= 0
        sids = np.clip(genome, 0, self.n_shortcuts)
        eff_with_thumb = self.effort_arr + self.thumb_busy_extra + self.toggled_layer_extra
        imp_vals = self.importance_arr[sids]
        # Quadratic effort scaling for important shortcuts
        eff_scaled = np.where(imp_vals >= 9.0, eff_with_thumb ** 2.0,
                     np.where(imp_vals >= 7.0, eff_with_thumb ** 1.5, eff_with_thumb))
        total = (eff_scaled * imp_vals * self.usage_boost[sids] * self.layer_imp_mult * self.layer_util_arr * mask).sum()
        fb = self._finger_balance(genome) * self.weights.get("finger_balance", 0.8)
        sfp = self._same_finger_penalty(genome) * self.weights.get("same_finger_penalty", 2.0)
        lc = self._learning_curve(genome) * self.weights.get("learning_curve", 0.5)
        # Hard floor + proportional unassignment penalty in effort
        unassign_eff = 0.0
        if self.current_genome is not None:
            cur_count = (self.current_genome >= 0).sum()
            now_count = mask.sum()
            if now_count < cur_count * 0.85:
                unassign_eff += 50000.0
            for i in range(len(genome)):
                if self.current_genome[i] >= 0 and genome[i] < 0:
                    imp = self.importance_arr[self.current_genome[i]]
                    unassign_eff += 2.0 + imp * imp * 1.0
        placement_reward = 0.0
        for i in range(len(genome)):
            if genome[i] >= 0:
                sid = genome[i]
                layer = self.positions[i].layer
                layer_mult = self.layer_usage_mult[sid, layer] if layer < self.layer_usage_mult.shape[1] else 1.0
                placement_reward += self.importance_arr[sid] * 8.0 * layer_mult
        position_waste = self._position_waste_penalty(genome)
        high_imp_misplacement = self._high_importance_misplacement_penalty(genome)
        importance_alignment = self._importance_effort_alignment_bonus(genome)
        access_effort = self._layer_access_effort_penalty(genome, validation)
        demand_penalty = self._layer_demand_penalty(genome, validation)
        return float(
            total * w + position_waste + high_imp_misplacement +
            access_effort + demand_penalty + fb + sfp + lc + unassign_eff -
            placement_reward - importance_alignment
        )

    def _position_waste_penalty(self, genome):
        pw_weight = float(self.weights.get("position_waste", 5.0))
        penalty = 0.0
        for i, sid in enumerate(genome):
            if sid >= 0:
                penalty += max(0.0, 6.0 - self.importance_arr[sid]) ** 2 * \
                    max(0.0, 2.0 - self.effort_arr[i]) * pw_weight
            elif self.effort_arr[i] <= 1.5 and self.positions[i].layer > 0:
                penalty += 30.0 * pw_weight
        return float(penalty)

    def _high_importance_misplacement_penalty(self, genome):
        """Push critical shortcuts away from top-row/edge reach positions."""
        penalty = 0.0
        weight = float(self.weights.get("high_importance_misplacement", 1.5))
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            imp = self.importance_arr[int(sid)]
            if imp >= 8.0:
                effective_effort = (
                    self.effort_arr[i] +
                    self.thumb_busy_extra[i] +
                    self.toggled_layer_extra[i]
                )
                eff_over = max(0.0, effective_effort - 2.0)
                extreme_mult = 3.0 if eff_over >= 3.0 else 1.0
                penalty += eff_over ** 2 * extreme_mult * imp * weight
        return float(penalty)

    def _importance_effort_alignment_bonus(self, genome):
        """Small reward for spending easy positions on genuinely important keys."""
        bonus = 0.0
        weight = float(self.weights.get("importance_effort_alignment", 0.25))
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            imp = self.importance_arr[int(sid)]
            effective_effort = (
                self.effort_arr[i] +
                self.thumb_busy_extra[i] +
                self.toggled_layer_extra[i]
            )
            bonus += max(0.0, imp - 4.0) * max(0.0, 4.0 - effective_effort) * weight
        return float(bonus)

    def _adjacency_score(self, genome):
        if self._has_invalid_sids(genome):
            return 0.0
        w = self.weights.get("adjacency", 1.5)
        total = 0.0
        pos_of_sid = {}
        for i, sid in enumerate(genome):
            if sid >= 0:
                pos_of_sid.setdefault(int(sid), []).append(i)
        for sid_a, sid_b, weight in self.conj_pairs:
            positions_a = pos_of_sid.get(sid_a, [])
            positions_b = pos_of_sid.get(sid_b, [])
            best_prox = 0.0
            for pa in positions_a:
                for pb in positions_b:
                    d = self.dist_matrix[pa, pb]
                    if d < 99:
                        prox = max(0, 1.0 - d * 0.2)
                        if self.hand_arr[pa] != self.hand_arr[pb]:
                            prox += 0.3
                        best_prox = max(best_prox, prox)
            total += weight * best_prox
            # Layer-switch penalty for cross-layer pairs
            if best_prox == 0 and positions_a and positions_b:
                layer_switch_w = self.weights.get("layer_switch_penalty", 0.5)
                if layer_switch_w > 0:
                    min_cost = min(
                        self.layer_switch_cost_matrix[self.layer_arr[pa], self.layer_arr[pb]]
                        for pa in positions_a for pb in positions_b
                    )
                    total -= weight * min_cost * layer_switch_w
        thumb_bonus = self._thumb_utilization(genome) * self.weights.get("thumb_utilization", 3.0)
        cl_bonus = self._cross_layer_consistency(genome) * self.weights.get("cross_layer_consistency", 2.0)
        tb_bonus = self._trackball_proximity(genome) * self.weights.get("trackball_proximity", 1.5)
        gp_bonus = self._group_placement_score(genome) * self.weights.get("group_placement", 2.0)
        ac_bonus = self._app_coherence_score(genome) * self.weights.get("app_coherence", 3.0)
        rel_bonus = self._relationship_awareness_score(genome) * self.weights.get("relationship_awareness", 1.0)
        ma_bonus = self._mouse_accessibility_score(genome) * self.weights.get("mouse_accessibility", 5.0)
        return total * w + thumb_bonus + cl_bonus + tb_bonus + gp_bonus + ac_bonus + rel_bonus + ma_bonus

    def _relationship_awareness_score(self, genome):
        """Soft neighborhood score for related keys and shortcuts."""
        pos_of_sid = {}
        for i, sid in enumerate(genome):
            if sid >= 0:
                pos_of_sid[int(sid)] = i
        score = 0.0
        for sid_a, sid_b, weight in self.relationship_pairs:
            pa = pos_of_sid.get(int(sid_a))
            pb = pos_of_sid.get(int(sid_b))
            if pa is None or pb is None:
                continue
            pos_a = self.positions[pa]
            pos_b = self.positions[pb]
            if pos_a.layer == pos_b.layer:
                if pos_a.hand == pos_b.hand:
                    dist = abs(pos_a.x - pos_b.x) + abs(pos_a.y - pos_b.y)
                    score += max(0.0, 5.0 - dist) * 1.6 * weight
                else:
                    score -= 3.0 * weight
            else:
                switch_cost = self.layer_switch_cost_matrix[pos_a.layer, pos_b.layer]
                score -= (4.0 + switch_cost) * weight
        return float(score)

    def _violation_score(self, genome):
        if self._has_invalid_sids(genome):
            return HARD_INVALID_FITNESS
        validation = self._layer_access_validation(genome)
        if validation is not None and not validation.valid:
            return HARD_INVALID_FITNESS
        w = self.weights.get("violations", 10.0)
        total = 0.0
        # layer_context_violations removed — always 0, app coherence is reward-based
        total += self._group_split_violations(genome) * self.weights.get("group_split", 50.0)
        total += self._duplicate_violations(genome) * self.weights.get("duplicate", 10.0)
        total += self._zmk_compatibility(genome) * self.weights.get("zmk_compatibility", 20.0)
        total += self._unassignment_penalty(genome) * self.weights.get("unassignment", 15.0)
        total += self._missing_important_penalty(genome) * self.weights.get("missing_important", 15.0)
        total += self._momentary_redundancy_penalty(genome) * self.weights.get("momentary_redundancy", 5.0)
        total += self._cross_layer_duplicate_penalty(genome) * self.weights.get("cross_layer_duplicate", 8.0)
        total += self._structural_duplicate_penalty(genome) * self.weights.get("structural_duplicate", 10.0)
        total += self._mouse_workflow_violation(genome) * self.weights.get("violations", 10.0)
        total += self._layer_redundancy_penalty(genome) * self.weights.get("layer_redundancy", 12.0)
        total += self._toggled_base_violation(genome) * self.weights.get("violations", 10.0)
        total += self._l0_key_displacement_violation(genome) * self.weights.get("violations", 10.0)
        total += self._frozen_l0_duplicate_violation(genome) * self.weights.get("violations", 10.0)
        total += self._l0_open_position_penalty(genome) * self.weights.get("violations", 10.0)
        return total

    def violation_breakdown(self, genome):
        """Return weighted violation components for debugging run quality."""
        genome = np.array(genome, dtype=np.int32)
        if self._has_invalid_sids(genome):
            return {"invalid_sid": HARD_INVALID_FITNESS}
        validation = self._layer_access_validation(genome)
        if validation is not None and not validation.valid:
            return {"layer_access_invalid": HARD_INVALID_FITNESS}

        components = {
            "group_split": self._group_split_violations(genome) * self.weights.get("group_split", 50.0),
            "duplicate": self._duplicate_violations(genome) * self.weights.get("duplicate", 10.0),
            "zmk_compatibility": self._zmk_compatibility(genome) * self.weights.get("zmk_compatibility", 20.0),
            "unassignment": self._unassignment_penalty(genome) * self.weights.get("unassignment", 15.0),
            "missing_important": self._missing_important_penalty(genome) * self.weights.get("missing_important", 15.0),
            "momentary_redundancy": self._momentary_redundancy_penalty(genome) * self.weights.get("momentary_redundancy", 5.0),
            "cross_layer_duplicate": self._cross_layer_duplicate_penalty(genome) * self.weights.get("cross_layer_duplicate", 8.0),
            "structural_duplicate": self._structural_duplicate_penalty(genome) * self.weights.get("structural_duplicate", 10.0),
            "mouse_workflow": self._mouse_workflow_violation(genome) * self.weights.get("violations", 10.0),
            "layer_redundancy": self._layer_redundancy_penalty(genome) * self.weights.get("layer_redundancy", 12.0),
            "toggled_base": self._toggled_base_violation(genome) * self.weights.get("violations", 10.0),
            "l0_key_displacement": self._l0_key_displacement_violation(genome) * self.weights.get("violations", 10.0),
            "frozen_l0_duplicate": self._frozen_l0_duplicate_violation(genome) * self.weights.get("violations", 10.0),
            "l0_open_position": self._l0_open_position_penalty(genome) * self.weights.get("violations", 10.0),
        }
        components["total"] = sum(components.values())
        return {name: float(value) for name, value in components.items()}

    def _l0_open_position_penalty(self, genome):
        """Penalize non-structural keys and empty slots on L0 mutable thumbs.
        L0 thumbs are for coach holds, mouse buttons, modifiers, layer switches.
        Content keys (arrows, F-keys, shortcuts) do not belong here."""
        penalty = 0.0
        for i in range(len(genome)):
            if self.l0_open_pos_arr[i] < 1.0:
                continue
            sid = genome[i]
            if sid < 0:
                penalty += 500.0
            elif self.l0_thumb_worthy[int(sid)] < 1.0:
                penalty += 2500.0
        return penalty

    def _mouse_workflow_violation(self, genome):
        """Penalize split mouse workflows for the right-hand trackball setup."""
        best_mb_count = 0
        for layer in self.left_hand_mouse_layers:
            count = 0
            for mb_num in ("1", "2", "3"):
                mb_sid = self.mouse_button_sids.get(mb_num)
                if mb_sid is None:
                    continue
                if any(
                    int(sid) == int(mb_sid)
                    and self.positions[i].layer == layer
                    and self.positions[i].hand == "left"
                    for i, sid in enumerate(genome)
                ):
                    count += 1
            best_mb_count = max(best_mb_count, count)

        clipboard_keys = {"Ctrl+C", "Ctrl+V", "Ctrl+Z", "Ctrl+X"}
        best_clip_count = 0
        for layer in self.left_hand_mouse_layers:
            seen = set()
            for i, sid in enumerate(genome):
                if sid < 0:
                    continue
                pos = self.positions[i]
                if pos.layer == layer and pos.hand == "left":
                    key = self.pool[int(sid)].keys
                    if key in clipboard_keys:
                        seen.add(key)
            best_clip_count = max(best_clip_count, len(seen))

        penalty = max(0, 3 - best_mb_count) ** 2 * 300.0
        penalty += max(0, 3 - best_clip_count) ** 2 * 80.0
        return float(penalty)

    def _structural_duplicate_penalty(self, genome):
        """Penalize excessive equivalent layer-access keys."""
        per_source_counts = {}
        global_counts = {}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            target = int(self.struct_cap_target_arr[int(sid)])
            mode = int(self.struct_cap_mode_arr[int(sid)])
            if target < 0 or mode < 0:
                continue
            source_key = (int(self.positions[i].layer), target, mode)
            global_key = (target, mode)
            per_source_counts[source_key] = per_source_counts.get(source_key, 0) + 1
            if mode != getattr(self, "struct_exit_to_base_mode_id", -1):
                global_counts[global_key] = global_counts.get(global_key, 0) + 1
        penalty = 0.0
        for count in per_source_counts.values():
            if count > 2:
                penalty += (count - 2) ** 2 * 10.0
        for count in global_counts.values():
            if count > 3:
                penalty += (count - 3) ** 2 * 10.0
        return penalty

    def structural_capability_duplicate_summary(self, genome):
        """Return worst global capability duplicate group for logging."""
        counts = {}
        mode_names = {v: k for k, v in getattr(self, "struct_cap_mode_ids", {}).items()}
        for sid in genome:
            if sid < 0 or sid >= self.n_shortcuts:
                continue
            target = int(self.struct_cap_target_arr[int(sid)])
            mode = int(self.struct_cap_mode_arr[int(sid)])
            if target < 0 or mode < 0:
                continue
            if mode == getattr(self, "struct_exit_to_base_mode_id", -1):
                continue
            key = (target, mode)
            counts[key] = counts.get(key, 0) + 1
        if not counts:
            return {"target": None, "mode": None, "count": 0, "excess": 0}
        (target, mode), count = max(counts.items(), key=lambda kv: kv[1])
        return {
            "target": int(target),
            "mode": mode_names.get(mode, str(mode)),
            "count": int(count),
            "excess": max(0, int(count) - 3),
        }

    def _toggled_base_violation(self, genome):
        """Penalize toggled layers that lack a coach_base key anywhere on the layer.
        Missing exit = keyboard soft-lock, so penalty is near-catastrophic."""
        penalty = 0.0
        for layer, indices in self.toggled_layer_indices.items():
            has_base = any(
                genome[i] >= 0 and genome[i] in self.coach_base_sids
                for i in indices
            )
            if not has_base:
                penalty += 5000.0
        return penalty

    def _l0_key_displacement_violation(self, genome):
        """Heavy penalty for L0-only base keys (letters, numbers) appearing on non-L0 layers."""
        if not self.l0_only_sids:
            return 0.0
        penalty = 0.0
        for i, sid in enumerate(genome):
            if sid >= 0 and self.positions[i].layer != 0 and sid in self.l0_only_sids:
                penalty += 50.0 + self.importance_arr[sid] * 2.0
        return penalty

    def _frozen_l0_duplicate_violation(self, genome):
        """Penalize mutable placements of keys already present in locked L0."""
        if not self.frozen_l0_sids:
            return 0.0
        penalty = 0.0
        for i, sid in enumerate(genome):
            if sid >= 0 and int(sid) in self.frozen_l0_sids:
                if self.frozen_l0_source_pos_arr[i] > 0:
                    continue
                penalty += 50.0 + self.importance_arr[int(sid)] * 5.0
        return penalty

    def _missing_important_penalty(self, genome):
        """Penalize shortcuts from the pool that aren't placed anywhere.
        All shortcuts in the pool are on mutable layers — bare keys like Vimium j/k
        belong on non-frozen layers and must be penalized if missing."""
        assigned_sids = set(int(g) for g in genome if g >= 0)
        penalty = 0.0
        for s in self.pool:
            if s.sid in assigned_sids:
                continue
            if s.sid in getattr(self, "mouse_button_required_sids", set()):
                penalty += max(10.0, self.importance_arr[s.sid]) ** 2 * 20.0
            if s.importance >= 9.0:
                penalty += s.importance * s.importance * 2.0
            elif s.importance >= 3.0:
                penalty += s.importance * s.importance * 0.5
            elif s.importance >= 1.0:
                penalty += s.importance * 0.5
        return float(penalty)

    def _finger_balance(self, genome):
        finger_loads = {}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            f = self.finger_arr[i]
            imp = self.importance_arr[sid]
            finger_loads[f] = finger_loads.get(f, 0) + imp
        if not finger_loads:
            return 0.0
        values = list(finger_loads.values())
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(variance)

    def _same_finger_penalty(self, genome):
        pos_of_sid = {}
        for i, sid in enumerate(genome):
            if sid >= 0:
                pos_of_sid.setdefault(int(sid), []).append(i)
        penalty = 0.0
        for sid_a, sid_b, weight in self.conj_pairs:
            if sid_a == sid_b:
                continue
            for pa in pos_of_sid.get(sid_a, []):
                for pb in pos_of_sid.get(sid_b, []):
                    if self.layer_arr[pa] == self.layer_arr[pb]:
                        if self.finger_arr[pa] == self.finger_arr[pb] and self.finger_arr[pa] >= 0:
                            penalty += weight * 0.5
        return penalty

    def same_finger_offenders(self, genome, limit=10):
        """Return top same-finger conjunction conflicts for verbose logging."""
        pos_of_sid = {}
        for i, sid in enumerate(genome):
            if sid >= 0:
                pos_of_sid.setdefault(int(sid), []).append(i)
        offenders = []
        for sid_a, sid_b, weight in self.conj_pairs:
            if sid_a == sid_b:
                continue
            total = 0.0
            examples = []
            for pa in pos_of_sid.get(sid_a, []):
                for pb in pos_of_sid.get(sid_b, []):
                    if self.layer_arr[pa] == self.layer_arr[pb] and self.finger_arr[pa] == self.finger_arr[pb] and self.finger_arr[pa] >= 0:
                        total += weight * 0.5
                        if len(examples) < 2:
                            examples.append((int(pa), int(pb), int(self.layer_arr[pa]), self.positions[pa].finger))
            if total > 0:
                offenders.append({
                    "sid_a": int(sid_a),
                    "key_a": self.pool[int(sid_a)].keys,
                    "sid_b": int(sid_b),
                    "key_b": self.pool[int(sid_b)].keys,
                    "score": float(total),
                    "examples": examples,
                })
        offenders.sort(key=lambda x: -x["score"])
        return offenders[:limit]

    def _thumb_utilization(self, genome):
        bonus = 0.0
        for layer_num, lp in self.layer_positions.items():
            thumbs = [p for p in lp if p.is_thumb]
            if not thumbs:
                continue
            if layer_num in self.toggled_layers:
                filled = sum(1 for p in thumbs if genome[p.gene_idx] >= 0)
                empty = len(thumbs) - filled
                bonus += filled * 3.0 - empty * 1.0
            elif layer_num in self.momentary_layers:
                access = LAYER_ACCESS.get(layer_num)
                hold_thumb = access.get("thumb") if access else None
                for p in thumbs:
                    is_free = hold_thumb and p.hand != hold_thumb
                    if genome[p.gene_idx] >= 0:
                        bonus += 5.0 if is_free else 1.0
                    else:
                        bonus -= 4.0 if is_free else 0.5
        return bonus

    def _thumb_util_ratio(self, genome):
        total = filled = 0
        for p in self.positions:
            if p.is_thumb:
                total += 1
                if genome[p.gene_idx] >= 0:
                    filled += 1
        return filled / max(total, 1)

    def _cross_layer_consistency(self, genome):
        sid_positions = {}
        for i, sid in enumerate(genome):
            if sid >= 0:
                sid_positions.setdefault(int(sid), []).append(self.positions[i])
        bonus = 0.0
        for sid, pos_list in sid_positions.items():
            if len(pos_list) < 2:
                continue
            coords = [(p.x, p.y) for p in pos_list]
            if len(set(coords)) == 1:
                layer_types = set()
                for p in pos_list:
                    if p.layer in self.toggled_layers:
                        layer_types.add("toggled")
                    elif p.layer in self.momentary_layers:
                        layer_types.add("momentary")
                weight = 2.5 if "toggled" in layer_types else 1.5
                imp_scale = max(1.0, self.importance_arr[sid]) * 0.5
                bonus += weight * len(pos_list) * imp_scale
        return bonus

    def _trackball_proximity(self, genome):
        bonus = 0.0
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            pos = self.positions[i]
            s = self.pool[sid]
            is_mouse_related = (s.app in ("windows",) and
                any(kw in s.action.lower() for kw in ("click", "scroll", "mouse", "drag", "snap", "move")))
            if pos.hand == "right":
                if pos.layer in self.synthetic_mouse_layers:
                    bonus += self.importance_arr[sid] * 0.2
                elif is_mouse_related and pos.y >= 2 and pos.layer not in self.any_mouse_layers:
                    bonus += self.importance_arr[sid] * 0.1
        return bonus

    def _app_balance(self, genome):
        top3 = other = 0.0
        top3_apps = {"teams", "browser", "vscode"}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            score = self.effort_arr[i] * self.importance_arr[sid]
            if self.app_ids.get(int(sid), "") in top3_apps:
                top3 += score
            else:
                other += score
        total = top3 + other
        return top3 / total if total > 0 else 0.5

    def _unassignment_penalty(self, genome):
        """Heavy penalty for removing a shortcut that was assigned in the current layout.
        Scales quadratically with importance so high-value keys are strongly retained."""
        if self.current_genome is None:
            return 0.0
        penalty = 0.0
        for i in range(len(genome)):
            if self.current_genome[i] >= 0 and genome[i] < 0:
                imp = self.importance_arr[self.current_genome[i]]
                penalty += 5.0 + imp * imp * 2.0
        return penalty

    def _learning_curve(self, genome, original=None):
        ref = original if original is not None else self.current_genome
        if ref is None:
            return 0.0

        # Build position lookup for nearby displacement check
        pos_of_sid = {}
        for j in range(len(genome)):
            if genome[j] >= 0:
                pos_of_sid.setdefault(int(genome[j]), []).append(j)

        cost = 0.0
        for i in range(len(genome)):
            if genome[i] == ref[i]:
                continue
            layer = self.positions[i].layer
            if ref[i] >= 0 and genome[i] >= 0:
                imp = self.importance_arr[ref[i]]
                swap_cost = 1.0 + imp * 0.5 + imp * imp * 0.01

                # L2 mouse button / clipboard protection
                if i in self.mouse_protected_positions:
                    swap_cost += imp * 100.0

                # 3-tier shortcut value system (skip mouse layers)
                sid = ref[i]
                if layer not in self.any_mouse_layers:
                    if sid in self.base_accessible_sids and self._shortcut_complexity(sid) <= 1.0:
                        swap_cost *= 0.3
                    elif sid not in self.base_accessible_sids:
                        swap_cost *= 1.5

                # Base keys on non-L0 layers get reduced learning curve
                if layer != 0 and ref[i] >= 0:
                    s = self.pool[ref[i]]
                    if s.category == 'base_key':
                        swap_cost *= 0.5

                # Nearby displacement discount: if the displaced key moved to a
                # nearby position on the same layer, the change is barely noticeable.
                # Skip L0 (touch typing muscle memory) and L2 protected (mouse buttons).
                if layer != 0 and i not in self.mouse_protected_positions:
                    old_sid = int(ref[i])
                    new_positions = pos_of_sid.get(old_sid, [])
                    nearby = False
                    for j in new_positions:
                        if j != i and self.positions[j].layer == layer:
                            dist = abs(self.positions[j].x - self.positions[i].x) + abs(self.positions[j].y - self.positions[i].y)
                            if dist <= 3:
                                nearby = True
                                break
                    if nearby:
                        swap_cost *= 0.2

                cost += swap_cost
            elif ref[i] >= 0 and genome[i] < 0:
                imp = self.importance_arr[ref[i]]
                remove_cost = 3.0 + imp * 1.0 + imp * imp * 0.02
                if i in self.mouse_protected_positions:
                    remove_cost += imp * 150.0
                cost += remove_cost
            else:
                cost += 0.3
        return cost

    def _zmk_compatibility(self, genome):
        return float(sum(1 for i, sid in enumerate(genome) if sid >= 0 and sid in self.zmk_incompat))

    def _app_coherence_score(self, genome):
        """Reward shortcuts sharing their primary app on the same layer.
        Uses primary app only (matches GPU path)."""
        layer_app_sids = {}
        for i, sid in enumerate(genome):
            if sid < 0 or sid not in self.shortcut_app_sets:
                continue
            layer = self.positions[i].layer
            app = self.shortcut_primary_app[sid]
            key = (layer, app)
            if key not in layer_app_sids:
                layer_app_sids[key] = []
            layer_app_sids[key].append(sid)

        bonus = 0.0
        for (layer, app), sids in layer_app_sids.items():
            if len(sids) < 2:
                continue
            avg_imp = sum(self.importance_arr[s] for s in sids) / len(sids)
            bonus += len(sids) * avg_imp * 0.3
        return bonus

    def _mouse_accessibility_score(self, genome):
        """Reward functional mouse modes discovered by the optimizer.

        Left-hand mouse mode: left-thumb momentary hold, right hand on trackball.
        Left hand does MB clicks, clipboard, navigation.
        Synthetic mouse mode: toggled or left-momentary layer where right hand
        stays near keyboard AND trackball for one-handed browsing."""
        bonus = 0.0

        mb_positions = {}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            for mb_num, mb_sid in self.mouse_button_sids.items():
                if sid == mb_sid:
                    mb_positions.setdefault(mb_num, []).append((i, self.positions[i]))

        critical_mbs = ['1', '2', '3']
        mb_weights = {'1': 2.0, '2': 1.5, '3': 1.0, '4': 0.3, '5': 0.3}

        for mb_num, mb_w in mb_weights.items():
            placements = mb_positions.get(mb_num, [])
            if not placements:
                if mb_num in critical_mbs:
                    bonus -= 40.0 * mb_w
                continue

            # Left-hand mouse mode: best placement per button
            best_lhm = 0
            has_lhm_right = False
            for i, pos in placements:
                score = 0
                if pos.layer in self.left_hand_mouse_layers:
                    if pos.hand == "left":
                        score += 14.0 * mb_w
                        if pos.effort <= 2:
                            score += 4.0 * mb_w
                        elif pos.effort <= 3:
                            score += 2.0 * mb_w
                    else:
                        score += 1.0 * mb_w
                        if mb_num in critical_mbs:
                            has_lhm_right = True
                best_lhm = max(best_lhm, score)
            bonus += best_lhm
            if has_lhm_right:
                bonus -= 60.0 * mb_w

            # Synthetic mouse mode: best placement per button
            best_synth = 0
            for i, pos in placements:
                score = 0
                if pos.layer in self.synthetic_mouse_layers:
                    if pos.hand == "right":
                        score += 10.0 * mb_w
                    else:
                        score += 6.0 * mb_w
                    if pos.effort <= 2:
                        score += 3.0 * mb_w
                best_synth = max(best_synth, score)
            bonus += best_synth

            if mb_num in critical_mbs:
                # Right-thumb momentary penalty: blocks trackball
                has_rtm = any(pos.layer in self.right_thumb_momentary_layers for _, pos in placements)
                if has_rtm:
                    bonus -= 500.0 * mb_w

        # MB grouping: reward MB1/2/3 clustered together on same layer
        best_left_mouse_layer_count = 0
        for layer in set(self.positions[i].layer for _, (i, _) in
                         ((0, x) for placements in mb_positions.values() for x in placements)):
            layer_mb_pos = []
            layer_left_mouse_pos = []
            for mb_num in critical_mbs:
                for i, pos in mb_positions.get(mb_num, []):
                    if pos.layer == layer:
                        layer_mb_pos.append(pos)
                        if pos.layer in self.left_hand_mouse_layers and pos.hand == "left":
                            layer_left_mouse_pos.append(pos)
            n = len(layer_mb_pos)
            if n >= 3:
                bonus += 15.0
            elif n >= 2:
                bonus += 5.0
            n_left_mouse = len(layer_left_mouse_pos)
            best_left_mouse_layer_count = max(best_left_mouse_layer_count, n_left_mouse)
            if n_left_mouse >= 3:
                bonus += 90.0
            elif n_left_mouse >= 2:
                bonus += 20.0
            for a in range(len(layer_mb_pos)):
                for b in range(a + 1, len(layer_mb_pos)):
                    dist = abs(layer_mb_pos[a].x - layer_mb_pos[b].x) + \
                           abs(layer_mb_pos[a].y - layer_mb_pos[b].y)
                    if dist <= 2:
                        bonus += 4.0
                    elif dist <= 3:
                        bonus += 2.0
        bonus -= max(0, 3 - best_left_mouse_layer_count) * 25.0

        # Left-hand mouse mode workflow completeness
        lhm_left_shortcuts = set()
        lhm_left_count = 0
        for i in range(len(genome)):
            if genome[i] < 0:
                continue
            pos = self.positions[i]
            if pos.layer in self.left_hand_mouse_layers and pos.hand == "left":
                s = self.pool[genome[i]]
                lhm_left_shortcuts.add(s.keys)
                lhm_left_count += 1

        clipboard_keys = {'Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X'}
        clipboard_on_lhm = len(clipboard_keys & lhm_left_shortcuts)
        bonus += clipboard_on_lhm * 6.0
        if clipboard_on_lhm >= 3:
            bonus += 8.0

        nav_utility = {'Ctrl+A', 'Ctrl+W', 'Ctrl+Y', 'Escape', 'Enter', 'Tab', 'Delete'}
        nav_on_lhm = len(nav_utility & lhm_left_shortcuts)
        bonus += nav_on_lhm * 4.0
        bonus += min(lhm_left_count, 15) * 1.5

        # Synthetic mouse mode: nav utility on any synthetic-capable layer
        synth_shortcuts = set()
        synth_count = 0
        for i in range(len(genome)):
            if genome[i] < 0:
                continue
            pos = self.positions[i]
            if pos.layer in self.synthetic_mouse_layers:
                s = self.pool[genome[i]]
                synth_shortcuts.add(s.keys)
                synth_count += 1
        nav_on_synth = len(nav_utility & synth_shortcuts)
        bonus += nav_on_synth * 2.0
        bonus += min(synth_count, 10) * 1.0

        return bonus

    def _group_split_violations(self, genome):
        violations = 0
        all_groups = list(KEY_GROUPS) + self.dynamic_groups
        for group in all_groups:
            if "behaviors" in group:
                continue
            is_dynamic = group.get("dynamic", False)
            group_weight = group.get("weight", 1.0)
            expected_size = len(group.get("params", [])) if not is_dynamic else len(group.get("sids", []))

            if is_dynamic:
                gp = []
                for i, sid in enumerate(genome):
                    if sid < 0:
                        continue
                    if sid in group["sids"]:
                        gp.append(self.positions[i])
            else:
                gp = []
                for i, sid in enumerate(genome):
                    if sid < 0:
                        continue
                    s = self.pool[sid]
                    if shortcut_matches_group(s, group):
                        gp.append(self.positions[i])

            if len(gp) < 2:
                continue
            by_layer = {}
            for p in gp:
                by_layer.setdefault(p.layer, []).append(p)
            spatial_group = group.get("name", "") in ("arrows",)

            # Group integrity: find the best layer+hand cluster. For spatial
            # groups, members must be on the same hand to be usable together.
            # A partial group (3/4 arrows) is worse than 0/4 because the user
            # expects the group to be complete and reaches for the missing key.
            best_cluster_size = 0
            for layer_members in by_layer.values():
                if spatial_group:
                    by_hand = {}
                    for m in layer_members:
                        by_hand.setdefault(m.hand, []).append(m)
                    for hand_members in by_hand.values():
                        best_cluster_size = max(best_cluster_size, len(hand_members))
                else:
                    best_cluster_size = max(best_cluster_size, len(layer_members))
            if expected_size > 0 and best_cluster_size < expected_size:
                missing = expected_size - best_cluster_size
                max_imp = max((self.importance_arr[genome[p.gene_idx]]
                              for p in gp if genome[p.gene_idx] >= 0), default=1.0)
                imp_scale = max(1.0, max_imp / 3.0)
                violations += missing * missing * 5.0 * group_weight * imp_scale

            for layer, members in by_layer.items():
                if len(members) < 2:
                    continue
                max_imp = max(
                    (self.importance_arr[genome[m.gene_idx]] for m in members
                     if genome[m.gene_idx] >= 0), default=1.0
                )
                imp_scale = max(1.0, max_imp / 3.0)
                if spatial_group:
                    hands = set(m.hand for m in members)
                    if len(hands) > 1:
                        violations += len(members) * 5 * group_weight * imp_scale
                # Adjacency: each member should have at least one neighbor
                for ii in range(len(members)):
                    same_hand = [m for m in members if m.hand == members[ii].hand]
                    has_neighbor = any(
                        abs(members[ii].x - m.x) <= 1 and abs(members[ii].y - m.y) <= 1
                        for m in same_hand if m is not members[ii]
                    )
                    if not has_neighbor and len(same_hand) >= 2:
                        violations += 1 * group_weight * imp_scale

            # Completeness bonus: all members on same layer+hand = bonus
            # This goes into violations as a negative (reward)
            for layer, members in by_layer.items():
                if len(members) == expected_size and expected_size >= 2:
                    same_hand_members = [m for m in members if m.hand == members[0].hand]
                    if len(same_hand_members) == expected_size:
                        # Full group, same hand — reward
                        max_dist = 0
                        for a in range(len(members)):
                            for b in range(a+1, len(members)):
                                d = abs(members[a].x - members[b].x) + abs(members[a].y - members[b].y)
                                max_dist = max(max_dist, d)
                        if max_dist <= expected_size:
                            violations -= expected_size * 3.0 * group_weight

        return violations

    def _group_placement_score(self, genome):
        """Balanced scoring: a group of N keys placed well scores like N individual keys.

        For each protected group, compute average effort of member positions.
        Weight by group importance (max importance of members × usage boost).
        A well-placed group of 2 scores ~= 2 well-placed individual keys.
        """
        bonus = 0.0
        all_groups = [g for g in KEY_GROUPS if g.get("protected")] + self.dynamic_groups
        for group in all_groups:
            is_dynamic = group.get("dynamic", False)
            if is_dynamic:
                members = [(i, sid) for i, sid in enumerate(genome) if sid >= 0 and sid in group["sids"]]
            else:
                if "behaviors" in group:
                    continue
                members = []
                for i, sid in enumerate(genome):
                    if sid < 0:
                        continue
                    s = self.pool[sid]
                    if shortcut_matches_group(s, group):
                        members.append((i, sid))

            if len(members) < 2:
                continue

            avg_effort = sum(self.effort_arr[i] for i, _ in members) / len(members)
            max_imp = max(self.importance_arr[sid] for _, sid in members)
            max_usage = max(self.usage_boost[sid] for _, sid in members)
            group_imp = max_imp * max_usage

            effort_quality = max(0, 1.0 - avg_effort / 8.0)
            bonus += effort_quality * group_imp * len(members)
        return bonus

    def _momentary_redundancy_penalty(self, genome):
        """Penalize base-accessible shortcuts placed on momentary layers.
        On momentary layers the user holds a thumb key — releasing is low-cost
        (small cognitive context-switch, ~1.5 effort) so duplicating a shortcut
        already reachable on L0 wastes a scarce position. Toggled layers get a
        pass because round-tripping costs two toggle presses.

        Complexity scaling: 3+ key combos (Ctrl+Shift+K) are much harder on L0
        than on a layer, so the redundancy penalty is reduced proportionally.
        A 3-key combo gets 55% discount, a 4-key combo gets 60% discount."""
        COGNITIVE_SWITCH_COST = 1.5
        penalty = 0.0
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            layer = self.positions[i].layer
            if layer not in self.momentary_layers:
                continue
            if layer in self.pure_momentary_layers and sid in self.coach_base_sids:
                penalty += 10.0 + self.importance_arr[sid]
                continue
            if sid not in self.base_accessible_sids:
                continue
            complexity = self._shortcut_complexity(sid)
            if complexity >= 1.8:
                continue  # 3+ key combos belong on layers, not redundancy
            pos_effort = self.effort_arr[i]
            # Higher complexity = lower penalty (layer placement is justified)
            complexity_discount = 1.0 / complexity
            if pos_effort >= COGNITIVE_SWITCH_COST:
                raw = (pos_effort - COGNITIVE_SWITCH_COST) * 0.3 + 1.0
            else:
                raw = 0.5
            penalty += raw * complexity_discount
        return penalty

    def _duplicate_violations(self, genome):
        """Penalize same-layer duplicates, exempting intentional duplicates from the current layout."""
        from collections import Counter
        penalty = 0.0
        for layer in set(p.layer for p in self.positions):
            layer_sids = []
            for i, sid in enumerate(genome):
                if sid >= 0 and self.positions[i].layer == layer:
                    layer_sids.append(int(sid))
            counts = Counter(layer_sids)
            for sid, cnt in counts.items():
                if cnt <= 1:
                    continue
                exempt = self.original_layer_sid_counts.get((layer, sid), 1)
                excess = cnt - exempt
                if excess > 0:
                    imp = self.importance_arr[sid]
                    penalty += excess * (1.0 + imp * imp * 0.5)
        return penalty

    def _cross_layer_duplicate_penalty(self, genome):
        """Penalize shortcuts that appear on more than 2 layers.
        Escalating cost per extra copy — low-importance duplicates penalized harder
        since they waste positions that high-importance unplaced shortcuts need."""
        sid_layers = {}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            if self.capability_sid_arr[int(sid)] > 0:
                continue
            sid_layers.setdefault(int(sid), set()).add(self.positions[i].layer)
        penalty = 0.0
        for sid, layers in sid_layers.items():
            n = len(layers)
            imp = self.importance_arr[sid]
            waste_factor = max(1.0, 10.0 - imp)
            if n == 2:
                penalty += waste_factor * 0.3
            elif n > 2:
                extra = n - 2
                penalty += extra * extra * waste_factor
        return penalty

    def _layer_redundancy_penalty(self, genome):
        """Penalize multiple layers with the same dominant app identity.

        Layer identity is dynamic and descriptive. This does not penalize a layer
        for becoming Windows instead of Excel, or for being mixed. It only pushes
        back when two populated layers both become >70% the same app.
        """
        layer_app_counts = {}
        for i, sid in enumerate(genome):
            if sid < 0 or sid not in self.shortcut_primary_app:
                continue
            layer = self.positions[i].layer
            if layer in (0, 7):
                continue
            app = self.shortcut_primary_app[sid]
            counts = layer_app_counts.setdefault(layer, {})
            counts[app] = counts.get(app, 0) + 1

        profiles = {}
        for layer, counts in layer_app_counts.items():
            total = sum(counts.values())
            if total < 4:
                continue
            app, count = max(counts.items(), key=lambda item: item[1])
            ratio = count / total
            if ratio > 0.7:
                profiles[layer] = (app, ratio, total)

        penalty = 0.0
        layers = sorted(profiles)
        for idx, la in enumerate(layers):
            app_a, ratio_a, total_a = profiles[la]
            for lb in layers[idx + 1:]:
                app_b, ratio_b, total_b = profiles[lb]
                if app_a != app_b:
                    continue
                excess = min(ratio_a, ratio_b) - 0.7
                pair_size = min(total_a, total_b, 12)
                penalty += (excess * 10.0) ** 2 * pair_size
        return penalty
