"""Custom mutation and crossover operators for keyboard layout evolution.

All operators are layer-aware, preserve structural positions, and protect key groups.
Includes batched GPU operators for population-level mutation.
"""
import random
import copy
import numpy as np
from representation import (
    Position, Shortcut, LAYER_ACCESS,
    build_layer_to_positions, is_structural,
    is_in_protected_group, find_group_members, KEY_GROUPS,
    is_frozen_l0_position, is_l0_thumb_worthy_shortcut,
    shortcut_matches_group,
)
from layer_access import shortcut_capability

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class OperatorContext:
    """Precomputed static data + per-genome helpers for operators.

    Created once at evolution start. Static data never changes during a run.
    Per-genome methods use the static data to answer questions in O(genome_len)
    with O(1) membership tests instead of O(genome_len * num_groups) with string matching.
    """

    def __init__(self, positions, shortcut_pool, layer_positions, dynamic_groups=None):
        self.positions = positions
        self.shortcut_pool = shortcut_pool
        self.layer_positions = layer_positions
        self.dynamic_groups = dynamic_groups or []
        self.pool_size = len(shortcut_pool)

        self.layer_gene_indices = {
            layer: tuple(p.gene_idx for p in pos_list)
            for layer, pos_list in layer_positions.items()
        }
        self.layer_thumb_indices = {
            layer: tuple(p.gene_idx for p in pos_list if p.is_thumb)
            for layer, pos_list in layer_positions.items()
        }
        self.layers_with_2plus = [l for l in layer_positions if len(layer_positions[l]) >= 2]
        self.layer_keys = list(layer_positions.keys())

        self.frozen_l0 = frozenset(
            i for i, p in enumerate(positions) if is_frozen_l0_position(p)
        )
        self.l0_mutable_thumb_indices = frozenset(
            i for i, p in enumerate(positions)
            if p.layer == 0 and p.is_thumb and not is_frozen_l0_position(p)
        )
        self.exit_sid_set = self._build_exit_sid_set()

        # Build protected SID flat set and group mappings
        self.protected_sid_set, self.sid_to_group_id, self.group_id_to_sids = \
            self._build_protected_sid_data()

        # Precompute shortcut metadata
        self.sid_apps = {}
        self.sid_is_base_key = set()
        self.l0_thumb_worthy_sids = set()
        self.critical_mouse_button_sids = set()
        for s in shortcut_pool:
            apps = frozenset(s.apps) if s.apps else frozenset({s.app})
            self.sid_apps[s.sid] = apps
            if s.category == "base_key":
                self.sid_is_base_key.add(s.sid)
            if is_l0_thumb_worthy_shortcut(s):
                self.l0_thumb_worthy_sids.add(s.sid)
            if s.keys in ("_base_select:mb1", "_base_select:mb2", "_base_select:mb3"):
                self.critical_mouse_button_sids.add(s.sid)

        self.importance_sorted_sids = sorted(
            [s.sid for s in shortcut_pool if s.sid not in self.sid_is_base_key],
            key=lambda sid: -shortcut_pool[sid].importance,
        )

        # Precomputed group matching data for move_group
        self.static_groups = []
        for g in KEY_GROUPS:
            if g.get("protected") and "behaviors" not in g:
                self.static_groups.append({
                    **g,
                    "_params_upper": set(p.upper() for p in g.get("params", [])),
                    "_mods_req": g.get("mods_required", ""),
                })

    def _build_protected_sid_data(self):
        all_sids = set()
        sid_to_group = {}
        group_to_sids = {}
        group_id = 0

        for group in KEY_GROUPS:
            if not group.get("protected"):
                continue
            if "behaviors" in group:
                continue
            sids = set()
            for s in self.shortcut_pool:
                if shortcut_matches_group(s, group):
                    sids.add(s.sid)
            if sids:
                group_to_sids[group_id] = frozenset(sids)
                for sid in sids:
                    sid_to_group[sid] = group_id
                    all_sids.add(sid)
                group_id += 1

        for dg in self.dynamic_groups:
            sids = frozenset(int(sid) for sid in dg.get("sids", []))
            if sids:
                group_to_sids[group_id] = sids
                for sid in sids:
                    sid_to_group[sid] = group_id
                    all_sids.add(sid)
                group_id += 1

        all_sids.update(self.exit_sid_set)
        return frozenset(all_sids), sid_to_group, group_to_sids

    def _build_exit_sid_set(self):
        exit_sids = set()
        probe = self.positions[0] if self.positions else None
        if probe is None:
            return exit_sids
        for s in self.shortcut_pool:
            if s.keys in ("_base_coach_base", "_base_coach_recover_base", "_base_coach_travel_off"):
                exit_sids.add(s.sid)
                continue
            cap = shortcut_capability(s, probe)
            if cap and cap.target == 0:
                exit_sids.add(s.sid)
        return exit_sids

    def build_gpu_tensors(self, device):
        """Build GPU tensors for batched population-level operators."""
        if not HAS_TORCH:
            return
        self.device = device
        d = device
        N = len(self.positions)
        S = self.pool_size

        t_protected = torch.zeros(S + 1, dtype=torch.bool, device=d)
        for sid in self.protected_sid_set:
            t_protected[sid] = True
        self.t_sid_is_protected = t_protected

        self.t_frozen_mask = torch.zeros(N, dtype=torch.bool, device=d)
        self._rebuild_frozen_tensor()

        layer_arr = np.array([p.layer for p in self.positions], dtype=np.int64)
        self.t_layer_arr = torch.tensor(layer_arr, device=d, dtype=torch.long)
        self.n_layers = int(layer_arr.max()) + 1

        effort_arr = np.array([p.effort for p in self.positions], dtype=np.float32)
        self.t_effort_arr = torch.tensor(effort_arr, device=d)

        imp_arr = np.zeros(S + 1, dtype=np.float32)
        for s in self.shortcut_pool:
            imp_arr[s.sid] = s.importance
        self.t_importance = torch.tensor(imp_arr, device=d)

        base_key_mask = torch.zeros(S + 1, dtype=torch.bool, device=d)
        for sid in self.sid_is_base_key:
            base_key_mask[sid] = True
        self.t_is_base_key = base_key_mask

        is_thumb = np.array([p.is_thumb for p in self.positions], dtype=bool)
        self.t_is_thumb = torch.tensor(is_thumb, device=d)
        l0_mutable = np.zeros(N, dtype=bool)
        for idx in self.l0_mutable_thumb_indices:
            l0_mutable[idx] = True
        self.t_l0_mutable_thumb = torch.tensor(l0_mutable, device=d)
        l0_worthy = torch.zeros(S + 1, dtype=torch.bool, device=d)
        for sid in self.l0_thumb_worthy_sids:
            l0_worthy[sid] = True
        self.t_l0_thumb_worthy_sid = l0_worthy

        self.layers_with_2plus_t = torch.tensor(self.layers_with_2plus, device=d, dtype=torch.long)
        self.layer_keys_t = torch.tensor(self.layer_keys, device=d, dtype=torch.long)

    def _rebuild_frozen_tensor(self):
        if not hasattr(self, 'device'):
            return
        frozen = torch.zeros(len(self.positions), dtype=torch.bool, device=self.device)
        for idx in self.frozen_l0:
            frozen[idx] = True
        self.t_frozen_mask = frozen

    def set_frozen_l0(self, positions, open_gene_indices):
        open_set = set(open_gene_indices)
        frozen = set()
        for i, p in enumerate(positions):
            if p.layer == 0 and i not in open_set:
                frozen.add(i)
        self.frozen_l0 = frozenset(frozen)
        self._rebuild_frozen_tensor()
        print(f"  L0 frozen: {len(frozen)} positions, {len(open_set)} open")

    def protected_indices(self, genome):
        protected = set(self.frozen_l0)
        psids = self.protected_sid_set
        if psids:
            protected.update(
                i for i, sid in enumerate(genome)
                if sid >= 0 and sid in psids and self.position_accepts_sid(i, sid)
            )
        return protected

    def position_accepts_sid(self, gene_idx, sid):
        """Return whether sid is legal at a physical position.

        Protected groups preserve good structure, but they must never preserve
        a shortcut in a position that violates a hard positional role.
        """
        if sid < 0 or sid >= self.pool_size:
            return True
        if gene_idx in self.l0_mutable_thumb_indices:
            return sid in self.l0_thumb_worthy_sids
        return True

    def incompatible_indices(self, genome):
        return [
            i for i, sid in enumerate(genome)
            if sid >= 0 and not self.position_accepts_sid(i, sid)
        ]

    def find_group_at(self, genome, gene_idx):
        sid = genome[gene_idx]
        if sid < 0:
            return None
        group_id = self.sid_to_group_id.get(sid)
        if group_id is None:
            return None
        group_sids = self.group_id_to_sids[group_id]
        layer = self.positions[gene_idx].layer
        members = [i for i, s in enumerate(genome)
                   if s >= 0 and s in group_sids and self.positions[i].layer == layer]
        return members if len(members) >= 2 else None

    def apps_for_sid(self, sid):
        return self.sid_apps.get(sid, frozenset())

    def top_unassigned(self, genome, min_importance=0.0):
        assigned = {sid for sid in genome if sid >= 0}
        pool = self.shortcut_pool
        return [sid for sid in self.importance_sorted_sids
                if sid not in assigned and pool[sid].importance >= min_importance]

    def is_left_mouse_workflow_source(self, gene_idx, sid):
        if sid not in self.critical_mouse_button_sids:
            return False
        pos = self.positions[gene_idx]
        access = LAYER_ACCESS.get(pos.layer, {})
        return pos.hand == "left" and access.get("thumb") == "left" and "momentary" in access.get("method", "")


