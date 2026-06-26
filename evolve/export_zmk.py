"""Export an evolution genome to ZMK Studio apply script format.

Reads an evolution result, maps genome changes back to ZMK Studio bindings,
and produces a JavaScript file that can be pasted into ZMK Studio's console.
"""
import json
import sys
import os
from pathlib import Path

from representation import (
    build_position_index, build_shortcut_pool, encode_current_layout,
    decode_genome, LAYER_NAMES, KNOWN_KEY_NAMES, split_shortcut_keys,
)
from layer_access import LayerAccessAnalyzer


# Map from optimizer shortcut keys to ZMK Studio parameter + modifiers.
# Modifier format in ZMK Studio: "L Ctrl", "L Shift", "L Alt", "L GUI"
MOD_MAP = {
    "Ctrl": "L Ctrl",
    "Shift": "L Shift",
    "Alt": "L Alt",
    "Win": "L GUI",
}

# Base key name to ZMK Studio "Keyboard X" parameter
KEY_TO_ZMK_PARAM = {}
for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    KEY_TO_ZMK_PARAM[letter] = f"Keyboard {letter}"

KEY_TO_ZMK_PARAM.update({
    # Digits — ZMK Studio uses full names
    "0": "Keyboard 0 and Right Bracket", "1": "Keyboard 1 and Bang",
    "2": "Keyboard 2 and At", "3": "Keyboard 3 and Hash",
    "4": "Keyboard 4 and Dollar", "5": "Keyboard 5 and Percent",
    "6": "Keyboard 6 and Caret", "7": "Keyboard 7 and Ampersand",
    "8": "Keyboard 8 and Star", "9": "Keyboard 9 and Left Bracket",
    # F-keys
    "F1": "Keyboard F1", "F2": "Keyboard F2", "F3": "Keyboard F3",
    "F4": "Keyboard F4", "F5": "Keyboard F5", "F6": "Keyboard F6",
    "F7": "Keyboard F7", "F8": "Keyboard F8", "F9": "Keyboard F9",
    "F10": "Keyboard F10", "F11": "Keyboard F11", "F12": "Keyboard F12",
    "F13": "Keyboard F13", "F14": "Keyboard F14", "F15": "Keyboard F15",
    "F16": "Keyboard F16", "F17": "Keyboard F17", "F18": "Keyboard F18",
    "F19": "Keyboard F19", "F20": "Keyboard F20", "F21": "Keyboard F21",
    "F22": "Keyboard F22", "F23": "Keyboard F23", "F24": "Keyboard F24",
    # Special keys
    "Enter": "Keyboard Return Enter", "Return": "Keyboard Return Enter",
    "Tab": "Keyboard Tab", "Escape": "Keyboard Escape", "Esc": "Keyboard Escape",
    "Space": "Keyboard Spacebar", "Delete": "Keyboard Delete",
    "Backspace": "Keyboard Delete",
    "LeftShift": "Keyboard LeftShift", "RightShift": "Keyboard RightShift",
    "LeftControl": "Keyboard LeftControl", "RightControl": "Keyboard RightControl",
    "LeftAlt": "Keyboard LeftAlt", "RightAlt": "Keyboard RightAlt",
    "LeftGUI": "Keyboard Left GUI",
    # Navigation
    "LeftArrow": "Keyboard LeftArrow", "RightArrow": "Keyboard RightArrow",
    "UpArrow": "Keyboard UpArrow", "DownArrow": "Keyboard DownArrow",
    "Left": "Keyboard LeftArrow", "Right": "Keyboard RightArrow",
    "Up": "Keyboard UpArrow", "Down": "Keyboard DownArrow",
    "Home": "Keyboard Home", "End": "Keyboard End",
    "PageUp": "Keyboard PageUp", "PageDown": "Keyboard PageDown",
    "Insert": "Keyboard Insert",
    "PrintScreen": "Keyboard PrintScreen and SysReq",
    "Print Screen": "Keyboard PrintScreen and SysReq",
    "Page Up": "Keyboard PageUp", "Page Down": "Keyboard PageDown",
    "Del": "Keyboard Delete Forward",
    "Shift": "Keyboard LeftShift",
    # Pause/Break not available in ZMK Studio — Win+Pause is in UNSUPPORTED_SHORTCUTS
    # Shifted symbols — map to base key (shift is a modifier)
    "!": "Keyboard 1 and Bang",
    "@": "Keyboard 2 and At",
    "#": "Keyboard 3 and Hash",
    "$": "Keyboard 4 and Dollar",
    "%": "Keyboard 5 and Percent",
    "^": "Keyboard 6 and Caret",
    "&": "Keyboard 7 and Ampersand",
    "*": "Keyboard 8 and Star",
    "(": "Keyboard 9 and Left Bracket",
    ")": "Keyboard 0 and Right Bracket",
    "_": "Keyboard Dash and Underscore",
    "{": "Keyboard Left Brace",
    "}": "Keyboard Right Brace",
    "|": "Keyboard Backslash and Pipe",
    ":": "Keyboard SemiColon and Colon",
    '"': "Keyboard Left Apos and Double",
    "<": "Keyboard Comma and LessThan",
    ">": "Keyboard Period and GreaterThan",
    "?": "Keyboard ForwardSlash and QuestionMark",
    # Symbols
    "`": "Keyboard Grave Accent and Tilde", "~": "Keyboard Grave Accent and Tilde",
    "-": "Keyboard Dash and Underscore",
    "=": "Keyboard Equals and Plus", "+": "Keyboard Equals and Plus",
    "[": "Keyboard Left Brace", "]": "Keyboard Right Brace",
    "\\": "Keyboard Backslash and Pipe",
    ";": "Keyboard SemiColon and Colon",
    "'": "Keyboard Left Apos and Double",
    ",": "Keyboard Comma and LessThan",
    ".": "Keyboard Period and GreaterThan",
    "/": "Keyboard ForwardSlash and QuestionMark",
    "Period": "Keyboard Period and GreaterThan",
    "Comma": "Keyboard Comma and LessThan",
    "Equal": "Keyboard Equals and Plus",
    "Equals": "Keyboard Equals and Plus",
    "Equal and Plus": "Keyboard Equals and Plus",
    "Minus": "Keyboard Dash and Underscore",
    "Dash": "Keyboard Dash and Underscore",
    "ForwardSlash": "Keyboard ForwardSlash and QuestionMark",
    "Backslash": "Keyboard Backslash and Pipe",
    "SemiColon": "Keyboard SemiColon and Colon",
    "Apostrophe": "Keyboard Left Apos and Double",
    "Grave": "Keyboard Grave Accent and Tilde",
    "Left Brace": "Keyboard Left Brace",
    "Right Brace": "Keyboard Right Brace",
})

