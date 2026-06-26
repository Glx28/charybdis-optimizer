"""Custom mutation and crossover operators for keyboard layout evolution.

All operators are layer-aware, preserve structural positions, and protect key groups.
"""
import random
import copy
from representation import (
    Position, Shortcut, LAYER_ACCESS,
    build_layer_to_positions, is_structural,
    is_in_protected_group, find_group_members, KEY_GROUPS,
)


_FROZEN_L0_OPEN = None
_FROZEN_L2_MOUSE = set()


def set_frozen_l0(positions, open_gene_indices):
    """Set which L0 positions are open for mutation. All other L0 positions are frozen."""
    global _FROZEN_L0_OPEN
    open_set = set(open_gene_indices)
    _FROZEN_L0_OPEN = set()
    for i, p in enumerate(positions):
        if p.layer == 0 and i not in open_set:
            _FROZEN_L0_OPEN.add(i)
    print(f"  L0 frozen: {len(_FROZEN_L0_OPEN)} positions, {len(open_set)} open")


def set_frozen_l2_mouse(positions, pool, genome):
    """Freeze all currently-assigned L2 positions in operators.
    L2 is one-handed mouse mode — every assigned key is contextually critical
    (mouse buttons, clipboard, window management, navigation). Displacing any
    of them breaks the one-handed workflow."""
    global _FROZEN_L2_MOUSE
    _FROZEN_L2_MOUSE = set()
    for i, p in enumerate(positions):
        if p.layer != 2:
            continue
        sid = genome[i] if i < len(genome) else -1
        if sid >= 0:
            _FROZEN_L2_MOUSE.add(i)
    print(f"  L2 frozen in operators: {len(_FROZEN_L2_MOUSE)} positions (all assigned)")


def _protected_gene_indices(genome, positions, pool, dynamic_groups=None):
    """Return set of gene indices that belong to protected groups or frozen L0."""
    protected = set()
    if _FROZEN_L0_OPEN is not None:
        protected.update(_FROZEN_L0_OPEN)
    # L2 mouse positions no longer frozen — protected by accessibility reward instead
    for group in KEY_GROUPS:
        if not group.get("protected"):
            continue
        if "behaviors" in group:
            continue
        params = [p.upper() for p in group.get("params", [])]
        mods_req = group.get("mods_required", "")
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            s = pool[sid]
            if s.base_key.upper() not in params:
                continue
            if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
                continue
            protected.add(i)
    for dg in (dynamic_groups or []):
        for i, sid in enumerate(genome):
            if sid >= 0 and sid in dg.get("sids", []):
                protected.add(i)
    return protected


def _find_group_members_at(genome, positions, pool, gene_idx):
    """If genome[gene_idx] is part of a protected group, return all gene indices
    of that group on the same layer. Otherwise return None."""
    sid = genome[gene_idx]
    if sid < 0 or pool is None:
        return None
    s = pool[sid]
    layer = positions[gene_idx].layer
    for group in KEY_GROUPS:
        if not group.get("protected") or "behaviors" in group:
            continue
        params = [p.upper() for p in group.get("params", [])]
        mods_req = group.get("mods_required", "")
        if s.base_key.upper() not in params:
            continue
        if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
            continue
        # Found the group — collect all members on same layer
        members = []
        for i, sid2 in enumerate(genome):
            if sid2 < 0 or positions[i].layer != layer:
                continue
            s2 = pool[sid2]
            if s2.base_key.upper() not in params:
                continue
            if mods_req and not any(mods_req.lower() in m.lower() for m in s2.modifiers):
                continue
            members.append(i)
        return members if len(members) >= 2 else None
    return None


def swap_within_layer(genome, positions, layer_positions=None, pool=None, dynamic_groups=None):
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)
    protected = _protected_gene_indices(genome, positions, pool, dynamic_groups) if pool else set()
    layers = [l for l in layer_positions if len(layer_positions[l]) >= 2]
    if not layers:
        return genome
    for _ in range(20):
        layer = random.choice(layers)
        pos_list = layer_positions[layer]
        a, b = random.sample(range(len(pos_list)), 2)
        ia = pos_list[a].gene_idx
        ib = pos_list[b].gene_idx
        if ia in protected or ib in protected:
            continue
        # If swapping a group member with a non-member, skip — would break group
        grp_a = _find_group_members_at(genome, positions, pool, ia)
        grp_b = _find_group_members_at(genome, positions, pool, ib)
        if grp_a and ib not in grp_a:
            continue
        if grp_b and ia not in grp_b:
            continue
        genome[ia], genome[ib] = genome[ib], genome[ia]
        return genome
    return genome