def repair_position_compatibility(genome, ctx):
    """Evacuate shortcuts from positions where their role is illegal.

    This is a genome-validity repair, not a layout preference. Example:
    raw arrow keys are protected as an arrow group, but a raw arrow on a
    mutable L0 thumb is an illegal physical role, so it must be movable.
    """
    g = copy.copy(genome)
    repaired = 0
    all_indices = list(range(len(g)))

    # First normalize mutable L0 thumbs. These are role-constrained premium
    # slots: if one is empty or contains content, promote the best movable
    # structural/L0-worthy key into it.
    l0_targets = [
        i for i in sorted(ctx.l0_mutable_thumb_indices, key=lambda j: (ctx.positions[j].effort, ctx.positions[j].y, ctx.positions[j].x))
        if g[i] < 0 or not ctx.position_accepts_sid(i, g[i])
    ]
    for idx in l0_targets:
        protected = ctx.protected_indices(g)
        old_sid = g[idx]
        assigned = {sid for sid in g if sid >= 0}

        swap_sources = [
            j for j in all_indices
            if j != idx
            and j not in protected
            and j not in ctx.l0_mutable_thumb_indices
            and g[j] >= 0
            and not ctx.is_left_mouse_workflow_source(j, g[j])
            and ctx.position_accepts_sid(idx, g[j])
            and (old_sid < 0 or ctx.position_accepts_sid(j, old_sid))
        ]
        if swap_sources:
            source = max(
                swap_sources,
                key=lambda j: (ctx.shortcut_pool[g[j]].importance, -ctx.positions[j].effort),
            )
            g[idx], g[source] = g[source], g[idx]
            repaired += 1
            continue

        unassigned = [
            s for s in ctx.shortcut_pool
            if s.sid not in assigned and ctx.position_accepts_sid(idx, s.sid)
        ]
        if unassigned:
            shortcut = max(unassigned, key=lambda s: s.importance)
            if old_sid >= 0:
                empty_targets = [
                    j for j in all_indices
                    if j != idx and g[j] < 0 and j not in protected and ctx.position_accepts_sid(j, old_sid)
                ]
                if empty_targets:
                    target = min(empty_targets, key=lambda j: (ctx.positions[j].effort, ctx.positions[j].layer, ctx.positions[j].y, ctx.positions[j].x))
                    g[target] = old_sid
            g[idx] = shortcut.sid
            repaired += 1

    illegal = ctx.incompatible_indices(g)
    protected = ctx.protected_indices(g)
    for idx in illegal:
        sid = g[idx]
        if sid < 0 or ctx.position_accepts_sid(idx, sid):
            continue

        empty_targets = [
            j for j in all_indices
            if j != idx and g[j] < 0 and j not in protected and ctx.position_accepts_sid(j, sid)
        ]
        if empty_targets:
            target = min(empty_targets, key=lambda j: (ctx.positions[j].effort, ctx.positions[j].layer, ctx.positions[j].y, ctx.positions[j].x))
            g[target] = sid
            g[idx] = -1
            repaired += 1
            continue

        swap_targets = [
            j for j in all_indices
            if j != idx and j not in protected and g[j] >= 0
            and ctx.position_accepts_sid(j, sid)
            and ctx.position_accepts_sid(idx, g[j])
        ]
        if swap_targets:
            target = min(swap_targets, key=lambda j: (ctx.shortcut_pool[g[j]].importance, ctx.positions[j].effort))
            g[idx], g[target] = g[target], g[idx]
            repaired += 1
            continue

        g[idx] = -1
        repaired += 1

    protected = ctx.protected_indices(g)
    assigned = {int(sid) for sid in g if sid >= 0}
    prime_empty = [
        i for i, pos in enumerate(ctx.positions)
        if pos.layer != 0
        and pos.effort <= 1.5
        and g[i] < 0
        and i not in protected
    ]
    for idx in sorted(prime_empty, key=lambda j: (ctx.positions[j].effort, ctx.positions[j].layer, ctx.positions[j].y, ctx.positions[j].x)):
        sid = next(
            (
                candidate
                for candidate in ctx.importance_sorted_sids
                if candidate not in assigned and ctx.position_accepts_sid(idx, candidate)
            ),
            None,
        )
        if sid is None:
            break
        g[idx] = sid
        assigned.add(sid)
        repaired += 1

    return g, repaired


