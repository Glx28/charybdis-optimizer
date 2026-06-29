import json
import sys
import os
import numpy as np
from collections import Counter, defaultdict

from representation import (
    build_position_index, build_shortcut_pool, build_layer_to_positions,
    decode_genome, is_frozen_l0_position, KEY_GROUPS, shortcut_matches_group
)
from fitness import FitnessEvaluator
from run_evolution import (
    load_build_data, build_conjunction_pairs_from_scores,
    repair_seeded_groups, preseed_unplaced_shortcuts
)
from representation import build_scratch_genome

BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build')

def format_shortcut(s):
    """Short format for a shortcut."""
    if s.keys.startswith('_base_'):
        return s.keys.replace('_base_', '')
    return s.keys

def analyze_group_integrity(genome, positions, pool, dynamic_groups):
    """Check if protected groups are properly clustered."""
    results = []
    all_groups = list(KEY_GROUPS) + dynamic_groups

    # Build pos_of_sid
    pos_of_sid = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid >= 0:
            pos_of_sid[sid].append(positions[i])

    for group in all_groups:
        if "behaviors" in group:
            continue
        is_dynamic = group.get("dynamic", False)
        expected_size = len(group.get("params", [])) if not is_dynamic else len(group.get("sids", []))

        # Find all members in genome
        members = []
        if is_dynamic:
            for sid in group.get("sids", []):
                members.extend(pos_of_sid.get(sid, []))
        else:
            for s in pool:
                if shortcut_matches_group(s, group):
                    members.extend(pos_of_sid.get(s.sid, []))

        if len(members) < 2:
            continue

        # Best layer+hand cluster
        by_layer = defaultdict(list)
        for p in members:
            by_layer[p.layer].append(p)

        best_cluster = 0
        best_layer = None
        best_hand = None
        is_spatial = group.get("name", "") in ("arrows", "win_directions")

        for layer, layer_members in by_layer.items():
            if is_spatial:
                by_hand = defaultdict(list)
                for m in layer_members:
                    by_hand[m.hand].append(m)
                for hand, hand_members in by_hand.items():
                    if len(hand_members) > best_cluster:
                        best_cluster = len(hand_members)
                        best_layer = layer
                        best_hand = hand
            else:
                if len(layer_members) > best_cluster:
                    best_cluster = len(layer_members)
                    best_layer = layer

        # Check if all members are on same layer+hand
        same_layer = len(set(p.layer for p in members)) == 1
        same_hand = True
        if is_spatial and members:
            same_hand = len(set(p.hand for p in members)) == 1

        # Check adjacency (max distance between any two members)
        max_dist = 0
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                d = abs(members[a].x - members[b].x) + abs(members[a].y - members[b].y)
                max_dist = max(max_dist, d)

        results.append({
            "name": group.get("name"),
            "expected": expected_size,
            "placed": len(members),
            "best_cluster": best_cluster,
            "best_layer": best_layer,
            "best_hand": best_hand,
            "same_layer": same_layer,
            "same_hand": same_hand,
            "max_dist": max_dist,
            "is_spatial": is_spatial,
        })

    return results