def swap_to_empty(genome, positions, layer_positions=None, pool=None, dynamic_groups=None):
    """Move an assigned shortcut to an empty position, biased toward lower effort."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)
    protected = _protected_gene_indices(genome, positions, pool, dynamic_groups) if pool else set()
    for _ in range(20):
        layer = random.choice(list(layer_positions.keys()))
        pos_list = layer_positions[layer]
        assigned = [p for p in pos_list if genome[p.gene_idx] >= 0 and p.gene_idx not in protected]
        empty = [p for p in pos_list if genome[p.gene_idx] < 0]
        if assigned and empty:
            src = random.choice(assigned)
            # Don't move a group member away from its group
            grp = _find_group_members_at(genome, positions, pool, src.gene_idx)
            if grp and len(grp) >= 2:
                continue
            # Bias toward lower-effort targets
            empty.sort(key=lambda p: p.effort)
            pick_idx = min(int(random.expovariate(2.0) * len(empty)), len(empty) - 1)
            dst = empty[pick_idx]
            genome[dst.gene_idx] = genome[src.gene_idx]
            genome[src.gene_idx] = -1
            return genome
    return genome


def thumb_fill(genome, positions, shortcut_pool, layer_positions=None):
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)

    assigned_sids = set(s for s in genome if s >= 0)
    unassigned = [s for s in shortcut_pool if s.sid not in assigned_sids]
    if not unassigned:
        return genome

    for layer, pos_list in layer_positions.items():
        empty_thumbs = [p for p in pos_list if p.is_thumb and genome[p.gene_idx] < 0]
        if not empty_thumbs:
            continue

        candidates = [s for s in unassigned if s.importance >= 3.0]
        if not candidates:
            continue

        target = random.choice(empty_thumbs)
        shortcut = max(candidates, key=lambda s: s.importance)
        genome[target.gene_idx] = shortcut.sid
        assigned_sids.add(shortcut.sid)
        unassigned = [s for s in unassigned if s.sid != shortcut.sid]

    return genome


def migrate_shortcut(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None):
    """Place an unassigned shortcut, prioritizing high-importance ones."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)

    assigned_sids = set(s for s in genome if s >= 0)
    unassigned = [s for s in shortcut_pool if s.sid not in assigned_sids]
    if not unassigned:
        return genome

    protected = _protected_gene_indices(genome, positions, shortcut_pool, dynamic_groups)

    # 70% chance pick from top-importance unassigned, 30% random
    if random.random() < 0.7:
        unassigned.sort(key=lambda s: -s.importance)
        # Pick from top 10 with exponential bias toward most important
        pick_idx = min(int(random.expovariate(1.5) * 10), len(unassigned) - 1)
        shortcut = unassigned[pick_idx]
    else:
        shortcut = random.choice(unassigned)

    # Try all layers, preferring those with existing same-app shortcuts (emergent coherence)
    layer_order = list(layer_positions.keys())
    random.shuffle(layer_order)
    shortcut_apps = set(shortcut.apps) if shortcut.apps else {shortcut.app}

    def layer_affinity(layer):
        score = 0
        for p in layer_positions[layer]:
            sid = genome[p.gene_idx]
            if sid < 0 or sid >= len(shortcut_pool):
                continue
            other_apps = set(shortcut_pool[sid].apps) if shortcut_pool[sid].apps else {shortcut_pool[sid].app}
            if shortcut_apps & other_apps:
                score += 1
        return score

    layer_order.sort(key=lambda l: -layer_affinity(l))
    for layer in layer_order:
        pos_list = layer_positions[layer]
        empty = [p for p in pos_list if genome[p.gene_idx] < 0 and p.gene_idx not in protected]
        if empty:
            target = min(empty, key=lambda p: p.effort)
            genome[target.gene_idx] = shortcut.sid
            return genome

    return genome