def swap_within_layer(genome, ctx):
    genome = copy.copy(genome)
    layers = ctx.layers_with_2plus
    if not layers:
        return genome
    protected = ctx.protected_indices(genome)
    for _ in range(20):
        layer = random.choice(layers)
        pos_list = ctx.layer_positions[layer]
        a, b = random.sample(range(len(pos_list)), 2)
        ia = pos_list[a].gene_idx
        ib = pos_list[b].gene_idx
        if ia in protected or ib in protected:
            continue
        grp_a = ctx.find_group_at(genome, ia)
        grp_b = ctx.find_group_at(genome, ib)
        if grp_a and ib not in grp_a:
            continue
        if grp_b and ia not in grp_b:
            continue
        if not ctx.position_accepts_sid(ia, genome[ib]):
            continue
        if not ctx.position_accepts_sid(ib, genome[ia]):
            continue
        genome[ia], genome[ib] = genome[ib], genome[ia]
        return genome
    return genome


def swap_to_empty(genome, ctx):
    """Move an assigned shortcut to an empty position, biased toward lower effort."""
    genome = copy.copy(genome)
    protected = ctx.protected_indices(genome)
    for _ in range(20):
        layer = random.choice(ctx.layer_keys)
        pos_list = ctx.layer_positions[layer]
        assigned = [p for p in pos_list if genome[p.gene_idx] >= 0 and p.gene_idx not in protected]
        empty = [p for p in pos_list if genome[p.gene_idx] < 0]
        if assigned and empty:
            src = random.choice(assigned)
            grp = ctx.find_group_at(genome, src.gene_idx)
            if grp and len(grp) >= 2:
                continue
            empty = [p for p in empty if ctx.position_accepts_sid(p.gene_idx, genome[src.gene_idx])]
            if not empty:
                continue
            empty.sort(key=lambda p: p.effort)
            pick_idx = min(int(random.expovariate(2.0) * len(empty)), len(empty) - 1)
            dst = empty[pick_idx]
            genome[dst.gene_idx] = genome[src.gene_idx]
            genome[src.gene_idx] = -1
            return genome
    return genome


def thumb_fill(genome, ctx):
    genome = copy.copy(genome)
    assigned_sids = {s for s in genome if s >= 0}
    pool = ctx.shortcut_pool
    unassigned = [s for s in pool if s.sid not in assigned_sids]
    if not unassigned:
        return genome

    for layer, pos_list in ctx.layer_positions.items():
        candidates = [s for s in unassigned if s.importance >= 3.0]
        if not candidates:
            continue

        empty_thumbs = [p for p in pos_list if p.is_thumb and genome[p.gene_idx] < 0]
        compatible = [
            (s, p) for s in candidates for p in empty_thumbs
            if ctx.position_accepts_sid(p.gene_idx, s.sid)
        ]
        if not compatible:
            continue

        shortcut, target = max(
            compatible,
            key=lambda item: (item[0].importance, -item[1].effort),
        )
        genome[target.gene_idx] = shortcut.sid
        assigned_sids.add(shortcut.sid)
        unassigned = [s for s in unassigned if s.sid != shortcut.sid]

    return genome


