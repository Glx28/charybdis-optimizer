"""Validate fitness model against real-world effort perception.

Outputs a table of shortcuts with model-predicted effort vs their position,
grouped by scenario. Run this, rate each shortcut's real effort 1-10, then
compute correlation to find miscalibrated fitness components.

Usage:
  python validate_fitness.py <build_dir>             # show validation table
  python validate_fitness.py <build_dir> --analyze ratings.json  # analyze ratings
"""
import sys, os, json, math
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from representation import (
    build_position_index, build_shortcut_pool, encode_current_layout,
    LAYER_NAMES, LAYER_ACCESS,
)
from fitness import FitnessEvaluator


def find_shortcut_position(keys, app_hint, genome, positions, pool):
    """Find where a shortcut is placed in the genome, returning (position, sid) or None."""
    candidates = []
    for s in pool:
        if s.keys.upper() == keys.upper():
            if app_hint and app_hint in (s.apps if s.apps else [s.app]):
                candidates.insert(0, s)
            else:
                candidates.append(s)

    for s in candidates:
        for i, sid in enumerate(genome):
            if sid == s.sid:
                return positions[i], s
    return None, None if not candidates else candidates[0]


def compute_step_effort(pos, shortcut, evaluator):
    """Compute model effort for pressing a shortcut at a position."""
    if pos is None:
        return None, "NOT PLACED"

    base_effort = pos.effort
    thumb_busy = evaluator.thumb_busy_extra[pos.gene_idx]
    imp = shortcut.importance if shortcut else 1.0
    layer_mult = evaluator.layer_imp_mult[pos.gene_idx]

    layer = pos.layer
    access = LAYER_ACCESS.get(layer, {})
    method = access.get("method", "direct")

    if method == "momentary":
        layer_cost = 1.5
    elif method in ("toggled", "momentary_or_locked"):
        layer_cost = 2.0
    elif method == "locked":
        layer_cost = 3.0
    else:
        layer_cost = 0.0

    total = base_effort + thumb_busy + layer_cost

    detail = f"pos=({pos.x},{pos.y}) eff={base_effort:.0f} layer_cost={layer_cost:.1f}"
    if thumb_busy > 0:
        detail += f" thumb_busy={thumb_busy:.0f}"

    return total, detail


# Scenarios — imported from realworld_compare.py's format
VALIDATION_SCENARIOS = {
    "Quick Teams standup": [
        ("Ctrl+Shift+M", "teams", "Toggle mute"),
        ("Ctrl+Shift+O", "teams", "Toggle camera"),
        ("Ctrl+E", "teams", "Search"),
        ("Enter", "teams", "Send"),
        ("Ctrl+Shift+H", "teams", "Hang up"),
    ],
    "VS Code editing burst": [
        ("Ctrl+P", "vscode", "Quick open"),
        ("Ctrl+/", "vscode", "Toggle comment"),
        ("Ctrl+D", "vscode", "Select next"),
        ("Ctrl+S", "vscode", "Save"),
        ("Ctrl+`", "vscode", "Terminal"),
        ("F5", "vscode", "Debug"),
        ("F12", "vscode", "Go to definition"),
        ("Ctrl+Shift+P", "vscode", "Command palette"),
        ("Ctrl+Shift+K", "vscode", "Delete line"),
    ],
    "Browser with Vimium": [
        ("j", "browser", "Scroll down"),
        ("k", "browser", "Scroll up"),
        ("f", "browser", "Link hints"),
        ("Ctrl+T", "browser", "New tab"),
        ("Ctrl+W", "browser", "Close tab"),
        ("Ctrl+Tab", "browser", "Next tab"),
        ("Ctrl+L", "browser", "Address bar"),
        ("Ctrl+F", "browser", "Find"),
    ],
    "Window management": [
        ("Win+Left", "windows", "Snap left"),
        ("Win+Right", "windows", "Snap right"),
        ("Win+Up", "windows", "Maximize"),
        ("Alt+Tab", "windows", "Switch app"),
        ("Win+D", "windows", "Desktop"),
        ("Win+E", "windows", "Explorer"),
    ],
    "M-Files workflow": [
        ("Ctrl+F", "mfiles", "Find"),
        ("F2", "mfiles", "Rename"),
        ("Alt+Enter", "mfiles", "Properties"),
        ("Enter", "mfiles", "Open"),
        ("Escape", "mfiles", "Close"),
    ],
    "Excel data work": [
        ("Ctrl+C", "excel", "Copy"),
        ("Ctrl+V", "excel", "Paste"),
        ("Tab", "excel", "Next cell"),
        ("Enter", "excel", "Confirm/next row"),
        ("Ctrl+Z", "excel", "Undo"),
        ("F2", "excel", "Edit cell"),
        ("Ctrl+Shift+L", "excel", "Filter"),
    ],
}


