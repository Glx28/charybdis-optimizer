"""Main entry point for DEAP + pyribs evolutionary keyboard layout optimization.

GPU-accelerated batch fitness evaluation + multiprocessing for operators.
Usage: python run_evolution.py <build_dir>
"""
import sys
import os
import json
import random
import time
import copy
import hashlib
from pathlib import Path
from multiprocessing import cpu_count

import numpy as np

from deap import base, creator, tools


def json_safe(obj):
    """Recursively convert numpy/scalar containers into JSON-serializable values."""
    if isinstance(obj, dict):
        return {str(json_safe(k)): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        safe = json_safe(obj)
        if safe is not obj:
            return safe
        return super().default(obj)


def _safe_replace(src, dst, retries=3):
    for i in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i < retries - 1:
                time.sleep(0.5)
    os.replace(src, dst)

from representation import (
    build_position_index, build_shortcut_pool, build_layer_to_positions,
    encode_current_layout, decode_genome, build_scratch_genome, KEY_GROUPS,
    is_frozen_l0_position,
    shortcut_matches_group,
    is_l0_thumb_worthy_shortcut,
)
from fitness import FitnessEvaluator
from operators import (
    custom_mutate, pmx_crossover, OperatorContext, GPU_OP_IDS,
    repair_position_compatibility,
)

HAS_TORCH = False
try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    pass
CUDA_OOM_ERRORS = (torch.cuda.OutOfMemoryError,) if HAS_TORCH else ()

QD_AVAILABLE = False
try:
    from ribs.archives import GridArchive
    from ribs.emitters import EvolutionStrategyEmitter
    from ribs.schedulers import Scheduler
    QD_AVAILABLE = True
except ImportError:
    pass


def load_config():
    config_path = Path(__file__).parent / "config.json"
    with open(config_path) as f:
        return json.load(f)


def load_config_scratch():
    config_path = Path(__file__).parent / "config_scratch.json"
    with open(config_path) as f:
        return json.load(f)


def load_build_data(build_dir):
    def load(name):
        with open(os.path.join(build_dir, name), encoding="utf-8") as f:
            return json.load(f)

    canonical = load("canonical.json")
    scores = load("app_shortcut_scores.json")

    usage_stats = {}
    try:
        usage_stats = load("usage_stats.json")
    except FileNotFoundError:
        pass

    conjunction_pairs = {}
    try:
        reorg = load("reorganize_proposals.json")
        if "conjunction_pairs_count" in reorg:
            pass
    except FileNotFoundError:
        pass

    return canonical, scores, usage_stats, conjunction_pairs


def build_conjunction_pairs_from_scores(scores):
    pairs = {}
    for app in scores["apps"]:
        by_cat = {}
        for s in app["shortcuts"]:
            if not s.get("mapped"):
                continue
            cat = s.get("category", "general")
            by_cat.setdefault(cat, []).append(s)
        for cat, shortcuts in by_cat.items():
            for i in range(len(shortcuts)):
                for j in range(i + 1, len(shortcuts)):
                    w = min(shortcuts[i]["importance"], shortcuts[j]["importance"]) * 0.3
                    key = "|".join(sorted([shortcuts[i]["keys"], shortcuts[j]["keys"]]))
                    pairs[key] = pairs.get(key, 0) + w
    return pairs


def pool_hash(shortcut_pool):
    payload = []
    for s in sorted(shortcut_pool, key=lambda x: x.sid):
        payload.append({
            "sid": int(s.sid),
            "keys": s.keys,
            "action": s.action,
            "app": s.app,
            "apps": sorted(s.apps or []),
            "category": s.category,
            "importance": float(s.importance),
            "base_key": s.base_key,
            "modifiers": list(s.modifiers or []),
            "zmk_parameter": s.zmk_parameter,
        })
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _sid_range_valid(genome, n_shortcuts):
    return all(-1 <= int(sid) < n_shortcuts for sid in genome)


def load_previous_elites(build_dir, n_positions, n_shortcuts, access_analyzer=None, expected_pool_hash=None):
    """Load genomes from previous evolution run if available.
    Checks both final results and interim results (from interrupted runs)."""
    elites = []
    for filename in ["evolution_results.json", "evolution_results_interim.json"]:
        results_path = os.path.join(build_dir, filename)
        if not os.path.exists(results_path):
            continue
        try:
            with open(results_path, "r", encoding="utf-8") as f:
                prev = json.load(f)
            if prev.get("pool_size", prev.get("shortcuts_count", n_shortcuts)) != n_shortcuts:
                continue
            if expected_pool_hash and prev.get("pool_hash") and prev.get("pool_hash") != expected_pool_hash:
                continue
            for sol in prev.get("pareto_front", []):
                g = sol.get("genome")
                if (g and len(g) == n_positions and _sid_range_valid(g, n_shortcuts)
                    and (access_analyzer is None or access_analyzer.validate(g).valid)):
                    elites.append(list(g))
            for sol in prev.get("qd_solutions", []):
                g = sol.get("genome")
                if (g and len(g) == n_positions and _sid_range_valid(g, n_shortcuts)
                    and (access_analyzer is None or access_analyzer.validate(g).valid)):
                    elites.append(list(g))
        except (json.JSONDecodeError, KeyError):
            continue
    # Deduplicate
    seen = set()
    unique = []
    for e in elites:
        key = tuple(e)
        if key not in seen:
            seen.add(key)
            unique.append(e)
    if unique:
        print(f"Loaded {len(unique)} elites from previous run(s)")
    return unique


def preseed_unplaced_shortcuts(genome, positions, shortcut_pool, layer_positions, verbose=True):
    """Place high-importance unassigned shortcuts into appropriate empty slots.
    Also seeds mouse workflow keys onto a left-hand mouse layer."""
    from representation import is_universal_shortcut, LAYER_ACCESS
    genome = copy.copy(genome)

    mouse_layers = [
        layer for layer, access in LAYER_ACCESS.items()
        if access.get("thumb") == "left" and "momentary" in access.get("method", "")
    ]
    mouse_layers.sort(key=lambda layer: (
        0 if LAYER_ACCESS.get(layer, {}).get("method") == "momentary_or_locked" else 1,
        min((p.effort for p in layer_positions.get(layer, []) if p.hand == "left"), default=99.0),
        -sum(1 for p in layer_positions.get(layer, []) if p.hand == "left"),
    ))
    mouse_layer = next((layer for layer in mouse_layers
                        if sum(1 for p in layer_positions.get(layer, []) if p.hand == "left") >= 7), None)

    def place_sid_at(sid, target):
        current_idx = next((i for i, gsid in enumerate(genome) if int(gsid) == sid), None)
        if current_idx == target.gene_idx:
            return False
        old_target_sid = genome[target.gene_idx]
        if current_idx is not None:
            genome[current_idx], genome[target.gene_idx] = old_target_sid, sid
            return True
        if old_target_sid >= 0:
            empty = next((p for layer_positions_list in layer_positions.values()
                          for p in sorted(layer_positions_list, key=lambda q: (q.effort, q.layer, q.y, q.x))
                          if genome[p.gene_idx] < 0 and p.gene_idx != target.gene_idx), None)
            if empty is not None:
                genome[empty.gene_idx] = old_target_sid
        genome[target.gene_idx] = sid
        return True

    def seed_mouse_workflow():
        if mouse_layer is None:
            return 0
        workflow_order = [
            "_base_select:mb1", "_base_select:mb2", "_base_select:mb3",
            "Ctrl+C", "Ctrl+V", "Ctrl+X", "Ctrl+Z", "Ctrl+A",
        ]
        sid_by_key = {s.keys: s.sid for s in shortcut_pool}
        targets = sorted(
            [p for p in layer_positions.get(mouse_layer, []) if p.hand == "left"],
            key=lambda p: (p.effort, p.y, p.x),
        )
        seeded = 0
        for key, target in zip(workflow_order, targets):
            sid = sid_by_key.get(key)
            if sid is not None and place_sid_at(sid, target):
                seeded += 1
        return seeded

    seeded = seed_mouse_workflow()
    if seeded and verbose:
        print(f"  Pre-seeded {seeded} mouse workflow keys onto layer {mouse_layer} left hand")

    assigned_sids = set(int(g) for g in genome if g >= 0)

    unplaced = [s for s in shortcut_pool if s.sid not in assigned_sids
                and s.category != "base_key" and s.importance >= 3.0]
    unplaced.sort(key=lambda s: -s.importance)

    momentary_layers = {l for l, a in LAYER_ACCESS.items()
                        if a["method"] in ("momentary", "momentary_or_locked")}

    # Pre-seed free-thumb positions on momentary layers first — these are the
    # highest-value empty positions (opposite thumb from hold key, very easy to press)
    free_thumb_seeded = 0
    for layer in momentary_layers:
        access = LAYER_ACCESS.get(layer, {})
        hold_thumb = access.get("thumb")
        if not hold_thumb:
            continue
        free_thumbs = sorted(
            [p for p in layer_positions.get(layer, [])
             if p.is_thumb and p.hand != hold_thumb and genome[p.gene_idx] < 0],
            key=lambda p: p.effort
        )
        for p in free_thumbs:
            if not unplaced:
                break
            # Pick highest importance unplaced shortcut
            for idx, s in enumerate(unplaced):
                if s.sid not in assigned_sids:
                    genome[p.gene_idx] = s.sid
                    assigned_sids.add(s.sid)
                    unplaced.pop(idx)
                    free_thumb_seeded += 1
                    break
    if free_thumb_seeded and verbose:
        print(f"  Pre-seeded {free_thumb_seeded} shortcuts into free-thumb positions")

    placed = 0
    for s in unplaced:
        best_pos = None
        best_score = 999

        for layer, pos_list in layer_positions.items():
            layer_bonus = 0
            if is_universal_shortcut(s) and layer in momentary_layers:
                layer_bonus = -3
            for p in pos_list:
                if genome[p.gene_idx] >= 0:
                    continue
                score = p.effort + layer_bonus
                if score < best_score:
                    best_score = score
                    best_pos = p

        if best_pos is not None:
            genome[best_pos.gene_idx] = s.sid
            placed += 1

    if placed > 0 and verbose:
        print(f"Pre-seeded {placed} high-importance shortcuts into empty slots")
    genome = repair_seeded_groups(genome, positions, shortcut_pool, layer_positions)
    seed_mouse_workflow()
    return genome


def _static_group_sids(shortcut_pool, group):
    if "params" not in group:
        return set()
    sids = set()
    for s in shortcut_pool:
        if shortcut_matches_group(s, group):
            sids.add(s.sid)
    return sids


def repair_seeded_groups(genome, positions, shortcut_pool, layer_positions):
    """Move true action groups together during seeding.

    Mouse buttons are handled by the trackball workflow seeder/scoring. Other
    action groups are workflows where layer-switching between members is nearly
    always wrong.
    """
    repaired = list(genome)
    pos_by_idx = {p.gene_idx: p for p in positions}
    for group_name in ("arrows", "win_directions", "clipboard", "f_keys_low", "f_keys_high"):
        group = next((g for g in KEY_GROUPS if g.get("name") == group_name), None)
        if not group:
            continue
        sids = _static_group_sids(shortcut_pool, group)
        members = [(i, int(sid)) for i, sid in enumerate(repaired) if sid in sids]
        if len(members) < 2:
            continue
        layer_counts = {}
        for idx, _sid in members:
            layer_counts[pos_by_idx[idx].layer] = layer_counts.get(pos_by_idx[idx].layer, 0) + 1
        target_layer = max(layer_counts, key=lambda layer: (layer_counts[layer], -layer))
        hand_counts = {}
        for idx, _sid in members:
            p = pos_by_idx[idx]
            if p.layer == target_layer:
                hand_counts[p.hand] = hand_counts.get(p.hand, 0) + 1
        target_hand = max(hand_counts, key=hand_counts.get) if hand_counts else "left"

        target_members = [pos_by_idx[idx] for idx, _sid in members if pos_by_idx[idx].layer == target_layer]
        cx = sum(p.x for p in target_members) / max(1, len(target_members))
        cy = sum(p.y for p in target_members) / max(1, len(target_members))

        empty_targets = [
            p for p in layer_positions.get(target_layer, [])
            if repaired[p.gene_idx] < 0 and p.hand == target_hand
        ]
        empty_targets.sort(key=lambda p: (abs(p.x - cx) + abs(p.y - cy), p.effort))

        for idx, sid in members:
            p = pos_by_idx[idx]
            if p.layer == target_layer and p.hand == target_hand:
                continue
            if not empty_targets:
                break
            target = empty_targets.pop(0)
            repaired[idx] = -1
            repaired[target.gene_idx] = sid
    return repaired


def _exit_required_layers(access_analyzer=None):
    if access_analyzer is not None:
        return set(access_analyzer.exit_required_layers)
    from representation import LAYER_ACCESS
    return {
        layer for layer, info in LAYER_ACCESS.items()
        if info.get("method") in ("toggled", "locked", "momentary_or_locked")
    }


_BASE_RETURN_SIDS_CACHE = {}


def _base_return_sids(shortcut_pool, positions, exit_required_layers):
    from layer_access import shortcut_capability
    cache_key = (id(shortcut_pool), id(positions), tuple(sorted(exit_required_layers)))
    if cache_key in _BASE_RETURN_SIDS_CACHE:
        return _BASE_RETURN_SIDS_CACHE[cache_key]
    by_layer = {}
    capability_sids = set()
    for layer in exit_required_layers:
        probe = next((p for p in positions if p.layer == layer), None)
        if probe is None:
            continue
        candidates = []
        for s in shortcut_pool:
            cap = shortcut_capability(s, probe)
            if cap:
                capability_sids.add(s.sid)
            if cap and cap.source == layer and cap.target == 0:
                priority = 0 if "coach_base" in s.keys else 1 if "recover_base" in s.keys else 2
                candidates.append((priority, -float(s.importance), s.sid))
        candidates.sort()
        by_layer[layer] = [sid for _, _, sid in candidates]
    _BASE_RETURN_SIDS_CACHE[cache_key] = (by_layer, capability_sids)
    return _BASE_RETURN_SIDS_CACHE[cache_key]


def ensure_structural_exits(genome, positions, shortcut_pool, layer_positions, access_analyzer=None,
                            randomize=False, top_k=5):
    """Repair missing exit keys on exit-required layers without pinning layouts."""
    g = list(genome)
    exit_required = _exit_required_layers(access_analyzer)
    return_sids_by_layer, capability_sids = _base_return_sids(shortcut_pool, positions, exit_required)
    changed = False

    for layer in sorted(exit_required):
        layer_pos = layer_positions.get(layer, [])
        if not layer_pos:
            continue
        exit_sids = set(return_sids_by_layer.get(layer, []))
        has_exit = any(
            0 <= g[p.gene_idx] < len(shortcut_pool) and int(g[p.gene_idx]) in exit_sids
            for p in layer_pos
        )
        if has_exit:
            continue

        candidates = list(return_sids_by_layer.get(layer, []))
        if not candidates:
            continue
        candidate_pool = candidates[:max(1, int(top_k))]
        sid_to_place = random.choice(candidate_pool) if randomize and candidate_pool else candidates[0]
        empty_slots = sorted([p for p in layer_pos if g[p.gene_idx] < 0], key=lambda p: (p.effort, p.y, p.x))
        target = None
        if empty_slots:
            target_pool = empty_slots[:max(1, int(top_k))]
            target = random.choice(target_pool) if randomize else empty_slots[0]
        if target is None:
            replaceable = []
            for p in layer_pos:
                sid = g[p.gene_idx]
                if sid < 0 or sid >= len(shortcut_pool):
                    continue
                if int(sid) in capability_sids:
                    continue
                replaceable.append((float(shortcut_pool[int(sid)].importance), -float(p.effort), p))
            if replaceable:
                replaceable.sort(key=lambda item: (item[0], item[1], item[2].layer, item[2].y, item[2].x))
                target_pool = replaceable[:max(1, int(top_k))]
                target = random.choice(target_pool)[2] if randomize else replaceable[0][2]
        if target is not None:
            g[target.gene_idx] = sid_to_place
            changed = True

    return g, changed


def population_diagnostics(population, positions, shortcut_pool, evaluator,
                           include_health=False, health_config=None):
    genomes = [list(ind) for ind in population]
    n = len(genomes)
    invalid_sid_rows = 0
    stale_sid_count = 0
    max_sid = -1
    structural_valid = 0
    exit_required = sorted(_exit_required_layers(evaluator.access_analyzer if evaluator else None))
    exit_counts = {str(layer): 0 for layer in exit_required}
    missing_layers = set(exit_required)
    low_imp_prime = 0
    imp_vals = []
    effort_vals = []
    worst_structural_dupe = {"target": None, "mode": None, "count": 0, "excess": 0}

    from layer_access import shortcut_capability
    for g in genomes:
        row_invalid = not _sid_range_valid(g, len(shortcut_pool))
        if row_invalid:
            invalid_sid_rows += 1
        for i, sid in enumerate(g):
            max_sid = max(max_sid, int(sid))
            if sid < -1 or sid >= len(shortcut_pool):
                stale_sid_count += 1
                continue
            if sid >= 0:
                imp = float(shortcut_pool[int(sid)].importance)
                eff = float(positions[i].effort)
                imp_vals.append(imp)
                effort_vals.append(eff)
                if imp < 4.0 and eff < 2.0:
                    low_imp_prime += 1
        if row_invalid:
            continue
        if evaluator and hasattr(evaluator, "structural_capability_duplicate_summary"):
            summary = evaluator.structural_capability_duplicate_summary(g)
            if summary.get("count", 0) > worst_structural_dupe.get("count", 0):
                worst_structural_dupe = summary
        analyzer = evaluator.access_analyzer if evaluator else None
        val = analyzer.validate(g) if analyzer else None
        if val is None or val.valid:
            structural_valid += 1
        caps = analyzer.capabilities_for_genome(g) if analyzer else []
        for layer in exit_required:
            method = None
            try:
                from representation import LAYER_ACCESS
                method = LAYER_ACCESS.get(layer, {}).get("method", "")
            except Exception:
                method = ""
            has_explicit_exit = any(cap.source == layer and cap.target == 0 for cap in caps)
            has_toggle_return = (
                method == "toggled"
                and any(cap.target == layer and cap.mode == "toggle" for cap in caps)
            )
            has_exit = has_explicit_exit or has_toggle_return
            if has_exit:
                exit_counts[str(layer)] += 1
                missing_layers.discard(layer)

    corr = 0.0
    if len(imp_vals) >= 2:
        corr = float(np.corrcoef(np.array(imp_vals), np.array(effort_vals))[0, 1])
        if np.isnan(corr):
            corr = 0.0
    diagnostics = {
        "structural_validity": {"valid": structural_valid, "total": n, "ratio": structural_valid / max(n, 1)},
        "exit_coverage": {"required_layers": exit_required, "exit_counts": exit_counts, "missing_layers": sorted(missing_layers)},
        "sid_health": {"invalid_genomes": invalid_sid_rows, "stale_sid_count": stale_sid_count, "max_sid": max_sid, "pool_size": len(shortcut_pool)},
        "position_quality": {"importance_effort_correlation": corr, "low_importance_on_prime": low_imp_prime},
        "structural_capability_duplicates": worst_structural_dupe,
        "group_integrity": group_integrity_metrics(genomes, positions, shortcut_pool),
    }
    if include_health:
        diagnostics["layout_health"] = layout_health_metrics(
            genomes, positions, shortcut_pool, evaluator, config=health_config or {}
        )
    return diagnostics


def group_integrity_metrics(genomes, positions, shortcut_pool):
    groups = {}
    for group in KEY_GROUPS:
        name = group.get("name", "group")
        if name == "bt_profiles":
            continue
        if "behaviors" in group and name == "mouse_buttons":
            sids = [s.sid for s in shortcut_pool if s.keys.startswith("select:mb")]
            expected = len(sids)
        else:
            sids = [s.sid for s in shortcut_pool if shortcut_matches_group(s, group)]
            expected = len(group.get("params", []))
        if expected >= 2 and len(sids) >= 2:
            groups[name] = {"sids": set(sids), "expected": expected, "spatial": name in ("arrows",)}

    result = {}
    for name, info in groups.items():
        intact = 0
        partial = 0
        for genome in genomes:
            clusters = {}
            for i, sid in enumerate(genome):
                if int(sid) not in info["sids"]:
                    continue
                pos = positions[i]
                key = (pos.layer, pos.hand) if info["spatial"] else (pos.layer,)
                clusters[key] = clusters.get(key, 0) + 1
            best = max(clusters.values(), default=0)
            if best >= info["expected"]:
                intact += 1
            elif best >= 2:
                partial += 1
        total = max(len(genomes), 1)
        result[name] = {
            "intact_pct": intact / total,
            "partial_pct": partial / total,
            "expected": info["expected"],
        }
    return result


def _shortcut_key(shortcut):
    return getattr(shortcut, "keys", str(shortcut))


def _sid_key(shortcut_pool, sid):
    if sid < 0:
        return "<empty>"
    if sid >= len(shortcut_pool):
        return f"<stale:{sid}>"
    return _shortcut_key(shortcut_pool[int(sid)])


def _position_label(pos):
    return f"L{pos.layer}:{pos.hand}:{pos.x},{pos.y}/e{pos.effort:g}"


def _cluster_sids_by_layer_hand(genome, positions, shortcut_pool, sid_filter):
    clusters = {}
    for i, sid in enumerate(genome):
        if sid < 0 or sid >= len(shortcut_pool):
            continue
        shortcut = shortcut_pool[int(sid)]
        if not sid_filter(shortcut):
            continue
        pos = positions[i]
        key = (pos.layer, pos.hand)
        clusters.setdefault(key, []).append((i, shortcut, pos))
    return clusters


def layout_health_metrics(genomes, positions, shortcut_pool, evaluator, config=None, sample_limit=None):
    """Broad health probes for live run debugging.

    These diagnostics intentionally describe generic failure modes: scattered
    workflows, empty valuable positions, illegal role placement, duplicate
    pressure, and bad high-importance placement. They are not used for fitness.
    """
    config = config or {}
    sample_limit = int(sample_limit if sample_limit is not None else config.get("health_sample_limit", 5))
    sample_limit = max(0, sample_limit)
    n = max(len(genomes), 1)
    health = {
        "workflow_clusters": {},
        "role_violations": {"l0_bad_total": 0, "l0_empty_total": 0, "examples": []},
        "prime_empty": {"total": 0, "with_unassigned_nonbase": 0, "examples": []},
        "high_importance": {"bad_position_total": 0, "examples": []},
        "duplicates": {"cross_layer_total": 0, "examples": []},
    }

    workflows = {
        "mouse_critical": {
            "expected": 3,
            "filter": lambda s: s.keys in {"_base_select:mb1", "_base_select:mb2", "_base_select:mb3"},
            "requires_left_mouse_layer": True,
        },
        "clipboard": {
            "expected": 5,
            "filter": lambda s: s.keys in {"Ctrl+A", "Ctrl+C", "Ctrl+V", "Ctrl+X", "Ctrl+Z"},
            "requires_left_mouse_layer": True,
        },
        "mouse_buttons": {
            "expected": 3,
            "filter": lambda s: "select:mb" in s.keys,
            "requires_left_mouse_layer": False,
        },
    }
    left_mouse_layers = getattr(evaluator, "left_hand_mouse_layers", set()) if evaluator else set()
    for name, spec in workflows.items():
        health["workflow_clusters"][name] = {
            "intact": 0,
            "partial": 0,
            "scattered": 0,
            "best_avg": 0.0,
            "bad_examples": [],
        }

    capability_sids = evaluator._capability_sid_set() if evaluator and hasattr(evaluator, "_capability_sid_set") else set()
    for genome in genomes:
        assigned = {int(sid) for sid in genome if sid >= 0 and sid < len(shortcut_pool)}
        unassigned_nonbase = [
            s for s in shortcut_pool
            if s.sid not in assigned and s.category != "base_key"
        ]

        for name, spec in workflows.items():
            clusters = _cluster_sids_by_layer_hand(genome, positions, shortcut_pool, spec["filter"])
            best_key, best_members = max(clusters.items(), key=lambda kv: len(kv[1]), default=(None, []))
            best_count = len(best_members)
            health["workflow_clusters"][name]["best_avg"] += best_count
            expected = spec["expected"]
            usable_mouse = True
            if spec["requires_left_mouse_layer"] and best_key is not None:
                usable_mouse = best_key[0] in left_mouse_layers and best_key[1] == "left"
            if best_count >= expected and usable_mouse:
                health["workflow_clusters"][name]["intact"] += 1
            elif best_count >= 2:
                health["workflow_clusters"][name]["partial"] += 1
                if sample_limit and len(health["workflow_clusters"][name]["bad_examples"]) < sample_limit:
                    health["workflow_clusters"][name]["bad_examples"].append({
                        "best_cluster": f"L{best_key[0]}:{best_key[1]}" if best_key else None,
                        "best_count": best_count,
                        "members": [_sid_key(shortcut_pool, genome[i]) for i, _s, _p in best_members[:expected]],
                    })
            else:
                health["workflow_clusters"][name]["scattered"] += 1
                if sample_limit and len(health["workflow_clusters"][name]["bad_examples"]) < sample_limit:
                    placements = [
                        f"{_sid_key(shortcut_pool, sid)}@{_position_label(positions[i])}"
                        for i, sid in enumerate(genome)
                        if sid >= 0 and sid < len(shortcut_pool) and spec["filter"](shortcut_pool[int(sid)])
                    ]
                    health["workflow_clusters"][name]["bad_examples"].append({
                        "best_cluster": f"L{best_key[0]}:{best_key[1]}" if best_key else None,
                        "best_count": best_count,
                        "placements": placements[:expected + 2],
                    })

        for i, sid in enumerate(genome):
            pos = positions[i]
            if pos.layer == 0 and pos.is_thumb and not is_frozen_l0_position(pos):
                if sid < 0:
                    health["role_violations"]["l0_empty_total"] += 1
                    if sample_limit and len(health["role_violations"]["examples"]) < sample_limit:
                        health["role_violations"]["examples"].append(f"<empty>@{_position_label(pos)}")
                elif sid >= len(shortcut_pool) or not is_l0_thumb_worthy_shortcut(shortcut_pool[int(sid)]):
                    health["role_violations"]["l0_bad_total"] += 1
                    if sample_limit and len(health["role_violations"]["examples"]) < sample_limit:
                        health["role_violations"]["examples"].append(f"{_sid_key(shortcut_pool, sid)}@{_position_label(pos)}")

            if sid < 0 and pos.layer != 0 and pos.effort <= 1.5:
                health["prime_empty"]["total"] += 1
                if unassigned_nonbase:
                    health["prime_empty"]["with_unassigned_nonbase"] += 1
                if sample_limit and len(health["prime_empty"]["examples"]) < sample_limit:
                    top_unassigned = sorted(unassigned_nonbase, key=lambda s: -float(s.importance))[:3]
                    health["prime_empty"]["examples"].append({
                        "position": _position_label(pos),
                        "unassigned_top": [f"{s.keys}:{s.importance:g}" for s in top_unassigned],
                    })

            if sid >= 0 and sid < len(shortcut_pool):
                shortcut = shortcut_pool[int(sid)]
                if shortcut.importance >= 8.0 and pos.effort >= 3.5:
                    health["high_importance"]["bad_position_total"] += 1
                    if sample_limit and len(health["high_importance"]["examples"]) < sample_limit:
                        health["high_importance"]["examples"].append(
                            f"{shortcut.keys}:{shortcut.importance:g}@{_position_label(pos)}"
                        )

        sid_layers = {}
        for i, sid in enumerate(genome):
            if sid >= 0 and sid < len(shortcut_pool) and int(sid) not in capability_sids:
                sid_layers.setdefault(int(sid), set()).add(positions[i].layer)
        for sid, layers in sid_layers.items():
            if len(layers) >= 3:
                health["duplicates"]["cross_layer_total"] += 1
                if sample_limit and len(health["duplicates"]["examples"]) < sample_limit:
                    health["duplicates"]["examples"].append(
                        f"{_sid_key(shortcut_pool, sid)}@{sorted(layers)}"
                    )

    for workflow in health["workflow_clusters"].values():
        workflow["intact_pct"] = workflow["intact"] / n
        workflow["partial_pct"] = workflow["partial"] / n
        workflow["scattered_pct"] = workflow["scattered"] / n
        workflow["best_avg"] = workflow["best_avg"] / n
    health["role_violations"]["l0_bad_avg"] = health["role_violations"]["l0_bad_total"] / n
    health["role_violations"]["l0_empty_avg"] = health["role_violations"]["l0_empty_total"] / n
    health["prime_empty"]["avg"] = health["prime_empty"]["total"] / n
    health["prime_empty"]["actionable_avg"] = health["prime_empty"]["with_unassigned_nonbase"] / n
    health["high_importance"]["bad_position_avg"] = health["high_importance"]["bad_position_total"] / n
    health["duplicates"]["cross_layer_avg"] = health["duplicates"]["cross_layer_total"] / n
    return health


def format_layout_health(health, detailed=False):
    lines = []
    wf_parts = []
    for name, vals in sorted(health.get("workflow_clusters", {}).items()):
        wf_parts.append(
            f"{name}={vals['intact_pct']:.0%}/best{vals['best_avg']:.1f}"
        )
    if wf_parts:
        lines.append(f"    health_workflows: {' '.join(wf_parts)}")
    role = health.get("role_violations", {})
    prime = health.get("prime_empty", {})
    hi = health.get("high_importance", {})
    dup = health.get("duplicates", {})
    lines.append(
        "    health_positions: "
        f"l0_bad_avg={role.get('l0_bad_avg', 0):.2f} "
        f"l0_empty_avg={role.get('l0_empty_avg', 0):.2f} "
        f"prime_empty_avg={prime.get('avg', 0):.2f} "
        f"actionable_prime_avg={prime.get('actionable_avg', 0):.2f} "
        f"hi_bad_avg={hi.get('bad_position_avg', 0):.2f} "
        f"xdup_avg={dup.get('cross_layer_avg', 0):.2f}"
    )
    if detailed:
        examples = []
        for name, vals in sorted(health.get("workflow_clusters", {}).items()):
            if vals.get("bad_examples"):
                examples.append(f"{name}:{vals['bad_examples'][:2]}")
        for key, vals in (("role", role), ("prime", prime), ("hi", hi), ("dup", dup)):
            if vals.get("examples"):
                examples.append(f"{key}:{vals['examples'][:3]}")
        if examples:
            lines.append(f"    health_examples: {' | '.join(examples)}")
    return lines


def diversity_injection_milestone(plateau_count, fired_milestones, config):
    """Return the next injection milestone to fire, or None."""
    milestones = sorted(int(x) for x in config.get("diversity_injection_plateaus", [150, 300, 450]))
    for milestone in milestones:
        if plateau_count >= milestone and milestone not in fired_milestones:
            return milestone
    return None


def scratch_phase_for_generation(gen, best_violation_history, config, scratch_mode):
    """Pick mutation phase from scratch improvement rate, with fixed fallback."""
    if not scratch_mode:
        return "explore" if gen < 100 else "balanced" if gen < 500 else "exploit"
    if gen < 150:
        return "explore"
    force_gen = int(config.get("scratch_exploit_force_gen", 1200))
    if gen >= force_gen:
        return "exploit"
    window = int(config.get("phase_window", 50))
    if len(best_violation_history) <= window:
        return "balanced"
    old = float(best_violation_history[-window - 1])
    new = float(best_violation_history[-1])
    denom = max(abs(old), 1.0)
    improvement = (old - new) / denom
    if improvement <= float(config.get("exploit_max_improvement", 0.001)):
        return "exploit"
    return "balanced"


def seed_population(current_genome, n_pop, positions, shortcut_pool, layer_positions,
                    build_dir=None, access_analyzer=None, ctx=None):
    from operators import swap_within_layer, swap_to_empty, migrate_shortcut, custom_mutate

    # Pre-seed unplaced important shortcuts into the base genome
    seeded_genome = preseed_unplaced_shortcuts(current_genome, positions, shortcut_pool, layer_positions)
    if ctx is not None:
        seeded_genome, _ = repair_position_compatibility(seeded_genome, ctx)

    population = [copy.copy(seeded_genome)]

    prev_elites = load_previous_elites(
        build_dir, len(current_genome), len(shortcut_pool), access_analyzer,
        expected_pool_hash=pool_hash(shortcut_pool)
    ) if build_dir else []

    # ~30% from previous elites (direct injection)
    elite_budget = int(n_pop * 0.3)
    for elite in prev_elites[:elite_budget]:
        if ctx is not None:
            elite, _ = repair_position_compatibility(elite, ctx)
        population.append(copy.copy(elite))

    # ~20% wild mutations of previous elites (explore around known good solutions)
    wild_budget = int(n_pop * 0.2)
    if prev_elites:
        for _ in range(wild_budget):
            base = copy.copy(random.choice(prev_elites))
            n_swaps = random.randint(10, 40)
            for _ in range(n_swaps):
                r = random.random()
                if r < 0.5:
                    base = swap_within_layer(base, ctx)
                elif r < 0.75:
                    base = swap_to_empty(base, ctx)
                else:
                    base = migrate_shortcut(base, ctx)
            base, _ = repair_position_compatibility(base, ctx)
            population.append(base)

    # Conservative mutations of seeded layout
    for _ in range(min(n_pop // 10, 50)):
        ind = copy.copy(seeded_genome)
        n_swaps = random.randint(1, 5)
        for _ in range(n_swaps):
            ind = swap_within_layer(ind, ctx)
        ind, _ = repair_position_compatibility(ind, ctx)
        population.append(ind)

    # Fill rest with fresh exploration from seeded layout
    while len(population) < n_pop:
        ind = copy.copy(seeded_genome)
        n_swaps = random.randint(5, 20)
        for _ in range(n_swaps):
            r = random.random()
            if r < 0.5:
                ind = swap_within_layer(ind, ctx)
            elif r < 0.75:
                ind = swap_to_empty(ind, ctx)
            else:
                ind = migrate_shortcut(ind, ctx)
        ind, _ = repair_position_compatibility(ind, ctx)
        population.append(ind)

    return population[:n_pop]


def seed_population_scratch(scratch_genome, n_pop, positions, shortcut_pool, layer_positions, ctx=None, access_analyzer=None):
    """Seed population for from-scratch mode. Each individual gets a random
    number of shortcuts placed via importance-biased migrate_shortcut."""
    from operators import swap_within_layer, migrate_shortcut

    population = []
    t0 = time.time()
    progress_every = max(250, n_pop // 20)
    for idx in range(n_pop):
        ind = copy.copy(scratch_genome)
        n_placements = random.randint(50, min(300, len(shortcut_pool)))
        for _ in range(n_placements):
            ind = migrate_shortcut(ind, ctx)
        n_swaps = random.randint(0, 15)
        for _ in range(n_swaps):
            ind = swap_within_layer(ind, ctx)
        ind = repair_seeded_groups(ind, positions, shortcut_pool, layer_positions)
        ind = preseed_unplaced_shortcuts(ind, positions, shortcut_pool, layer_positions, verbose=False)
        ind, _ = ensure_structural_exits(
            ind, positions, shortcut_pool, layer_positions, access_analyzer,
            randomize=True, top_k=5,
        )
        ind, _ = repair_position_compatibility(ind, ctx)
        population.append(ind)
        if (idx + 1) % progress_every == 0 or (idx + 1) == n_pop:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed if elapsed > 0 else 0.0
            print(f"  Scratch seeded {idx + 1}/{n_pop} ({rate:.1f}/s, {elapsed:.1f}s)")
            sys.stdout.flush()
    return population[:n_pop]


def run_nsga2(evaluator, current_genome, positions, shortcut_pool, config,
              usage_stats=None, conjunction_pairs=None, build_dir=None, scratch_mode=False,
              ctx=None):
    layer_positions = build_layer_to_positions(positions)
    n_pos = len(positions)
    if ctx is None:
        ctx = OperatorContext(positions, shortcut_pool, layer_positions, evaluator.dynamic_groups)
        if HAS_TORCH and evaluator.device != "cpu":
            ctx.build_gpu_tensors(evaluator.device)

    if hasattr(creator, "FitnessMulti"):
        del creator.FitnessMulti
    if hasattr(creator, "Individual"):
        del creator.Individual

    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    violation_threshold = [100000.0]  # mutable; decreases over generations

    def _nsga2_core(individuals, k):
        """Core NSGA-II: Pareto fronts + crowding distance."""
        n = len(individuals)
        fits_np = np.array([ind.fitness.values for ind in individuals], dtype=np.float32)

        if use_gpu_batch and HAS_TORCH and torch.cuda.is_available():
            d = "cuda"
            fits_t = torch.tensor(fits_np, device=d)
        else:
            d = None
            fits_t = None

        ranks = np.full(n, -1, dtype=np.int32)
        remaining = np.ones(n, dtype=bool)
        front_rank = 0
        selected_count = 0

        while selected_count < k and remaining.any():
            idxs = np.where(remaining)[0]
            m = len(idxs)

            if d and m > 50:
                f = fits_t[torch.tensor(idxs, device=d, dtype=torch.long)]
                dominated = torch.zeros(m, device=d, dtype=torch.bool)
                GPU_CHUNK = min(m, 2000)
                for ci in range(0, m, GPU_CHUNK):
                    ce = min(ci + GPU_CHUNK, m)
                    chunk = f[ci:ce]
                    le = (f.unsqueeze(0) <= chunk.unsqueeze(1))
                    lt = (f.unsqueeze(0) < chunk.unsqueeze(1))
                    dom = le.all(dim=2) & lt.any(dim=2)
                    arange = torch.arange(ci, ce, device=d)
                    dom[torch.arange(ce - ci, device=d), arange] = False
                    dominated[ci:ce] = dom.any(dim=1)
                dominated_np = dominated.cpu().numpy()
            else:
                f = fits_np[idxs]
                dominated_np = np.zeros(m, dtype=bool)
                for i in range(m):
                    if dominated_np[i]:
                        continue
                    le = (f[i] <= f).all(axis=1)
                    lt = (f[i] < f).any(axis=1)
                    i_dominates = le & lt
                    i_dominates[i] = False
                    dominated_np |= i_dominates

            front_idxs = idxs[~dominated_np]
            if selected_count + len(front_idxs) <= k:
                ranks[front_idxs] = front_rank
                remaining[front_idxs] = False
                selected_count += len(front_idxs)
            else:
                ff = fits_np[front_idxs]
                n_front = len(front_idxs)
                crowding = np.zeros(n_front, dtype=np.float64)
                for obj in range(fits_np.shape[1]):
                    order = np.argsort(ff[:, obj])
                    crowding[order[0]] = np.inf
                    crowding[order[-1]] = np.inf
                    obj_range = float(ff[order[-1], obj] - ff[order[0], obj])
                    if obj_range > 0:
                        crowding[order[1:-1]] += (ff[order[2:], obj] - ff[order[:-2], obj]) / obj_range
                need = k - selected_count
                best = np.argsort(-crowding)[:need]
                ranks[front_idxs[best]] = front_rank
                selected_count += need
                break
            front_rank += 1

        return [individuals[i] for i in range(n) if ranks[i] >= 0]

    def fast_selNSGA2(individuals, k):
        """Feasibility-first NSGA-II: prefer feasible individuals (violations below threshold)."""
        fits_np = np.array([ind.fitness.values for ind in individuals], dtype=np.float32)
        viol_col = fits_np[:, 2]
        feasible_mask = viol_col <= violation_threshold[0]
        n_feasible = int(feasible_mask.sum())

        if 0 < n_feasible < len(individuals) and n_feasible >= k:
            feasible_inds = [individuals[i] for i in range(len(individuals)) if feasible_mask[i]]
            return _nsga2_core(feasible_inds, k)
        return _nsga2_core(individuals, k)

    toolbox = base.Toolbox()
    toolbox.register("evaluate", evaluator.evaluate)
    toolbox.register("select", fast_selNSGA2)

    current_gen = [0]  # mutable container for closure access
    plateau_intensity = [1]  # mutation intensity: 1 normal, 2-3 when plateaued
    best_violation_history = []

    pop_size = config.get("pop_size", 2000)
    n_gen = config.get("generations", 500)
    cxpb = config.get("crossover_rate", 0.7)
    mutpb = config.get("mutation_rate", 0.15)

    def vary_population(population):
        """Custom variation: crossover + mutation with no clones.
        Every offspring is either crossed, mutated, or both."""
        offspring = [toolbox.clone(ind) for ind in population]
        n = len(offspring)
        intensity = plateau_intensity[0]
        gen = current_gen[0]
        phase = scratch_phase_for_generation(gen, best_violation_history, config, scratch_mode)

        # Crossover pass: pairs of consecutive individuals
        for i in range(1, n, 2):
            if random.random() < cxpb:
                c1, c2 = pmx_crossover(list(offspring[i-1]), list(offspring[i]), ctx)
                c1, _ = repair_position_compatibility(c1, ctx)
                c2, _ = repair_position_compatibility(c2, ctx)
                offspring[i-1] = creator.Individual(c1)
                offspring[i] = creator.Individual(c2)
                del offspring[i-1].fitness.values, offspring[i].fitness.values

        # Mutation pass: mutate with mutpb, but guarantee no clones
        for i in range(n):
            if random.random() < mutpb or offspring[i].fitness.valid:
                # offspring[i].fitness.valid means it wasn't crossed — must mutate to avoid clone
                result = custom_mutate(list(offspring[i]), ctx,
                                       scratch_mode=scratch_mode,
                                       generation=gen,
                                       n_ops=intensity,
                                       phase=phase)
                repaired, _ = repair_position_compatibility(result[0], ctx)
                offspring[i] = creator.Individual(repaired)
                del offspring[i].fitness.values

        return offspring

    # Cached numpy array for population — avoids repeated list→numpy conversion
    pop_cache = [None]  # [np.ndarray or None]

    def _pop_to_numpy(population):
        """Convert population to numpy, using cache when possible."""
        cached = pop_cache[0]
        if cached is not None and cached.shape[0] == len(population):
            return cached
        arr = np.array([list(ind) for ind in population], dtype=np.int32)
        pop_cache[0] = arr
        return arr

    verbose = config.get("verbose_logging", False)
    _vary_timings = {}  # accumulated timing for verbose logging

    def vary_population_gpu(population):
        """GPU-accelerated variation: crossover + mutation hybrid GPU+CPU."""
        from operators import (compute_protected_mask_gpu, GPU_OP_MAP, GPU_OP_IDS,
                                _pick_operator, batch_crossover_gpu)
        n = len(population)
        intensity = plateau_intensity[0]
        gen = current_gen[0]
        S = ctx.pool_size
        d = ctx.device

        t_vary_start = time.perf_counter()

        # Stack all genomes into tensor (int32 for faster transfer)
        all_np = _pop_to_numpy(population).copy()
        all_np[all_np < 0] = S
        t_all = torch.tensor(all_np, device=d, dtype=torch.long)
        t_data_in = time.perf_counter() - t_vary_start

        # Track which indices have been modified
        modified = np.zeros(n, dtype=bool)

        # GPU crossover
        cx_pairs_1 = []
        cx_pairs_2 = []
        for i in range(1, n, 2):
            if random.random() < cxpb:
                cx_pairs_1.append(i - 1)
                cx_pairs_2.append(i)

        t_cx_start = time.perf_counter()
        if cx_pairs_1:
            idx1 = torch.tensor(cx_pairs_1, device=d, dtype=torch.long)
            idx2 = torch.tensor(cx_pairs_2, device=d, dtype=torch.long)
            prot_all = compute_protected_mask_gpu(t_all, ctx)
            prot_cx = prot_all[idx1] | prot_all[idx2]
            c1, c2 = batch_crossover_gpu(t_all[idx1], t_all[idx2], prot_cx, ctx)
            t_all[idx1] = c1
            t_all[idx2] = c2
            for a in cx_pairs_1:
                modified[a] = True
            for b in cx_pairs_2:
                modified[b] = True
        if HAS_TORCH:
            torch.cuda.synchronize()
        t_cx = time.perf_counter() - t_cx_start

        # Determine phase (shortened explore for faster convergence)
        phase = scratch_phase_for_generation(gen, best_violation_history, config, scratch_mode)

        # Partition GPU vs CPU mutations
        gpu_mut_indices = []
        gpu_ops = []
        cpu_tasks = []
        op_counts = {}
        for i in range(n):
            if random.random() < mutpb or not modified[i]:
                op = _pick_operator(random.random(), phase, scratch=scratch_mode)
                op_counts[op] = op_counts.get(op, 0) + 1
                if op in GPU_OP_IDS:
                    gpu_mut_indices.append(i)
                    gpu_ops.append(op)
                else:
                    ops_for_this = [op]
                    for _ in range(intensity - 1):
                        extra_op = _pick_operator(random.random(), phase, scratch=scratch_mode)
                        ops_for_this.append(extra_op)
                    cpu_tasks.append((i, ops_for_this))
                modified[i] = True

        # GPU batch mutation
        t_gpu_mut_start = time.perf_counter()
        gpu_op_counts = {}
        if gpu_mut_indices:
            t_idx = torch.tensor(gpu_mut_indices, device=d, dtype=torch.long)
            sub_g = t_all[t_idx]
            sub_prot = compute_protected_mask_gpu(sub_g, ctx)

            op_arr = np.array(gpu_ops, dtype=np.int32)
            for op_id, batch_fn in GPU_OP_MAP.items():
                mask_np = (op_arr == op_id)
                cnt = int(mask_np.sum())
                if cnt == 0:
                    continue
                gpu_op_counts[op_id] = cnt
                oi = np.where(mask_np)[0]
                t_oi = torch.tensor(oi, device=d, dtype=torch.long)
                sg = sub_g[t_oi]
                sp = sub_prot[t_oi]
                for _ in range(intensity):
                    sg = batch_fn(sg, sp, ctx)
                sub_g[t_oi] = sg
            t_all[t_idx] = sub_g
        if HAS_TORCH:
            torch.cuda.synchronize()
        t_gpu_mut = time.perf_counter() - t_gpu_mut_start

        # Transfer back once, use int32 for faster tolist()
        t_out_start = time.perf_counter()
        result_np = t_all.cpu().numpy().astype(np.int32)
        result_np[result_np >= S] = -1

        # Build offspring — create Individuals directly from numpy rows
        offspring = [None] * n
        cpu_set = set()
        for idx, _ in cpu_tasks:
            cpu_set.add(idx)

        for i in range(n):
            if i in cpu_set:
                offspring[i] = creator.Individual(list(population[i]))
            elif modified[i]:
                repaired, _ = repair_position_compatibility(result_np[i].tolist(), ctx)
                ind = creator.Individual(repaired)
                del ind.fitness.values
                offspring[i] = ind
            else:
                offspring[i] = creator.Individual(list(population[i]))
        t_data_out = time.perf_counter() - t_out_start

        # CPU fallback for complex operators
        t_cpu_mut_start = time.perf_counter()
        for off_idx, ops in cpu_tasks:
            g = list(offspring[off_idx])
            for op in ops:
                r = custom_mutate(g, ctx, scratch_mode=scratch_mode, generation=gen, n_ops=1, phase=phase)
                g = r[0]
            g, _ = repair_position_compatibility(g, ctx)
            offspring[off_idx] = creator.Individual(g)
            if hasattr(offspring[off_idx].fitness, 'values'):
                del offspring[off_idx].fitness.values
        t_cpu_mut = time.perf_counter() - t_cpu_mut_start

        t_vary_total = time.perf_counter() - t_vary_start

        # Accumulate timings for verbose logging
        if verbose:
            tv = _vary_timings
            tv["data_in"] = tv.get("data_in", 0) + t_data_in
            tv["crossover"] = tv.get("crossover", 0) + t_cx
            tv["gpu_mut"] = tv.get("gpu_mut", 0) + t_gpu_mut
            tv["cpu_mut"] = tv.get("cpu_mut", 0) + t_cpu_mut
            tv["data_out"] = tv.get("data_out", 0) + t_data_out
            tv["total"] = tv.get("total", 0) + t_vary_total
            tv["n_cx"] = tv.get("n_cx", 0) + len(cx_pairs_1)
            tv["n_gpu"] = tv.get("n_gpu", 0) + len(gpu_mut_indices)
            tv["n_cpu"] = tv.get("n_cpu", 0) + len(cpu_tasks)
            tv["calls"] = tv.get("calls", 0) + 1
            for k, v in gpu_op_counts.items():
                tv[f"gpu_op_{k}"] = tv.get(f"gpu_op_{k}", 0) + v
            for k, v in op_counts.items():
                tv[f"op_{k}"] = tv.get(f"op_{k}", 0) + v

        # Repairs may have changed rows after the GPU transfer.
        pop_cache[0] = None

        return offspring

    use_gpu_batch = evaluator.device != "cpu" and HAS_TORCH
    print(f"Seeding population: {pop_size} individuals, {n_pos} mutable positions")
    print(f"Device: {evaluator.device} | GPU batch eval: {use_gpu_batch}")
    sys.stdout.flush()
    if scratch_mode:
        raw_pop = seed_population_scratch(
            current_genome, pop_size, positions, shortcut_pool, layer_positions,
            ctx=ctx, access_analyzer=evaluator.access_analyzer
        )
    else:
        raw_pop = seed_population(
            current_genome, pop_size, positions, shortcut_pool, layer_positions,
            build_dir, evaluator.access_analyzer, ctx=ctx
        )
    population = [creator.Individual(ind) for ind in raw_pop]

    def batch_evaluate(pop_list, use_cached_np=False):
        if use_gpu_batch:
            cached = pop_cache[0] if use_cached_np else None
            if cached is not None and cached.shape[0] == len(pop_list):
                return evaluator.evaluate_batch_gpu(None, prebuilt_np=cached)
            return evaluator.evaluate_batch_gpu([list(ind) for ind in pop_list])
        return [toolbox.evaluate(ind) for ind in pop_list]

    def evaluate_and_assign(pop_list, label):
        print(f"  {label} ({len(pop_list)} genomes)...")
        sys.stdout.flush()
        t_eval = time.perf_counter()
        fitnesses = batch_evaluate(pop_list)
        for ind, fit in zip(pop_list, fitnesses):
            ind.fitness.values = fit
        elapsed = time.perf_counter() - t_eval
        if use_gpu_batch and HAS_TORCH and torch.cuda.is_available():
            alloc = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            max_alloc = torch.cuda.max_memory_allocated() / 1e9
            max_reserved = torch.cuda.max_memory_reserved() / 1e9
            print(
                f"  {label} complete in {elapsed:.1f}s "
                f"(vram alloc={alloc:.2f}GB reserved={reserved:.2f}GB "
                f"peak={max_alloc:.2f}/{max_reserved:.2f}GB)"
            )
        else:
            print(f"  {label} complete in {elapsed:.1f}s")
        sys.stdout.flush()
        return fitnesses

    checkpoint_interval = config.get("checkpoint_interval", 25)
    ckpt_name = "evolution_scratch_checkpoint.json" if scratch_mode else "evolution_checkpoint.json"
    checkpoint_path = os.path.join(build_dir, ckpt_name) if build_dir else None
    current_pool_hash = pool_hash(shortcut_pool)

    # Try to resume from checkpoint
    start_gen = 0
    convergence = []
    best_effort_ever = float('inf')
    plateau_count = 0

    if checkpoint_path and os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                ckpt = json.load(f)
            if (ckpt.get("n_positions") == n_pos and
                ckpt.get("pop_size") == pop_size and
                ckpt.get("config_hash") == _config_hash(config) and
                ckpt.get("pool_size") == len(shortcut_pool) and
                ckpt.get("pool_hash") == current_pool_hash):
                # Load population: try npz first (fast), fall back to JSON
                npz_path = checkpoint_path.replace('.json', '.npz')
                if os.path.exists(npz_path):
                    pop_arr = np.load(npz_path)["population"].astype(np.int32)
                    saved_pop = [pop_arr[i].tolist() for i in range(pop_arr.shape[0])]
                elif "population" in ckpt:
                    saved_pop = ckpt["population"]
                else:
                    raise KeyError("No population data in checkpoint")
                if any(not _sid_range_valid(g, len(shortcut_pool)) for g in saved_pop):
                    print("  Checkpoint found but contains stale/out-of-range SIDs -- starting fresh")
                    sys.stdout.flush()
                    raise ValueError("checkpoint contains stale SID")
                saved_pop = [repair_position_compatibility(g, ctx)[0] for g in saved_pop]
                if evaluator.access_analyzer and any(
                    not evaluator.access_analyzer.validate(g).valid for g in saved_pop
                ):
                    print("  Checkpoint found but layer access invariant fails -- starting fresh")
                    sys.stdout.flush()
                    raise ValueError("checkpoint violates layer access invariant")
                population = [creator.Individual(g) for g in saved_pop]
                fitnesses = evaluate_and_assign(population, "Evaluating checkpoint population")
                start_gen = ckpt.get("generation", 0) + 1
                convergence = ckpt.get("convergence", [])
                best_effort_ever = ckpt.get("best_effort_ever", float('inf'))
                plateau_count = ckpt.get("plateau_count", 0)
                print(f"  RESUMED from checkpoint at gen {start_gen - 1} "
                      f"(best effort {best_effort_ever:.1f})")
                sys.stdout.flush()
            else:
                print("  Checkpoint found but metadata changed -- starting fresh")
                sys.stdout.flush()
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"  Checkpoint load failed ({e}) -- starting fresh")
            sys.stdout.flush()

    if start_gen == 0:
        fitnesses = evaluate_and_assign(population, "Evaluating initial population")

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", lambda fits: tuple(min(f[i] for f in fits) for i in range(3)))
    stats.register("avg", lambda fits: tuple(np.mean([f[i] for f in fits]) for i in range(3)))

    logbook = tools.Logbook()
    logbook.header = ["gen", "nevals", "min", "avg"]

    fired_injection_milestones = set()

    t0 = time.time()

    def save_checkpoint(gen):
        if not checkpoint_path:
            return
        # Save population as compressed numpy for speed + size (~2MB vs ~20MB JSON)
        pop_arr = np.array([list(ind) for ind in population], dtype=np.int16)
        npz_path = checkpoint_path.replace('.json', '.npz')
        tmp_npz = npz_path + ".tmp.npz"
        np.savez_compressed(tmp_npz, population=pop_arr)
        _safe_replace(tmp_npz, npz_path)
        # Save metadata as small JSON
        meta = {
            "generation": gen,
            "n_positions": n_pos,
            "pop_size": pop_size,
            "config_hash": _config_hash(config),
            "pool_size": len(shortcut_pool),
            "pool_hash": current_pool_hash,
            "best_effort_ever": float(best_effort_ever),
            "plateau_count": int(plateau_count),
            "convergence": convergence,
        }
        tmp = checkpoint_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(json_safe(meta), f, cls=NumpyEncoder)
        _safe_replace(tmp, checkpoint_path)

    def save_interim_results(gen):
        """Save current Pareto front as results so progress is never lost."""
        if not build_dir:
            return
        try:
            health_enabled = bool(config.get("health_logging", False))
            diagnostics = population_diagnostics(
                population, positions, shortcut_pool, evaluator,
                include_health=health_enabled, health_config=config,
            )
            cur_front = tools.sortNondominated(population, len(population), first_front_only=True)[0]
            cur_front.sort(key=lambda ind: (ind.fitness.values[2], ind.fitness.values[0], ind.fitness.values[1]))
            interim = []
            for i, ind in enumerate(cur_front[:config.get("pareto_front_size", 20)]):
                genome = list(ind)
                if not _sid_range_valid(genome, len(shortcut_pool)):
                    continue
                access_validation = evaluator.access_analyzer.validate(genome) if evaluator.access_analyzer else None
                if access_validation is not None and not access_validation.valid:
                    continue
                interim.append({
                    "id": f"evo_{i}",
                    "fitness": {
                        "effort": round(ind.fitness.values[0], 2),
                        "adjacency": round(-ind.fitness.values[1], 2),
                        "violations": round(ind.fitness.values[2], 2),
                    },
                    "genome": genome,
                    "total_assignments": sum(1 for g in genome if g >= 0),
                })
            # Save best_weighted, best_effort, best_violations in interim
            w = config.get("weights", {})
            viol_w = w.get("violations", 50.0)
            def _interim_weighted(ind):
                e, neg_a, v = ind.fitness.values
                return e + abs(neg_a) + v * viol_w
            interim_best_weighted = min(population, key=_interim_weighted)
            interim_best_eff = min(population, key=lambda ind: ind.fitness.values[0])
            interim_best_viol = min(population, key=lambda ind: ind.fitness.values[2])
            extras = {}
            for label, ind in [("best_weighted", interim_best_weighted),
                               ("best_effort", interim_best_eff),
                               ("best_violations", interim_best_viol)]:
                g = list(ind)
                if _sid_range_valid(g, len(shortcut_pool)):
                    v_check = evaluator.access_analyzer.validate(g) if evaluator.access_analyzer else None
                    if v_check is None or v_check.valid:
                        extras[label] = {
                            "fitness": {
                                "effort": round(ind.fitness.values[0], 2),
                                "adjacency": round(-ind.fitness.values[1], 2),
                                "violations": round(ind.fitness.values[2], 2),
                            },
                            "genome": g,
                            "total_assignments": sum(1 for x in g if x >= 0),
                        }

            interim_name = "evolution_scratch_results_interim.json" if scratch_mode else "evolution_results_interim.json"
            interim_path = os.path.join(build_dir, interim_name)
            tmp = interim_path + ".tmp"
            interim_data = {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "generation": gen,
                    "status": "in_progress",
                    "pool_size": len(shortcut_pool),
                    "pool_hash": current_pool_hash,
                    "diagnostics": diagnostics,
                    "pareto_front": interim,
                    "convergence": convergence,
            }
            interim_data.update(extras)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(json_safe(interim_data), f, indent=2, cls=NumpyEncoder)
            _safe_replace(tmp, interim_path)
        except Exception as e:
            print(f"  WARNING: interim save failed: {e}")

    try:
        for gen in range(start_gen, n_gen):
            current_gen[0] = gen
            if use_gpu_batch and hasattr(ctx, 'device') and ctx.device != 'cpu':
                try:
                    offspring = vary_population_gpu(population)
                except (RuntimeError,) + CUDA_OOM_ERRORS:
                    if HAS_TORCH:
                        torch.cuda.empty_cache()
                    if hasattr(evaluator, "_validation_cache"):
                        evaluator._validation_cache.clear()
                    save_checkpoint(gen)
                    save_interim_results(gen)
                    print(f"  CUDA OOM/runtime error during variation at gen {gen}; falling back to CPU variation")
                    sys.stdout.flush()
                    offspring = vary_population(population)
            else:
                offspring = vary_population(population)

            invalid = [ind for ind in offspring if not ind.fitness.valid]
            t_eval_start = time.perf_counter()
            all_invalid = (len(invalid) == len(offspring))
            try:
                fitnesses = batch_evaluate(invalid, use_cached_np=all_invalid)
            except CUDA_OOM_ERRORS:
                if HAS_TORCH:
                    torch.cuda.empty_cache()
                if hasattr(evaluator, "_validation_cache"):
                    evaluator._validation_cache.clear()
                save_checkpoint(gen)
                save_interim_results(gen)
                print(f"  CUDA OOM during eval at gen {gen}; cleared cache and retrying once")
                sys.stdout.flush()
                try:
                    fitnesses = batch_evaluate(invalid, use_cached_np=all_invalid)
                except CUDA_OOM_ERRORS:
                    if HAS_TORCH:
                        torch.cuda.empty_cache()
                    if hasattr(evaluator, "_validation_cache"):
                        evaluator._validation_cache.clear()
                    use_gpu_batch = False
                    print(f"  CUDA OOM repeated at gen {gen}; switching to CPU evaluation")
                    sys.stdout.flush()
                    fitnesses = batch_evaluate(invalid, use_cached_np=False)
            for ind, fit in zip(invalid, fitnesses):
                ind.fitness.values = fit
            t_eval = time.perf_counter() - t_eval_start

            t_sel_start = time.perf_counter()
            try:
                population = toolbox.select(population + offspring, pop_size)
            except CUDA_OOM_ERRORS:
                if HAS_TORCH:
                    torch.cuda.empty_cache()
                if hasattr(evaluator, "_validation_cache"):
                    evaluator._validation_cache.clear()
                save_checkpoint(gen)
                save_interim_results(gen)
                print(f"  CUDA OOM during selection at gen {gen}; retrying selection on CPU")
                sys.stdout.flush()
                use_gpu_batch = False
                population = toolbox.select(population + offspring, pop_size)
            t_sel = time.perf_counter() - t_sel_start
            pop_cache[0] = None  # invalidate cache after selection reshuffles

            if verbose:
                _vary_timings["eval"] = _vary_timings.get("eval", 0) + t_eval
                _vary_timings["select"] = _vary_timings.get("select", 0) + t_sel
                _vary_timings["n_invalid"] = _vary_timings.get("n_invalid", 0) + len(invalid)
                if hasattr(evaluator, '_last_cache_hits'):
                    _vary_timings["cache_hits"] = _vary_timings.get("cache_hits", 0) + evaluator._last_cache_hits
                    _vary_timings["cache_misses"] = _vary_timings.get("cache_misses", 0) + evaluator._last_cache_misses

            record = stats.compile(population)
            logbook.record(gen=gen, nevals=len(invalid), **record)

            # Multi-objective plateau: track best violations (primary target)
            best_eff = min(population, key=lambda ind: ind.fitness.values[0])
            best_viol = min(population, key=lambda ind: ind.fitness.values[2])
            current_best_viol = best_viol.fitness.values[2]
            best_violation_history.append(float(current_best_viol))

            if current_best_viol < best_effort_ever - 1.0:
                best_effort_ever = current_best_viol
                plateau_count = 0
            else:
                plateau_count += 1

            # Adaptive mutation intensity: escalate when stuck
            if plateau_count < 50:
                plateau_intensity[0] = 1
            elif plateau_count < 150:
                plateau_intensity[0] = 2
            else:
                plateau_intensity[0] = 3

            # Diversity injection: replace a small fraction at fixed plateau milestones.
            injection_milestone = diversity_injection_milestone(plateau_count, fired_injection_milestones, config)
            if injection_milestone is not None:
                from operators import migrate_shortcut
                base_rate = float(config.get("diversity_injection_rate", 0.02))
                if injection_milestone >= 4000:
                    injection_rate = min(0.15, base_rate * 5)
                elif injection_milestone >= 1500:
                    injection_rate = min(0.10, base_rate * 3)
                elif injection_milestone >= 700:
                    injection_rate = min(0.05, base_rate * 2)
                else:
                    injection_rate = base_rate
                n_inject = max(1, int(pop_size * injection_rate)) if injection_rate > 0 else 0
                if n_inject <= 0:
                    fired_injection_milestones.add(injection_milestone)
                else:
                    inject_indices = random.sample(range(pop_size), min(n_inject, pop_size))
                    for ii in inject_indices:
                        fresh = copy.copy(current_genome)
                        for _ in range(random.randint(20, 50)):
                            fresh = migrate_shortcut(fresh, ctx)
                        fresh, _ = ensure_structural_exits(
                            fresh, positions, shortcut_pool, layer_positions, evaluator.access_analyzer,
                            randomize=True, top_k=5,
                        )
                        fresh, _ = repair_position_compatibility(fresh, ctx)
                        population[ii] = creator.Individual(fresh)
                        del population[ii].fitness.values
                    fresh_fits = batch_evaluate([population[ii] for ii in inject_indices])
                    for ii_idx, ii in enumerate(inject_indices):
                        population[ii].fitness.values = fresh_fits[ii_idx]
                    fired_injection_milestones.add(injection_milestone)
                    pop_cache[0] = None
                    print(f"  Injected {n_inject} fresh genomes at plateau {plateau_count} (milestone {injection_milestone})")
                    sys.stdout.flush()

            # Decay violation threshold for feasibility-first selection
            violation_threshold[0] = max(5000.0, current_best_viol * 2.0)

            if gen % checkpoint_interval == 0 or gen == n_gen - 1:
                elapsed = time.time() - t0
                mut_info = f" mut_x{plateau_intensity[0]}" if plateau_intensity[0] > 1 else ""
                print(f"  Gen {gen:4d}: eff={best_eff.fitness.values[0]:.0f} "
                      f"adj={-best_eff.fitness.values[1]:.0f} "
                      f"viol={best_viol.fitness.values[2]:.0f} "
                      f"({elapsed:.1f}s) plateau={plateau_count}{mut_info}")

                if verbose:
                    try:
                        fits = np.array([ind.fitness.values for ind in population], dtype=np.float32)
                        assigned_counts = np.array([sum(1 for g in ind if g >= 0) for ind in population])
                        unique_genomes = len(set(tuple(ind) for ind in population))
                        n_feasible = int((fits[:, 2] <= violation_threshold[0]).sum())

                        # Population stats
                        print(f"    pop: {unique_genomes}/{pop_size} unique, "
                              f"{n_feasible}/{pop_size} feasible (viol<={violation_threshold[0]:.0f}), "
                              f"assigned={assigned_counts.min()}-{assigned_counts.max()} "
                              f"(mean={assigned_counts.mean():.0f})")
                        print(f"    fitness: eff={fits[:,0].min():.0f}/{fits[:,0].mean():.0f}/{fits[:,0].std():.0f} "
                              f"adj={-fits[:,1].max():.0f}/{-fits[:,1].mean():.0f}/{-fits[:,1].min():.0f} "
                              f"viol={fits[:,2].min():.0f}/{fits[:,2].mean():.0f}/{fits[:,2].std():.0f}")

                        health_enabled = bool(config.get("health_logging", False))
                        diagnostics = population_diagnostics(
                            population, positions, shortcut_pool, evaluator,
                            include_health=health_enabled, health_config=config,
                        )
                        sv = diagnostics["structural_validity"]
                        sid_h = diagnostics["sid_health"]
                        ex = diagnostics["exit_coverage"]
                        pq = diagnostics["position_quality"]
                        scd = diagnostics["structural_capability_duplicates"]
                        gi = diagnostics.get("group_integrity", {})
                        health = diagnostics.get("layout_health", {})
                        print(f"    structural: {sv['valid']}/{sv['total']} valid "
                              f"({sv['ratio']:.0%}), missing_exits={ex['missing_layers']}")
                        if sv["valid"] == 0:
                            print("    WARNING: structural validity is 0%; selection has no valid layouts")
                        print(f"    sid_health: stale={sid_h['stale_sid_count']} "
                              f"invalid_genomes={sid_h['invalid_genomes']} max_sid={sid_h['max_sid']} "
                              f"pool={sid_h['pool_size']}")
                        print(f"    position_quality: imp_eff_corr={pq['importance_effort_correlation']:.3f} "
                              f"low_imp_prime={pq['low_importance_on_prime']}")
                        print(f"    structural_capability_duplicates: target={scd['target']} "
                              f"mode={scd['mode']} count={scd['count']} excess={scd['excess']}")
                        if gi:
                            gi_parts = [
                                f"{name}={vals['intact_pct']:.0%}"
                                for name, vals in sorted(gi.items())
                            ]
                            print(f"    group_integrity: {' '.join(gi_parts)}")
                        if health_enabled:
                            for line in format_layout_health(
                                health,
                                detailed=bool(config.get("health_logging_examples", False)),
                            ):
                                print(line)

                        # Best individual breakdown
                        best_genome = list(best_viol)
                        bd = evaluator.evaluate_full(best_genome)
                        skip_keys = {"effort", "adjacency", "violations", "layer_access_valid",
                                     "layer_exit_valid", "layer_access_cost", "layer_access_errors",
                                     "layer_demand", "per_layer_access_costs", "per_layer_depth"}
                        parts = []
                        for k, val_v in bd.items():
                            if k in skip_keys:
                                continue
                            try:
                                fv = float(val_v)
                            except (TypeError, ValueError):
                                continue
                            if abs(fv) > 0.01:
                                parts.append(f"{k}={fv:.1f}")
                        if parts:
                            print(f"    best: {', '.join(parts)}")
                        offenders = evaluator.same_finger_offenders(best_genome, limit=10) if hasattr(evaluator, "same_finger_offenders") else []
                        if offenders:
                            offender_parts = [
                                f"{o['key_a']}+{o['key_b']}={o['score']:.1f}"
                                for o in offenders[:10]
                            ]
                            print(f"    same_finger_top: {'; '.join(offender_parts)}")

                        # Cross-layer duplicates count
                        sid_layers = {}
                        cap_sids = evaluator._capability_sid_set() if hasattr(evaluator, "_capability_sid_set") else set()
                        for idx_g, sid in enumerate(best_genome):
                            if sid >= 0 and sid not in cap_sids:
                                sid_layers.setdefault(sid, set()).add(positions[idx_g].layer)
                        xdupes = sum(1 for s, ls in sid_layers.items() if len(ls) >= 3)
                        if xdupes > 0:
                            print(f"    cross_dupes: {xdupes} SIDs on 3+ layers")

                        # Diversity: average hamming distance between 20 random pairs
                        sample_size = min(20, pop_size // 2)
                        sample_idx = random.sample(range(pop_size), sample_size * 2)
                        hamming_dists = []
                        for hi in range(0, sample_size * 2, 2):
                            g1 = population[sample_idx[hi]]
                            g2 = population[sample_idx[hi + 1]]
                            hamming_dists.append(sum(1 for a, b in zip(g1, g2) if a != b))
                        avg_hamming = sum(hamming_dists) / len(hamming_dists) if hamming_dists else 0

                        # Pareto front stats
                        try:
                            pf = tools.sortNondominated(population, len(population), first_front_only=True)[0]
                            pf_fits = np.array([ind.fitness.values for ind in pf], dtype=np.float32)
                            pf_info = f"pf={len(pf)} eff=[{pf_fits[:,0].min():.0f},{pf_fits[:,0].max():.0f}] viol=[{pf_fits[:,2].min():.0f},{pf_fits[:,2].max():.0f}]"
                        except Exception:
                            pf_info = ""
                        print(f"    diversity: hamming={avg_hamming:.0f} {pf_info}")

                        # Timing + cache stats
                        tv = _vary_timings
                        nc = max(tv.get("calls", 1), 1)
                        t_gen_avg = (tv.get('total',0) + tv.get('eval',0) + tv.get('select',0)) / nc
                        cache_entries = len(evaluator._validation_cache) if hasattr(evaluator, '_validation_cache') else 0
                        cache_hits = tv.get('cache_hits', 0)
                        cache_misses = tv.get('cache_misses', 0)
                        cache_total = cache_hits + cache_misses
                        cache_rate = f" hit={cache_hits/cache_total:.0%}" if cache_total > 0 else ""
                        print(f"    timing: {t_gen_avg*1000:.0f}ms/gen "
                              f"(vary={tv.get('total',0)/nc*1000:.0f} "
                              f"eval={tv.get('eval',0)/nc*1000:.0f} "
                              f"sel={tv.get('select',0)/nc*1000:.0f}) "
                              f"nevals={tv.get('n_invalid',0)//nc} "
                              f"vcache={cache_entries}{cache_rate}")
                        if HAS_TORCH and evaluator.device != "cpu" and torch.cuda.is_available():
                            alloc = torch.cuda.memory_allocated() / 1e9
                            reserved = torch.cuda.memory_reserved() / 1e9
                            max_alloc = torch.cuda.max_memory_allocated() / 1e9
                            max_reserved = torch.cuda.max_memory_reserved() / 1e9
                            print(f"    vram: alloc={alloc:.2f}GB reserved={reserved:.2f}GB "
                                  f"max_alloc={max_alloc:.2f}GB max_reserved={max_reserved:.2f}GB")
                            torch.cuda.reset_peak_memory_stats()
                        if tv.get('total', 0) > 0:
                            print(f"    vary: data_in={tv.get('data_in',0)/nc*1000:.0f} "
                                  f"cx={tv.get('crossover',0)/nc*1000:.0f} "
                                  f"gpu={tv.get('gpu_mut',0)/nc*1000:.0f} "
                                  f"cpu={tv.get('cpu_mut',0)/nc*1000:.0f} "
                                  f"out={tv.get('data_out',0)/nc*1000:.0f}")

                        # Phase + operator distribution
                        cur_phase = scratch_phase_for_generation(gen, best_violation_history, config, scratch_mode)
                        op_names = {0:"swp",1:"s2e",2:"mig",3:"grp",4:"thm",
                                    5:"dup",6:"coh",7:"sly",8:"red",9:"xld"}
                        op_parts = []
                        for oid in range(10):
                            c = tv.get(f"op_{oid}", 0)
                            if c > 0:
                                tag = "G" if oid in GPU_OP_IDS else "C"
                                op_parts.append(f"{op_names[oid]}={c//nc}{tag}")
                        print(f"    ops: phase={cur_phase} cx={tv.get('n_cx',0)//nc} "
                              f"gpu={tv.get('n_gpu',0)//nc} cpu={tv.get('n_cpu',0)//nc} "
                              f"| {' '.join(op_parts)}")
                    except Exception as log_err:
                        print(f"    [log error: {log_err}]")
                    _vary_timings.clear()

                sys.stdout.flush()
                convergence.append({
                    "gen": gen, "elapsed_s": round(elapsed, 1),
                    "best_effort": round(best_eff.fitness.values[0], 2),
                    "best_adjacency": round(-best_eff.fitness.values[1], 2),
                    "best_violations": round(best_viol.fitness.values[2], 2),
                })
                save_checkpoint(gen)
                save_interim_results(gen)

            early_stop_plateau = int(config.get("early_stop_plateau", 2500))
            if plateau_count >= early_stop_plateau:
                print(f"  EARLY STOP: violations plateaued for {plateau_count} gens at gen {gen}")
                sys.stdout.flush()
                break

    except KeyboardInterrupt:
        print(f"\n  INTERRUPTED at gen {gen} -- saving progress...")
        sys.stdout.flush()
        save_checkpoint(gen)
        save_interim_results(gen)
    except Exception as e:
        print(f"\n  ERROR at gen {gen}: {e!r} -- saving progress...")
        sys.stdout.flush()
        save_checkpoint(gen)
        save_interim_results(gen)
        raise

    front = tools.sortNondominated(population, len(population), first_front_only=True)[0]
    front.sort(key=lambda ind: ind.fitness.values[0])
    best_viol = min(population, key=lambda ind: ind.fitness.values[2])
    best_eff = min(population, key=lambda ind: ind.fitness.values[0])
    w = config.get("weights", {})
    viol_w = w.get("violations", 30.0)
    def _weighted(ind):
        e, neg_a, v = ind.fitness.values
        return e + abs(neg_a) + v * viol_w
    best_weighted = min(population, key=_weighted)
    return front, convergence, best_viol, best_eff, best_weighted


def _config_hash(config):
    """Hash the config keys that affect population compatibility."""
    import hashlib
    relevant = {
        "frozen_layers": config.get("frozen_layers"),
        "weights": config.get("weights"),
    }
    return hashlib.md5(json.dumps(relevant, sort_keys=True).encode()).hexdigest()[:12]


def run_qd(evaluator, current_genome, positions, shortcut_pool, config, ctx=None):
    if not QD_AVAILABLE:
        print("pyribs not available, skipping QD. Install with: pip install ribs")
        return None, []

    layer_positions = build_layer_to_positions(positions)
    n_pos = len(positions)

    grid_dims = config.get("qd_grid_dims", [10, 10])
    archive = GridArchive(
        solution_dim=n_pos,
        dims=grid_dims,
        ranges=[(0.0, 1.0), (0.0, 1.0)],
    )

    seed = np.array(current_genome, dtype=np.float64)
    archive.add(seed.reshape(1, -1),
                np.array([-evaluator.evaluate(current_genome)[0]]),
                np.array([evaluator.behavior_descriptors(current_genome)]))

    n_gen = min(config.get("generations", 500), 200)
    print(f"Running QD MAP-Elites: {n_gen} iterations, grid {grid_dims}")

    for gen in range(n_gen):
        if archive.stats.num_elites > 0:
            elite_idx = random.randint(0, archive.stats.num_elites - 1)
            elites = list(archive)
            if elite_idx < len(elites):
                parent = list(elites[elite_idx]["solution"].astype(int))
            else:
                parent = copy.copy(current_genome)
        else:
            parent = copy.copy(current_genome)

        if ctx is None:
            ctx = OperatorContext(positions, shortcut_pool, layer_positions, evaluator.dynamic_groups)
        child = custom_mutate(parent, ctx, scratch_mode=False)[0]
        child_arr = np.array(child, dtype=np.float64)
        fitness_tuple = evaluator.evaluate(child)
        obj = -fitness_tuple[0]
        bds = evaluator.behavior_descriptors(child)

        archive.add(child_arr.reshape(1, -1), np.array([obj]), np.array([bds]))

        if gen % 50 == 0:
            print(f"  QD gen {gen}: {archive.stats.num_elites} elites, "
                  f"coverage={archive.stats.coverage:.1%}")
            sys.stdout.flush()

    results = []
    for elite in archive:
        genome = list(elite["solution"].astype(int))
        bd = elite["measures"]
        results.append({
            "genome": genome,
            "objective": float(elite["objective"]),
            "behavior": {"app_balance": float(bd[0]), "thumb_utilization": float(bd[1])},
        })

    results.sort(key=lambda r: -r["objective"])
    return results, archive


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_evolution.py <build_dir> [--scratch]")
        sys.exit(1)

    build_dir = sys.argv[1]
    scratch_mode = "--scratch" in sys.argv

    config = load_config_scratch() if scratch_mode else load_config()

    if config.get("seed") is not None:
        random.seed(config["seed"])
        np.random.seed(config["seed"])

    print("=" * 60)
    if scratch_mode:
        print("CHARYBDIS FROM-SCRATCH LAYOUT OPTIMIZER")
    else:
        print("CHARYBDIS EVOLUTIONARY LAYOUT OPTIMIZER")
    print("=" * 60)

    canonical, scores, usage_stats, _ = load_build_data(build_dir)
    conjunction_pairs = build_conjunction_pairs_from_scores(scores)

    # Merge real-world usage sequences as conjunction pairs (stronger than corpus-derived)
    usage_sequences = usage_stats.get("sequences", {})
    usage_conj_count = 0
    for seq_key, seq_data in usage_sequences.items():
        parts = seq_key.split(" -> ")
        if len(parts) != 2:
            continue
        count = seq_data.get("count", 0)
        avg_gap = seq_data.get("avg_gap_ms", 9999)
        if count < 1 or avg_gap > 5000:
            continue
        # Weight: faster transitions = stronger pairing, count amplifies
        speed_weight = max(0.5, 2.0 - avg_gap / 2000.0)
        weight = count * speed_weight * 0.5
        pair_key = "|".join(sorted(parts))
        conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + weight
        usage_conj_count += 1
    if usage_conj_count:
        print(f"Added {usage_conj_count} usage-derived conjunction pairs")

    # Merge chains: boost adjacent pairs + add transitive pairs for non-adjacent members
    usage_chains = usage_stats.get("chains", {})
    chain_count = 0
    for chain_key, chain_data in usage_chains.items():
        parts = chain_key.split(" -> ")
        count = chain_data.get("count", 0)
        if count < 2 or len(parts) < 2:
            continue
        # Adjacent pairs get full boost
        for i in range(len(parts) - 1):
            pair_key = "|".join(sorted([parts[i], parts[i+1]]))
            conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.3
        # Non-adjacent transitive pairs get distance-decayed boost
        for i in range(len(parts)):
            for j in range(i+2, len(parts)):
                pair_key = "|".join(sorted([parts[i], parts[j]]))
                distance_decay = 1.0 / (j - i)
                conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.2 * distance_decay
        chain_count += 1
    if chain_count:
        print(f"Added {chain_count} chain-derived conjunction boosts")

    # Chain similarity: if chain A is a sub-sequence of chain B (shared suffix,
    # prefix, or contained), boost the overlapping shortcuts' conjunction weights.
    # e.g. [Ctrl+P, Ctrl+E] inside [Ctrl+G, Ctrl+P, Ctrl+E] → shared pair boosted.
    chain_list = []
    for chain_key, chain_data in usage_chains.items():
        parts = chain_key.split(" -> ")
        count = chain_data.get("count", 0)
        if count >= 2 and len(parts) >= 2:
            chain_list.append((parts, count))
    sim_boost_count = 0
    for i in range(len(chain_list)):
        for j in range(i + 1, len(chain_list)):
            a_parts, a_count = chain_list[i]
            b_parts, b_count = chain_list[j]
            shorter, longer = (a_parts, b_parts) if len(a_parts) <= len(b_parts) else (b_parts, a_parts)
            # Check if shorter is a contiguous subsequence of longer
            s_str = " -> ".join(shorter)
            l_str = " -> ".join(longer)
            if s_str not in l_str:
                continue
            # Found overlap — boost all pairwise within the shared segment
            combined_count = min(a_count, b_count)
            for si in range(len(shorter)):
                for sj in range(si + 1, len(shorter)):
                    pair_key = "|".join(sorted([shorter[si], shorter[sj]]))
                    conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + combined_count * 0.4
                    sim_boost_count += 1
    if sim_boost_count:
        print(f"Added {sim_boost_count} chain-similarity conjunction boosts")

    # Merge workflows: all pairwise combinations weighted by proximity in sequence
    usage_workflows = usage_stats.get("workflows", {})
    wf_count = 0
    for wf_key, wf_data in usage_workflows.items():
        parts = wf_key.split(" -> ")
        count = wf_data.get("count", 0)
        if count < 3 or len(parts) < 3:
            continue
        for i in range(len(parts)):
            for j in range(i+1, len(parts)):
                pair_key = "|".join(sorted([parts[i], parts[j]]))
                distance_factor = 1.0 / (j - i)
                conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.4 * distance_factor
        wf_count += 1
    if wf_count:
        print(f"Added {wf_count} workflow-derived conjunction boosts")

    # Layer session common_keys: keys used together on the same layer
    layer_sessions = usage_stats.get("layer_sessions", {})
    ls_count = 0
    for layer_str, session_data in layer_sessions.items():
        common_keys = session_data.get("common_keys", [])
        count = session_data.get("count", 1)
        if len(common_keys) < 2:
            continue
        for i in range(min(len(common_keys), 5)):
            for j in range(i+1, min(len(common_keys), 5)):
                pair_key = "|".join(sorted([common_keys[i], common_keys[j]]))
                conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.2
                ls_count += 1
    if ls_count:
        print(f"Added {ls_count} layer-session conjunction pairs")

    frozen = set(config.get("frozen_layers", [7]))
    positions = build_position_index(canonical, frozen)
    shortcut_pool = build_shortcut_pool(scores, canonical)

    print(f"\nPositions: {len(positions)} mutable ({sum(1 for p in positions if p.is_thumb)} thumb)")
    print(f"Shortcuts: {len(shortcut_pool)} in corpus")
    print(f"Conjunction pairs: {len(conjunction_pairs)}")
    from representation import discover_dynamic_groups
    preview_dg = discover_dynamic_groups(conjunction_pairs, usage_stats, shortcut_pool, threshold=0.3)
    print(f"Dynamic groups discovered: {len(preview_dg)}")

    # Auto-detect GPU
    import torch
    if config.get("use_gpu", True) and torch.cuda.is_available():
        device = "cuda"
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        device = "cpu"
        print("GPU: not available, using CPU")

    print(f"CPU cores: {cpu_count()}")
    sys.stdout.flush()

    if scratch_mode:
        current_genome = build_scratch_genome(canonical, positions, shortcut_pool)
        layer_positions = build_layer_to_positions(positions)
        current_genome, repaired = ensure_structural_exits(
            current_genome, positions, shortcut_pool, layer_positions
        )
        if repaired:
            print("Seeded structural exits into scratch base genome")
        current_genome = repair_seeded_groups(current_genome, positions, shortcut_pool, layer_positions)
        current_genome = preseed_unplaced_shortcuts(current_genome, positions, shortcut_pool, layer_positions)
        current_genome, _ = ensure_structural_exits(
            current_genome, positions, shortcut_pool, layer_positions
        )
        open_l0 = [i for i, p in enumerate(positions)
                    if p.layer == 0 and not is_frozen_l0_position(p)]
    else:
        current_genome = encode_current_layout(canonical, positions, shortcut_pool)
        layer_positions = build_layer_to_positions(positions)
        open_l0 = [i for i, p in enumerate(positions)
                    if p.layer == 0 and not is_frozen_l0_position(p)]

    evaluator = FitnessEvaluator(
        positions, shortcut_pool, config,
        usage_stats=usage_stats,
        conjunction_pairs=conjunction_pairs,
        device=device,
        current_genome=current_genome,
        canonical=canonical,
    )

    ctx = OperatorContext(positions, shortcut_pool, layer_positions, evaluator.dynamic_groups)
    ctx.set_frozen_l0(positions, open_l0)
    current_genome, position_repairs = repair_position_compatibility(current_genome, ctx)
    if position_repairs:
        print(f"Repaired {position_repairs} position-role violation(s) in seed genome")
    if HAS_TORCH and device != "cpu":
        ctx.build_gpu_tensors(device)
    assigned_count = sum(1 for g in current_genome if g >= 0)
    print(f"Current layout: {assigned_count}/{len(current_genome)} positions assigned")

    seed_fitness = evaluator.evaluate(current_genome)
    seed_breakdown = evaluator.evaluate_full(current_genome)
    print(f"Seed fitness: effort={seed_fitness[0]:.1f}, adj={-seed_fitness[1]:.1f}, viol={seed_fitness[2]:.1f}")
    print(f"Breakdown: {json.dumps({k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in seed_breakdown.items()}, default=str)}")
    sys.stdout.flush()

    # Run NSGA-II
    print(f"\n--- NSGA-II ({config.get('pop_size', 2000)} pop, {config.get('generations', 500)} gen) ---")
    sys.stdout.flush()
    front, convergence, best_viol_ind, best_eff_ind, best_weighted_ind = run_nsga2(evaluator, current_genome, positions, shortcut_pool, config,
                                    usage_stats=usage_stats, conjunction_pairs=conjunction_pairs,
                                    build_dir=build_dir, scratch_mode=scratch_mode, ctx=ctx)
    health_enabled = bool(config.get("health_logging", False))
    final_diagnostics = population_diagnostics(
        front, positions, shortcut_pool, evaluator,
        include_health=health_enabled, health_config=config,
    )
    current_pool_hash = pool_hash(shortcut_pool)

    pareto_solutions = []
    valid_front = []
    for ind in front:
        genome = list(ind)
        if (not _sid_range_valid(genome, len(shortcut_pool))):
            continue
        if evaluator.access_analyzer is None or evaluator.access_analyzer.validate(genome).valid:
            valid_front.append(ind)
    if len(valid_front) < len(front):
        print(f"Filtered {len(front) - len(valid_front)} invalid layer-access solution(s) from Pareto front")
    if not valid_front:
        print("WARNING: no structurally valid Pareto solutions; writing diagnostic result only")

    for i, ind in enumerate(valid_front[:config.get("pareto_front_size", 20)]):
        genome = list(ind)
        breakdown = evaluator.evaluate_full(genome)
        bd = evaluator.behavior_descriptors(genome)
        changes = decode_genome(genome, positions, shortcut_pool)

        pareto_solutions.append({
            "id": f"evo_{i}",
            "fitness": {
                "effort": round(ind.fitness.values[0], 2),
                "adjacency": round(-ind.fitness.values[1], 2),
                "violations": round(ind.fitness.values[2], 2),
            },
            "behavior": {"app_balance": round(bd[0], 3), "thumb_utilization": round(bd[1], 3)},
            "scoring_breakdown": {k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in breakdown.items()},
            "total_assignments": sum(1 for g in genome if g >= 0),
            "changes_from_current": sum(1 for i in range(len(genome)) if genome[i] != current_genome[i]),
            "genome": genome,
            "changes": changes[:50],
        })

    # Run QD (optional)
    qd_results = None
    qd_archive_stats = {}
    if QD_AVAILABLE:
        print(f"\n--- Quality-Diversity MAP-Elites ---")
        sys.stdout.flush()
        qd_elites, qd_archive = run_qd(evaluator, current_genome, positions, shortcut_pool, config, ctx=ctx)
        if qd_elites:
            qd_results = []
            for i, elite in enumerate(qd_elites[:20]):
                genome = elite["genome"]
                if not _sid_range_valid(genome, len(shortcut_pool)):
                    continue
                if evaluator.access_analyzer and not evaluator.access_analyzer.validate(genome).valid:
                    continue
                changes = decode_genome(genome, positions, shortcut_pool)
                breakdown = evaluator.evaluate_full(genome)
                qd_results.append({
                    "id": f"qd_{i}",
                    "objective": elite["objective"],
                    "behavior": elite["behavior"],
                    "scoring_breakdown": {k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in breakdown.items()},
                    "total_assignments": sum(1 for g in genome if g >= 0),
                    "genome": genome,
                    "changes": changes[:50],
                })
            if qd_archive:
                qd_archive_stats = {
                    "num_elites": int(qd_archive.stats.num_elites),
                    "coverage": round(float(qd_archive.stats.coverage), 4),
                    "qd_score": round(float(qd_archive.stats.qd_score), 2),
                }

    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": config,
        "device": device,
        "positions_count": len(positions),
        "shortcuts_count": len(shortcut_pool),
        "pool_size": len(shortcut_pool),
        "pool_hash": current_pool_hash,
        "conjunction_pairs_count": len(conjunction_pairs),
        "status": "ok" if pareto_solutions else "no_valid_solutions",
        "diagnostics": final_diagnostics,
        "seed_fitness": {
            "effort": round(seed_fitness[0], 2),
            "adjacency": round(-seed_fitness[1], 2),
            "violations": round(seed_fitness[2], 2),
        },
        "seed_breakdown": {k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in seed_breakdown.items()},
        "pareto_front": pareto_solutions,
        "convergence": convergence,
    }

    # Save the population's best-violations individual (may not be in pareto front)
    if best_viol_ind is not None:
        bv_genome = list(best_viol_ind)
        bv_valid = _sid_range_valid(bv_genome, len(shortcut_pool))
        if bv_valid and (evaluator.access_analyzer is None or evaluator.access_analyzer.validate(bv_genome).valid):
            bv_breakdown = evaluator.evaluate_full(bv_genome)
            bv_changes = decode_genome(bv_genome, positions, shortcut_pool)
            output["best_violations"] = {
                "fitness": {
                    "effort": round(best_viol_ind.fitness.values[0], 2),
                    "adjacency": round(-best_viol_ind.fitness.values[1], 2),
                    "violations": round(best_viol_ind.fitness.values[2], 2),
                },
                "scoring_breakdown": {k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in bv_breakdown.items()},
                "total_assignments": sum(1 for g in bv_genome if g >= 0),
                "genome": bv_genome,
                "changes": bv_changes[:50],
            }

    # Save the population's best-effort individual
    if best_eff_ind is not None:
        be_genome = list(best_eff_ind)
        be_valid = _sid_range_valid(be_genome, len(shortcut_pool))
        if be_valid and (evaluator.access_analyzer is None or evaluator.access_analyzer.validate(be_genome).valid):
            be_breakdown = evaluator.evaluate_full(be_genome)
            be_changes = decode_genome(be_genome, positions, shortcut_pool)
            output["best_effort"] = {
                "fitness": {
                    "effort": round(best_eff_ind.fitness.values[0], 2),
                    "adjacency": round(-best_eff_ind.fitness.values[1], 2),
                    "violations": round(best_eff_ind.fitness.values[2], 2),
                },
                "scoring_breakdown": {k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in be_breakdown.items()},
                "total_assignments": sum(1 for g in be_genome if g >= 0),
                "genome": be_genome,
                "changes": be_changes[:50],
            }

    # Save the population's best weighted-sum individual
    if best_weighted_ind is not None:
        bw_genome = list(best_weighted_ind)
        bw_valid = _sid_range_valid(bw_genome, len(shortcut_pool))
        if bw_valid and (evaluator.access_analyzer is None or evaluator.access_analyzer.validate(bw_genome).valid):
            bw_breakdown = evaluator.evaluate_full(bw_genome)
            bw_changes = decode_genome(bw_genome, positions, shortcut_pool)
            output["best_weighted"] = {
                "fitness": {
                    "effort": round(best_weighted_ind.fitness.values[0], 2),
                    "adjacency": round(-best_weighted_ind.fitness.values[1], 2),
                    "violations": round(best_weighted_ind.fitness.values[2], 2),
                },
                "scoring_breakdown": {k: round(float(v), 2) if isinstance(v, (int, float)) else v for k, v in bw_breakdown.items()},
                "total_assignments": sum(1 for g in bw_genome if g >= 0),
                "genome": bw_genome,
                "changes": bw_changes[:50],
            }

    if qd_results:
        output["qd_archive"] = qd_archive_stats
        output["qd_solutions"] = qd_results

    results_name = "evolution_scratch_results.json" if scratch_mode else "evolution_results.json"
    out_path = os.path.join(build_dir, results_name)
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(json_safe(output), f, indent=2, cls=NumpyEncoder)
    _safe_replace(tmp_path, out_path)

    # Clean up checkpoint and interim on successful completion
    if scratch_mode:
        cleanup_files = ["evolution_scratch_checkpoint.json", "evolution_scratch_results_interim.json",
                         "evolution_scratch_checkpoint.npz"]
    else:
        cleanup_files = ["evolution_checkpoint.json", "evolution_results_interim.json",
                         "evolution_checkpoint.npz"]
    for cleanup in cleanup_files:
        p = os.path.join(build_dir, cleanup)
        if os.path.exists(p):
            os.remove(p)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {len(pareto_solutions)} Pareto front solutions")
    if qd_results:
        print(f"QD: {qd_archive_stats.get('num_elites', 0)} elites, "
              f"{qd_archive_stats.get('coverage', 0):.1%} coverage")
    print(f"Written to: {out_path}")
    print("=" * 60)
    sys.stdout.flush()

    # Auto-analyze best solution
    try:
        from analyze_results import load_data, analyze
        _, a_positions, a_pool, a_current, _ = load_data(build_dir, scratch=scratch_mode)
        best_genome = pareto_solutions[0]["genome"] if pareto_solutions else None
        if best_genome:
            print("\n" + analyze(best_genome, a_positions, a_pool, a_current, canonical, config))
    except Exception as e:
        print(f"Auto-analysis skipped: {e}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