# Shortcuts that can't be represented as a single Key Press in ZMK Studio
UNSUPPORTED_SHORTCUTS = {"Click", "Alt+Click", "Ctrl+Click", "Shift+Click",
                         "Ctrl+K S",  # VS Code chord — can't be single ZMK binding
                         "Win+Pause",  # Pause/Break not in ZMK Studio key list
                         "Alt+Shift",  # modifier-only language switch
                         }


def shortcut_to_zmk_binding(shortcut):
    """Convert a Shortcut object to ZMK Studio binding dict."""
    if shortcut.category == "base_key":
        return _base_key_to_binding(shortcut)

    if shortcut.keys in UNSUPPORTED_SHORTCUTS:
        return None

    keys = shortcut.keys
    zmk_mods = []
    mods, base = split_shortcut_keys(keys)
    if keys.startswith("Ctrl+K ") or not base:
        return None
    for p in mods:
        zmk_mod = MOD_MAP.get(p)
        if zmk_mod:
            zmk_mods.append(zmk_mod)

    if shortcut.zmk_parameter:
        param = shortcut.zmk_parameter
    else:
        param = KEY_TO_ZMK_PARAM.get(base, KEY_TO_ZMK_PARAM.get(base.upper(), f"Keyboard {base}"))

    return {
        "behavior": "Key Press",
        "parameter": param,
        "modifiers": zmk_mods,
        "label": shortcut.keys,
    }


