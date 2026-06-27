"""Export evolved layout as keybindings_explained.csv.

Merges evolved changes with the current canonical layout to produce
a complete CSV suitable for zmk-config/layout/keybindings_explained.csv.

Usage: python export_csv.py <build_dir> [solution_index]
"""
import json
import sys
import os
import csv
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_csv.py <build_dir> [solution_index]")
        sys.exit(1)

    build_dir = sys.argv[1]
    sol_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None

    canonical = json.load(open(os.path.join(build_dir, "canonical.json"), encoding="utf-8"))
    scores = json.load(open(os.path.join(build_dir, "app_shortcut_scores.json"), encoding="utf-8"))
    results = json.load(open(os.path.join(build_dir, "evolution_results.json"), encoding="utf-8"))

    positions = build_position_index(canonical, {7})
    pool = build_shortcut_pool(scores, canonical)
    analyzer = LayerAccessAnalyzer(canonical, positions, pool)

    front = results.get("pareto_front", [])
    if not front:
        print("No pareto front solutions found")
        sys.exit(1)

    if sol_idx is not None:
        solution = front[sol_idx]
        validation = analyzer.validate(solution["genome"])
        if not validation.valid:
            print(f"Solution {solution.get('id', sol_idx)} violates layer access invariant:")
            for err in validation.errors:
                print(f"  - {err}")
            raise SystemExit(1)
    else:
        valid_front = [s for s in front if analyzer.validate(s["genome"]).valid]
        if not valid_front:
            print("No valid layer-access solutions found")
            raise SystemExit(1)
        solution = min(valid_front, key=lambda s: s["fitness"]["effort"] + s["fitness"]["violations"])

    genome = solution["genome"]
    sol_id = solution.get("id", f"sol_{sol_idx or 0}")
    changes = export_genome_to_zmk(genome, positions, pool, canonical, sol_id)
    layer_roles = derive_layer_roles(genome, positions, pool)

    # Build changed coords lookup
    changed = {}
    for c in changes:
        changed[(c["layer"], c["x"], c["y"])] = c

    # Read current CSV to preserve structure/ordering
    csv_path = os.path.join(os.path.dirname(os.path.dirname(build_dir)),
                            "charybdis-zmk-config", "layout", "keybindings_explained.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(build_dir, "..", "..", "charybdis-zmk-config",
                                "layout", "keybindings_explained.csv")

    rows = []
    headers = ["layer", "layer_role", "x", "y", "visual_label", "behavior",
               "parameter", "modifiers", "purpose", "usage_notes"]

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Canonical CSV not found at {csv_path} — cannot generate evolved CSV")

    if os.path.exists(csv_path):
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


if __name__ == "__main__":
    main()