def deduplicate(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None):
    """Remove a same-layer duplicate and optionally replace with an unassigned shortcut."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)

    # Find same-layer duplicates
    for layer, pos_list in layer_positions.items():
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
        # Remove a random duplicate
        target = random.choice(dupes)
        genome[target.gene_idx] = -1

        # 50% chance: fill with unassigned important shortcut
        if random.random() < 0.5:
            assigned_sids = set(s for s in genome if s >= 0)
            candidates = [s for s in shortcut_pool if s.sid not in assigned_sids]
            if candidates:
                best = max(candidates, key=lambda s: s.importance)
                genome[target.gene_idx] = best.sid
        return genome

    return genome


def improve_coherence(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None):
    """Move a shortcut to a layer with more same-app shortcuts (emergent coherence)."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)
    protected = _protected_gene_indices(genome, positions, shortcut_pool, dynamic_groups) if shortcut_pool else set()

    candidates = []
    for i, sid in enumerate(genome):
        if sid < 0 or i in protected or sid >= len(shortcut_pool):
            continue
        s = shortcut_pool[sid]
        if s.category == "base_key":
            continue
        candidates.append(i)

    if not candidates:
        return genome

    src_idx = random.choice(candidates)
    sid = genome[src_idx]
    s = shortcut_pool[sid]
    src_layer = positions[src_idx].layer
    shortcut_apps = set(s.apps) if s.apps else {s.app}

    # Count same-app shortcuts per layer
    layer_affinity = {}
    for layer, pos_list in layer_positions.items():
        if layer == src_layer:
            continue
        count = 0
        for p in pos_list:
            other = genome[p.gene_idx]
            if other < 0 or other >= len(shortcut_pool):
                continue
            other_apps = set(shortcut_pool[other].apps) if shortcut_pool[other].apps else {shortcut_pool[other].app}
            if shortcut_apps & other_apps:
                count += 1
        if count > 0:
            layer_affinity[layer] = count

    if not layer_affinity:
        return genome

    best_layer = max(layer_affinity, key=layer_affinity.get)
    empty = [p for p in layer_positions[best_layer]
             if genome[p.gene_idx] < 0 and p.gene_idx not in protected]
    if empty:
        target = min(empty, key=lambda p: p.effort)
        genome[target.gene_idx] = sid
        genome[src_idx] = -1

    return genome


def move_group(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None):
    """Move an entire protected group to a new location on the same hand, same layer."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)

    all_groups = [g for g in KEY_GROUPS if g.get("protected") and "behaviors" not in g] + (dynamic_groups or [])
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
                    by_layer.setdefault(positions[i].layer, []).append(i)
            else:
                params = [p.upper() for p in group.get("params", [])]
                mods_req = group.get("mods_required", "")
                s = shortcut_pool[sid]
                if s.base_key.upper() not in params:
                    continue
                if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
                    continue
                by_layer.setdefault(positions[i].layer, []).append(i)

        if not by_layer:
            continue

        layer = random.choice(list(by_layer.keys()))
        member_indices = by_layer[layer]
        if len(member_indices) < 2:
            continue

        member_hand = positions[member_indices[0]].hand
        pos_list = layer_positions.get(layer, [])
        same_hand = [p for p in pos_list if p.hand == member_hand]
        non_member = [p for p in same_hand if p.gene_idx not in set(member_indices)]

        empty_on_hand = [p for p in non_member if genome[p.gene_idx] < 0]
        if len(empty_on_hand) < len(member_indices):
            continue

        anchor = random.choice(empty_on_hand)
        targets = sorted(empty_on_hand, key=lambda p: abs(p.x - anchor.x) + abs(p.y - anchor.y))
        targets = targets[:len(member_indices)]

        sids = [genome[i] for i in member_indices]
        for i in member_indices:
            genome[i] = -1
        for sid, t in zip(sids, targets):
            genome[t.gene_idx] = sid

        return genome

    return genome


def swap_layer_content(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None):
    """Swap all shortcuts between two layers. Explores whether a different
    layer arrangement is better (e.g. Nav on L1 vs L3 changes thumb access cost)."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)
    protected = _protected_gene_indices(genome, positions, shortcut_pool, dynamic_groups) if shortcut_pool else set()
    layers = list(layer_positions.keys())
    if len(layers) < 2:
        return genome
    la, lb = random.sample(layers, 2)
    pos_a = layer_positions[la]
    pos_b = layer_positions[lb]
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
        if i < len(empty_a):
            genome[empty_a[i].gene_idx] = sid
    for i, (_, sid) in enumerate(sids_a):
        if i < len(empty_b):
            genome[empty_b[i].gene_idx] = sid
    _repair_layer_dupes(genome, positions, pos_a, protected)
    _repair_layer_dupes(genome, positions, pos_b, protected)
    return genome


