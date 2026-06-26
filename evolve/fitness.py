"""12-factor fitness function for keyboard layout evolution.

Pure-tensor GPU batch evaluation — evaluates entire populations in one call
with zero Python loops in the hot path.
"""
import math
import numpy as np

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
        for s in self.pool:
            self.importance_arr[s.sid] = s.importance

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
        by_layer_shortcut = self.usage_stats.get("by_layer_shortcut", {})
        for keys, layer_counts in by_layer_shortcut.items():
            sid = None
            for s in self.pool:
                if s.keys == keys:
                    sid = s.sid
                    break
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

        # Blind spot importance boost: shortcuts the user SHOULD use but doesn't
        # get a mild importance boost to ensure they're placed accessibly
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
        self.momentary_layers = {
            layer for layer, info in LAYER_ACCESS.items()
            if "momentary" in info.get("method", "")
        }
        self._build_thumb_busy_penalty()
        self._build_layer_importance_multipliers()
        self.base_accessible_sids = self._find_base_accessible()
        self._build_zmk_compat()
        self._build_layer_context_mask()
        self._build_thumb_vectors()
        self._build_original_dupe_exempt()
        self._build_l2_mouse_protection()
        self._build_toggled_layer_effort()
        self._build_toggled_base_requirement()
        self._build_l0_only_base_keys()
        self._build_app_coherence_data()
        self._build_mouse_accessibility_data()
        self._build_layer_demand()

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
        """Layer context is no longer hardcoded. App coherence emerges from
        conjunction pairs and the app-coherence reward. The pos_violation matrix
        is zeroed — no per-position app-based violations."""
        S = self.n_shortcuts
        self.pos_violation = np.zeros((self.n_positions, S + 1), dtype=np.float32)

    def _build_app_coherence_data(self):
        """Precompute per-shortcut app sets for the app-coherence reward.
        Shortcuts sharing an app on the same layer get a bonus, naturally
        creating layer themes without hardcoded LAYER_APP_CONTEXT."""
        self.shortcut_app_sets = {}
        for s in self.pool:
            if s.category == "base_key":
                continue
            self.shortcut_app_sets[s.sid] = set(s.apps) if s.apps else {s.app}

    def _build_mouse_accessibility_data(self):
        """Precompute mouse button SIDs and ideal L2 left-hand positions for
        the mouse accessibility reward. MB1/2/3 get strong reward for being
        on L2, left hand, low effort, and grouped together."""
        self.mouse_button_sids = {}  # maps mb number to sid
        for s in self.pool:
            if 'select:mb' in s.keys:
                mb_num = s.keys.replace('_base_select:mb', '')
                self.mouse_button_sids[mb_num] = s.sid
        self.l2_left_low_effort = []
        for i, p in enumerate(self.positions):
            if p.layer == 2 and p.hand == "left" and p.effort <= 3:
                self.l2_left_low_effort.append(i)

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
        """Per-position importance multiplier based on layer context.
        L2 (Mouse) is one-handed mode: left hand does everything while right
        hand is on trackball. Left-hand shortcuts get 2.5x importance,
        right-hand gets 0.5x (user can't easily reach them)."""
        N = self.n_positions
        self.layer_imp_mult = np.ones(N, dtype=np.float32)
        mouse_bonus_w = self.weights.get("mouse_layer_bonus", 5.0)
        for i, pos in enumerate(self.positions):
            if pos.layer == 2:
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

    def _build_l2_mouse_protection(self):
        """Identify L2 mouse button positions and essential clipboard shortcuts.
        These must resist displacement because L2 is one-handed mouse mode."""
        self.l2_protected_sids = set()
        self.l2_protected_positions = set()
        if self.current_genome is None:
            return
        for i, sid in enumerate(self.current_genome):
            if sid < 0 or self.positions[i].layer != 2:
                continue
            s = self.pool[sid]
            is_mouse_button = 'select:mb' in s.keys
            is_clipboard = s.keys in ('Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X', 'Ctrl+A')
            if is_mouse_button or is_clipboard:
                self.l2_protected_sids.add(sid)
                self.l2_protected_positions.add(i)

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
        """Precompute: for each toggled layer, which positions exist and
        which SIDs are coach_base/coach_recover_base (return-to-L0 keys)."""
        self.toggled_layer_indices = {}
        self.coach_base_sids = set()
        for s in self.pool:
            if s.keys in ('_base_coach_base', '_base_coach_recover_base'):
                self.coach_base_sids.add(s.sid)
        for layer in self.toggled_layers:
            indices = [i for i, p in enumerate(self.positions)
                       if p.layer == layer]
            if indices:
                self.toggled_layer_indices[layer] = indices

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
        '_base_coach_l1_hold', '_base_coach_l2_hold',
        '_base_coach_l3_hold', '_base_coach_l4_hold',
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
        self.t_usage_boost = torch.tensor(self.usage_boost, device=d)
        self.t_finger = torch.tensor(self.finger_arr, device=d, dtype=torch.long)
        self.t_hand = torch.tensor(self.hand_arr, device=d, dtype=torch.long)
        self.t_layer = torch.tensor(self.layer_arr, device=d, dtype=torch.long)
        self.t_is_thumb = torch.tensor(self.is_thumb_arr, device=d)
        self.t_x_arr = torch.tensor(self.x_arr, device=d, dtype=torch.long)
        self.t_y_arr = torch.tensor(self.y_arr, device=d, dtype=torch.long)
        self.t_dist_matrix = torch.tensor(self.dist_matrix, device=d)
        self.t_zmk_incompat = torch.tensor(self.zmk_incompat_arr, device=d)
        self.t_pos_violation = torch.tensor(self.pos_violation, device=d)

        # App coherence GPU data: primary app ID per shortcut
        unique_apps = sorted(set(app for apps in self.shortcut_app_sets.values() for app in apps))
        app_to_id = {app: i for i, app in enumerate(unique_apps)}
        self._n_unique_apps = len(unique_apps)
        primary_app_arr = np.full(S + 1, -1, dtype=np.int64)
        for sid, apps in self.shortcut_app_sets.items():
            primary_app_arr[sid] = app_to_id[next(iter(apps))]
        self.t_primary_app_id = torch.tensor(primary_app_arr, device=d, dtype=torch.long)
        self.t_thumb_filled_w = torch.tensor(self.thumb_filled_weight, device=d)
        self.t_thumb_empty_w = torch.tensor(self.thumb_empty_weight, device=d)
        self.t_layer_imp_mult = torch.tensor(self.layer_imp_mult, device=d)
        self.t_thumb_busy_extra = torch.tensor(self.thumb_busy_extra, device=d)
        self.t_toggled_extra = torch.tensor(self.toggled_layer_extra, device=d)

        # L2 mouse/clipboard protection mask for GPU learning curve
        l2_prot = np.zeros(N, dtype=np.float32)
        for idx in self.l2_protected_positions:
            l2_prot[idx] = 1.0
        self.t_l2_protected = torch.tensor(l2_prot, device=d)

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

        # Layer switch cost matrix and layer utilization
        self.t_layer_switch_cost = torch.tensor(self.layer_switch_cost_matrix, device=d)
        self.t_layer_util = torch.tensor(self.layer_util_arr, device=d)
        self.t_layer_usage_mult = torch.tensor(self.layer_usage_mult, device=d)

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

        # One-hot encoding: onehot[sid, pos] = positions where sid could appear
        # For batch: genome_onehot[batch, sid, pos] built at eval time
        self.n_fingers_unique = int(max(self.finger_arr.max() + 1, 1))

        # Unique layers for duplicate detection
        self.unique_layers = sorted(set(p.layer for p in self.positions))
        layer_masks = {}
        for l in self.unique_layers:
            layer_masks[l] = torch.tensor(self.layer_arr == l, device=d, dtype=torch.bool)
        self.t_layer_masks = layer_masks

        # Original duplicate exemption per (layer, sid)
        self.t_original_dupe_counts = {}
        for (layer, sid), cnt in self.original_layer_sid_counts.items():
            self.t_original_dupe_counts[(layer, sid)] = cnt

        # Precompute group SIDs for GPU group-split and placement checking
        self._gpu_group_sids = []
        for group in list(KEY_GROUPS) + self.dynamic_groups:
            if "behaviors" in group:
                continue
            if group.get("dynamic", False):
                group_sids = list(group.get("sids", []))
                expected_size = len(group_sids)
            else:
                params = [p.upper() for p in group.get("params", [])]
                mods_req = group.get("mods_required", "")
                group_sids = []
                for s in self.pool:
                    if s.base_key.upper() not in params:
                        continue
                    if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
                        continue
                    group_sids.append(s.sid)
                expected_size = len(group.get("params", []))
            if len(group_sids) >= 2:
                is_spatial = group.get("name", "") in ("arrows",)
                self._gpu_group_sids.append(
                    (
                        torch.tensor(group_sids, device=d, dtype=torch.long),
                        is_spatial,
                        float(group.get("weight", 1.0)),
                        float(expected_size),
                    )
                )

    @torch.no_grad()
    def evaluate_batch_gpu(self, genomes_list):
        """Evaluate entire population on GPU. Returns list of (effort, -adj, viol)."""
        B = len(genomes_list)
        N = self.n_positions
        S = self.n_shortcuts
        d = self.device

        # Convert genomes: -1 → S (sentinel for empty)
        g_np = np.array(genomes_list, dtype=np.int64)
        g_np[g_np < 0] = S
        t_g = torch.tensor(g_np, device=d, dtype=torch.long)  # (B, N)
        assigned = (t_g < S)  # (B, N) bool
        assigned_f = assigned.float()

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

        # Finger balance: load per finger, variance
        finger_ids = self.t_finger.unsqueeze(0).expand(B, -1)  # (B, N)
        finger_loads = torch.zeros(B, self.n_fingers_unique, device=d)
        for f in range(self.n_fingers_unique):
            mask = (finger_ids == f) & assigned  # (B, N)
            finger_loads[:, f] = (imp * mask.float()).sum(dim=1)
        fb_mean = finger_loads.mean(dim=1, keepdim=True)
        finger_balance = ((finger_loads - fb_mean) ** 2).mean(dim=1).sqrt() * self.weights.get("finger_balance", 0.8)

        # Same-finger penalty: for each conjunction pair, check if both sids
        # are placed on the same finger. Use sid->position lookup table.
        sfp = torch.zeros(B, device=d)
        if len(self.conj_pairs) > 0:
            # Build sid-to-finger lookup: for each genome, what finger is each sid on?
            # sid_finger[b, sid] = finger_id if sid is placed, else -1
            sid_finger = torch.full((B, S + 1), -1, device=d, dtype=torch.long)
            # Scatter: for each position n with genome[b,n]=sid, set sid_finger[b,sid]=finger[n]
            finger_expanded = self.t_finger.unsqueeze(0).expand(B, -1)  # (B, N)
            # Only write for assigned positions
            sid_finger.scatter_(1, t_g, finger_expanded)
            # Sentinel positions get -1
            sid_finger[:, S] = -1

            CHUNK = 500
            for start in range(0, len(self.conj_pairs), CHUNK):
                end = min(start + CHUNK, len(self.conj_pairs))
                ca = self.t_conj_sid_a[start:end]
                cb = self.t_conj_sid_b[start:end]
                cw = self.t_conj_weight[start:end]
                # Gather fingers for sid_a and sid_b: (B, C)
                fa = sid_finger.gather(1, ca.unsqueeze(0).expand(B, -1))
                fb = sid_finger.gather(1, cb.unsqueeze(0).expand(B, -1))
                same = ((fa == fb) & (fa >= 0)).float()  # (B, C)
                sfp += (same * cw.unsqueeze(0) * 0.5).sum(dim=1)

        sfp *= self.weights.get("same_finger_penalty", 2.0)

        # Hard floor: penalize genomes that removed too many assignments
        unassign_effort = torch.zeros(B, device=d)
        if self.current_genome is not None:
            cur_t_e = torch.tensor(self.current_genome, device=d, dtype=torch.long)
            cur_count = (cur_t_e >= 0).sum().float()
            now_count = assigned.sum(dim=1).float()
            min_ratio = 0.85
            below_floor = (now_count < cur_count * min_ratio).float()
            # Catastrophic penalty for going below floor
            unassign_effort += below_floor * 50000.0
            # Proportional penalty folded into effort for any removal
            cur_assigned_e = (cur_t_e >= 0)
            now_empty_e = ~assigned
            removed_e = cur_assigned_e.unsqueeze(0) & now_empty_e
            cur_sids_e = cur_t_e.clone()
            cur_sids_e[cur_sids_e < 0] = S
            cur_imp_e = self.t_importance[cur_sids_e]
            unassign_effort += (removed_e.float() * (2.0 + cur_imp_e.unsqueeze(0).pow(2) * 1.0)).sum(dim=1)

        # Learning curve: penalize changes from current layout
        lc = torch.zeros(B, device=d)
        if self.current_genome is not None:
            cur_t_lc = torch.tensor(self.current_genome, device=d, dtype=torch.long)
            cur_sids_lc = cur_t_lc.clone()
            cur_sids_lc[cur_sids_lc < 0] = S
            cur_imp_lc = self.t_importance[cur_sids_lc]  # (N,)
            changed = (t_g != cur_t_lc.unsqueeze(0))  # (B, N)
            cur_had = (cur_t_lc >= 0).unsqueeze(0)  # (1, N)
            now_has = assigned  # (B, N)
            # Swaps: both had and have something, but different
            swapped = changed & cur_had & now_has  # (B, N)
            imp_sq = cur_imp_lc.unsqueeze(0).pow(2)
            swap_cost = (1.0 + cur_imp_lc.unsqueeze(0) * 0.5 + imp_sq * 0.01) * swapped.float()
            # L2 mouse/clipboard protection
            swap_cost += (cur_imp_lc.unsqueeze(0) * 100.0) * (swapped.float() * self.t_l2_protected.unsqueeze(0))
            # 3-tier multiplier
            is_l2 = (self.t_layer == 2).unsqueeze(0).float()
            tier_per_pos = self.t_tier_mult[cur_sids_lc].unsqueeze(0)  # (1, N)
            tier_adjusted = torch.where(is_l2 > 0, torch.ones_like(tier_per_pos), tier_per_pos)
            swap_cost *= tier_adjusted
            # Base keys on non-L0 layers get 0.5× learning curve
            is_l0 = (self.t_layer == 0).unsqueeze(0)  # (1, N)
            is_base = self.t_is_base_key[cur_sids_lc].unsqueeze(0)  # (1, N)
            base_on_layer = (~is_l0).float() * is_base * swapped.float()
            swap_cost *= (1.0 - base_on_layer * 0.5)  # multiply by 0.5 where base_on_layer
            # Nearby displacement discount: if old sid moved to nearby same-layer pos, 80% off
            # Skip L0 (touch typing muscle memory) and L2 protected positions (mouse buttons)
            sid_pos_lc = torch.full((B, S + 1), N, device=d, dtype=torch.long)
            pos_idx = torch.arange(N, device=d).unsqueeze(0).expand(B, -1)
            sid_pos_lc.scatter_(1, t_g, pos_idx)
            old_sids_exp = cur_sids_lc.unsqueeze(0).expand(B, -1).long()  # (B, N)
            new_pos_of_old = sid_pos_lc.gather(1, old_sids_exp)  # (B, N)
            new_pos_clamp = new_pos_of_old.clamp(max=N-1)
            same_layer_near = (self.t_layer[new_pos_clamp] == self.t_layer.unsqueeze(0)) & (new_pos_of_old < N)
            manhattan = (self.t_x_arr[new_pos_clamp] - self.t_x_arr.unsqueeze(0)).abs() + \
                        (self.t_y_arr[new_pos_clamp] - self.t_y_arr.unsqueeze(0)).abs()
            not_self = (new_pos_of_old != pos_idx)
            not_l0 = (~is_l0).float()  # (1, N)
            not_l2_prot = (1.0 - self.t_l2_protected.unsqueeze(0))  # (1, N)
            nearby_discount = (same_layer_near & (manhattan <= 3) & not_self & swapped).float()
            nearby_discount *= not_l0 * not_l2_prot
            swap_cost *= (1.0 - nearby_discount * 0.8)  # multiply by 0.2 where nearby
            # Removals: had something, now empty
            removed_lc = changed & cur_had & ~now_has
            remove_cost = (3.0 + cur_imp_lc.unsqueeze(0) * 1.0 + imp_sq * 0.02) * removed_lc.float()
            remove_cost += (cur_imp_lc.unsqueeze(0) * 150.0) * (removed_lc.float() * self.t_l2_protected.unsqueeze(0))
            # Additions: was empty, now has something
            added = changed & ~cur_had & now_has
            add_cost = 0.3 * added.float()
            lc = (swap_cost + remove_cost + add_cost).sum(dim=1)
        lc *= self.weights.get("learning_curve", 0.5)

        # Placement reward: placing important shortcuts reduces net effort
        layer_for_pos = self.t_layer.unsqueeze(0).expand(B, -1)
        layer_usage_for_pos = self.t_layer_usage_mult[t_g, layer_for_pos]
        placement_reward = (imp * assigned_f * 8.0 * layer_usage_for_pos).sum(dim=1)
        effort_total = effort_raw + finger_balance + sfp + unassign_effort + lc - placement_reward

        # ── ADJACENCY ──
        # For each conjunction pair (a,b,w): look up where a and b are placed,
        # then index into the adjacency matrix. Uses sid->position lookup.
        adj_scores = torch.zeros(B, device=d)
        if len(self.conj_pairs) > 0:
            # Build sid-to-position lookup: sid_pos[b, sid] = position index (or N as sentinel)
            sid_pos = torch.full((B, S + 1), N, device=d, dtype=torch.long)
            pos_indices = torch.arange(N, device=d).unsqueeze(0).expand(B, -1)
            sid_pos.scatter_(1, t_g, pos_indices)
            sid_pos[:, S] = N  # sentinel

            # Extend adj_matrix with a zero row/col for sentinel position N
            adj_ext = torch.zeros(N + 1, N + 1, device=d)
            adj_ext[:N, :N] = self.t_adj_matrix

            CHUNK = 500
            for start in range(0, len(self.conj_pairs), CHUNK):
                end = min(start + CHUNK, len(self.conj_pairs))
                ca = self.t_conj_sid_a[start:end]
                cb = self.t_conj_sid_b[start:end]
                cw = self.t_conj_weight[start:end]
                # Position of sid_a and sid_b in each genome: (B, C)
                pa = sid_pos.gather(1, ca.unsqueeze(0).expand(B, -1))
                pb = sid_pos.gather(1, cb.unsqueeze(0).expand(B, -1))
                # Look up adjacency score: adj_ext[pa, pb] for each (b, c)
                flat_a = pa.reshape(-1)
                flat_b = pb.reshape(-1)
                adj_vals = adj_ext[flat_a, flat_b].reshape(B, -1)  # (B, C)
                adj_scores += (adj_vals * cw.unsqueeze(0)).sum(dim=1)

                # Layer-switch penalty for cross-layer conjunction pairs
                layer_switch_w = self.weights.get("layer_switch_penalty", 0.5)
                if layer_switch_w > 0:
                    # Clamp positions to valid range for layer lookup
                    pa_clamp = pa.clamp(max=N-1)
                    pb_clamp = pb.clamp(max=N-1)
                    la = self.t_layer[pa_clamp.reshape(-1)].reshape(B, -1)  # (B, C)
                    lb = self.t_layer[pb_clamp.reshape(-1)].reshape(B, -1)  # (B, C)
                    switch_cost = self.t_layer_switch_cost[la.reshape(-1), lb.reshape(-1)].reshape(B, -1)
                    cross_layer = (adj_vals == 0).float()
                    # Only penalize when both shortcuts are actually placed (not sentinel)
                    both_placed = ((pa < N) & (pb < N)).float()
                    adj_scores -= (cross_layer * both_placed * switch_cost * cw.unsqueeze(0) * layer_switch_w).sum(dim=1)

        # Thumb utilization
        thumb_filled = assigned_f * self.t_thumb_filled_w.unsqueeze(0)
        thumb_empty = (1.0 - assigned_f) * self.t_thumb_empty_w.unsqueeze(0)
        thumb_util = thumb_filled.sum(dim=1) + thumb_empty.sum(dim=1)

        # Cross-layer consistency: reward same sid at same physical position across layers
        cl_bonus = torch.zeros(B, device=d)
        # Build (x,y) per position as a unique coord id
        coord_ids = self.t_x_arr * 100 + self.t_y_arr  # unique coord per physical position
        for sid_val in range(S):
            sid_mask = (t_g == sid_val)  # (B, N)
            count = sid_mask.sum(dim=1)  # (B,)
            multi = (count >= 2)
            if not multi.any():
                continue
            # Check if all positions with this sid share the same coord
            # For each genome, gather coords where sid appears
            sid_coords = sid_mask.float() * coord_ids.unsqueeze(0).float()  # (B, N)
            # Unique coords: if all same, variance is 0
            # Approximate: check if min == max of non-zero coords
            big_val = 99999.0
            masked_min = torch.where(sid_mask, sid_coords, torch.tensor(big_val, device=d)).min(dim=1).values
            masked_max = torch.where(sid_mask, sid_coords, torch.tensor(-1.0, device=d)).max(dim=1).values
            same_coord = (masked_min == masked_max) & multi
            cl_bonus += same_coord.float() * count.float() * 2.0

        # Trackball proximity (simplified: right-hand mouse layer bonus)
        tb_bonus = torch.zeros(B, device=d)
        mouse_layer_mask = (self.t_layer == 2).unsqueeze(0) & (self.t_hand.unsqueeze(0) == 1) & assigned
        tb_bonus = (mouse_layer_mask.float() * imp * 0.2).sum(dim=1)

        # App coherence: reward shortcuts sharing primary app on same layer
        ac_bonus = torch.zeros(B, device=d)
        if hasattr(self, 't_primary_app_id'):
            app_ids_per_pos = self.t_primary_app_id[t_g]  # (B, N)
            for l in self.unique_layers:
                if l not in self.t_layer_masks:
                    continue
                lmask = self.t_layer_masks[l].unsqueeze(0) & assigned  # (B, N)
                for app_id in range(self._n_unique_apps):
                    app_on_layer = lmask & (app_ids_per_pos == app_id)
                    count = app_on_layer.float().sum(dim=1)  # (B,)
                    imp_sum = (app_on_layer.float() * imp).sum(dim=1)
                    has_cluster = (count >= 2).float()
                    avg_imp = imp_sum / count.clamp(min=1)
                    ac_bonus += has_cluster * count * avg_imp * 0.3

        # Mouse accessibility: reward functional one-handed mouse mode
        ma_bonus = torch.zeros(B, device=d)
        mb_weights = {'1': 2.0, '2': 1.5, '3': 1.0, '4': 0.3, '5': 0.3}
        is_l2 = (self.t_layer == 2).unsqueeze(0)
        is_left = (self.t_hand.unsqueeze(0) == 0)
        low_eff = (self.t_effort <= 2).unsqueeze(0)
        med_eff = ((self.t_effort > 2) & (self.t_effort <= 3)).unsqueeze(0)

        l2_mb_count = torch.zeros(B, device=d)
        for mb_num, mb_w in mb_weights.items():
            mb_sid = self.mouse_button_sids.get(mb_num)
            if mb_sid is None:
                continue
            mb_mask = (t_g == mb_sid) & assigned
            has_any = mb_mask.any(dim=1).float()
            on_l2 = mb_mask & is_l2
            on_l2_left = on_l2 & is_left

            if mb_num in ('1', '2', '3'):
                ma_bonus -= (1.0 - has_any) * 40.0 * mb_w
                l2_mb_count += on_l2.any(dim=1).float()
                # Heavy penalty for MB1/2/3 on L2 right hand (can't reach during mouse mode)
                on_l2_right = on_l2 & ~is_left
                ma_bonus -= on_l2_right.any(dim=1).float() * 60.0 * mb_w

            # Best-placement reward (approximate: use sum, CPU uses max)
            ma_bonus += on_l2.float().sum(dim=1) * 8.0 * mb_w
            ma_bonus += on_l2_left.float().sum(dim=1) * 6.0 * mb_w
            ma_bonus += (on_l2_left & low_eff).float().sum(dim=1) * 4.0 * mb_w
            ma_bonus += (on_l2_left & med_eff).float().sum(dim=1) * 2.0 * mb_w

        ma_bonus += (l2_mb_count >= 3).float() * 15.0
        ma_bonus += ((l2_mb_count >= 2) & (l2_mb_count < 3)).float() * 5.0

        l2_left_filled = (assigned & is_l2 & is_left).float().sum(dim=1)
        ma_bonus += l2_left_filled.clamp(max=15) * 1.5

        for clip_key in ['Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X']:
            clip_sids = [s.sid for s in self.pool if s.keys == clip_key]
            if clip_sids:
                clip_mask = (t_g == clip_sids[0]) & assigned & is_l2 & is_left
                ma_bonus += clip_mask.any(dim=1).float() * 6.0

        # Group placement reward: GPU approximation of _group_placement_score.
        gp_bonus = torch.zeros(B, device=d)
        if hasattr(self, '_gpu_group_sids') and self._gpu_group_sids:
            for group_t, _is_spatial, _group_weight, _expected_size in self._gpu_group_sids:
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

        adj_total = adj_scores * self.weights.get("adjacency", 1.5) + \
                    thumb_util * self.weights.get("thumb_utilization", 3.0) + \
                    cl_bonus * self.weights.get("cross_layer_consistency", 2.0) + \
                    tb_bonus * self.weights.get("trackball_proximity", 1.5) + \
                    gp_bonus * self.weights.get("group_placement", 2.0) + \
                    ac_bonus * self.weights.get("app_coherence", 3.0) + \
                    ma_bonus * self.weights.get("mouse_accessibility", 5.0)

        # ── VIOLATIONS ──
        # Layer context: gather from precomputed violation matrix, weighted by importance
        viol_per_pos = torch.gather(self.t_pos_violation.unsqueeze(0).expand(B, -1, -1),
                                    2, t_g.unsqueeze(2)).squeeze(2)  # (B, N)
        viol_imp_weight = 1.0 + imp * 0.5  # importance-weighted violations
        layer_viol = (viol_per_pos * assigned_f * viol_imp_weight).sum(dim=1)

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
        if self.current_genome is not None:
            cur_t = torch.tensor(self.current_genome, device=d, dtype=torch.long)
            cur_assigned = (cur_t >= 0)
            now_empty = ~assigned
            removed = cur_assigned.unsqueeze(0) & now_empty  # (B, N)
            cur_sids = cur_t.clone()
            cur_sids[cur_sids < 0] = S
            cur_imp = self.t_importance[cur_sids]
            unassign_viol = (removed.float() * (2.0 + cur_imp.unsqueeze(0).pow(2) * 0.8)).sum(dim=1)

        # Group-split violations: spatial split + group integrity (partial groups)
        group_split_viol = torch.zeros(B, device=d)
        if hasattr(self, '_gpu_group_sids') and self._gpu_group_sids:
            for group_t, is_spatial, group_weight, expected_size in self._gpu_group_sids:
                member_mask = torch.zeros(B, N, device=d, dtype=torch.bool)
                for gs in group_t:
                    member_mask |= (t_g == gs.item())
                member_count = member_mask.sum(dim=1).float()
                masked_imp = torch.where(member_mask, imp, torch.zeros_like(imp))
                max_imp = masked_imp.max(dim=1).values
                imp_scale = torch.maximum(torch.ones_like(max_imp), max_imp / 3.0)
                if is_spatial:
                    left_members = (member_mask & (self.t_hand.unsqueeze(0) == 0)).sum(dim=1).float()
                    right_members = member_count - left_members
                    both_hands = (left_members > 0) & (right_members > 0)
                    group_split_viol += both_hands.float() * member_count * 5.0 * group_weight * imp_scale
                # Group integrity: find best layer cluster, penalize missing members
                best_layer_count = torch.zeros(B, device=d)
                for layer_id in self.unique_layers:
                    lm = self.t_layer_masks[layer_id].unsqueeze(0) & member_mask
                    layer_count = lm.sum(dim=1).float()
                    best_layer_count = torch.maximum(best_layer_count, layer_count)
                    has_group = (layer_count >= 2).float()
                    group_split_viol += has_group * 0.5 * group_weight
                # Partial group penalty: quadratic for missing members
                missing = (expected_size - best_layer_count).clamp(min=0)
                has_partial_group = member_count >= 2
                group_split_viol += has_partial_group.float() * missing * missing * 5.0 * group_weight * imp_scale
                # Completeness bonus: all members on same layer
                complete = (best_layer_count >= expected_size).float()
                group_split_viol -= complete * expected_size * 3.0 * group_weight

        # Missing important shortcuts penalty — all pool shortcuts on mutable layers
        very_high_imp_sids = [s.sid for s in self.pool if s.importance >= 9.0]
        high_imp_sids = [s.sid for s in self.pool if 3.0 <= s.importance < 9.0]
        med_imp_sids = [s.sid for s in self.pool if 1.0 <= s.importance < 3.0]
        missing_viol = torch.zeros(B, device=d)
        if very_high_imp_sids:
            vh_t = torch.tensor(very_high_imp_sids, device=d, dtype=torch.long)
            vh_imp = self.t_importance[vh_t]
            present_vh = (t_g.unsqueeze(2) == vh_t.unsqueeze(0).unsqueeze(0)).any(dim=1)
            missing_viol += ((~present_vh).float() * (vh_imp * vh_imp).unsqueeze(0) * 2.0).sum(dim=1)
        if high_imp_sids:
            hi_t = torch.tensor(high_imp_sids, device=d, dtype=torch.long)
            hi_imp = self.t_importance[hi_t]
            present = (t_g.unsqueeze(2) == hi_t.unsqueeze(0).unsqueeze(0)).any(dim=1)
            missing_viol += ((~present).float() * (hi_imp * hi_imp).unsqueeze(0) * 0.5).sum(dim=1)
        if med_imp_sids:
            med_t = torch.tensor(med_imp_sids, device=d, dtype=torch.long)
            med_imp = self.t_importance[med_t]
            present_m = (t_g.unsqueeze(2) == med_t.unsqueeze(0).unsqueeze(0)).any(dim=1)
            missing_viol += ((~present_m).float() * med_imp.unsqueeze(0) * 0.5).sum(dim=1)

        # Momentary redundancy: penalize base-accessible shortcuts on momentary layers
        # Complexity-aware: 3-key combos get reduced penalty (justified on layers)
        COGNITIVE_SWITCH_COST = 1.5
        base_sids = torch.tensor(sorted(self.base_accessible_sids), device=d, dtype=torch.long)
        is_momentary = torch.zeros(N, device=d, dtype=torch.bool)
        for l in self.momentary_layers:
            if l in self.t_layer_masks:
                is_momentary |= self.t_layer_masks[l]
        is_base_accessible = (t_g.unsqueeze(2) == base_sids.unsqueeze(0).unsqueeze(0)).any(dim=2)
        is_complex = (self.t_complex_base[t_g] > 0)  # 3+ key combos: skip redundancy penalty
        redundant = assigned & is_momentary.unsqueeze(0) & is_base_accessible & ~is_complex
        eff_over = (self.t_effort.unsqueeze(0) - COGNITIVE_SWITCH_COST).clamp(min=0) * 0.3 + 1.0
        eff_under = torch.full_like(eff_over, 0.5)
        per_pos = torch.where(self.t_effort.unsqueeze(0) >= COGNITIVE_SWITCH_COST, eff_over, eff_under)
        complexity_disc = self.t_complexity_discount[t_g]  # (B, N)
        redundancy_viol = (redundant.float() * per_pos * complexity_disc).sum(dim=1)

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
            # Penalize sids on 3+ layers
            excess = (sid_layer_count - 2).clamp(min=0)  # (B, S)
            imp_penalty = 1.0 + self.t_importance[:S].unsqueeze(0) * 0.3  # (1, S)
            cross_dupe_viol = (excess * imp_penalty).sum(dim=1)

        dupe_weight = self.weights.get("duplicate", 10.0)
        group_split_weight = self.weights.get("group_split", 50.0)
        viol_total = layer_viol * self.weights.get("violations", 10.0) + \
                     zmk_viol * self.weights.get("zmk_compatibility", 20.0) + \
                     dupe_viol * dupe_weight + \
                     unassign_viol * self.weights.get("unassignment", 15.0) + \
                     missing_viol * self.weights.get("missing_important", 15.0) + \
                     group_split_viol * group_split_weight + \
                     redundancy_viol * self.weights.get("momentary_redundancy", 5.0) + \
                     cross_dupe_viol * self.weights.get("cross_layer_duplicate", 8.0)

        # Toggled layer base requirement: penalize toggled layers without coach_base anywhere
        toggled_base_viol = torch.zeros(B, device=d)
        if self.toggled_layer_indices and self.coach_base_sids:
            base_sids = torch.tensor(sorted(self.coach_base_sids), device=d, dtype=torch.long)
            for layer, layer_idxs in self.toggled_layer_indices.items():
                lidx = torch.tensor(layer_idxs, device=d, dtype=torch.long)
                layer_sids = t_g[:, lidx]
                has_base = (layer_sids.unsqueeze(2) == base_sids.unsqueeze(0).unsqueeze(0)).any(dim=2).any(dim=1)
                toggled_base_viol += (~has_base).float() * 500.0
        viol_total += toggled_base_viol * self.weights.get("violations", 10.0)

        # L0-only base key displacement: letters/numbers on non-L0 layers
        l0_only_flags = self.t_l0_only[t_g]  # (B, N) — 1.0 if L0-only key
        not_l0_layer = (self.t_layer != 0).unsqueeze(0).float()  # (1, N)
        displaced = l0_only_flags * not_l0_layer * assigned_f
        l0_displace_viol = (displaced * (50.0 + imp * 2.0)).sum(dim=1)
        viol_total += l0_displace_viol * self.weights.get("violations", 10.0)

        e = effort_total.cpu().numpy()
        a = adj_total.cpu().numpy()
        v = viol_total.cpu().numpy()
        if self.access_analyzer:
            for i, genome in enumerate(genomes_list):
                validation = self.access_analyzer.validate(genome)
                if not validation.valid:
                    e[i] = HARD_INVALID_FITNESS
                    a[i] = 0.0
                    v[i] = HARD_INVALID_FITNESS
                else:
                    e[i] += self._layer_access_effort_penalty(np.array(genome, dtype=np.int32), validation)
        return [(float(e[i]), float(-a[i]), float(v[i])) for i in range(B)]

    # =========================================================================
    # SINGLE-GENOME CPU EVALUATION (used for QD, final breakdown)
    # =========================================================================

    def evaluate(self, genome):
        genome = np.array(genome, dtype=np.int32)
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
        validation = self._layer_access_validation(genome)
        access_valid = validation.layer_access_valid if validation else 1.0
        exit_valid = validation.layer_exit_valid if validation else 1.0
        access_cost = validation.total_access_cost if validation else 0.0
        return {
            "effort": self._effort_score(genome),
            "adjacency": self._adjacency_score(genome),
            "violations": self._violation_score(genome),
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
        access_effort = self._layer_access_effort_penalty(genome, validation)
        demand_penalty = self._layer_demand_penalty(genome, validation)
        return float(total * w + access_effort + demand_penalty + fb + sfp + lc + unassign_eff - placement_reward)

    def _adjacency_score(self, genome):
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
        ma_bonus = self._mouse_accessibility_score(genome) * self.weights.get("mouse_accessibility", 5.0)
        return total * w + thumb_bonus + cl_bonus + tb_bonus + gp_bonus + ac_bonus + ma_bonus

    def _violation_score(self, genome):
        validation = self._layer_access_validation(genome)
        if validation is not None and not validation.valid:
            return HARD_INVALID_FITNESS
        w = self.weights.get("violations", 10.0)
        total = 0.0
        total += self._layer_context_violations(genome) * w
        total += self._group_split_violations(genome) * self.weights.get("group_split", 50.0)
        total += self._duplicate_violations(genome) * self.weights.get("duplicate", 10.0)
        total += self._zmk_compatibility(genome) * self.weights.get("zmk_compatibility", 20.0)
        total += self._unassignment_penalty(genome) * self.weights.get("unassignment", 15.0)
        total += self._missing_important_penalty(genome) * self.weights.get("missing_important", 15.0)
        total += self._momentary_redundancy_penalty(genome) * self.weights.get("momentary_redundancy", 5.0)
        total += self._cross_layer_duplicate_penalty(genome) * self.weights.get("cross_layer_duplicate", 8.0)
        total += self._toggled_base_violation(genome) * self.weights.get("violations", 10.0)
        total += self._l0_key_displacement_violation(genome) * self.weights.get("violations", 10.0)
        return total

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

    def _missing_important_penalty(self, genome):
        """Penalize shortcuts from the pool that aren't placed anywhere.
        All shortcuts in the pool are on mutable layers — bare keys like Vimium j/k
        belong on non-frozen layers and must be penalized if missing."""
        assigned_sids = set(int(g) for g in genome if g >= 0)
        penalty = 0.0
        for s in self.pool:
            if s.sid in assigned_sids:
                continue
            if s.importance >= 9.0:
                penalty += s.importance * s.importance * 2.0
            elif s.importance >= 3.0:
                penalty += s.importance * s.importance * 0.5
            elif s.importance >= 1.0:
                penalty += s.importance * 0.5
        return penalty

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
            for pa in pos_of_sid.get(sid_a, []):
                for pb in pos_of_sid.get(sid_b, []):
                    if self.layer_arr[pa] == self.layer_arr[pb]:
                        if self.finger_arr[pa] == self.finger_arr[pb] and self.finger_arr[pa] >= 0:
                            penalty += weight * 0.5
        return penalty

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
                # Same physical position across layers — reward proportional to count
                layer_types = set()
                for p in pos_list:
                    if p.layer in self.toggled_layers:
                        layer_types.add("toggled")
                    elif p.layer in self.momentary_layers:
                        layer_types.add("momentary")
                weight = 2.5 if "toggled" in layer_types else 1.5
                bonus += weight * len(pos_list)
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
                if pos.layer == 2:
                    bonus += self.importance_arr[sid] * 0.2
                elif is_mouse_related and pos.y >= 2:
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
                if i in self.l2_protected_positions:
                    swap_cost += imp * 100.0

                # 3-tier shortcut value system (skip L2)
                sid = ref[i]
                if layer != 2:
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
                if layer != 0 and i not in self.l2_protected_positions:
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
                if i in self.l2_protected_positions:
                    remove_cost += imp * 150.0
                cost += remove_cost
            else:
                cost += 0.3
        return cost

    def _zmk_compatibility(self, genome):
        return float(sum(1 for i, sid in enumerate(genome) if sid >= 0 and sid in self.zmk_incompat))

    def _compute_layer_app_dominance(self, genome):
        """Kept for compatibility with evaluate_full breakdown."""
        return {}

    def _layer_context_violations(self, genome):
        """No hardcoded layer-app context. Returns 0 — layer themes emerge
        from app-coherence reward and conjunction pairs."""
        return 0.0

    def _app_coherence_score(self, genome):
        """Reward shortcuts sharing their primary app on the same layer.
        Uses primary app only (matches GPU path)."""
        layer_app_sids = {}
        for i, sid in enumerate(genome):
            if sid < 0 or sid not in self.shortcut_app_sets:
                continue
            layer = self.positions[i].layer
            app = next(iter(self.shortcut_app_sets[sid]))
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
        """Reward a functional one-handed mouse mode layer.

        The user holds L2 with left thumb, right hand on trackball. A good
        mouse layer needs: MB1/2/3 grouped on left hand at low effort,
        clipboard shortcuts (Ctrl+C/V/Z/X) on left hand, and common
        navigation (Escape, Enter, Tab, arrows) accessible one-handed.

        The reward is large enough that starting from scratch, the optimizer
        will actively BUILD this layer structure."""
        bonus = 0.0

        # --- Mouse button placement (per button, per instance) ---
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
            best_score = 0
            has_l2_right = False
            for i, pos in placements:
                score = 0
                if pos.layer == 2:
                    if pos.hand == "left":
                        score += 8.0 * mb_w
                        score += 6.0 * mb_w
                        if pos.effort <= 2:
                            score += 4.0 * mb_w
                        elif pos.effort <= 3:
                            score += 2.0 * mb_w
                    else:
                        score += 1.0 * mb_w
                        if mb_num in ('1', '2', '3'):
                            has_l2_right = True
                best_score = max(best_score, score)
            bonus += best_score
            if has_l2_right:
                bonus -= 60.0 * mb_w

        # --- MB grouping: reward MB1/2/3 clustered together on same layer ---
        for layer in set(self.positions[i].layer for _, (i, _) in
                         ((0, x) for placements in mb_positions.values() for x in placements)):
            layer_mb_pos = []
            for mb_num in critical_mbs:
                for i, pos in mb_positions.get(mb_num, []):
                    if pos.layer == layer:
                        layer_mb_pos.append(pos)
            n = len(layer_mb_pos)
            if n >= 3:
                bonus += 15.0
            elif n >= 2:
                bonus += 5.0
            for a in range(len(layer_mb_pos)):
                for b in range(a + 1, len(layer_mb_pos)):
                    dist = abs(layer_mb_pos[a].x - layer_mb_pos[b].x) + \
                           abs(layer_mb_pos[a].y - layer_mb_pos[b].y)
                    if dist <= 2:
                        bonus += 4.0
                    elif dist <= 3:
                        bonus += 2.0

        # --- One-handed workflow completeness on L2 ---
        l2_left_shortcuts = set()
        l2_left_count = 0
        for i in range(len(genome)):
            if genome[i] < 0 or self.positions[i].layer != 2:
                continue
            if self.positions[i].hand == "left":
                s = self.pool[genome[i]]
                l2_left_shortcuts.add(s.keys)
                l2_left_count += 1

        clipboard_keys = {'Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X'}
        clipboard_on_l2 = len(clipboard_keys & l2_left_shortcuts)
        bonus += clipboard_on_l2 * 6.0
        if clipboard_on_l2 >= 3:
            bonus += 8.0

        nav_utility = {'Ctrl+A', 'Ctrl+W', 'Ctrl+Y', 'Escape', 'Enter', 'Tab', 'Delete'}
        nav_on_l2 = len(nav_utility & l2_left_shortcuts)
        bonus += nav_on_l2 * 4.0

        bonus += min(l2_left_count, 15) * 1.5

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
                params = [p.upper() for p in group.get("params", [])]
                mods_req = group.get("mods_required", "")
                gp = []
                for i, sid in enumerate(genome):
                    if sid < 0:
                        continue
                    s = self.pool[sid]
                    if s.base_key.upper() not in params:
                        continue
                    if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
                        continue
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
                params = [p.upper() for p in group.get("params", [])]
                mods_req = group.get("mods_required", "")
                members = []
                for i, sid in enumerate(genome):
                    if sid < 0:
                        continue
                    s = self.pool[sid]
                    if s.base_key.upper() not in params:
                        continue
                    if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
                        continue
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
            sid_layers.setdefault(int(sid), set()).add(self.positions[i].layer)
        penalty = 0.0
        for sid, layers in sid_layers.items():
            n = len(layers)
            if n > 2:
                imp = self.importance_arr[sid]
                extra = n - 2
                waste_factor = max(1.0, 10.0 - imp)
                penalty += extra * extra * waste_factor
        return penalty
