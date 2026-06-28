"""Export evolved layout as keybindings_explained.csv.

Merges evolved changes with the current canonical layout to produce
a complete CSV suitable for zmk-config/layout/keybindings_explained.csv.

Usage: python export_csv.py <build_dir> [solution_index]
"""
import json
import sys
import os
import csv
from pathlib import Path
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from representation import (
    build_position_index, build_shortcut_pool, encode_current_layout,
)
from export_zmk import export_genome_to_zmk, KEY_TO_ZMK_PARAM
from layer_access import LayerAccessAnalyzer


# Reverse map: ZMK Studio parameter -> short CSV parameter
ZMK_TO_CSV_PARAM = {}
for short, full in KEY_TO_ZMK_PARAM.items():
    if full not in ZMK_TO_CSV_PARAM:
        ZMK_TO_CSV_PARAM[full] = short


def zmk_param_to_csv_param(param):
    """Convert ZMK Studio parameter to short CSV format."""
    if param in ZMK_TO_CSV_PARAM:
        return ZMK_TO_CSV_PARAM[param]
    if param.startswith("Keyboard "):
        return param.replace("Keyboard ", "")
    return param


def make_purpose(label, behavior, param, mods):
    if behavior == "Transparent":
        return "Transparent/reserved: falls through to lower active layer or does nothing if no lower binding applies."
    if behavior == "Key Press":
        mod_str = "+".join(mods) + "+" if mods else ""
        return f"Sends {mod_str}{param}."
    return f"{behavior}: {param}" if param else behavior


def make_usage(label, behavior, param, mods):
    if behavior == "Transparent":
        return "Intentionally leaves the underlying layer behavior available."
    if behavior == "Key Press":
        mod_str = "+".join(mods) + "+" if mods else ""
        return f"Sends {mod_str}{param}."
    return ""


def derive_layer_roles(genome, positions, pool):
    """Describe layers from evolved contents, not historical semantic names."""
    by_layer = {}
    for i, sid in enumerate(genome):
        if sid < 0 or sid >= len(pool):
            continue
        by_layer.setdefault(positions[i].layer, []).append(pool[sid])

    roles = {}
    for layer in sorted({p.layer for p in positions}):
        if layer == 0:
            roles[layer] = "Base typing and thumb access"
            continue
        if layer == 7:
            roles[layer] = "Game layer"
            continue

        shortcuts = [s for s in by_layer.get(layer, []) if s.category != "base_key"]
        if shortcuts:
            apps = Counter(s.app for s in shortcuts)
            top = apps.most_common(2)
            total = sum(apps.values())
            if top[0][1] >= total * 0.5:
                roles[layer] = f"Dynamic {top[0][0].title()} layer"
            elif len(top) > 1:
                roles[layer] = f"Dynamic mixed {top[0][0].title()}/{top[1][0].title()} layer"
            else:
                roles[layer] = "Dynamic mixed shortcut layer"
            continue

        base_keys = by_layer.get(layer, [])
        if any("select:mb" in s.keys for s in base_keys):
            roles[layer] = "Dynamic mouse/control layer"
        elif any("coach_" in s.keys for s in base_keys):
            roles[layer] = "Dynamic layer access/control layer"
        elif base_keys:
            roles[layer] = "Dynamic utility layer"
        else:
            roles[layer] = "Dynamic available layer"
    return roles


def _load_results(build_dir):
    for name in (
        "evolution_scratch_results.json",
        "evolution_scratch_results_interim.json",
        "evolution_results.json",
        "evolution_results_interim.json",
    ):
        path = os.path.join(build_dir, name)
        if os.path.exists(path):
            return json.load(open(path, encoding="utf-8")), name
    raise FileNotFoundError(f"No evolution results found in {build_dir}")


def _select_solution(results, analyzer, sol_idx=None):
    if sol_idx is not None:
        front = results.get("pareto_front", [])
        solution = front[sol_idx]
        validation = analyzer.validate(solution["genome"])
        if not validation.valid:
            print(f"Solution {solution.get('id', sol_idx)} violates layer access invariant:")
            for err in validation.errors:
                print(f"  - {err}")
            raise SystemExit(1)
        return solution

    candidates = []
    for key in ("best_weighted", "best_effort", "best_violations"):
        entry = results.get(key)
        if entry and entry.get("genome"):
            item = dict(entry)
            item.setdefault("id", key)
            candidates.append(item)
    candidates.extend(s for s in results.get("pareto_front", []) if s.get("genome"))
    valid = [s for s in candidates if analyzer.validate(s["genome"]).valid]
    if not valid:
        print("No valid layer-access solutions found")
        raise SystemExit(1)
    feasible = [s for s in valid if s.get("fitness", {}).get("violations", 1e18) < 200]
    if feasible:
        return min(feasible, key=lambda s: s["fitness"]["effort"])
    return min(valid, key=lambda s: s.get("fitness", {}).get("violations", 1e18))