def _base_key_to_binding(shortcut):
    """Convert a base key shortcut back to its ZMK binding."""
    key_id = shortcut.base_key
    action = shortcut.action

    if key_id.startswith("select:mb"):
        num = key_id.replace("select:mb", "")
        return {
            "behavior": "Mouse Key Press",
            "parameter": f"MB{num}",
            "modifiers": [],
            "label": f"MB{num}",
        }

    if key_id.startswith("bt_sel"):
        num = key_id.replace("bt_sel", "").strip().strip("_").strip()
        return {
            "behavior": "Bluetooth",
            "parameter": f"BT_SEL {num}",
            "modifiers": [],
            "label": "Bluetooth",
        }

    if key_id.startswith("coach_"):
        return {
            "behavior": key_id,
            "parameter": "",
            "modifiers": [],
            "label": key_id,
        }

    for prefix, behavior in [("momentary_layer_", "Momentary Layer"),
                              ("toggle_layer_", "Toggle Layer"),
                              ("to_layer_", "To Layer")]:
        if key_id.startswith(prefix):
            return {
                "behavior": behavior,
                "parameter": shortcut.zmk_parameter,
                "modifiers": [],
                "label": behavior,
            }

    if key_id in ("reset", "bootloader"):
        return {
            "behavior": key_id.capitalize(),
            "parameter": "",
            "modifiers": [],
            "label": key_id.capitalize(),
        }

    if key_id == "select:clear selected profile":
        return {
            "behavior": "Bluetooth",
            "parameter": "Clear Selected Profile",
            "modifiers": [],
            "label": key_id,
        }

    if key_id.startswith("select:"):
        # USB Output, BLE Output, Toggle Outputs — not available in Studio UI
        return {
            "behavior": "Output Selection",
            "parameter": key_id.replace("select:", "").title(),
            "modifiers": [],
            "label": key_id,
            "studio_skip": True,
        }

    # Try zmk_parameter first, with validation
    if shortcut.zmk_parameter:
        param = shortcut.zmk_parameter
        # Try KEY_TO_ZMK_PARAM first (handles aliases like "Print Screen" -> full name)
        mapped = KEY_TO_ZMK_PARAM.get(param)
        if mapped and mapped in KNOWN_KEY_NAMES:
            param = mapped
        elif not param.startswith("Keyboard ") and not param.startswith("Keypad "):
            param = f"Keyboard {param}"
        if param in KNOWN_KEY_NAMES:
            return {
                "behavior": "Key Press",
                "parameter": param,
                "modifiers": [],
                "label": key_id,
            }

    # Look up from our validated mapping
    # Strip _combo suffix and try common aliases
    clean_id = key_id.replace("_combo", "")
    ALIAS = {
        "equal": "=", "equals": "=", "minus": "-", "dash": "-",
        "left bracket": "[", "right bracket": "]", "left brace": "[", "right brace": "]",
        "comma": ",", "period": ".", "semicolon": ";",
        "forwardslash": "/", "backslash": "\\", "grave accent": "`",
        "left apos": "'",
    }
    if clean_id in ALIAS:
        clean_id = ALIAS[clean_id]
    param = KEY_TO_ZMK_PARAM.get(clean_id) or KEY_TO_ZMK_PARAM.get(clean_id.upper())
    if param and param in KNOWN_KEY_NAMES:
        return {
            "behavior": "Key Press",
            "parameter": param,
            "modifiers": [],
            "label": key_id,
        }

    # Last resort: try the raw zmk_parameter
    if shortcut.zmk_parameter:
        param = shortcut.zmk_parameter
        if not param.startswith("Keyboard "):
            param = f"Keyboard {param}"
        return {
            "behavior": "Key Press",
            "parameter": param,
            "modifiers": [],
            "label": key_id,
        }

    return {
        "behavior": "Key Press",
        "parameter": f"Keyboard {key_id.title()}",
        "modifiers": [],
        "label": key_id,
    }