def print_validation_table(build_dir):
    canonical = json.load(open(os.path.join(build_dir, "canonical.json"), encoding="utf-8"))
    scores = json.load(open(os.path.join(build_dir, "app_shortcut_scores.json"), encoding="utf-8"))
    config = json.load(open(os.path.join(build_dir, "..", "evolve", "config.json"), encoding="utf-8"))

    positions = build_position_index(canonical, {7})
    pool = build_shortcut_pool(scores, canonical)
    genome = encode_current_layout(canonical, positions, pool)
    ev = FitnessEvaluator(positions, pool, config, current_genome=genome)

    print("=" * 90)
    print("FITNESS VALIDATION TABLE")
    print("Rate each shortcut's REAL effort 1-10 (1=effortless, 10=painful)")
    print("=" * 90)

    all_entries = []

    for scenario, steps in VALIDATION_SCENARIOS.items():
        print(f"\n### {scenario}")
        print(f"{'Keys':25s} {'App':10s} {'Layer':8s} {'Model':7s} {'Position':20s} {'Your rating':12s}")
        print("-" * 85)

        for keys, app, desc in steps:
            pos, shortcut = find_shortcut_position(keys, app, genome, positions, pool)
            effort, detail = compute_step_effort(pos, shortcut, ev)

            layer_str = f"L{pos.layer} {LAYER_NAMES.get(pos.layer, '')}" if pos else "MISSING"
            effort_str = f"{effort:.1f}" if effort is not None else "N/A"

            print(f"{keys:25s} {app:10s} {layer_str:8s} {effort_str:7s} {detail:20s} [___/10]")

            all_entries.append({
                "scenario": scenario,
                "keys": keys,
                "app": app,
                "desc": desc,
                "layer": pos.layer if pos else None,
                "model_effort": round(float(effort), 1) if effort is not None else None,
                "position": f"({pos.x},{pos.y})" if pos else None,
                "detail": detail,
            })

    # Write template for ratings
    template = {"entries": all_entries, "instructions": "Add 'real_effort' (1-10) to each entry, then run with --analyze"}
    template_path = os.path.join(build_dir, "fitness_validation_template.json")
    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2)
    print(f"\n\nTemplate saved to: {template_path}")
    print("Add 'real_effort' (1-10) to each entry and rerun with --analyze")


def analyze_ratings(build_dir, ratings_path):
    with open(ratings_path, encoding="utf-8") as f:
        data = json.load(f)

    entries = data["entries"]
    rated = [e for e in entries if e.get("real_effort") is not None and e.get("model_effort") is not None]

    if len(rated) < 5:
        print(f"Need at least 5 rated entries, got {len(rated)}")
        return

    model = [e["model_effort"] for e in rated]
    real = [e["real_effort"] for e in rated]

    # Pearson correlation
    n = len(model)
    mean_m = sum(model) / n
    mean_r = sum(real) / n
    cov = sum((m - mean_m) * (r - mean_r) for m, r in zip(model, real)) / n
    std_m = math.sqrt(sum((m - mean_m) ** 2 for m in model) / n)
    std_r = math.sqrt(sum((r - mean_r) ** 2 for r in real) / n)
    corr = cov / (std_m * std_r) if std_m > 0 and std_r > 0 else 0

    print(f"Correlation (model vs real): {corr:.3f}")
    print(f"  > 0.7 = good calibration")
    print(f"  0.4-0.7 = needs tuning")
    print(f"  < 0.4 = fitness model is miscalibrated\n")

    # Find worst mismatches
    mismatches = []
    for e in rated:
        # Normalize both to 1-10 scale
        model_norm = min(10, max(1, e["model_effort"]))
        real_norm = e["real_effort"]
        gap = abs(model_norm - real_norm)
        mismatches.append({**e, "gap": gap, "direction": "model too high" if model_norm > real_norm else "model too low"})

    mismatches.sort(key=lambda x: -x["gap"])
    print("WORST MISMATCHES (model vs reality):")
    print(f"{'Keys':25s} {'App':10s} {'Model':7s} {'Real':6s} {'Gap':5s} {'Direction'}")
    print("-" * 70)
    for m in mismatches[:10]:
        print(f"{m['keys']:25s} {m['app']:10s} {m['model_effort']:7.1f} {m['real_effort']:6.1f} {m['gap']:5.1f} {m['direction']}")

    # Identify systematic biases
    print("\nSYSTEMATIC BIASES:")
    by_layer = {}
    for e in rated:
        l = e.get("layer")
        if l is not None:
            by_layer.setdefault(l, []).append((e["model_effort"], e["real_effort"]))

    for layer in sorted(by_layer):
        pairs = by_layer[layer]
        avg_model = sum(m for m, _ in pairs) / len(pairs)
        avg_real = sum(r for _, r in pairs) / len(pairs)
        bias = avg_model - avg_real
        if abs(bias) > 1.0:
            direction = "overestimates" if bias > 0 else "underestimates"
            print(f"  L{layer} ({LAYER_NAMES.get(layer, '')}): model {direction} effort by {abs(bias):.1f}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python validate_fitness.py <build_dir>              # generate validation table")
        print("  python validate_fitness.py <build_dir> --analyze <ratings.json>  # analyze")
        sys.exit(1)

    build_dir = sys.argv[1]
    if "--analyze" in sys.argv:
        idx = sys.argv.index("--analyze")
        if idx + 1 < len(sys.argv):
            analyze_ratings(build_dir, sys.argv[idx + 1])
        else:
            analyze_ratings(build_dir, os.path.join(build_dir, "fitness_validation_template.json"))
    else:
        print_validation_table(build_dir)


if __name__ == "__main__":
    main()
