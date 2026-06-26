"""Real-world scenario comparison: current layout vs evolved layout.

Defines realistic multi-app work sessions as sequences of shortcut actions,
then measures total effort, missing shortcuts, and layer transitions for
each layout. This tests whether the optimizer actually improves daily usage.
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from representation import (
    build_position_index, build_shortcut_pool, encode_current_layout,
    decode_genome, LAYER_NAMES, LAYER_ACCESS, LAYER_APP_CONTEXT,
)

# ── Real-world scenarios ──────────────────────────────────────────────
# Each scenario is a sequence of (keys, app_hint) tuples representing
# what a user would actually do. app_hint helps disambiguate shortcuts
# that exist in multiple apps.

SCENARIOS = {
    "Morning standup + code review": {
        "weight": 1.0,
        "description": "Open Teams, join standup, mute/unmute, then switch to VS Code for code review",
        "actions": [
            ("Win+1", "windows"),       # open pinned Teams
            ("Ctrl+E", "teams"),        # search bar
            ("Enter", "teams"),         # send/confirm
            ("Ctrl+Shift+M", "teams"),  # toggle mute
            ("Ctrl+Shift+M", "teams"),  # unmute to speak
            ("Ctrl+Shift+O", "teams"),  # toggle camera
            ("Alt+Tab", "windows"),     # switch to VS Code
            ("Ctrl+P", "vscode"),       # quick open file
            ("Ctrl+/", "vscode"),       # toggle comment
            ("Ctrl+S", "vscode"),       # save
            ("Ctrl+Shift+G", "vscode"), # source control
            ("Ctrl+Shift+M", "teams"),  # mute again before speaking
            ("Ctrl+Shift+H", "teams"),  # hang up
        ],
    },

    "Deep coding session": {
        "weight": 1.0,
        "description": "Editing, debugging, navigating code in VS Code",
        "actions": [
            ("Ctrl+P", "vscode"),       # open file
            ("Ctrl+G", "vscode"),       # go to line
            ("Ctrl+D", "vscode"),       # select next occurrence
            ("Ctrl+D", "vscode"),       # select another
            ("Ctrl+/", "vscode"),       # toggle comment
            ("Ctrl+S", "vscode"),       # save
            ("F5", "vscode"),           # start debugging
            ("F9", "vscode"),           # toggle breakpoint
            ("F10", "vscode"),          # step over
            ("F10", "vscode"),          # step over
            ("F11", "vscode"),          # step into
            ("Shift+F11", "vscode"),    # step out
            ("Shift+F5", "vscode"),     # stop debugging
            ("Ctrl+`", "vscode"),       # toggle terminal
            ("Ctrl+Shift+P", "vscode"), # command palette
            ("Ctrl+Shift+F", "vscode"), # find in files / format
            ("Ctrl+T", "vscode"),       # new tab / go to symbol
            ("Ctrl+W", "vscode"),       # close tab
            ("F2", "vscode"),           # rename symbol
            ("F12", "vscode"),          # go to definition
            ("F8", "vscode"),           # next problem
            ("Ctrl+Shift+K", "vscode"), # delete line
        ],
    },

    "Browser research + Vimium": {
        "weight": 0.9,
        "description": "Browsing with Vimium keys, tabs, navigation",
        "actions": [
            ("j", "browser"),           # scroll down
            ("j", "browser"),           # scroll down
            ("k", "browser"),           # scroll up
            ("f", "browser"),           # show link hints
            ("F", "browser"),           # open in new tab
            ("d", "browser"),           # half page down
            ("u", "browser"),           # half page up
            ("o", "browser"),           # open URL bar
            ("x", "browser"),           # close tab
            ("H", "browser"),           # go back
            ("Ctrl+T", "browser"),      # new tab
            ("Ctrl+W", "browser"),      # close tab
            ("Ctrl+Tab", "browser"),    # next tab
            ("Ctrl+Shift+Tab", "browser"), # prev tab
            ("Ctrl+L", "browser"),      # address bar
            ("Ctrl+F", "browser"),      # find on page
            ("Alt+Left", "browser"),    # back
            ("Alt+Right", "browser"),   # forward
            ("Ctrl+Shift+T", "browser"),# reopen closed tab
            ("Space", "browser"),       # scroll page
        ],
    },

    "Window management": {
        "weight": 0.8,
        "description": "Snapping windows, switching monitors, virtual desktops",
        "actions": [
            ("Win+Left", "windows"),     # snap left
            ("Win+Right", "windows"),    # snap right
            ("Win+Up", "windows"),       # maximize
            ("Win+Down", "windows"),     # minimize/restore
            ("Win+Tab", "windows"),      # task view
            ("Alt+Tab", "windows"),      # switch apps
            ("Alt+Tab", "windows"),      # switch again
            ("Win+D", "windows"),        # show desktop
            ("Win+E", "windows"),        # file explorer
            ("Win+Shift+Left", "windows"),  # move to left monitor
            ("Win+Shift+Right", "windows"), # move to right monitor
            ("Win+Shift+S", "windows"),  # screenshot snip
            ("Win+S", "windows"),        # search
            ("Win+V", "windows"),        # clipboard history
            ("Win+L", "windows"),        # lock PC
        ],
    },

    "Teams chat workflow": {
        "weight": 0.7,
        "description": "Chatting, reacting, navigating Teams",
        "actions": [
            ("Ctrl+E", "teams"),        # search
            ("Ctrl+3", "teams"),        # teams/channels
            ("Ctrl+1", "teams"),        # activity
            ("Ctrl+4", "teams"),        # calendar
            ("Enter", "teams"),         # send message
            ("Shift+Enter", "teams"),   # new line
            ("Enter", "teams"),         # send
            ("Ctrl+Shift+M", "teams"),  # mute
            ("Ctrl+Shift+O", "teams"),  # camera
            ("Ctrl+Shift+H", "teams"),  # hang up
            ("Up", "teams"),            # edit last message
            ("Ctrl+R", "teams"),        # reply
        ],
    },

    "Excel data analysis": {
        "weight": 0.6,
        "description": "Navigating, selecting, formatting in Excel",
        "actions": [
            ("Ctrl+Home", "excel"),      # go to A1
            ("Ctrl+End", "excel"),       # go to last cell
            ("Ctrl+Shift+End", "excel"), # select to last cell
            ("F4", "excel"),             # toggle absolute ref
            ("Ctrl+C", "excel"),         # copy
            ("Ctrl+V", "excel"),         # paste
            ("Ctrl+Z", "excel"),         # undo
            ("Ctrl+S", "excel"),         # save
            ("Ctrl+B", "excel"),         # bold
            ("Ctrl+F", "excel"),         # find
            ("Ctrl+H", "excel"),         # find and replace
            ("Ctrl+A", "excel"),         # select all
            ("F2", "excel"),             # edit cell
            ("Ctrl+D", "excel"),         # fill down
            ("Ctrl+1", "excel"),         # format cells
            ("Ctrl+Right", "excel"),     # jump right
            ("Ctrl+Shift+Home", "excel"),# select to A1
        ],
    },

    "Quick save-close-switch": {
        "weight": 0.9,
        "description": "Rapid micro-tasks: save, close, switch — the stuff you do 50x/day",
        "actions": [
            ("Ctrl+S", "vscode"),
            ("Ctrl+W", "vscode"),
            ("Alt+Tab", "windows"),
            ("Ctrl+S", "vscode"),
            ("Ctrl+Tab", "browser"),
            ("Ctrl+W", "browser"),
            ("Alt+Tab", "windows"),
            ("Ctrl+C", "windows"),
            ("Ctrl+V", "windows"),
            ("Ctrl+Z", "windows"),
            ("Escape", "windows"),
            ("Delete", "windows"),
        ],
    },
}


def build_shortcut_index(genome, positions, pool):
    """Build a lookup: (keys_lower, app) -> list of (effort, layer, position)."""
    index = defaultdict(list)
    for i, sid in enumerate(genome):
        if sid < 0:
            continue
        s = pool[sid]
        pos = positions[i]
        # Index by keys (case-sensitive for Vimium) + each app
        for app in (s.apps if s.apps else [s.app]):
            index[(s.keys, app)].append({
                "effort": pos.effort,
                "layer": pos.layer,
                "hand": pos.hand,
                "is_thumb": pos.is_thumb,
                "coord": pos.coord,
                "action": s.action,
            })
        # Also index without app for fallback
        index[(s.keys, "*")].append({
            "effort": pos.effort,
            "layer": pos.layer,
            "hand": pos.hand,
            "is_thumb": pos.is_thumb,
            "coord": pos.coord,
            "action": s.action,
        })
    return index


def find_best_assignment(index, keys, app_hint):
    """Find the lowest-effort position for a shortcut, preferring correct app layer."""
    # Try exact app match first
    candidates = index.get((keys, app_hint), [])

    # Check which layers are valid for this app
    valid_layers = set()
    for layer, apps in LAYER_APP_CONTEXT.items():
        if app_hint in apps:
            valid_layers.add(layer)

    # Prefer candidates on valid layers
    on_layer = [c for c in candidates if c["layer"] in valid_layers]
    if on_layer:
        return min(on_layer, key=lambda c: c["effort"]), True, True

    # Any layer with this app's shortcut
    if candidates:
        return min(candidates, key=lambda c: c["effort"]), True, False

    # Fallback: any occurrence of this key combo
    fallback = index.get((keys, "*"), [])
    on_layer_fb = [c for c in fallback if c["layer"] in valid_layers]
    if on_layer_fb:
        return min(on_layer_fb, key=lambda c: c["effort"]), True, True
    if fallback:
        return min(fallback, key=lambda c: c["effort"]), True, False

    return None, False, False


def layer_access_effort(layer):
    """Effort to access a layer (thumb hold or toggle activation)."""
    access = LAYER_ACCESS.get(layer)
    if not access:
        return 0
    method = access.get("method", "momentary")
    if method == "momentary":
        kx, ky = access.get("key_x", 0), access.get("key_y", 0)
        from representation import effort as calc_effort
        return calc_effort(kx, ky)
    elif method in ("toggled", "locked", "momentary_or_locked"):
        return 2  # flat cost for toggle
    return 0


def evaluate_scenario(name, scenario, index):
    """Run one scenario and return metrics."""
    actions = scenario["actions"]
    total_effort = 0
    missing = []
    wrong_layer = []
    last_layer = 0
    layer_switches = 0
    details = []

    for keys, app_hint in actions:
        best, found, correct_layer = find_best_assignment(index, keys, app_hint)
        if not found:
            missing.append((keys, app_hint))
            details.append(f"  MISSING: {keys:<25} ({app_hint})")
            total_effort += 20  # heavy penalty for missing shortcut
            continue

        key_effort = best["effort"]
        if best["layer"] != last_layer:
            switch_cost = layer_access_effort(best["layer"])
            key_effort += switch_cost
            layer_switches += 1
            last_layer = best["layer"]

        total_effort += key_effort
        layer_tag = f"L{best['layer']}"
        wrong_tag = "" if correct_layer else " [WRONG LAYER]"
        if not correct_layer:
            wrong_layer.append((keys, app_hint, best["layer"]))
        details.append(f"  e={key_effort:<4.0f} {layer_tag:<4} {keys:<25} ({app_hint}){wrong_tag}")

    return {
        "total_effort": total_effort,
        "missing": missing,
        "wrong_layer": wrong_layer,
        "layer_switches": layer_switches,
        "n_actions": len(actions),
        "details": details,
    }


def main():
    build_dir = sys.argv[1] if len(sys.argv) > 1 else "../build"
    results_file = sys.argv[2] if len(sys.argv) > 2 else "evolution_results.json"

    canonical = json.load(open(os.path.join(build_dir, "canonical.json"), encoding="utf-8"))
    scores = json.load(open(os.path.join(build_dir, "app_shortcut_scores.json"), encoding="utf-8"))

    frozen = {7}
    positions = build_position_index(canonical, frozen)
    pool = build_shortcut_pool(scores, canonical)
    current = encode_current_layout(canonical, positions, pool)

    # Load evolution results
    results_path = os.path.join(build_dir, results_file)
    if not os.path.exists(results_path):
        print(f"No results file at {results_path}")
        return

    results = json.load(open(results_path, encoding="utf-8"))
    front = results.get("pareto_front", [])
    if not front:
        print("Empty Pareto front.")
        return

    best = min(front, key=lambda s: s["fitness"]["effort"])
    evolved = best["genome"]

    # Build shortcut indices
    current_idx = build_shortcut_index(current, positions, pool)
    evolved_idx = build_shortcut_index(evolved, positions, pool)

    print("=" * 72)
    print("REAL-WORLD SCENARIO COMPARISON: Current vs Evolved Layout")
    print("=" * 72)

    totals_current = {"effort": 0, "missing": 0, "wrong_layer": 0, "switches": 0}
    totals_evolved = {"effort": 0, "missing": 0, "wrong_layer": 0, "switches": 0}

    for name, scenario in SCENARIOS.items():
        w = scenario["weight"]
        cur = evaluate_scenario(name, scenario, current_idx)
        evo = evaluate_scenario(name, scenario, evolved_idx)

        effort_delta = evo["total_effort"] - cur["total_effort"]
        pct = (effort_delta / cur["total_effort"] * 100) if cur["total_effort"] > 0 else 0

        print(f"\n{'─' * 72}")
        print(f"  {name} (weight: {w})")
        print(f"  {scenario['description']}")
        print(f"{'─' * 72}")
        print(f"  {'Metric':<25} {'Current':>10} {'Evolved':>10} {'Delta':>10}")
        print(f"  {'─'*55}")
        print(f"  {'Total effort':<25} {cur['total_effort']:>10.0f} {evo['total_effort']:>10.0f} {effort_delta:>+10.0f} ({pct:+.1f}%)")
        print(f"  {'Missing shortcuts':<25} {len(cur['missing']):>10} {len(evo['missing']):>10}")
        print(f"  {'Wrong-layer placements':<25} {len(cur['wrong_layer']):>10} {len(evo['wrong_layer']):>10}")
        print(f"  {'Layer switches':<25} {cur['layer_switches']:>10} {evo['layer_switches']:>10}")

        # Show missing shortcuts
        if evo["missing"]:
            print(f"\n  Evolved layout MISSING:")
            for keys, app in evo["missing"]:
                also_missing = any(k == keys and a == app for k, a in cur["missing"])
                tag = " (also missing in current)" if also_missing else " << REGRESSION"
                print(f"    {keys:<25} ({app}){tag}")

        if cur["missing"] and not evo["missing"]:
            print(f"\n  Current layout was missing (now fixed in evolved):")
            for keys, app in cur["missing"]:
                if not any(k == keys and a == app for k, a in evo["missing"]):
                    print(f"    {keys:<25} ({app})  ✓ now assigned")

        # Show wrong-layer specifics for evolved
        if evo["wrong_layer"]:
            print(f"\n  Wrong-layer in evolved:")
            for keys, app, layer in evo["wrong_layer"]:
                print(f"    {keys:<25} ({app}) on L{layer} ({LAYER_NAMES.get(layer, '?')})")

        totals_current["effort"] += cur["total_effort"] * w
        totals_current["missing"] += len(cur["missing"])
        totals_current["wrong_layer"] += len(cur["wrong_layer"])
        totals_current["switches"] += cur["layer_switches"]
        totals_evolved["effort"] += evo["total_effort"] * w
        totals_evolved["missing"] += len(evo["missing"])
        totals_evolved["wrong_layer"] += len(evo["wrong_layer"])
        totals_evolved["switches"] += evo["layer_switches"]

    # Overall summary
    overall_delta = totals_evolved["effort"] - totals_current["effort"]
    overall_pct = (overall_delta / totals_current["effort"] * 100) if totals_current["effort"] > 0 else 0
    print(f"\n{'=' * 72}")
    print(f"OVERALL WEIGHTED SUMMARY")
    print(f"{'=' * 72}")
    print(f"  {'Metric':<30} {'Current':>10} {'Evolved':>10} {'Delta':>10}")
    print(f"  {'─'*60}")
    print(f"  {'Weighted effort':<30} {totals_current['effort']:>10.0f} {totals_evolved['effort']:>10.0f} {overall_delta:>+10.0f} ({overall_pct:+.1f}%)")
    print(f"  {'Total missing shortcuts':<30} {totals_current['missing']:>10} {totals_evolved['missing']:>10}")
    print(f"  {'Total wrong-layer':<30} {totals_current['wrong_layer']:>10} {totals_evolved['wrong_layer']:>10}")
    print(f"  {'Total layer switches':<30} {totals_current['switches']:>10} {totals_evolved['switches']:>10}")

    if overall_pct < -5:
        print(f"\n  VERDICT: Evolved layout is BETTER ({overall_pct:+.1f}% effort reduction)")
    elif overall_pct > 5:
        print(f"\n  VERDICT: Evolved layout is WORSE ({overall_pct:+.1f}% effort increase)")
    else:
        print(f"\n  VERDICT: Marginal difference ({overall_pct:+.1f}%)")

    # Detailed drill-down for a few key shortcuts
    print(f"\n{'=' * 72}")
    print(f"KEY SHORTCUT PLACEMENT CHECK")
    print(f"{'=' * 72}")
    critical = [
        ("Win+Left", "windows"), ("Win+Right", "windows"),
        ("Ctrl+T", "browser"), ("Ctrl+W", "browser"),
        ("j", "browser"), ("k", "browser"), ("f", "browser"),
        ("Enter", "teams"), ("Ctrl+/", "vscode"), ("Ctrl+`", "vscode"),
        ("Ctrl+Shift+M", "teams"), ("Alt+Tab", "windows"),
        ("Ctrl+S", "vscode"), ("Ctrl+P", "vscode"),
        ("F5", "vscode"), ("F12", "vscode"),
    ]
    print(f"  {'Shortcut':<20} {'App':<10} {'Current':>20} {'Evolved':>20}")
    print(f"  {'─'*70}")
    for keys, app in critical:
        cur_best, cur_found, _ = find_best_assignment(current_idx, keys, app)
        evo_best, evo_found, _ = find_best_assignment(evolved_idx, keys, app)
        cur_str = f"L{cur_best['layer']} e={cur_best['effort']:.0f}" if cur_found else "MISSING"
        evo_str = f"L{evo_best['layer']} e={evo_best['effort']:.0f}" if evo_found else "MISSING"
        marker = ""
        if cur_found and evo_found:
            if evo_best["effort"] < cur_best["effort"]:
                marker = " ✓"
            elif evo_best["effort"] > cur_best["effort"]:
                marker = " ✗"
        elif not cur_found and evo_found:
            marker = " ✓ NEW"
        elif cur_found and not evo_found:
            marker = " ✗ LOST"
        print(f"  {keys:<20} {app:<10} {cur_str:>20} {evo_str:>20}{marker}")


if __name__ == "__main__":
    main()