def export_evolved_csv(*args):
    """Export evolved CSV.

    Supports both CLI-style export_evolved_csv(build_dir, solution_index=None)
    and analyzer-style export_evolved_csv(genome, positions, pool, canonical, build_dir).
    """
    if len(args) >= 5:
        genome, positions, pool, canonical, build_dir = args[:5]
        sol_id = "selected"
    else:
        build_dir = args[0]
        solution_index = args[1] if len(args) > 1 else None
        canonical = json.load(open(os.path.join(build_dir, "canonical.json"), encoding="utf-8"))
        scores = json.load(open(os.path.join(build_dir, "app_shortcut_scores.json"), encoding="utf-8"))
        results, _source = _load_results(build_dir)

        positions = build_position_index(canonical, {7})
        pool = build_shortcut_pool(scores, canonical)
        analyzer = LayerAccessAnalyzer(canonical, positions, pool)

        solution = _select_solution(results, analyzer, solution_index)
        genome = solution["genome"]
        sol_id = solution.get("id", "selected")
    changes = export_genome_to_zmk(genome, positions, pool, canonical, sol_id)
    layer_roles = derive_layer_roles(genome, positions, pool)

    # Build changed coords lookup
    changed = {}
    for c in changes:
        changed[(c["layer"], c["x"], c["y"])] = c

    # Read current CSV to preserve structure/ordering
    repo_root = Path(__file__).resolve().parents[1]
    sibling_root = repo_root.parent / "charybdis-zmk-config"
    csv_path = sibling_root / "layout" / "keybindings_explained.csv"

    rows = []
    headers = ["layer", "layer_role", "x", "y", "visual_label", "behavior",
               "parameter", "modifiers", "purpose", "usage_notes"]

    if not csv_path.exists():
        raise FileNotFoundError(f"Canonical CSV not found at {csv_path} — cannot generate evolved CSV")

    if csv_path.exists():
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                layer = int(row["layer"])
                x = int(row["x"])
                y = int(row["y"])
                key = (layer, x, y)

                if key in changed:
                    c = changed.pop(key)
                    behavior = c["behavior"]
                    param = zmk_param_to_csv_param(c.get("parameter", ""))
                    mods = ",".join(c.get("modifiers", []))
                    label = c.get("label", row.get("visual_label", ""))
                    if not label or label == c.get("parameter", ""):
                        label = param[:10] if param else behavior[:10]

                    rows.append({
                        "layer": str(layer),
                        "layer_role": layer_roles.get(layer, row.get("layer_role", "")),
                        "x": str(x),
                        "y": str(y),
                        "visual_label": label,
                        "behavior": behavior,
                        "parameter": param,
                        "modifiers": mods,
                        "purpose": f"Evolved ({sol_id}): {make_purpose(label, behavior, param, c.get('modifiers', []))}",
                        "usage_notes": make_usage(label, behavior, param, c.get("modifiers", [])),
                    })
                else:
                    row["layer_role"] = layer_roles.get(layer, row.get("layer_role", ""))
                    rows.append(row)

        # Add any remaining changed coords not in original CSV
        for key, c in sorted(changed.items()):
            layer, x, y = key
            behavior = c["behavior"]
            param = zmk_param_to_csv_param(c.get("parameter", ""))
            mods = ",".join(c.get("modifiers", []))
            label = c.get("label", param[:10] if param else behavior[:10])
            rows.append({
                "layer": str(layer),
                "layer_role": layer_roles.get(layer, ""),
                "x": str(x),
                "y": str(y),
                "visual_label": label,
                "behavior": behavior,
                "parameter": param,
                "modifiers": mods,
                "purpose": f"Evolved ({sol_id}): {make_purpose(label, behavior, param, c.get('modifiers', []))}",
                "usage_notes": make_usage(label, behavior, param, c.get("modifiers", [])),
            })
    else:
        print(f"WARNING: Current CSV not found at {csv_path}")
        print("Generating from scratch using canonical.json + evolved keys")
        sys.exit(1)

    # Write output
    out_path = os.path.join(build_dir, "evolved_keybindings_explained.csv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in headers})

    print(f"Exported {len(rows)} rows to {out_path}")
    print(f"  Exported: {len(changes)} keys")
    print(f"  Copy to: charybdis-zmk-config/layout/keybindings_explained.csv")
    return out_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_csv.py <build_dir> [solution_index]")
        sys.exit(1)

    build_dir = sys.argv[1]
    sol_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
    export_evolved_csv(build_dir, sol_idx)


if __name__ == "__main__":
    main()
