#!/usr/bin/env python3
"""Analyze evolution results and generate a human-readable layout summary.

Usage: python analyze_results.py <build_dir> [--export]
  --export: also generate apply script, verify script, and CSV

Reads evolution_results.json (or interim), picks the best-violations solution,
and prints a full layout summary with per-layer breakdown, changes from current,
layer access status, missing shortcuts, duplicates, and risk flags.
"""
import json
import os
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(__file__))

from representation import (
    build_shortcut_pool, build_position_index, encode_current_layout,
    build_layer_to_positions,
)
from fitness import FitnessEvaluator
from layer_access import LayerAccessAnalyzer

LAYER_NAMES = {
    0: "Base", 1: "Nav", 2: "Mouse", 3: "Window", 4: "System",
    5: "Code", 6: "Scroll", 7: "RPG", 8: "Speed", 9: "M-Files", 10: "Excel",
}


def load_data(build_dir):
    main_build = Path(__file__).resolve().parents[1] / "build"
    def find(name):
        for d in [Path(build_dir), main_build]:
            p = d / name
            if p.exists():
                return p
        raise FileNotFoundError(f"{name} not found in {build_dir} or {main_build}")
    canonical = json.loads(find("canonical.json").read_text(encoding="utf-8"))
    scores = json.loads(find("app_shortcut_scores.json").read_text(encoding="utf-8"))
    config_path = Path(__file__).parent / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    positions = build_position_index(canonical, set(config.get("frozen_layers", [7])))
    pool = build_shortcut_pool(scores, canonical)
    current = encode_current_layout(canonical, positions, pool)
    return canonical, positions, pool, current, config


def load_best_genome(build_dir, scratch=False):
    prefix = "evolution_scratch" if scratch else "evolution"
    for suffix in ["_results.json", "_results_interim.json"]:
        p = Path(build_dir) / f"{prefix}{suffix}"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            pf = data.get("pareto_front", [])
            if pf:
                best = min(pf, key=lambda x: x.get("fitness", {}).get("violations", 1e18))
                gen = data.get("generation", "?")
                return best["genome"], gen, best.get("fitness", {}), str(p.name)
    return None, None, None, None


