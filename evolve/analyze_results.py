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
    build_layer_to_positions, LAYER_ACCESS,
)
from fitness import FitnessEvaluator
from layer_access import LayerAccessAnalyzer, shortcut_capability

def derive_layer_name(layer, shortcuts, pool):
    """Name a layer based on what's actually on it — dominant app or category."""
    if layer == 0:
        return "Base"
    if layer == 7:
        return "Game"
    app_shortcuts = [s for s in shortcuts if s.category != "base_key"]
    if not app_shortcuts:
        base_types = Counter()
        for s in shortcuts:
            if "coach_" in s.keys:
                base_types["access"] += 1
            elif "arrow" in s.keys or "page" in s.keys or "home" in s.keys or "end" in s.keys:
                base_types["nav"] += 1
            elif s.keys.startswith("_base_f"):
                base_types["fkeys"] += 1
            elif "select:mb" in s.keys:
                base_types["mouse"] += 1
            else:
                base_types["base"] += 1
        if base_types:
            return base_types.most_common(1)[0][0].title()
        return f"L{layer}"
    apps = Counter(s.app for s in app_shortcuts)
    top_app, top_count = apps.most_common(1)[0]
    total = len(app_shortcuts)
    if top_count >= total * 0.5:
        return top_app.title()
    top2 = apps.most_common(2)
    return f"{top2[0][0]}/{top2[1][0]}".title() if len(top2) > 1 else top_app.title()


