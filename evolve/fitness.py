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
    Position, Shortcut, LAYER_APP_CONTEXT, KEY_GROUPS,
    FINGER_MAP, THUMB_HAND, LEFT_COLS, RIGHT_COLS,
    KNOWN_KEY_NAMES, LAYER_ACCESS, build_layer_to_positions,
    discover_dynamic_groups,
)


class FitnessEvaluator:
    def __init__(self, positions, shortcut_pool, config, usage_stats=None,
                 conjunction_pairs=None, device="cpu", current_genome=None):
        self.positions = positions
        self.pool = shortcut_pool
        self.config = config
        self.weights = config.get("weights", {})
        self.usage_stats = usage_stats or {}
        self.conjunction_pairs = conjunction_pairs or {}
        self.device = device
        self.n_positions = len(positions)
        self.n_shortcuts = len(shortcut_pool)
        self.layer_positions = build_layer_to_positions(positions)
        self.current_genome = np.array(current_genome, dtype=np.int32) if current_genome is not None else None

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
            if count > 0:
                self.usage_boost[s.sid] = math.log(1 + count)

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

        self.toggled_layers = {5, 9, 10}
        self.momentary_layers = {1, 3, 4}
        self._build_zmk_compat()
        self._build_layer_context_mask()
        self._build_thumb_vectors()

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
        """Build per-position violation mask: pos_violation_mask[i, sid] = 1.0 if sid on position i is a violation."""
        S = self.n_shortcuts

        layer_allowed_apps = {}
        for layer, apps in LAYER_APP_CONTEXT.items():
            layer_allowed_apps[layer] = set(apps)

        # pos_violation[i, sid] = 1.0 if placing sid at position i violates layer context
        # A shortcut is valid if ANY of its apps match the layer's allowed apps
        self.pos_violation = np.zeros((self.n_positions, S + 1), dtype=np.float32)
        for i, pos in enumerate(self.positions):
            allowed = layer_allowed_apps.get(pos.layer)
            if allowed is None:
                continue
            for s in self.pool:
                shortcut_apps = set(s.apps) if s.apps else {s.app}
                if not shortcut_apps & allowed:
                    self.pos_violation[i, s.sid] = 1.0

    def _build_thumb_vectors(self):
        """Per-position weights for thumb scoring."""
        N = self.n_positions
        self.thumb_filled_weight = np.zeros(N, dtype=np.float32)
        self.thumb_empty_weight = np.zeros(N, dtype=np.float32)
        for i, pos in enumerate(self.positions):
            if pos.is_thumb:
                if pos.layer in self.toggled_layers:
                    self.thumb_filled_weight[i] = 3.0
                    self.thumb_empty_weight[i] = -1.0
                elif pos.layer in self.momentary_layers:
                    self.thumb_filled_weight[i] = 2.0

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
        self.t_dist_matrix = torch.tensor(self.dist_matrix, device=d)
        self.t_zmk_incompat = torch.tensor(self.zmk_incompat_arr, device=d)
        self.t_pos_violation = torch.tensor(self.pos_violation, device=d)
        self.t_thumb_filled_w = torch.tensor(self.thumb_filled_weight, device=d)
        self.t_thumb_empty_w = torch.tensor(self.thumb_empty_weight, device=d)

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

        # Precompute group SIDs for GPU group-split checking
        self._gpu_group_sids = []
        for group in KEY_GROUPS:
            if "behaviors" in group:
                continue
            params = [p.upper() for p in group.get("params", [])]
            mods_req = group.get("mods_required", "")
            group_sids = []
            for s in self.pool:
                if s.base_key.upper() not in params:
                    continue
                if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
                    continue
                group_sids.append(s.sid)
            if len(group_sids) >= 2:
                is_spatial = group.get("name", "") in ("arrows",)
                self._gpu_group_sids.append(
                    (torch.tensor(group_sids, device=d, dtype=torch.long), is_spatial)
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
        eff = self.t_effort.unsqueeze(0)    # (1, N)
        weighted = eff * imp * usage * assigned_f
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

        effort_total = effort_raw + finger_balance + sfp + unassign_effort

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

        # Thumb utilization
        thumb_filled = assigned_f * self.t_thumb_filled_w.unsqueeze(0)
        thumb_empty = (1.0 - assigned_f) * self.t_thumb_empty_w.unsqueeze(0)
        thumb_util = thumb_filled.sum(dim=1) + thumb_empty.sum(dim=1)

        adj_total = adj_scores * self.weights.get("adjacency", 1.5) + \
                    thumb_util * self.weights.get("thumb_utilization", 3.0)

        # ── VIOLATIONS ──
        # Layer context: gather from precomputed violation matrix, weighted by importance
        viol_per_pos = torch.gather(self.t_pos_violation.unsqueeze(0).expand(B, -1, -1),
                                    2, t_g.unsqueeze(2)).squeeze(2)  # (B, N)
        viol_imp_weight = 1.0 + imp * 0.5  # importance-weighted violations
        layer_viol = (viol_per_pos * assigned_f * viol_imp_weight).sum(dim=1)

        # ZMK compat
        zmk_viol = (self.t_zmk_incompat[t_g] * assigned_f).sum(dim=1)

        # Duplicates per layer (importance-weighted, matching CPU path)
        dupe_viol = torch.zeros(B, device=d)
        for l in self.unique_layers:
            lmask = self.t_layer_masks[l].unsqueeze(0) & assigned  # (B, N)
            layer_sids = t_g.clone()
            layer_sids[~lmask] = S  # sentinel
            sorted_sids, _ = layer_sids.sort(dim=1)
            consecutive_eq = (sorted_sids[:, 1:] == sorted_sids[:, :-1]) & (sorted_sids[:, 1:] < S)
            # Importance-weighted: 1.0 + imp^2 * 0.5 per duplicate
            dupe_imp = self.t_importance[sorted_sids[:, 1:]]
            dupe_penalty = (1.0 + dupe_imp.pow(2) * 0.5) * consecutive_eq.float()
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
            unassign_viol = (removed.float() * (1.0 + cur_imp.unsqueeze(0).pow(2) * 0.3)).sum(dim=1)

        # Approximate group-split violations: check arrow group spatial split
        group_split_viol = torch.zeros(B, device=d)
        if hasattr(self, '_gpu_group_sids') and self._gpu_group_sids:
            for group_t, is_spatial in self._gpu_group_sids:
                # For each genome, find positions of group members
                # group_t: tensor of SIDs in this group
                member_mask = torch.zeros(B, N, device=d, dtype=torch.bool)
                for gs in group_t:
                    member_mask |= (t_g == gs.item())
                member_count = member_mask.sum(dim=1).float()
                if is_spatial:
                    # Check hand split: members on both hands
                    left_members = (member_mask & (self.t_hand.unsqueeze(0) == 0)).sum(dim=1).float()
                    right_members = member_count - left_members
                    both_hands = (left_members > 0) & (right_members > 0)
                    group_split_viol += both_hands.float() * member_count * 5.0
                # Non-adjacent penalty approximation: variance of positions
                for layer_id in self.unique_layers:
                    lm = self.t_layer_masks[layer_id].unsqueeze(0) & member_mask
                    layer_count = lm.sum(dim=1).float()
                    has_group = (layer_count >= 2).float()
                    group_split_viol += has_group * 0.5  # mild penalty for any group

        # Missing important shortcuts penalty (skip bare keys - they're on frozen base layer)
        high_imp_sids = [s.sid for s in self.pool if s.importance >= 3.0 and s.modifiers]
        missing_viol = torch.zeros(B, device=d)
        if high_imp_sids:
            hi_t = torch.tensor(high_imp_sids, device=d, dtype=torch.long)
            hi_imp = self.t_importance[hi_t]  # (H,)
            # Check if each high-imp sid is in each genome: (B, H)
            present = (t_g.unsqueeze(2) == hi_t.unsqueeze(0).unsqueeze(0)).any(dim=1)  # (B, H)
            missing_viol = ((~present).float() * hi_imp.unsqueeze(0) * 0.5).sum(dim=1)

        dupe_weight = self.weights.get("duplicate", 10.0)
        group_split_weight = self.weights.get("group_split", 50.0)
        viol_total = layer_viol * self.weights.get("violations", 10.0) + \
                     zmk_viol * self.weights.get("zmk_compatibility", 20.0) + \
                     dupe_viol * dupe_weight + \
                     unassign_viol * self.weights.get("unassignment", 15.0) + \
                     missing_viol * self.weights.get("missing_important", 15.0) + \
                     group_split_viol * group_split_weight

        # Return as list of tuples
        e = effort_total.cpu().numpy()
        a = adj_total.cpu().numpy()
        v = viol_total.cpu().numpy()
        return [(float(e[i]), float(-a[i]), float(v[i])) for i in range(B)]

    # =========================================================================
    # SINGLE-GENOME CPU EVALUATION (used for QD, final breakdown)
    # =========================================================================

    def evaluate(self, genome):
        genome = np.array(genome, dtype=np.int32)
        obj1 = self._effort_score(genome)
        obj2 = self._adjacency_score(genome)
        obj3 = self._violation_score(genome)
        return (obj1, -obj2, obj3)

    def evaluate_full(self, genome):
        genome = np.array(genome, dtype=np.int32)
        return {
            "effort": self._effort_score(genome),
            "adjacency": self._adjacency_score(genome),
            "violations": self._violation_score(genome),
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

    def _effort_score(self, genome):
        w = self.weights.get("effort", 1.0)
        mask = genome >= 0
        sids = np.clip(genome, 0, self.n_shortcuts)
        total = (self.effort_arr * self.importance_arr[sids] * self.usage_boost[sids] * mask).sum()
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
        return float(total * w + fb + sfp + lc + unassign_eff)

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
        thumb_bonus = self._thumb_utilization(genome) * self.weights.get("thumb_utilization", 3.0)
        cl_bonus = self._cross_layer_consistency(genome) * self.weights.get("cross_layer_consistency", 2.0)
        tb_bonus = self._trackball_proximity(genome) * self.weights.get("trackball_proximity", 1.5)
        gp_bonus = self._group_placement_score(genome) * self.weights.get("group_placement", 2.0)
        return total * w + thumb_bonus + cl_bonus + tb_bonus + gp_bonus

    def _violation_score(self, genome):
        w = self.weights.get("violations", 10.0)
        total = 0.0
        total += self._layer_context_violations(genome) * w
        total += self._group_split_violations(genome) * self.weights.get("group_split", 50.0)
        total += self._duplicate_violations(genome) * self.weights.get("duplicate", 10.0)
        total += self._zmk_compatibility(genome) * self.weights.get("zmk_compatibility", 20.0)
        total += self._unassignment_penalty(genome) * self.weights.get("unassignment", 15.0)
        total += self._missing_important_penalty(genome) * self.weights.get("missing_important", 15.0)
        return total

    def _missing_important_penalty(self, genome):
        """Penalize shortcuts from the pool that aren't placed anywhere.
        Skip bare keys (no modifiers) - they belong on base layer (frozen)."""
        assigned_sids = set(int(g) for g in genome if g >= 0)
        penalty = 0.0
        for s in self.pool:
            if s.sid in assigned_sids:
                continue
            if not s.modifiers:
                continue
            if s.importance >= 3.0:
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
            filled = sum(1 for p in thumbs if genome[p.gene_idx] >= 0)
            empty = len(thumbs) - filled
            if layer_num in self.toggled_layers:
                bonus += filled * 3.0 - empty * 1.0
            elif layer_num in self.momentary_layers:
                bonus += filled * 2.0
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
        """Heavy penalty for removing a shortcut that was assigned in the current layout."""
        if self.current_genome is None:
            return 0.0
        penalty = 0.0
        for i in range(len(genome)):
            if self.current_genome[i] >= 0 and genome[i] < 0:
                imp = self.importance_arr[self.current_genome[i]]
                # Quadratic scaling: removing high-importance keys is much worse
                penalty += 1.0 + imp * imp * 0.3
        return penalty

    def _learning_curve(self, genome, original=None):
        ref = original if original is not None else self.current_genome
        if ref is None:
            return 0.0
        cost = 0.0
        for i in range(len(genome)):
            if genome[i] == ref[i]:
                continue
            # Moving a key costs less than removing or adding one
            if ref[i] >= 0 and genome[i] >= 0:
                cost += 0.3  # swap — user relearns position
            elif ref[i] >= 0 and genome[i] < 0:
                cost += 1.0  # removal — user loses a shortcut
            else:
                cost += 0.2  # addition — easy to learn
        return cost

    def _zmk_compatibility(self, genome):
        return float(sum(1 for i, sid in enumerate(genome) if sid >= 0 and sid in self.zmk_incompat))

    def _layer_context_violations(self, genome):
        violations = 0.0
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            allowed = LAYER_APP_CONTEXT.get(self.positions[i].layer)
            if allowed is None:
                continue
            s = self.pool[sid]
            shortcut_apps = set(s.apps) if s.apps else {s.app}
            allowed_set = set(allowed)
            if not shortcut_apps & allowed_set:
                imp = self.importance_arr[sid]
                violations += 1.0 + imp * 0.5
        return violations

    def _group_split_violations(self, genome):
        violations = 0
        all_groups = list(KEY_GROUPS) + self.dynamic_groups
        for group in all_groups:
            if "behaviors" in group:
                continue
            is_dynamic = group.get("dynamic", False)
            group_weight = group.get("weight", 1.0)

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
            # Only spatial-grouping groups (arrows) get cross-hand penalty
            spatial_group = group.get("name", "") in ("arrows",)

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

    def _duplicate_violations(self, genome):
        """Penalize same-layer duplicates only. Cross-layer duplication is handled
        by cross_layer_consistency (reward) and is intentional for universal shortcuts."""
        layer_sids = {}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            layer_sids.setdefault(self.positions[i].layer, []).append(int(sid))
        penalty = 0.0
        for sids in layer_sids.values():
            seen = set()
            for sid in sids:
                if sid in seen:
                    imp = self.importance_arr[sid]
                    penalty += 1.0 + imp * imp * 0.5
                seen.add(sid)
        return penalty