def analyze_mouse_mode(genome, positions, pool, evaluator):
    """Check if mouse buttons are accessible on left-hand mouse layers."""
    import re

    # Find mouse button SIDs
    mb_sids = {}
    for s in pool:
        m = re.search(r"mb([1-5])", s.keys.lower())
        if m:
            mb_sids[m.group(1)] = s.sid

    # Find clipboard SIDs
    clip_sids = {}
    for s in pool:
        if s.keys in ('Ctrl+C', 'Ctrl+V', 'Ctrl+Z', 'Ctrl+X'):
            clip_sids[s.keys] = s.sid

    left_mouse_layers = evaluator.left_hand_mouse_layers

    # Find positions of mouse buttons
    mb_positions = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid < 0:
            continue
        for mb_num, mb_sid in mb_sids.items():
            if sid == mb_sid:
                mb_positions[mb_num].append(positions[i])

    clip_positions = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid < 0:
            continue
        for key, clip_sid in clip_sids.items():
            if sid == clip_sid:
                clip_positions[key].append(positions[i])

    results = {
        "mouse_buttons": {},
        "clipboard": {},
    }

    for mb_num, mb_pos_list in mb_positions.items():
        best_lhm = None
        best_lhm_score = float('inf')
        best_any = None
        best_any_score = float('inf')
        for pos in mb_pos_list:
            score = pos.effort
            if pos.layer in left_mouse_layers and pos.hand == "left":
                if score < best_lhm_score:
                    best_lhm_score = score
                    best_lhm = pos
            if score < best_any_score:
                best_any_score = score
                best_any = pos
        results["mouse_buttons"][mb_num] = {
            "placements": len(mb_pos_list),
            "best_lhm": f"L{best_lhm.layer} ({best_lhm.x},{best_lhm.y}) eff={best_lhm.effort:.1f}" if best_lhm else None,
            "best_any": f"L{best_any.layer} ({best_any.x},{best_any.y}) eff={best_any.effort:.1f}" if best_any else None,
        }

    for key, clip_pos_list in clip_positions.items():
        best_lhm = None
        best_lhm_score = float('inf')
        for pos in clip_pos_list:
            if pos.layer in left_mouse_layers and pos.hand == "left":
                if pos.effort < best_lhm_score:
                    best_lhm_score = pos.effort
                    best_lhm = pos
        results["clipboard"][key] = {
            "placements": len(clip_pos_list),
            "best_lhm": f"L{best_lhm.layer} ({best_lhm.x},{best_lhm.y}) eff={best_lhm.effort:.1f}" if best_lhm else None,
        }

    return results


def analyze_effort_distribution(genome, positions, pool):
    """Check how important shortcuts are distributed across effort levels."""
    effort_buckets = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid < 0:
            continue
        s = pool[sid]
        effort = positions[i].effort
        effort_buckets[effort].append({
            "keys": format_shortcut(s),
            "importance": s.importance,
            "layer": positions[i].layer,
            "hand": positions[i].hand,
        })

    # Summarize by effort tier
    summary = {}
    for eff in sorted(effort_buckets.keys()):
        items = effort_buckets[eff]
        avg_imp = sum(x["importance"] for x in items) / len(items) if items else 0
        high_imp = sum(1 for x in items if x["importance"] >= 9.0)
        summary[eff] = {
            "count": len(items),
            "avg_importance": avg_imp,
            "high_importance": high_imp,
        }

    # Find misplaced high-importance shortcuts
    misplaced = []
    for i, sid in enumerate(genome):
        if sid < 0:
            continue
        s = pool[sid]
        if s.importance >= 8.0 and positions[i].effort >= 3.5:
            misplaced.append({
                "keys": format_shortcut(s),
                "importance": s.importance,
                "effort": positions[i].effort,
                "layer": positions[i].layer,
                "coord": positions[i].coord,
            })

    return summary, misplaced


def analyze_layer_contents(genome, positions, pool):
    """Show what's on each layer."""
    layers = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid < 0:
            continue
        s = pool[sid]
        layers[positions[i].layer].append({
            "keys": format_shortcut(s),
            "importance": s.importance,
            "effort": positions[i].effort,
            "hand": positions[i].hand,
            "coord": positions[i].coord,
            "x": positions[i].x,
            "y": positions[i].y,
        })

    # Sort by position within each layer
    for layer in layers:
        layers[layer].sort(key=lambda x: (x["y"], x["x"]))

    return layers


def analyze_toggled_layer_exits(genome, positions, pool, evaluator):
    """Check that toggled/locked layers have coach_base exits."""
    exit_layers = evaluator.exit_required_layers
    coach_base_sids = evaluator.coach_base_sids

    results = {}
    for layer in exit_layers:
        layer_indices = [i for i, p in enumerate(positions) if p.layer == layer]
        has_base = any(genome[i] in coach_base_sids for i in layer_indices if genome[i] >= 0)
        base_pos = None
        for i in layer_indices:
            if genome[i] in coach_base_sids:
                base_pos = positions[i]
                break
        results[layer] = {
            "has_exit": has_base,
            "exit_position": f"({base_pos.x},{base_pos.y})" if base_pos else None,
        }

    return results