def load_data(build_dir, scratch=False):
    main_build = Path(__file__).resolve().parents[1] / "build"
    def find(name):
        for d in [Path(build_dir), main_build]:
            p = d / name
            if p.exists():
                return p
        raise FileNotFoundError(f"{name} not found in {build_dir} or {main_build}")
    canonical = json.loads(find("canonical.json").read_text(encoding="utf-8"))
    scores = json.loads(find("app_shortcut_scores.json").read_text(encoding="utf-8"))
    config_path = Path(__file__).parent / ("config_scratch.json" if scratch else "config.json")
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
    capabilities = analyzer.capabilities_for_genome(genome)
    exit_layers = {cap.source for cap in capabilities if cap.target == 0}
    toggle_return_layers = {
        cap.target for cap in capabilities
        if cap.mode == "toggle" and cap.target in analyzer.exit_required_layers
    }
    probe_pos = positions[0] if positions else None
    capability_sids = {
        s.sid for s in pool
        if probe_pos is not None and shortcut_capability(s, probe_pos)
    }

    lines = []
    w = lines.append

    # Per-layer summary
    layer_shortcuts = defaultdict(list)
    invalid_sid_count = 0
    for i, sid in enumerate(genome):
        if sid < -1 or sid >= len(pool):
            invalid_sid_count += 1
            continue
        if sid >= 0:
            layer_shortcuts[positions[i].layer].append((positions[i], pool[sid]))

    assigned = sum(1 for g in genome if g >= 0)
    w(f"Assigned: {assigned}/{N} positions ({assigned*100//N}%)")
    if invalid_sid_count:
        w(f"Invalid/stale SIDs skipped in analysis: {invalid_sid_count}")
    w(f"Layer access: {'VALID' if validation.valid else 'INVALID'}")
    if validation.errors:
        for err in validation.errors:
            w(f"  !! {err}")
    w("")

    # Derive dynamic layer names from content
    layer_names = {}
    for layer in sorted(set(p.layer for p in positions)):
        items = layer_shortcuts.get(layer, [])
        shortcuts_only = [s for _, s in items]
        layer_names[layer] = derive_layer_name(layer, shortcuts_only, pool)

    for layer in sorted(set(p.layer for p in positions)):
        if layer == 7:
            continue
        items = layer_shortcuts.get(layer, [])
        lname = layer_names.get(layer, f"L{layer}")
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
        has_exit = layer in exit_layers
        for p, s in items:
            if "coach_" in s.keys or "toggle_layer" in s.keys or "momentary_layer" in s.keys or "to_layer" in s.keys:
                access_keys.append(s.keys.replace("_base_", ""))
            if "coach_base" in s.keys or "coach_recover" in s.keys or "coach_travel_off" in s.keys:
                has_exit = True

        w(f"L{layer} [{lname}] — {len(items)} keys, depth={depth}, cost={cost}")
        w(f"  Apps: {app_str}")
        w(f"  Changes: {changed} ({added} added, {removed} removed)")
        if access_keys:
            w(f"  Access: {', '.join(access_keys)}")
        if layer in analyzer.exit_required_layers and not (has_exit or layer in toggle_return_layers):
            w(f"  !! NO EXIT KEY — soft-lock risk")

        # Top shortcuts
        top5 = sorted(app_shortcuts, key=lambda x: -x[1].importance)[:5]
        if top5:
            w(f"  Top shortcuts:")
            for p, s in top5:
                w(f"    ({p.x},{p.y}) {s.keys:<28} imp={s.importance:.0f}  eff={p.effort:.0f}  app={s.app}")
        w("")

    # Missing high-importance
    assigned_sids = set(g for g in genome if 0 <= g < len(pool))
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
        if sid < -1 or sid >= len(pool):
            continue
        if sid >= 0 and sid not in capability_sids:
            sid_layers[sid].add(positions[i].layer)
    dups = [(sid, layers) for sid, layers in sid_layers.items() if len(layers) > 2]
    if dups:
        w(f"Cross-layer duplicates (3+ layers): {len(dups)}")
        for sid, layers in sorted(dups, key=lambda x: -len(x[1]))[:10]:
            w(f"  {pool[sid].keys:<30} on {len(layers)} layers: {sorted(layers)}")
        w("")

    # Layer redundancy: detect layers with the same dominant app profile.
    # Mixed layers are allowed; this flags "four VS Code layers" style collapse.
    layer_app_profiles = {}
    for layer in sorted(set(p.layer for p in positions)):
        if layer in (0, 7):
            continue
        items = layer_shortcuts.get(layer, [])
        app_counts = Counter(s.app for _, s in items if s.category != "base_key")
        if app_counts:
            layer_app_profiles[layer] = app_counts

    redundant_pairs = []
    layers_checked = sorted(layer_app_profiles.keys())
    for i, la in enumerate(layers_checked):
        for lb in layers_checked[i+1:]:
            pa, pb = layer_app_profiles[la], layer_app_profiles[lb]
            total_a, total_b = sum(pa.values()), sum(pb.values())
            app_a, count_a = pa.most_common(1)[0]
            app_b, count_b = pb.most_common(1)[0]
            overlap_a = count_a / max(total_a, 1)
            overlap_b = count_b / max(total_b, 1)
            if app_a != app_b:
                continue
            if overlap_a > 0.7 and overlap_b > 0.7:
                redundant_pairs.append((la, lb, app_a, overlap_a, overlap_b))

    if redundant_pairs:
        w("Layer redundancy (same dominant app >70% on both layers):")
        for la, lb, app, oa, ob in redundant_pairs:
            w(f"  L{la} [{layer_names.get(la)}] and L{lb} [{layer_names.get(lb)}]: "
              f"{app} dominates both ({oa:.0%} / {ob:.0%})")
        w("")

    # Risk summary
    risks = []
    if invalid_sid_count:
        risks.append(f"{invalid_sid_count} invalid/stale SID placement(s)")
    if not validation.valid:
        risks.append("LAYER ACCESS INVALID — cannot apply this layout")
    for layer in sorted(set(p.layer for p in positions)):
        if layer in (0, 7):
            continue
        if layer not in analyzer.exit_required_layers:
            continue
        keys_on_layer = [s.keys for _, s in layer_shortcuts.get(layer, [])]
        has_mutable_exit = any("coach_base" in k or "coach_recover" in k or "coach_travel_off" in k for k in keys_on_layer)
        if layer not in exit_layers and layer not in toggle_return_layers and not has_mutable_exit:
            risks.append(f"L{layer} [{layer_names.get(layer)}] has no exit key")
    if len(dups) > 15:
        risks.append(f"{len(dups)} cross-layer duplicates (>15 is excessive)")
    if len(missing) > 20:
        risks.append(f"{len(missing)} high-importance shortcuts unplaced")
    if redundant_pairs:
        risks.append(f"{len(redundant_pairs)} redundant layer pair(s) — consider merging")

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

    canonical, positions, pool, current, config = load_data(build_dir, scratch=scratch)
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
            keys = export_genome_to_zmk(genome, positions, pool, canonical)
            script = generate_apply_script(keys, build_dir)
            apply_path = os.path.join(build_dir, "evolved_apply.js")
            with open(apply_path, "w", encoding="utf-8") as f:
                f.write(script)
            print(f"  Apply script: {apply_path} ({len(keys)} keys)")
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