def migrate_shortcut(genome, ctx):
    """Place an unassigned shortcut, prioritizing high-importance ones."""
    genome = copy.copy(genome)
    pool = ctx.shortcut_pool

    assigned_sids = {sid for sid in genome if sid >= 0}
    unassigned = [s for s in pool if s.sid not in assigned_sids]
    if not unassigned:
        return genome

    protected = ctx.protected_indices(genome)

    if random.random() < 0.7:
        unassigned.sort(key=lambda s: -s.importance)
        pick_idx = min(int(random.expovariate(1.5) * 10), len(unassigned) - 1)
        shortcut = unassigned[pick_idx]
    else:
        shortcut = random.choice(unassigned)

    layer_order = list(ctx.layer_positions.keys())
    random.shuffle(layer_order)
    shortcut_apps = ctx.apps_for_sid(shortcut.sid)

    def layer_affinity(layer):
        score = 0
        for p in ctx.layer_positions[layer]:
            sid = genome[p.gene_idx]
            if sid < 0 or sid >= ctx.pool_size:
                continue
            if shortcut_apps & ctx.apps_for_sid(sid):
                score += 1
        return score

    layer_order.sort(key=lambda l: -layer_affinity(l))
    for layer in layer_order:
        pos_list = ctx.layer_positions[layer]
        empty = [
            p for p in pos_list
            if genome[p.gene_idx] < 0 and p.gene_idx not in protected
            and ctx.position_accepts_sid(p.gene_idx, shortcut.sid)
        ]
        if empty:
            target = min(empty, key=lambda p: p.effort)
            genome[target.gene_idx] = shortcut.sid
            return genome

    return genome


def deduplicate(genome, ctx):
    """Remove a same-layer duplicate and optionally replace with an unassigned shortcut."""
    genome = copy.copy(genome)
    pool = ctx.shortcut_pool

    for layer, pos_list in ctx.layer_positions.items():
        seen = {}
        dupes = []
        for p in pos_list:
            sid = genome[p.gene_idx]
            if sid < 0:
                continue
            if sid in seen:
                dupes.append(p)
            else:
                seen[sid] = p
        if not dupes:
            continue
        target = random.choice(dupes)
        genome[target.gene_idx] = -1

        if random.random() < 0.5:
            assigned_sids = {s for s in genome if s >= 0}
            candidates = [
                s for s in pool
                if s.sid not in assigned_sids and ctx.position_accepts_sid(target.gene_idx, s.sid)
            ]
            if candidates:
                best = max(candidates, key=lambda s: s.importance)
                genome[target.gene_idx] = best.sid
        return genome

    return genome


def improve_coherence(genome, ctx):
    """Move a shortcut to a layer with more same-app shortcuts (emergent coherence)."""
    genome = copy.copy(genome)
    pool = ctx.shortcut_pool
    protected = ctx.protected_indices(genome)

    candidates = []
    for i, sid in enumerate(genome):
        if sid < 0 or i in protected or sid >= ctx.pool_size:
            continue
        if sid in ctx.sid_is_base_key:
            continue
        candidates.append(i)

    if not candidates:
        return genome

    src_idx = random.choice(candidates)
    sid = genome[src_idx]
    src_layer = ctx.positions[src_idx].layer
    shortcut_apps = ctx.apps_for_sid(sid)

    layer_affinity = {}
    for layer, pos_list in ctx.layer_positions.items():
        if layer == src_layer:
            continue
        count = 0
        for p in pos_list:
            other = genome[p.gene_idx]
            if other < 0 or other >= ctx.pool_size:
                continue
            if shortcut_apps & ctx.apps_for_sid(other):
                count += 1
        if count > 0:
            layer_affinity[layer] = count

    if not layer_affinity:
        return genome

    best_layer = max(layer_affinity, key=layer_affinity.get)
    empty = [p for p in ctx.layer_positions[best_layer]
             if genome[p.gene_idx] < 0 and p.gene_idx not in protected
             and ctx.position_accepts_sid(p.gene_idx, sid)]
    if empty:
        target = min(empty, key=lambda p: p.effort)
        genome[target.gene_idx] = sid
        genome[src_idx] = -1

    return genome


def move_group(genome, ctx):
    """Move an entire protected group to a new location on the same hand, same layer."""
    genome = copy.copy(genome)
    pool = ctx.shortcut_pool

    all_groups = list(ctx.static_groups) + ctx.dynamic_groups
    if not all_groups:
        return genome

    random.shuffle(all_groups)
    for group in all_groups:
        is_dynamic = group.get("dynamic", False)

        by_layer = {}
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            if is_dynamic:
                if sid in group["sids"]:
                    by_layer.setdefault(ctx.positions[i].layer, []).append(i)
            else:
                s = pool[sid]
                if shortcut_matches_group(s, group):
                    by_layer.setdefault(ctx.positions[i].layer, []).append(i)

        if not by_layer:
            continue

        layer = random.choice(list(by_layer.keys()))
        member_indices = by_layer[layer]
        if len(member_indices) < 2:
            continue

        member_hand = ctx.positions[member_indices[0]].hand
        pos_list = ctx.layer_positions.get(layer, [])
        same_hand = [p for p in pos_list if p.hand == member_hand]
        member_set = set(member_indices)
        non_member = [p for p in same_hand if p.gene_idx not in member_set]

        empty_on_hand = [p for p in non_member if genome[p.gene_idx] < 0]
        if len(empty_on_hand) < len(member_indices):
            continue

        anchor = random.choice(empty_on_hand)
        targets = sorted(empty_on_hand, key=lambda p: abs(p.x - anchor.x) + abs(p.y - anchor.y))
        targets = targets[:len(member_indices)]

        sids = [genome[i] for i in member_indices]
        if any(not ctx.position_accepts_sid(t.gene_idx, sid) for sid, t in zip(sids, targets)):
            continue
        for i in member_indices:
            genome[i] = -1
        for sid, t in zip(sids, targets):
            genome[t.gene_idx] = sid

        return genome

    return genome