def print_layout_grid(layer_data, layer_num):
    """Print a visual grid of a layer."""
    items = layer_data.get(layer_num, [])
    if not items:
        print(f"  Layer {layer_num}: EMPTY")
        return

    # Build grid
    grid = {}
    for item in items:
        grid[(item["x"], item["y"])] = item

    print(f"  Layer {layer_num}:")
    # Find bounds
    xs = [k[0] for k in grid.keys()]
    ys = [k[1] for k in grid.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            if (x, y) in grid:
                key = grid[(x, y)]["keys"]
                # Truncate long keys
                if len(key) > 8:
                    key = key[:7] + "..."
                row.append(f"{key:8s}")
            else:
                row.append("        ")
        print(f"    y={y}: {' | '.join(row)}")


def main():
    # 1. Load data exactly as the run does
    canonical, scores, usage_stats, _ = load_build_data(BUILD_DIR)
    conjunction_pairs = build_conjunction_pairs_from_scores(scores)

    # Augment with usage data (same as run)
    usage_sequences = usage_stats.get("sequences", {})
    for seq_key, seq_data in usage_sequences.items():
        parts = seq_key.split(" -> ")
        if len(parts) != 2:
            continue
        count = seq_data.get("count", 0)
        avg_gap = seq_data.get("avg_gap_ms", 9999)
        if count < 1 or avg_gap > 5000:
            continue
        speed_weight = max(0.5, 2.0 - avg_gap / 2000.0)
        weight = count * speed_weight * 0.5
        pair_key = "|".join(sorted(parts))
        conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + weight

    usage_chains = usage_stats.get("chains", {})
    for chain_key, chain_data in usage_chains.items():
        parts = chain_key.split(" -> ")
        count = chain_data.get("count", 0)
        if count < 2 or len(parts) < 2:
            continue
        for i in range(len(parts) - 1):
            pair_key = "|".join(sorted([parts[i], parts[i+1]]))
            conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.3

    # 2. Build pool and positions
    config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_scratch.json'), encoding='utf-8'))
    frozen = set(config.get("frozen_layers", [7]))
    positions = build_position_index(canonical, frozen)
    pool = build_shortcut_pool(scores, canonical)

    # 3. Build current_genome (scratch mode)
    scratch_genome = build_scratch_genome(canonical, positions, pool)
    layer_positions = {}
    for pos in positions:
        layer_positions.setdefault(pos.layer, []).append(pos)
    scratch_genome = repair_seeded_groups(scratch_genome, positions, pool, layer_positions)
    scratch_genome = preseed_unplaced_shortcuts(scratch_genome, positions, pool, layer_positions)
    current_genome = scratch_genome

    # 4. Build evaluator
    evaluator = FitnessEvaluator(
        positions, pool, config, device='cpu',
        current_genome=current_genome, canonical=canonical,
        usage_stats=usage_stats, conjunction_pairs=conjunction_pairs
    )

    dynamic_groups = evaluator.dynamic_groups

    # 5. Load interim results
    interim_path = os.path.join(BUILD_DIR, 'evolution_scratch_results_interim.json')
    interim = json.load(open(interim_path, encoding='utf-8'))

    print("=" * 70)
    print("RUN 12 LAYOUT ANALYSIS")
    print(f"Generation: {interim.get('generation', 'unknown')}")
    print(f"Pool size: {interim.get('pool_size')}, hash: {interim.get('pool_hash', 'unknown')[:8]}")
    print("=" * 70)

    # 6. Analyze convergence
    print("\n" + "=" * 70)
    print("CONVERGENCE TRENDS")
    print("=" * 70)
    conv = interim.get('convergence', [])
    if conv:
        print(f"{'Gen':>6} {'Effort':>10} {'Adjacency':>10} {'Violations':>10} {'Elapsed':>10}")
        for entry in conv:
            print(f"{entry['gen']:6d} {entry['best_effort']:10.2f} {entry['best_adjacency']:10.2f} {entry['best_violations']:10.2f} {entry['elapsed_s']:10.1f}s")

        # Check if violations are improving
        viols = [e['best_violations'] for e in conv]
        if len(viols) >= 2:
            first_v = viols[0]
            last_v = viols[-1]
            improvement = last_v - first_v
            print(f"\nViolation change: {first_v:.2f} -> {last_v:.2f} (delta: {improvement:+.2f})")
            if improvement > 0:
                print("  -> Violations are IMPROVING (more negative = better)")
            elif improvement < 0:
                print("  -> Violations are WORSENING (more positive = worse)")
            else:
                print("  -> Violations are FLAT")

            # Find last improvement
            last_improvement_gen = None
            for i in range(len(viols) - 1, 0, -1):
                if viols[i] < viols[i-1]:
                    last_improvement_gen = conv[i]['gen']
                    break
            if last_improvement_gen:
                print(f"  -> Last violation improvement at gen {last_improvement_gen}")
            else:
                print("  -> No improvement in violation since first checkpoint")

        # Effort trend
        effs = [e['best_effort'] for e in conv]
        if len(effs) >= 2:
            print(f"\nEffort change: {effs[0]:.2f} -> {effs[-1]:.2f} (delta: {effs[-1]-effs[0]:+.2f})")
            if effs[-1] < effs[0]:
                print("  -> Effort is improving (lower = better)")
            else:
                print("  -> Effort is worsening")

    # 7. Analyze each best genome
    genomes_to_analyze = {
        "best_violations": interim.get("best_violations", {}),
        "best_effort": interim.get("best_effort", {}),
        "best_weighted": interim.get("best_weighted", {}),
    }

    for label, data in genomes_to_analyze.items():
        if not data or "genome" not in data:
            continue

        genome = np.array(data["genome"], dtype=np.int32)
        stored_fit = data.get("fitness", {})

        # Re-evaluate with correct CPU evaluator
        cpu_fit = evaluator.evaluate(genome)
        full = evaluator.evaluate_full(genome)

        print(f"\n{'=' * 70}")
        print(f"{label.upper()} GENOME")
        print(f"{'=' * 70}")
        print(f"Stored fitness:   effort={stored_fit.get('effort', 0):.2f}, adj={stored_fit.get('adjacency', 0):.2f}, viol={stored_fit.get('violations', 0):.2f}")
        print(f"CPU re-evaluated: effort={cpu_fit[0]:.2f}, adj={cpu_fit[1]:.2f}, viol={cpu_fit[2]:.2f}")
        print(f"Assignments: {sum(1 for g in genome if g >= 0)} / {len(genome)}")

        # Violation breakdown
        if "violation_breakdown" in full:
            print("\nViolation breakdown:")
            for name, value in sorted(full["violation_breakdown"].items(), key=lambda x: -x[1]):
                print(f"  {name:30s}: {value:10.2f}")

        # Group integrity
        print("\nGroup integrity:")
        group_results = analyze_group_integrity(genome, positions, pool, dynamic_groups)
        for gr in group_results:
            status = "OK" if gr["best_cluster"] >= gr["expected"] else "FAIL"
            if gr["is_spatial"] and not gr["same_hand"]:
                status = "FAIL SPLIT"
            print(f"  {status} {gr['name']:20s}: expected={gr['expected']}, placed={gr['placed']}, "
                  f"best_cluster={gr['best_cluster']} on L{gr['best_layer']}{'/' + gr['best_hand'] if gr['best_hand'] else ''}, "
                  f"same_layer={gr['same_layer']}, same_hand={gr['same_hand']}, max_dist={gr['max_dist']}")

        # Mouse mode
        print("\nMouse mode:")
        mouse = analyze_mouse_mode(genome, positions, pool, evaluator)
        for mb_num, info in mouse["mouse_buttons"].items():
            print(f"  MB{mb_num}: {info['placements']} placements, best_lhm={info['best_lhm']}, best_any={info['best_any']}")
        for key, info in mouse["clipboard"].items():
            print(f"  {key}: {info['placements']} placements, best_lhm={info['best_lhm']}")

        # Toggled layer exits
        print("\nToggled/locked layer exits:")
        exits = analyze_toggled_layer_exits(genome, positions, pool, evaluator)
        for layer, info in exits.items():
            status = "OK" if info["has_exit"] else "FAIL MISSING"
            print(f"  {status} L{layer}: exit={info['exit_position']}")

        # Effort distribution
        print("\nEffort distribution:")
        effort_summary, misplaced = analyze_effort_distribution(genome, positions, pool)
        for eff in sorted(effort_summary.keys()):
            info = effort_summary[eff]
            print(f"  eff={eff:4.1f}: {info['count']:3d} keys, avg_imp={info['avg_importance']:.1f}, high_imp={info['high_importance']}")

        if misplaced:
            print(f"\n  High-importance shortcuts on bad positions (>=3.5 effort):")
            for m in misplaced[:15]:
                print(f"    {m['keys']:20s} imp={m['importance']:5.1f} at L{m['layer']} {m['coord']} eff={m['effort']:.1f}")

        # Layer contents (top layers only)
        print("\nLayer contents (first few keys per layer):")
        layer_data = analyze_layer_contents(genome, positions, pool)
        for layer_num in sorted(layer_data.keys()):
            items = layer_data[layer_num]
            print(f"  L{layer_num}: {len(items)} keys")
            # Show top 8 by importance
            top = sorted(items, key=lambda x: -x["importance"])[:8]
            for item in top:
                print(f"    {item['keys']:20s} imp={item['importance']:5.1f} {item['hand']:5s} ({item['x']},{item['y']}) eff={item['effort']:.1f}")

    # 8. Comparison with canonical
    print(f"\n{'=' * 70}")
    print("COMPARISON WITH CANONICAL LAYOUT")
    print(f"{'=' * 70}")

    from representation import encode_current_layout
    canonical_genome = encode_current_layout(canonical, positions, pool)
    canonical_cpu = evaluator.evaluate(canonical_genome)
    canonical_full = evaluator.evaluate_full(canonical_genome)

    print(f"Canonical: effort={canonical_cpu[0]:.2f}, adj={canonical_cpu[1]:.2f}, viol={canonical_cpu[2]:.2f}")
    print(f"Canonical assignments: {sum(1 for g in canonical_genome if g >= 0)} / {len(canonical_genome)}")

    if "violation_breakdown" in canonical_full:
        print("\nCanonical violation breakdown:")
        for name, value in sorted(canonical_full["violation_breakdown"].items(), key=lambda x: -x[1]):
            print(f"  {name:30s}: {value:10.2f}")

    # Compare each best with canonical
    print("\nImprovement over canonical:")
    for label, data in genomes_to_analyze.items():
        if not data or "genome" not in data:
            continue
        genome = np.array(data["genome"], dtype=np.int32)
        cpu_fit = evaluator.evaluate(genome)
        eff_delta = cpu_fit[0] - canonical_cpu[0]
        adj_delta = abs(cpu_fit[1]) - abs(canonical_cpu[1])  # adj is negative in fitness, higher absolute = better
        viol_delta = cpu_fit[2] - canonical_cpu[2]
        print(f"  {label:20s}: effort={eff_delta:+8.2f}, adj={adj_delta:+8.2f}, viol={viol_delta:+8.2f}")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print("""
Key questions:
1. Are violations actually improving? Check the trend line.
2. Are groups together on same hand/layer? Check group integrity.
3. Are mouse buttons accessible on left-hand mouse layers? Check mouse mode.
4. Are toggled layers escapable? Check exits.
5. Are high-importance shortcuts on easy positions? Check effort distribution.
6. Is this better than canonical? Check comparison table.
""")

    return 0


if __name__ == '__main__':
    sys.exit(main())
