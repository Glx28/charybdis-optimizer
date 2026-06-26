"""Decode evolution results into human-readable layout changes."""
import sys
import os
import json
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from representation import (
    build_position_index, build_shortcut_pool, encode_current_layout,
    decode_genome, LAYER_NAMES,
)


def load(build_dir, name):
    with open(os.path.join(build_dir, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    build_dir = sys.argv[1] if len(sys.argv) > 1 else "../build"
    results_file = sys.argv[2] if len(sys.argv) > 2 else "evolution_results_interim.json"

    canonical = load(build_dir, "canonical.json")
    scores = load(build_dir, "app_shortcut_scores.json")
    results = load(build_dir, results_file)

    frozen = {7}
    positions = build_position_index(canonical, frozen)
    pool = build_shortcut_pool(scores, canonical)
    current = encode_current_layout(canonical, positions, pool)

    print(f"Generation: {results.get('generation', '?')}")
    print(f"Pareto front size: {len(results.get('pareto_front', []))}")
    print()

    # Pick the best-effort solution from the Pareto front
    front = results.get("pareto_front", [])
    if not front:
        print("No solutions found.")
        return

    # Show all Pareto solutions summary
    print("=== PARETO FRONT SUMMARY ===")
    print(f"{'ID':<8} {'Effort':>8} {'Adj':>8} {'Viol':>8} {'Assign':>8} {'Changed':>8}")
    for sol in front:
        f = sol["fitness"]
        genome = sol.get("genome", [])
        assigned = sum(1 for g in genome if g >= 0)
        changed = sum(1 for i, g in enumerate(genome) if g != current[i])
        print(f"{sol['id']:<8} {f['effort']:>8.1f} {f['adjacency']:>8.1f} {f['violations']:>8.1f} {assigned:>8} {changed:>8}")

    # Pick solution with lowest effort
    best = min(front, key=lambda s: s["fitness"]["effort"])
    print(f"\n=== BEST EFFORT SOLUTION: {best['id']} ===")
    print(f"Effort: {best['fitness']['effort']:.1f} (seed was 3778.2)")
    print(f"Adjacency: {best['fitness']['adjacency']:.1f}")
    print(f"Violations: {best['fitness']['violations']:.1f} (seed was 18421.8)")

    genome = best["genome"]
    changes = decode_genome(genome, positions, pool)

    # Group by layer
    by_layer = defaultdict(list)
    for c in changes:
        by_layer[c["layer"]].append(c)

    # Also decode current layout
    current_changes = decode_genome(current, positions, pool)
    current_by_pos = {}
    for c in current_changes:
        current_by_pos[(c["layer"], c["coord"])] = c

    print(f"\nTotal assignments: {len(changes)}")
    print(f"Positions changed from current: {sum(1 for i, g in enumerate(genome) if g != current[i])}")

    for layer_num in sorted(by_layer.keys()):
        layer_changes = sorted(by_layer[layer_num], key=lambda c: (c["y"], c["x"]))
        layer_name = LAYER_NAMES.get(layer_num, f"Layer {layer_num}")
        print(f"\n--- Layer {layer_num}: {layer_name} ({len(layer_changes)} keys) ---")

        for c in layer_changes:
            pos_key = (c["layer"], c["coord"])
            prev = current_by_pos.get(pos_key)
            marker = ""
            if prev is None or prev["shortcut_id"] != c["shortcut_id"]:
                prev_label = prev["keys"] if prev else "(empty)"
                marker = f"  << was: {prev_label}"
            hand_label = "L" if c["hand"] == "left" else "R"
            thumb = "T" if c["is_thumb"] else " "
            print(f"  [{c['coord']:>5}] {hand_label}{thumb} e={c['effort']:.0f}  "
                  f"{c['keys']:<25} ({c['action'][:40]}){marker}")

    # Violation analysis
    print(f"\n=== VIOLATION ANALYSIS ===")
    print(f"Total violations score: {best['fitness']['violations']:.1f}")
    print("(Lower is better. Violations include: duplicate shortcuts, wrong-app-layer,")
    print(" missing important shortcuts, protected-group splits, etc.)")

    # Count unassigned important shortcuts
    assigned_sids = set(g for g in genome if g >= 0)
    unassigned_important = []
    for s in pool:
        if s.sid not in assigned_sids and s.importance >= 3.0:
            unassigned_important.append(s)

    if unassigned_important:
        print(f"\n  Unassigned important shortcuts (importance >= 3.0): {len(unassigned_important)}")
        for s in sorted(unassigned_important, key=lambda s: -s.importance)[:20]:
            print(f"    {s.keys:<25} imp={s.importance:.1f}  {s.action[:50]}  ({s.app})")

    # Check duplicates
    sid_positions = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid >= 0:
            sid_positions[sid].append(i)
    dupes = {sid: idxs for sid, idxs in sid_positions.items() if len(idxs) > 1}
    if dupes:
        print(f"\n  Duplicate assignments: {len(dupes)}")
        for sid, idxs in list(dupes.items())[:10]:
            s = pool[sid]
            coords = [f"L{positions[i].layer}:{positions[i].coord}" for i in idxs]
            print(f"    {s.keys}: {', '.join(coords)}")


if __name__ == "__main__":
    main()