def swap_layer_content(genome, ctx):
    """Swap all shortcuts between two layers."""
    genome = copy.copy(genome)
    protected = ctx.protected_indices(genome)
    layers = ctx.layer_keys
    if len(layers) < 2:
        return genome
    la, lb = random.sample(layers, 2)
    pos_a = ctx.layer_positions[la]
    pos_b = ctx.layer_positions[lb]
    sids_a = [(p.gene_idx, genome[p.gene_idx]) for p in pos_a if genome[p.gene_idx] >= 0 and p.gene_idx not in protected]
    sids_b = [(p.gene_idx, genome[p.gene_idx]) for p in pos_b if genome[p.gene_idx] >= 0 and p.gene_idx not in protected]
    for idx, _ in sids_a:
        genome[idx] = -1
    for idx, _ in sids_b:
        genome[idx] = -1
    empty_a = [p for p in pos_a if genome[p.gene_idx] < 0 and p.gene_idx not in protected]
    empty_b = [p for p in pos_b if genome[p.gene_idx] < 0 and p.gene_idx not in protected]
    empty_a.sort(key=lambda p: p.effort)
    empty_b.sort(key=lambda p: p.effort)
    for i, (_, sid) in enumerate(sids_b):
        targets = [p for p in empty_a if ctx.position_accepts_sid(p.gene_idx, sid)]
        if targets:
            target = targets[0]
            genome[target.gene_idx] = sid
            empty_a.remove(target)
    for i, (_, sid) in enumerate(sids_a):
        targets = [p for p in empty_b if ctx.position_accepts_sid(p.gene_idx, sid)]
        if targets:
            target = targets[0]
            genome[target.gene_idx] = sid
            empty_b.remove(target)
    _repair_layer_dupes(genome, pos_a, protected)
    _repair_layer_dupes(genome, pos_b, protected)
    return genome


def _repair_layer_dupes(genome, layer_pos_list, protected=None):
    """Remove same-layer duplicates created by layer swaps."""
    protected = protected or set()
    seen = set()
    for p in layer_pos_list:
        sid = genome[p.gene_idx]
        if sid < 0:
            continue
        if sid in seen and p.gene_idx not in protected:
            genome[p.gene_idx] = -1
        else:
            seen.add(sid)


def redistribute_shortcuts(genome, ctx):
    """Move a random subset of shortcuts from one layer to another with empty slots."""
    genome = copy.copy(genome)
    protected = ctx.protected_indices(genome)
    layers = ctx.layer_keys
    if len(layers) < 2:
        return genome
    src_layer = random.choice(layers)
    dst_layer = random.choice([l for l in layers if l != src_layer])
    src_pos = ctx.layer_positions[src_layer]
    dst_pos = ctx.layer_positions[dst_layer]
    movable = [p for p in src_pos if genome[p.gene_idx] >= 0 and p.gene_idx not in protected
                and not ctx.find_group_at(genome, p.gene_idx)]
    empty_dst = [p for p in dst_pos if genome[p.gene_idx] < 0]
    if not movable or not empty_dst:
        return genome
    n_move = random.randint(1, min(5, len(movable), len(empty_dst)))
    to_move = random.sample(movable, n_move)
    empty_dst.sort(key=lambda p: p.effort)
    for i, src_p in enumerate(to_move):
        targets = [p for p in empty_dst if ctx.position_accepts_sid(p.gene_idx, genome[src_p.gene_idx])]
        if targets:
            target = targets[0]
            genome[target.gene_idx] = genome[src_p.gene_idx]
            genome[src_p.gene_idx] = -1
            empty_dst.remove(target)
    return genome


def cross_layer_deduplicate(genome, ctx):
    """Remove a cross-layer duplicate (shortcut on 3+ layers) and replace with unassigned."""
    genome = copy.copy(genome)
    pool = ctx.shortcut_pool
    positions = ctx.positions
    sid_positions = {}
    for i, sid in enumerate(genome):
        if sid >= 0:
            sid_positions.setdefault(int(sid), []).append(i)
    cross_dupes = {sid: idxs for sid, idxs in sid_positions.items()
                   if len(set(positions[i].layer for i in idxs)) > 2}
    if not cross_dupes:
        return genome
    sid = random.choice(list(cross_dupes.keys()))
    idxs = cross_dupes[sid]
    remove_idx = random.choice(idxs)
    genome[remove_idx] = -1
    if random.random() < 0.6:
        assigned_sids = {s for s in genome if s >= 0}
        candidates = [
            s for s in pool
            if s.sid not in assigned_sids and s.importance >= 3.0
            and ctx.position_accepts_sid(remove_idx, s.sid)
        ]
        if candidates:
            best = max(candidates, key=lambda s: s.importance)
            genome[remove_idx] = best.sid
    return genome


def _pick_operator(r, phase, scratch=False):
    """Return operator index based on random value and evolution phase.
    Phase: 'explore' (early), 'balanced' (mid), 'exploit' (late).
    Operator order: swap_within, swap_to_empty, migrate, move_group, thumb_fill,
                    deduplicate, improve_coherence, swap_layer_content,
                    redistribute, cross_layer_dedup."""
    if scratch:
        if phase == "explore":
            # Heavy migrate + redistribute + cross-layer dedup to build and balance layers
            thresholds = [0.04, 0.08, 0.38, 0.43, 0.50, 0.58, 0.65, 0.72, 0.85, 1.00]
        elif phase == "exploit":
            # Refinement: swap, coherence, deduplicate
            thresholds = [0.18, 0.25, 0.35, 0.42, 0.48, 0.60, 0.75, 0.80, 0.88, 1.00]
        else:
            # Balanced: all operators active
            thresholds = [0.08, 0.14, 0.34, 0.40, 0.47, 0.57, 0.68, 0.75, 0.87, 1.00]
    else:
        if phase == "explore":
            thresholds = [0.05, 0.10, 0.40, 0.46, 0.52, 0.60, 0.68, 0.73, 0.80, 1.00]
        elif phase == "exploit":
            thresholds = [0.20, 0.26, 0.36, 0.42, 0.48, 0.60, 0.75, 0.80, 0.86, 1.00]
        else:
            thresholds = [0.08, 0.14, 0.35, 0.42, 0.48, 0.60, 0.70, 0.76, 0.84, 1.00]
    for i, t in enumerate(thresholds):
        if r < t:
            return i
    return 9