def _validate_layer_access_or_raise(genome, positions, pool, canonical):
    analyzer = LayerAccessAnalyzer(canonical, positions, pool)
    validation = analyzer.validate(genome)
    if not validation.valid:
        print("\n" + "=" * 60)
        print("LAYER ACCESS VALIDATION FAILED")
        print("=" * 60)
        for err in validation.errors:
            print(f"  - {err}")
        print("Refusing to export an apply script that can soft-lock layers.")
        print("=" * 60 + "\n")
        raise ValueError("invalid layer access graph")
    return validation


def export_genome_to_zmk(genome, positions, pool, canonical, solution_id="evolved"):
    """Generate ZMK Studio apply script entries from a genome.

    Returns the full layout (unchanged + changed keys) as a list of dicts.
    """
    _validate_layer_access_or_raise(genome, positions, pool, canonical)
    current = encode_current_layout(canonical, positions, pool)
    changes = []

    for i, (new_sid, old_sid) in enumerate(zip(genome, current)):
        if new_sid == old_sid:
            continue
        pos = positions[i]
        if new_sid < 0:
            binding = {
                "behavior": "Transparent",
                "parameter": "",
                "modifiers": [],
                "label": "",
            }
            rationale = f"Cleared by optimizer ({solution_id})"
        else:
            shortcut = pool[new_sid]
            binding = shortcut_to_zmk_binding(shortcut)
            if binding is None:
                continue
            rationale = f"Optimizer ({solution_id}): {shortcut.keys} ({shortcut.action})"

        changes.append({
            "layer": pos.layer,
            "x": pos.x,
            "y": pos.y,
            "behavior": binding["behavior"],
            "parameter": binding["parameter"],
            "modifiers": binding["modifiers"],
            "label": binding["label"],
            "rationale": rationale,
            "optimizer_changed": True,
        })

    return changes