def analyze(genome, positions, pool, current, canonical, config):
    N = len(positions)
    if len(genome) < N:
        genome = genome + [-1] * (N - len(genome))

    analyzer = LayerAccessAnalyzer(canonical, positions, pool)
    validation = analyzer.validate(genome)
    depths = analyzer.access_depth(genome)

    lines = []
    w = lines.append

    # Per-layer summary
    layer_shortcuts = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid >= 0:
            layer_shortcuts[positions[i].layer].append((positions[i], pool[sid]))

    assigned = sum(1 for g in genome if g >= 0)
    w(f"Assigned: {assigned}/{N} positions ({assigned*100//N}%)")
    w(f"Layer access: {'VALID' if validation.valid else 'INVALID'}")
    if validation.errors:
        for err in validation.errors:
            w(f"  !! {err}")
    w("")

    for layer in sorted(set(p.layer for p in positions)):
        if layer == 7:
            continue
        items = layer_shortcuts.get(layer, [])
        lname = LAYER_NAMES.get(layer, f"L{layer}")
        depth = depths.get(layer, "?")
        cost = validation.access_costs.get(layer, "?")

        base_keys = [(p, s) for p, s in items if s.category == "base_key"]
        app_shortcuts = [(p, s) for p, s in items if s.category != "base_key"]
        apps = Counter(s.app for _, s in app_shortcuts)
        top_apps = apps.most_common(3)
        app_str = ", ".join(f"{a}({c})" for a, c in top_apps) if top_apps else "none"

        # Changes from current
        changed = 0
        added = 0
        removed = 0
        for i in range(N):
            if positions[i].layer != layer:
                continue
            c = current[i] if i < len(current) else -1
            g = genome[i]
            if c != g:
                changed += 1
                if c < 0 and g >= 0:
                    added += 1
                elif c >= 0 and g < 0:
                    removed += 1

        # Access keys on this layer
        access_keys = []
        has_exit = False
        for p, s in items:
            if "coach_" in s.keys or "toggle_layer" in s.keys or "momentary_layer" in s.keys or "to_layer" in s.keys:
                access_keys.append(s.keys.replace("_base_", ""))
            if "coach_base" in s.keys or "coach_recover" in s.keys or "coach_travel_off" in s.keys:
                has_exit = True

        w(f"L{layer} ({lname}) — {len(items)} keys, depth={depth}, cost={cost}")
        w(f"  Apps: {app_str}")
        w(f"  Changes: {changed} ({added} added, {removed} removed)")
        if access_keys:
            w(f"  Access: {', '.join(access_keys)}")
        if layer in (5, 8, 9, 10) and not has_exit:
            w(f"  !! NO EXIT KEY — soft-lock risk")

        # Top shortcuts
        top5 = sorted(app_shortcuts, key=lambda x: -x[1].importance)[:5]
        if top5:
            w(f"  Top shortcuts:")
            for p, s in top5:
                w(f"    ({p.x},{p.y}) {s.keys:<28} imp={s.importance:.0f}  eff={p.effort:.0f}  app={s.app}")
        w("")

    # Missing high-importance
    assigned_sids = set(g for g in genome if g >= 0)
    missing = [s for s in pool if s.sid not in assigned_sids and s.importance >= 5.0]
    missing.sort(key=lambda s: -s.importance)
    if missing:
        w(f"Missing (imp>=5): {len(missing)} shortcuts")
        for s in missing[:15]:
            w(f"  {s.keys:<30} imp={s.importance:.0f}  app={s.app}")
        w("")

    # Cross-layer duplicates
    sid_layers = defaultdict(set)
    for i, sid in enumerate(genome):
        if sid >= 0:
            sid_layers[sid].add(positions[i].layer)
    dups = [(sid, layers) for sid, layers in sid_layers.items() if len(layers) > 2]
    if dups:
        w(f"Cross-layer duplicates (3+ layers): {len(dups)}")
        for sid, layers in sorted(dups, key=lambda x: -len(x[1]))[:10]:
            w(f"  {pool[sid].keys:<30} on {len(layers)} layers: {sorted(layers)}")
        w("")

    # Risk summary
    risks = []
    if not validation.valid:
        risks.append("LAYER ACCESS INVALID — cannot apply this layout")
    for layer in (5, 8, 9, 10):
        keys_on_layer = [s.keys for _, s in layer_shortcuts.get(layer, [])]
        if not any("coach_base" in k or "coach_recover" in k or "coach_travel_off" in k for k in keys_on_layer):
            risks.append(f"L{layer} ({LAYER_NAMES.get(layer)}) has no exit key")
    if len(dups) > 15:
        risks.append(f"{len(dups)} cross-layer duplicates (>15 is excessive)")
    if len(missing) > 20:
        risks.append(f"{len(missing)} high-importance shortcuts unplaced")

    if risks:
        w("RISKS:")
        for r in risks:
            w(f"  !! {r}")
    else:
        w("No risks detected — layout looks safe to apply.")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <build_dir> [--export] [--scratch]")
        sys.exit(1)

    build_dir = sys.argv[1]
    do_export = "--export" in sys.argv
    scratch = "--scratch" in sys.argv

    canonical, positions, pool, current, config = load_data(build_dir)
    genome, gen, fitness, source_file = load_best_genome(build_dir, scratch)

    if genome is None:
        print("No evolution results found.")
        sys.exit(1)

    print("=" * 60)
    print(f"LAYOUT ANALYSIS — {source_file}")
    print(f"Generation: {gen}")
    if fitness:
        print(f"Fitness: effort={fitness.get('effort', '?'):.0f}  "
              f"adj={fitness.get('adjacency', '?'):.0f}  "
              f"viol={fitness.get('violations', '?'):.0f}")
    print("=" * 60)
    print()
    print(analyze(genome, positions, pool, current, canonical, config))

    if do_export:
        print("\n" + "=" * 60)
        print("EXPORTING...")
        print("=" * 60)
        try:
            from export_zmk import export_genome_to_zmk, generate_apply_script
            changes = export_genome_to_zmk(genome, positions, pool, canonical)
            script = generate_apply_script(changes, build_dir)
            apply_path = os.path.join(build_dir, "evolved_apply.js")
            with open(apply_path, "w", encoding="utf-8") as f:
                f.write(script)
            print(f"  Apply script: {apply_path} ({len(changes)} changes)")
        except Exception as e:
            print(f"  Export failed: {e}")

        try:
            from export_csv import export_evolved_csv
            csv_path = export_evolved_csv(genome, positions, pool, canonical, build_dir)
            print(f"  CSV: {csv_path}")
        except Exception as e:
            print(f"  CSV export failed: {e}")


if __name__ == "__main__":
    main()