def custom_mutate(genome, ctx, scratch_mode=False, generation=0, n_ops=1, phase=None):
    """Apply n_ops mutation operators in sequence. n_ops > 1 for stronger mutation."""
    ops = [
        lambda g: swap_within_layer(g, ctx),
        lambda g: swap_to_empty(g, ctx),
        lambda g: migrate_shortcut(g, ctx),
        lambda g: move_group(g, ctx),
        lambda g: thumb_fill(g, ctx),
        lambda g: deduplicate(g, ctx),
        lambda g: improve_coherence(g, ctx),
        lambda g: swap_layer_content(g, ctx),
        lambda g: redistribute_shortcuts(g, ctx),
        lambda g: cross_layer_deduplicate(g, ctx),
    ]

    if phase is not None:
        pass
    elif scratch_mode:
        if generation < 150:
            phase = "explore"
        elif generation < 800:
            phase = "balanced"
        else:
            phase = "exploit"
    else:
        if generation < 100:
            phase = "explore"
        elif generation < 500:
            phase = "balanced"
        else:
            phase = "exploit"

    g = genome
    for _ in range(n_ops):
        idx = _pick_operator(random.random(), phase, scratch=scratch_mode)
        g = ops[idx](g)
    g, _ = repair_position_compatibility(g, ctx)
    return (g,)


def pmx_crossover(parent1, parent2, ctx):
    child1 = copy.copy(parent1)
    child2 = copy.copy(parent2)

    protected1 = ctx.protected_indices(parent1)
    protected2 = ctx.protected_indices(parent2)

    for layer, indices in ctx.layer_gene_indices.items():
        if len(indices) < 4:
            continue

        safe_indices = [i for i in indices if i not in protected1 and i not in protected2]
        if len(safe_indices) < 4:
            continue

        n = len(safe_indices)
        a, b = sorted(random.sample(range(n), 2))

        seg1 = [parent1[safe_indices[i]] for i in range(a, b)]
        seg2 = [parent2[safe_indices[i]] for i in range(a, b)]

        for i in range(a, b):
            target = safe_indices[i]
            if ctx.position_accepts_sid(target, seg2[i - a]):
                child1[target] = seg2[i - a]
            if ctx.position_accepts_sid(target, seg1[i - a]):
                child2[target] = seg1[i - a]

        _repair_duplicates_on_layer(child1, indices)
        _repair_duplicates_on_layer(child2, indices)

    return child1, child2


def _repair_duplicates_on_layer(genome, layer_indices, protected=None):
    protected = protected or set()
    seen = set()
    for i in layer_indices:
        sid = genome[i]
        if sid < 0:
            continue
        if sid in seen and i not in protected:
            genome[i] = -1
        else:
            seen.add(sid)


# ---------------------------------------------------------------------------
# Batched GPU operators — population-level mutation on CUDA tensors
# ---------------------------------------------------------------------------
# All batch operators use sentinel S (pool_size) for empty positions (not -1).
# Genomes tensor: (B, N) long, values in [0, S] where S = empty.
# Protected mask: (B, N) bool, True = cannot modify.

def compute_protected_mask_gpu(genomes, ctx):
    """Compute protection mask for B genomes in one tensor operation."""
    S = ctx.pool_size
    safe_g = genomes.clamp(min=0, max=S)
    assigned = (genomes >= 0) & (genomes < S)
    illegal_l0 = (
        ctx.t_l0_mutable_thumb.unsqueeze(0) &
        assigned &
        ~ctx.t_l0_thumb_worthy_sid[safe_g]
    )
    protected_by_sid = ctx.t_sid_is_protected[safe_g] & assigned & ~illegal_l0
    return protected_by_sid | ctx.t_frozen_mask.unsqueeze(0)


def _gpu_position_accepts_sid(ctx, idx, sid):
    safe_sid = sid.clamp(min=0, max=ctx.pool_size)
    needs_worthy = ctx.t_l0_mutable_thumb[idx]
    return (~needs_worthy) | ctx.t_l0_thumb_worthy_sid[safe_sid]


def batch_swap_within_layer(genomes, protected_mask, ctx):
    """Swap two non-protected positions on a random layer, for all B genomes."""
    B, N = genomes.shape
    d = ctx.device
    S = ctx.pool_size

    n_layers = len(ctx.layers_with_2plus)
    if n_layers == 0:
        return genomes.clone()
    layer_choice = torch.randint(0, n_layers, (B,), device=d)
    chosen = ctx.layers_with_2plus_t[layer_choice]

    on_layer = (ctx.t_layer_arr.unsqueeze(0) == chosen.unsqueeze(1))
    mutable = on_layer & ~protected_mask
    mutable_count = mutable.long().sum(dim=1)
    valid = (mutable_count >= 2)

    noise = torch.rand(B, N, device=d)
    noise[~mutable] = -1.0
    _, top2 = noise.topk(2, dim=1)
    idx_a = top2[:, 0]
    idx_b = top2[:, 1]

    val_a = genomes.gather(1, idx_a.unsqueeze(1)).squeeze(1)
    val_b = genomes.gather(1, idx_b.unsqueeze(1)).squeeze(1)
    valid = valid & _gpu_position_accepts_sid(ctx, idx_a, val_b)
    valid = valid & _gpu_position_accepts_sid(ctx, idx_b, val_a)

    result = genomes.clone()
    v = valid.unsqueeze(1)
    result.scatter_(1, idx_a.unsqueeze(1), torch.where(v, val_b.unsqueeze(1), val_a.unsqueeze(1)))
    result.scatter_(1, idx_b.unsqueeze(1), torch.where(v, val_a.unsqueeze(1), val_b.unsqueeze(1)))
    return result