def _repair_layer_dupes(genome, positions, layer_pos_list, protected=None):
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


def redistribute_shortcuts(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None):
    """Move a random subset of shortcuts from one layer to another with empty slots."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)
    protected = _protected_gene_indices(genome, positions, shortcut_pool, dynamic_groups) if shortcut_pool else set()
    layers = list(layer_positions.keys())
    if len(layers) < 2:
        return genome
    src_layer = random.choice(layers)
    dst_layer = random.choice([l for l in layers if l != src_layer])
    src_pos = layer_positions[src_layer]
    dst_pos = layer_positions[dst_layer]
    movable = [p for p in src_pos if genome[p.gene_idx] >= 0 and p.gene_idx not in protected
                and not _find_group_members_at(genome, positions, shortcut_pool, p.gene_idx)]
    empty_dst = [p for p in dst_pos if genome[p.gene_idx] < 0]
    if not movable or not empty_dst:
        return genome
    n_move = random.randint(1, min(5, len(movable), len(empty_dst)))
    to_move = random.sample(movable, n_move)
    empty_dst.sort(key=lambda p: p.effort)
    for i, src_p in enumerate(to_move):
        if i < len(empty_dst):
            genome[empty_dst[i].gene_idx] = genome[src_p.gene_idx]
            genome[src_p.gene_idx] = -1
    return genome


def cross_layer_deduplicate(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None):
    """Remove a cross-layer duplicate (shortcut on 3+ layers) and replace with unassigned."""
    genome = copy.copy(genome)
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)
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
        assigned_sids = set(s for s in genome if s >= 0)
        candidates = [s for s in shortcut_pool if s.sid not in assigned_sids and s.importance >= 3.0]
        if candidates:
            best = max(candidates, key=lambda s: s.importance)
            genome[remove_idx] = best.sid
    return genome


def custom_mutate(genome, positions, shortcut_pool, layer_positions=None, dynamic_groups=None, scratch_mode=False):
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)
    r = random.random()
    if scratch_mode:
        if r < 0.40:
            return (migrate_shortcut(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
        elif r < 0.55:
            return (improve_coherence(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
        elif r < 0.70:
            return (swap_within_layer(genome, positions, layer_positions, shortcut_pool, dynamic_groups),)
        elif r < 0.80:
            return (thumb_fill(genome, positions, shortcut_pool, layer_positions),)
        elif r < 0.90:
            return (deduplicate(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
        else:
            return (move_group(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
    if r < 0.08:
        return (swap_within_layer(genome, positions, layer_positions, shortcut_pool, dynamic_groups),)
    elif r < 0.14:
        return (swap_to_empty(genome, positions, layer_positions, shortcut_pool, dynamic_groups),)
    elif r < 0.35:
        return (migrate_shortcut(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
    elif r < 0.42:
        return (move_group(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
    elif r < 0.48:
        return (thumb_fill(genome, positions, shortcut_pool, layer_positions),)
    elif r < 0.60:
        return (deduplicate(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
    elif r < 0.70:
        return (improve_coherence(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
    elif r < 0.76:
        return (swap_layer_content(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
    elif r < 0.84:
        return (redistribute_shortcuts(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)
    else:
        return (cross_layer_deduplicate(genome, positions, shortcut_pool, layer_positions, dynamic_groups),)


def pmx_crossover(parent1, parent2, positions, layer_positions=None, pool=None, dynamic_groups=None):
    if layer_positions is None:
        layer_positions = build_layer_to_positions(positions)

    child1 = copy.copy(parent1)
    child2 = copy.copy(parent2)

    protected1 = _protected_gene_indices(parent1, positions, pool, dynamic_groups) if pool else set()
    protected2 = _protected_gene_indices(parent2, positions, pool, dynamic_groups) if pool else set()

    for layer, pos_list in layer_positions.items():
        if len(pos_list) < 4:
            continue

        indices = [p.gene_idx for p in pos_list]
        safe_indices = [i for i in indices if i not in protected1 and i not in protected2]
        if len(safe_indices) < 4:
            continue

        n = len(safe_indices)
        a, b = sorted(random.sample(range(n), 2))

        seg1 = [parent1[safe_indices[i]] for i in range(a, b)]
        seg2 = [parent2[safe_indices[i]] for i in range(a, b)]

        for i in range(a, b):
            child1[safe_indices[i]] = seg2[i - a]
            child2[safe_indices[i]] = seg1[i - a]

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