def generate_apply_script(changes, version="evolved"):
    """Generate a self-contained ZMK Studio apply script.

    Reads the apply logic from apply_every_key.js in the sibling repo
    and bundles it with the evolved layout data. One paste, applies everything."""
    for c in changes:
        c["apply_batch"] = True
        if not c.get("rationale"):
            c["rationale"] = f"Optimizer {version}"

    # Validate all parameters and print suggestions for bad ones
    bad = []
    for c in changes:
        if c["behavior"] == "Key Press" and c.get("parameter"):
            if c["parameter"] not in KNOWN_KEY_NAMES:
                # Find similar candidates
                param_lower = c["parameter"].lower()
                candidates = []
                for known in sorted(KNOWN_KEY_NAMES):
                    # Match if any significant word overlaps
                    param_words = set(param_lower.replace("keyboard ", "").split())
                    known_words = set(known.lower().replace("keyboard ", "").split())
                    if param_words & known_words:
                        candidates.append(known)
                bad.append((c, candidates))

    if bad:
        print(f"\n{'='*60}")
        print(f"PARAMETER VALIDATION: {len(bad)} bad parameters found")
        print(f"{'='*60}")
        for c, candidates in bad:
            print(f"\n  L{c['layer']} ({c['x']},{c['y']}): \"{c['parameter']}\" [{c.get('label','')}]")
            if candidates:
                print(f"  Suggestions:")
                for cand in candidates[:5]:
                    print(f"    -> \"{cand}\"")
            else:
                print(f"  No suggestions found — check zmk_studio_key_names.json")
        print(f"\nFix these in KEY_TO_ZMK_PARAM or ALIAS in export_zmk.py before applying.")
        print(f"{'='*60}\n")
        raise ValueError(f"{len(bad)} invalid ZMK Studio key parameter(s)")

    layers = sorted(set(c["layer"] for c in changes))
    keys_json = json.dumps(changes, indent=2)

    # Read the apply logic from the sibling repo
    apply_script_path = Path(__file__).parent.parent.parent / "charybdis-zmk-config" / "scripts" / "zmk-studio" / "apply_every_key.js"
    apply_logic = ""
    if apply_script_path.exists():
        full_text = apply_script_path.read_text(encoding="utf-8")
        # Extract the async function (from "(async function" to the end)
        marker = "(async function CharybdisStudioAssistant()"
        idx = full_text.find(marker)
        if idx >= 0:
            apply_logic = full_text[idx:]

    if not apply_logic:
        print("WARNING: Could not find apply_every_key.js — generating data-only payload")
        apply_logic = 'console.log("Apply logic not found. Paste apply_every_key.js manually after this.");'
    else:
        # Patch: replace hard throws with logging + candidate suggestions
        apply_logic = apply_logic.replace(
            'throw new Error(`UNKNOWN KEY NAME: "${parameter}" is not in KNOWN_KEY_NAMES. This would silently fall to "Keyboard B". Fix the parameter name in the layout data. See scripts/zmk-studio/zmk_studio_key_names.json for valid names.`);',
            """const candidates = [...KNOWN_KEY_NAMES].filter(k => {
        const pWords = parameter.toLowerCase().split(/\\s+/);
        return pWords.some(w => w.length > 2 && k.toLowerCase().includes(w));
      });
      console.error(`UNKNOWN KEY: "${parameter}"`);
      if (candidates.length) console.log("  Candidates:", candidates.join(", "));
      window._CHARYBDIS_APPLY_ERRORS.push({parameter, candidates, layer: arguments[0]?.layer, x: arguments[0]?.x, y: arguments[0]?.y});
      return;"""
        )
        apply_logic = apply_logic.replace(
            'throw new Error(`NO MATCHING OPTION for "${parameter}". Refusing to proceed — would silently select wrong key (likely "Keyboard B"). Check the parameter name.`);',
            """const allOptions = [...document.querySelectorAll("[role=option], li")]
        .filter(el => el.offsetParent !== null)
        .map(el => el.textContent.trim())
        .filter(Boolean);
      console.error(`NO MATCH: "${parameter}"`);
      if (allOptions.length) console.log("  Visible options:", allOptions.slice(0, 10).join(", "));
      window._CHARYBDIS_APPLY_ERRORS.push({parameter, visibleOptions: allOptions.slice(0, 10)});
      return;"""
        )

    # Inject result tracking: override console.error/warn to capture failures
    summary_script = """
// Post-apply summary — runs after apply_every_key.js finishes
window._CHARYBDIS_APPLY_ERRORS = window._CHARYBDIS_APPLY_ERRORS || [];
window._CHARYBDIS_APPLY_SKIPPED = window._CHARYBDIS_APPLY_SKIPPED || [];
const _origError = console.error.bind(console);
const _origWarn = console.warn.bind(console);
console.error = function(...args) {
  const msg = args.map(String).join(" ");
  if (msg.includes("UNKNOWN KEY") || msg.includes("NO MATCHING") || msg.includes("Failed L")) {
    window._CHARYBDIS_APPLY_ERRORS.push(msg);
  }
  _origError(...args);
};
console.warn = function(...args) {
  const msg = args.map(String).join(" ");
  if (msg.includes("No exact visible") || msg.includes("Verify manually")) {
    window._CHARYBDIS_APPLY_ERRORS.push(msg);
  }
  _origWarn(...args);
};
"""

    post_summary = """
// Restore console and print summary with suggestions
setTimeout(function() {
  if (typeof _origError !== "undefined") {
    console.error = _origError;
    console.warn = _origWarn;
  }
  const errors = window._CHARYBDIS_APPLY_ERRORS || [];
  const total = window.CHARYBDIS_FINAL_LAYOUT?.keyCount || 0;
  console.log("\\n" + "=".repeat(60));
  console.log("APPLY SUMMARY");
  console.log("=".repeat(60));
  console.log("Total keys: " + total);
  console.log("Errors: " + errors.length);
  if (errors.length > 0) {
    console.log("\\nFAILED KEYS WITH SUGGESTIONS:");
    errors.forEach(function(e) {
      if (typeof e === "object") {
        const pos = e.layer !== undefined ? "L" + e.layer + " (" + e.x + "," + e.y + ")" : "";
        console.log("  " + pos + " " + (e.parameter || ""));
        if (e.candidates && e.candidates.length) {
          console.log("    Candidates: " + e.candidates.join(", "));
        }
        if (e.visibleOptions && e.visibleOptions.length) {
          console.log("    Visible options: " + e.visibleOptions.join(", "));
        }
      } else {
        console.log("  " + e);
      }
    });
    console.log("\\nFix these parameter names in export_zmk.py, regenerate, and re-apply.");
  } else {
    console.log("All keys applied or already correct.");
  }
  console.log("=".repeat(60));
}, 2000);
"""

    return f"""/*
Charybdis optimizer layout — {version}
{len(changes)} key changes across layers {layers}.
Self-contained: paste this one file in ZMK Studio console to apply all changes.
*/

{summary_script}

window.CHARYBDIS_FINAL_LAYOUT = {{
  "project": "Charybdis Optimizer Layout",
  "version": "{version}",
  "keyCount": {len(changes)},
  "keys": {keys_json}
}};

window.CHARYBDIS_MODE = "applyLayer";
window.CHARYBDIS_APPLY_LAYER_INDEX = "all";
window.CHARYBDIS_ENABLE_LAYER_APPLY = true;

console.log("Applying " + window.CHARYBDIS_FINAL_LAYOUT.keyCount + " keys across layers {layers}...");

{apply_logic}

{post_summary}
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_zmk.py <build_dir> [solution_index]")
        print("  solution_index: index into pareto_front (default: best balanced)")
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
            print(f"Solution {solution.get('id', sol_idx)} is invalid:")
            for err in validation.errors:
                print(f"  - {err}")
            raise ValueError("selected solution violates layer access invariant")
    else:
        # Best balanced: lowest effort + violations
        valid_front = [s for s in front if analyzer.validate(s["genome"]).valid]
        if not valid_front:
            print("No valid layer-access solutions found in Pareto front")
            for s in front[:5]:
                validation = analyzer.validate(s["genome"])
                print(f"  {s.get('id', '?')}: {'; '.join(validation.errors) or 'unknown'}")
            raise ValueError("no valid layer-access solution")
        skipped = len(front) - len(valid_front)
        if skipped:
            print(f"Skipped {skipped} invalid layer-access solution(s)")
        solution = min(valid_front, key=lambda s: s["fitness"]["effort"] + s["fitness"]["violations"])

    genome = solution["genome"]
    sol_id = solution.get("id", f"sol_{sol_idx or 0}")
    fitness = solution["fitness"]

    print(f"Exporting solution {sol_id}:")
    print(f"  Effort: {fitness['effort']:.0f}")
    print(f"  Adjacency: {fitness['adjacency']:.0f}")
    print(f"  Violations: {fitness['violations']:.0f}")
    print(f"  Assignments: {solution.get('total_assignments', '?')}")
    print(f"  Changes: {solution.get('changes_from_current', '?')}")

    changes = export_genome_to_zmk(genome, positions, pool, canonical, sol_id)
    print(f"\n  ZMK Studio changes: {len(changes)} keys")

    script = generate_apply_script(changes, version=f"evolved-{sol_id}")
    out_path = os.path.join(build_dir, "evolved_apply.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"  Written to: {out_path}")

    # Also write a human-readable diff
    diff_lines = [f"# Evolved layout diff — {sol_id}\n"]
    diff_lines.append(f"# Effort: {fitness['effort']:.0f}  Adj: {fitness['adjacency']:.0f}  Viol: {fitness['violations']:.0f}\n\n")
    by_layer = {}
    for c in changes:
        by_layer.setdefault(c["layer"], []).append(c)
    for layer in sorted(by_layer):
        lname = LAYER_NAMES.get(layer, f"Layer {layer}")
        diff_lines.append(f"## Layer {layer} ({lname}) — {len(by_layer[layer])} changes\n")
        for c in sorted(by_layer[layer], key=lambda c: (c["y"], c["x"])):
            mod_str = "+".join(c.get("modifiers", [])) + "+" if c.get("modifiers") else ""
            diff_lines.append(f"  ({c['x']},{c['y']}) → {c['behavior']} {mod_str}{c['parameter']}  [{c.get('rationale', '')}]\n")
        diff_lines.append("\n")

    diff_path = os.path.join(build_dir, "evolved_diff.txt")
    with open(diff_path, "w", encoding="utf-8") as f:
        f.writelines(diff_lines)
    print(f"  Diff written to: {diff_path}")


if __name__ == "__main__":
    main()