def batch_swap_to_empty(genomes, protected_mask, ctx):
    """Move an assigned non-protected shortcut to an empty position, effort-biased."""
    B, N = genomes.shape
    d = ctx.device
    S = ctx.pool_size

    n_layers = len(ctx.layer_keys)
    layer_choice = torch.randint(0, n_layers, (B,), device=d)
    chosen = ctx.layer_keys_t[layer_choice]

    on_layer = (ctx.t_layer_arr.unsqueeze(0) == chosen.unsqueeze(1))
    assigned = (genomes >= 0) & (genomes < S)
    src_cand = on_layer & assigned & ~protected_mask
    empty = (genomes >= S)
    dst_cand = on_layer & empty & ~protected_mask

    has_src = src_cand.any(dim=1)
    has_dst = dst_cand.any(dim=1)
    valid = has_src & has_dst

    src_noise = torch.rand(B, N, device=d)
    src_noise[~src_cand] = -1.0
    _, src_top = src_noise.topk(1, dim=1)
    src_idx = src_top.squeeze(1)

    effort_w = torch.exp(-2.0 * ctx.t_effort_arr).unsqueeze(0)
    dst_score = effort_w * dst_cand.float() + torch.rand(B, N, device=d) * 0.01 * dst_cand.float()
    dst_score[~dst_cand] = -1.0
    _, dst_top = dst_score.topk(1, dim=1)
    dst_idx = dst_top.squeeze(1)

    src_vals = genomes.gather(1, src_idx.unsqueeze(1))
    valid = valid & _gpu_position_accepts_sid(ctx, dst_idx, src_vals.squeeze(1))
    result = genomes.clone()
    v = valid.unsqueeze(1)
    result.scatter_(1, dst_idx.unsqueeze(1), torch.where(v, src_vals, result.gather(1, dst_idx.unsqueeze(1))))
    result.scatter_(1, src_idx.unsqueeze(1), torch.where(v, torch.full_like(src_vals, S), result.gather(1, src_idx.unsqueeze(1))))
    return result


def batch_migrate_shortcut(genomes, protected_mask, ctx):
    """Place one unassigned high-importance shortcut per genome."""
    B, N = genomes.shape
    S = ctx.pool_size
    d = ctx.device

    safe_g = genomes.clamp(min=0, max=S)
    sid_count = torch.zeros(B, S + 1, device=d, dtype=torch.int16)
    ones = torch.ones(B, N, device=d, dtype=torch.int16)
    sid_count.scatter_add_(1, safe_g, ones)

    unassigned = (sid_count[:, :S] == 0) & ~ctx.t_is_base_key[:S].unsqueeze(0)
    imp = ctx.t_importance[:S].unsqueeze(0) * unassigned.float()
    imp += torch.rand(B, S, device=d) * 0.1 * unassigned.float()
    imp[~unassigned] = -1.0
    _, chosen_sid = imp.topk(1, dim=1)
    chosen_sid = chosen_sid.squeeze(1)

    empty = (genomes >= S)
    chosen_worthy = ctx.t_l0_thumb_worthy_sid[chosen_sid].unsqueeze(1)
    dst_compatible = (~ctx.t_l0_mutable_thumb.unsqueeze(0)) | chosen_worthy
    dst_cand = empty & ~protected_mask & dst_compatible
    effort_score = -ctx.t_effort_arr.unsqueeze(0) * dst_cand.float()
    effort_score += torch.rand(B, N, device=d) * 0.01 * dst_cand.float()
    effort_score[~dst_cand] = -float('inf')
    _, dst_idx = effort_score.topk(1, dim=1)
    dst_idx = dst_idx.squeeze(1)

    has_unassigned = unassigned.any(dim=1)
    has_empty = dst_cand.any(dim=1)
    valid = has_unassigned & has_empty

    result = genomes.clone()
    v = valid.unsqueeze(1)
    result.scatter_(1, dst_idx.unsqueeze(1), torch.where(v, chosen_sid.unsqueeze(1), result.gather(1, dst_idx.unsqueeze(1))))
    return result


def batch_deduplicate(genomes, protected_mask, ctx):
    """Remove one same-layer duplicate SID per genome."""
    B, N = genomes.shape
    S = ctx.pool_size
    d = ctx.device

    safe_g = genomes.clamp(min=0, max=S)
    assigned = (genomes >= 0) & (genomes < S)
    layer_sid = ctx.t_layer_arr.unsqueeze(0) * (S + 1) + safe_g
    layer_sid_count = torch.zeros(B, ctx.n_layers * (S + 1), device=d, dtype=torch.int16)
    ones = torch.ones(B, N, device=d, dtype=torch.int16)
    layer_sid_count.scatter_add_(1, layer_sid, ones * assigned.short())

    pos_count = layer_sid_count.gather(1, layer_sid)
    is_dupe = (pos_count >= 2) & assigned & ~protected_mask

    noise = torch.rand(B, N, device=d)
    noise[~is_dupe] = -1.0
    _, top = noise.topk(1, dim=1)
    dupe_idx = top.squeeze(1)
    has_dupe = is_dupe.any(dim=1)

    result = genomes.clone()
    v = has_dupe.unsqueeze(1)
    result.scatter_(1, dupe_idx.unsqueeze(1), torch.where(v, torch.full((B, 1), S, device=d, dtype=genomes.dtype), result.gather(1, dupe_idx.unsqueeze(1))))
    return result


def batch_cross_layer_deduplicate(genomes, protected_mask, ctx):
    """Remove one instance of a SID appearing on 3+ different layers."""
    B, N = genomes.shape
    S = ctx.pool_size
    d = ctx.device
    n_layers = ctx.n_layers

    safe_g = genomes.clamp(min=0, max=S)
    assigned = (genomes >= 0) & (genomes < S)
    layers = ctx.t_layer_arr

    layer_present = torch.zeros(B, S, n_layers, device=d, dtype=torch.bool)
    for l in range(n_layers):
        on_l = (layers == l).unsqueeze(0) & assigned
        l_sids = safe_g.clone()
        l_sids[~on_l] = S
        present = torch.zeros(B, S + 1, device=d, dtype=torch.bool)
        present.scatter_(1, l_sids, on_l)
        layer_present[:, :, l] = present[:, :S]

    n_distinct = layer_present.long().sum(dim=2)
    cross_dupe = (n_distinct >= 3)

    sid_is_cross = torch.zeros(B, S + 1, device=d, dtype=torch.bool)
    sid_is_cross[:, :S] = cross_dupe
    removable = sid_is_cross.gather(1, safe_g) & assigned & ~protected_mask

    noise = torch.rand(B, N, device=d)
    noise[~removable] = -1.0
    _, top = noise.topk(1, dim=1)
    remove_idx = top.squeeze(1)
    has_removable = removable.any(dim=1)

    result = genomes.clone()
    v = has_removable.unsqueeze(1)
    result.scatter_(1, remove_idx.unsqueeze(1), torch.where(v, torch.full((B, 1), S, device=d, dtype=genomes.dtype), result.gather(1, remove_idx.unsqueeze(1))))
    return result


def batch_thumb_fill(genomes, protected_mask, ctx):
    """Fill one empty thumb position per genome with a high-importance unassigned shortcut."""
    B, N = genomes.shape
    S = ctx.pool_size
    d = ctx.device

    safe_g = genomes.clamp(min=0, max=S)
    sid_count = torch.zeros(B, S + 1, device=d, dtype=torch.int16)
    ones = torch.ones(B, N, device=d, dtype=torch.int16)
    sid_count.scatter_add_(1, safe_g, ones)

    unassigned = (sid_count[:, :S] == 0) & ~ctx.t_is_base_key[:S].unsqueeze(0)
    imp = ctx.t_importance[:S].unsqueeze(0) * unassigned.float()
    imp[~unassigned] = -1.0
    has_unassigned = unassigned.any(dim=1)
    _, chosen_sid = imp.topk(1, dim=1)
    chosen_sid = chosen_sid.squeeze(1)

    is_thumb = ctx.t_is_thumb.unsqueeze(0).expand(B, -1)
    empty = (genomes >= S)
    chosen_worthy = ctx.t_l0_thumb_worthy_sid[chosen_sid].unsqueeze(1)
    dst_compatible = (~ctx.t_l0_mutable_thumb.unsqueeze(0)) | chosen_worthy
    thumb_cand = is_thumb & empty & ~protected_mask & dst_compatible
    has_thumb = thumb_cand.any(dim=1)

    noise = torch.rand(B, N, device=d)
    noise[~thumb_cand] = -1.0
    _, top = noise.topk(1, dim=1)
    dst_idx = top.squeeze(1)

    valid = has_unassigned & has_thumb
    result = genomes.clone()
    v = valid.unsqueeze(1)
    result.scatter_(1, dst_idx.unsqueeze(1), torch.where(v, chosen_sid.unsqueeze(1), result.gather(1, dst_idx.unsqueeze(1))))
    return result


def batch_redistribute(genomes, protected_mask, ctx):
    """Move 1-3 shortcuts from one random layer to another with empty slots."""
    B, N = genomes.shape
    S = ctx.pool_size
    d = ctx.device

    n_layers = len(ctx.layer_keys)
    if n_layers < 2:
        return genomes.clone()

    src_choice = torch.randint(0, n_layers, (B,), device=d)
    dst_choice = (src_choice + torch.randint(1, n_layers, (B,), device=d)) % n_layers
    src_layer = ctx.layer_keys_t[src_choice]
    dst_layer = ctx.layer_keys_t[dst_choice]

    layers = ctx.t_layer_arr.unsqueeze(0)
    assigned = (genomes >= 0) & (genomes < S)

    on_src = (layers == src_layer.unsqueeze(1))
    movable = on_src & assigned & ~protected_mask
    on_dst = (layers == dst_layer.unsqueeze(1))
    empty_dst = on_dst & (genomes >= S) & ~protected_mask

    has_movable = movable.any(dim=1)
    has_empty = empty_dst.any(dim=1)
    valid = has_movable & has_empty

    # Pick one random movable position
    src_noise = torch.rand(B, N, device=d)
    src_noise[~movable] = -1.0
    _, src_top = src_noise.topk(1, dim=1)
    src_idx = src_top.squeeze(1)

    # Pick one empty destination (effort-biased)
    effort_w = torch.exp(-2.0 * ctx.t_effort_arr).unsqueeze(0)
    dst_score = effort_w * empty_dst.float() + torch.rand(B, N, device=d) * 0.01 * empty_dst.float()
    dst_score[~empty_dst] = -1.0
    _, dst_top = dst_score.topk(1, dim=1)
    dst_idx = dst_top.squeeze(1)

    result = genomes.clone()
    src_vals = result.gather(1, src_idx.unsqueeze(1))
    valid = valid & _gpu_position_accepts_sid(ctx, dst_idx, src_vals.squeeze(1))
    v = valid.unsqueeze(1)
    result.scatter_(1, dst_idx.unsqueeze(1), torch.where(v, src_vals, result.gather(1, dst_idx.unsqueeze(1))))
    result.scatter_(1, src_idx.unsqueeze(1), torch.where(v, torch.full_like(src_vals, S), result.gather(1, src_idx.unsqueeze(1))))
    return result


def batch_crossover_gpu(parents1, parents2, protected_mask, ctx):
    """Uniform layer crossover for P pairs on GPU.

    For each layer, each non-protected position independently picks from
    parent1 or parent2 with 50% probability. No duplicate repair needed
    since parents already have valid per-layer SID sets and the deduplicate
    mutation operator handles any cross-parent conflicts.
    """
    P, N = parents1.shape
    d = ctx.device

    # Per-position random coin flip: True = take from parent2
    coin = torch.rand(P, N, device=d) > 0.5
    # Protected positions keep parent1's value
    coin = coin & ~protected_mask

    child1 = torch.where(coin, parents2, parents1)
    child2 = torch.where(coin, parents1, parents2)

    return child1, child2


GPU_OP_MAP = {0: batch_swap_within_layer, 1: batch_swap_to_empty,
              2: batch_migrate_shortcut, 4: batch_thumb_fill,
              5: batch_deduplicate, 8: batch_redistribute,
              9: batch_cross_layer_deduplicate}
GPU_OP_IDS = frozenset(GPU_OP_MAP.keys())
