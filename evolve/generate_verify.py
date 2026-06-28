"""Generate a ZMK Studio verify script for an evolved layout.

Reads the evolved apply script's key data and the verify logic from
charybdis-zmk-config, bundles them into a self-contained verify script.

Usage: python generate_verify.py <build_dir>
"""
import json
import sys
import os
import csv
import io
from pathlib import Path

from representation import (
    build_position_index, build_shortcut_pool, encode_current_layout,
    LAYER_NAMES, KNOWN_KEY_NAMES,
)
from export_zmk import export_genome_to_zmk, shortcut_to_zmk_binding, MOD_MAP
from layer_access import LayerAccessAnalyzer


def build_expected_csv(changes, canonical):
    """Build EXPECTED_CSV rows from the evolved changes merged with the current layout.

    For positions that the optimizer changed, use the evolved binding.
    For unchanged positions, use the canonical layout's binding."""
    rows = []
    changed_coords = {}
    for c in changes:
        key = (c["layer"], c["x"], c["y"])
        changed_coords[key] = c

    numeric_layers = [
        (layer_id, layer_data)
        for layer_id, layer_data in canonical["layers"].items()
        if str(layer_id).strip().isdigit()
    ]
    for layer_id, layer_data in sorted(numeric_layers, key=lambda x: int(x[0])):
        layer_num = int(layer_id)
        if layer_num == 7:
            continue
        for coord, binding in sorted(layer_data.get("keys", {}).items()):
            x, y = map(int, coord.split(":"))
            key = (layer_num, x, y)

            if key in changed_coords:
                c = changed_coords[key]
                behavior = c["behavior"]
                parameter = c.get("parameter", "")
                modifiers = c.get("modifiers", [])
                label = c.get("label", "")
            else:
                behavior = binding.get("behavior", "")
                parameter = binding.get("parameter", "")
                modifiers = binding.get("modifiers", [])
                label = parameter.replace("Keyboard ", "")[:10] if parameter else behavior[:10]

            if behavior.lower() in ("transparent", "none", ""):
                continue

            checked_mods = "+".join(modifiers) if modifiers else ""
            param_summary = parameter if behavior == "Key Press" else parameter
            text_params = f"default_transform: | Key::{parameter}" if behavior == "Key Press" and parameter else ""
            select_params = "default_transform:default_transform" if behavior == "Key Press" else ""

            rows.append({
                "layer": str(layer_num),
                "layer_name": str(layer_num),
                "x": str(x),
                "y": str(y),
                "visual_label": label,
                "visual_text": behavior,
                "visual_behavior": behavior,
                "behavior": behavior,
                "parameter_summary": param_summary,
                "text_parameters": text_params,
                "select_parameters": select_params,
                "checked_modifiers": checked_mods,
            })

    return rows


def rows_to_csv_string(rows):
    output = io.StringIO()
    fields = ["layer", "layer_name", "x", "y", "visual_label", "visual_text",
              "visual_behavior", "behavior", "parameter_summary", "text_parameters",
              "select_parameters", "checked_modifiers"]
    writer = csv.DictWriter(output, fieldnames=fields, quoting=csv.QUOTE_ALL,
                            lineterminator="\r\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return output.getvalue()


def generate_verify_script(changes, canonical, version="evolved", access_report=None):
    """Generate a self-contained verify script."""
    rows = build_expected_csv(changes, canonical)
    csv_string = rows_to_csv_string(rows)

    # Only verify the layers we changed
    changed_layers = sorted(set(c["layer"] for c in changes))
    access_report = access_report or {"valid": True, "reachable_layers": [], "required_layers": [], "access_cost": 0}
    access_report_json = json.dumps(access_report, indent=2)

    verify_logic = _fallback_verify(changes, changed_layers)

    return f"""/*
Charybdis optimizer layout VERIFY — {version}
Verifies {len(changes)} evolved changes across layers {changed_layers}.
Paste in ZMK Studio console AFTER applying. Does not edit or save.
*/

window.CHARYBDIS_LAYER_ACCESS_REPORT = {access_report_json};

{verify_logic}
"""


def _fallback_verify(changes, changed_layers):
    """Generate verify script using the same DOM selectors as the apply script."""
    changes_json = json.dumps(changes, indent=2)
    return f"""
(async function VerifyEvolvedLayout() {{
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const clean = (s) => String(s || "").trim();
  const qa = (sel, root) => [...(root || document).querySelectorAll(sel)];

  const expected = {changes_json};
  const layers = {json.dumps(changed_layers)};
  const accessReport = window.CHARYBDIS_LAYER_ACCESS_REPORT || {{}};

  // --- Layer selection (mirrors apply script) ---

  function findLayerButton(layer) {{
    const layerList = document.querySelector('[aria-label="Keymap Layer"]');
    return layerList?.querySelector('[role="option"][data-key="' + layer + '"]')
      || qa('[role="option"]', layerList || document).find(el => clean(el.textContent) === String(layer));
  }}

  function selectedLayer() {{
    const selected = document.querySelector('[aria-label="Keymap Layer"] [role="option"][aria-selected="true"]');
    return clean(selected?.textContent || "");
  }}

  async function selectLayer(layer) {{
    if (selectedLayer() === String(layer)) return true;
    const el = findLayerButton(layer);
    if (!el) {{
      console.error("Layer " + layer + " not found in ZMK Studio layer list");
      return false;
    }}
    el.click();
    await sleep(650);
    if (selectedLayer() !== String(layer)) {{
      console.error("Failed to switch to layer " + layer + " (stuck on " + selectedLayer() + ")");
      return false;
    }}
    return true;
  }}

  // --- Key selection (mirrors apply script) ---

  function findKeyElement(x, y) {{
    const holder = document.querySelector('[x="' + x + '"][y="' + y + '"]');
    return holder?.querySelector("button") || holder;
  }}

  async function selectKey(x, y) {{
    const el = findKeyElement(x, y);
    if (!el) return false;
    (el.closest("button") || el).click();
    await sleep(220);
    return true;
  }}

  // --- Read current key state ---

  function visibleSelects() {{
    return qa("select").filter(s => s.offsetParent !== null);
  }}

  function isBehaviorSelect(s) {{
    return [...s.options].some(o => clean(o.textContent) === "Key Press")
      && [...s.options].some(o => clean(o.textContent) === "Transparent");
  }}

  function isZoomSelect(s) {{
    return [...s.options].some(o => clean(o.textContent) === "Auto")
      && [...s.options].some(o => clean(o.textContent) === "100%");
  }}

  function isDefaultTransformSelect(s) {{
    return [...s.options].some(o => clean(o.textContent) === "default_transform")
      && s.options.length <= 3;
  }}

  function readCurrent() {{
    const allSelects = visibleSelects();
    const bSel = allSelects.find(isBehaviorSelect);
    const behavior = bSel ? clean(bSel.options[bSel.selectedIndex]?.textContent) : "";

    const combobox = qa("input").find(i => i.offsetParent !== null && i.getAttribute("role") === "combobox");
    let parameter = combobox ? clean(combobox.value) : "";

    if (!parameter) {{
      const paramSelect = allSelects.find(s =>
        s !== bSel && !isBehaviorSelect(s) && !isZoomSelect(s) && !isDefaultTransformSelect(s)
      );
      if (paramSelect) {{
        parameter = clean(paramSelect.options[paramSelect.selectedIndex]?.textContent) || "";
      }}
    }}

    if (behavior === "Bluetooth" && (parameter === "Select Profile" || parameter === "Disconnect Profile")) {{
      const numInput = qa("input[type=number]").find(i => i.offsetParent !== null);
      if (numInput) {{
        parameter = "BT_SEL " + clean(numInput.value);
      }}
    }}

    const checkboxes = qa("input[type=checkbox]").filter(c => c.offsetParent !== null && c.checked);
    const modifiers = checkboxes.map(c => {{
      const label = c.closest("label")?.textContent || c.parentElement?.textContent || "";
      return clean(label);
    }}).filter(Boolean);
    return {{ behavior, parameter, modifiers }};
  }}

  // --- Main verify loop ---

  console.log("Verifying " + expected.length + " evolved keys across layers " + JSON.stringify(layers) + "...");
  let passed = 0, failed = 0, skipped = 0;
  const failures = [];
  let currentLayer = null;
  for (const key of expected) {{
    if (!layers.includes(key.layer)) continue;
    if (key.studio_skip) {{ skipped++; continue; }}

    if (currentLayer !== key.layer) {{
      const switched = await selectLayer(key.layer);
      if (!switched) {{
        failures.push({{ layer: key.layer, x: key.x, y: key.y, label: key.label, issues: ["could not switch to layer " + key.layer], expected: key, actual: {{}} }});
        failed++;
        continue;
      }}
      currentLayer = key.layer;
      console.log("Verifying layer " + key.layer + "...");
    }}

    const found = await selectKey(key.x, key.y);
    if (!found) {{
      failures.push({{ layer: key.layer, x: key.x, y: key.y, label: key.label, issues: ["key not found in Studio UI"], expected: key, actual: {{}} }});
      failed++;
      continue;
    }}

    const actual = readCurrent();
    const issues = [];

    if (actual.behavior !== key.behavior) {{
      issues.push("behavior: expected " + key.behavior + ", got " + actual.behavior);
    }}

    if (key.parameter && actual.parameter) {{
      const expNorm = clean(key.parameter).replace("Keyboard ", "").toUpperCase();
      const actNorm = clean(actual.parameter).replace("Keyboard ", "").toUpperCase();
      if (expNorm !== actNorm) {{
        issues.push("parameter: expected \\"" + key.parameter + "\\", got \\"" + actual.parameter + "\\"");
      }}
    }} else if (key.parameter && !actual.parameter) {{
      issues.push("parameter: expected \\"" + key.parameter + "\\", got empty");
    }}

    const expMods = (key.modifiers || []).sort().join("+");
    const actMods = actual.modifiers.sort().join("+");
    if (expMods !== actMods) {{
      issues.push("modifiers: expected \\"" + expMods + "\\", got \\"" + actMods + "\\"");
    }}

    if (issues.length > 0) {{
      failures.push({{ layer: key.layer, x: key.x, y: key.y, label: key.label, issues, expected: key, actual }});
      failed++;
      console.warn("FAIL L" + key.layer + " (" + key.x + "," + key.y + ") " + (key.label || "") + ": " + issues.join("; "));
    }} else {{
      passed++;
    }}
  }}

  console.log("\\n" + "=".repeat(50));
  console.log("LAYER ACCESS");
  console.log("Valid expected graph: " + (accessReport.valid ? "YES" : "NO"));
  if (accessReport.required_layers) console.log("Required layers: " + accessReport.required_layers.join(", "));
  if (accessReport.reachable_layers) console.log("Reachable layers: " + accessReport.reachable_layers.join(", "));
  if (accessReport.access_cost !== undefined) console.log("Total access cost: " + accessReport.access_cost);
  if (accessReport.errors && accessReport.errors.length) console.error("Access errors: " + accessReport.errors.join("; "));
  console.log("-".repeat(50));
  if (failed === 0) {{
    console.log("PASSED: All " + passed + " keys verified correctly." + (skipped ? " (" + skipped + " firmware-only keys skipped)" : ""));
  }} else {{
    console.error("FAILED: " + failed + " of " + (passed + failed) + " keys mismatch." + (skipped ? " (" + skipped + " firmware-only skipped)" : ""));
    console.table(failures.map(f => ({{
      position: "L" + f.layer + " (" + f.x + "," + f.y + ")",
      label: f.label || "",
      issues: f.issues?.join("; ") || f.issue || ""
    }})));
  }}
  console.log("=".repeat(50));
}})();
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_verify.py <build_dir>")
        sys.exit(1)

    build_dir = sys.argv[1]

    canonical = json.load(open(os.path.join(build_dir, "canonical.json"), encoding="utf-8"))
    scores = json.load(open(os.path.join(build_dir, "app_shortcut_scores.json"), encoding="utf-8"))

    # Read the evolved apply script to extract changes
    apply_path = os.path.join(build_dir, "evolved_apply.js")
    with open(apply_path, encoding="utf-8") as f:
        content = f.read()

    # Extract keys from CHARYBDIS_FINAL_LAYOUT
    start = content.find('"keys":')
    if start < 0:
        print("No keys found in evolved_apply.js")
        sys.exit(1)

    # Find the matching closing bracket (string-aware)
    bracket_start = content.index('[', start)
    depth = 0
    in_string = False
    bracket_end = len(content)
    for i in range(bracket_start, len(content)):
        ch = content[i]
        if ch == '"':
            backslashes = 0
            j = i - 1
            while j >= 0 and content[j] == '\\':
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                bracket_end = i + 1
                break

    changes = json.loads(content[bracket_start:bracket_end])
    print(f"Loaded {len(changes)} changes from evolved_apply.js")

    positions = build_position_index(canonical, {7})
    pool = build_shortcut_pool(scores, canonical)
    genome = encode_current_layout(canonical, positions, pool)
    key_to_idx = {(p.layer, p.x, p.y): i for i, p in enumerate(positions)}
    binding_to_sid = {}
    for shortcut in pool:
        binding = shortcut_to_zmk_binding(shortcut)
        if not binding:
            continue
        key = (
            binding.get("behavior", ""),
            binding.get("parameter", ""),
            tuple(sorted(binding.get("modifiers", []))),
        )
        binding_to_sid.setdefault(key, shortcut.sid)

    for c in changes:
        idx = key_to_idx.get((c["layer"], c["x"], c["y"]))
        if idx is None:
            continue
        if c["behavior"] == "Transparent":
            genome[idx] = -1
            continue
        key = (
            c.get("behavior", ""),
            c.get("parameter", ""),
            tuple(sorted(c.get("modifiers", []))),
        )
        sid = binding_to_sid.get(key)
        if sid is not None:
            genome[idx] = sid

    access_validation = LayerAccessAnalyzer(canonical, positions, pool).validate(genome)
    access_report = {
        "valid": access_validation.valid,
        "required_layers": sorted(access_validation.required_layers),
        "reachable_layers": sorted(access_validation.reachable_layers),
        "access_cost": round(access_validation.total_access_cost, 2),
        "errors": access_validation.errors,
    }
    if not access_validation.valid:
        print("Layer access validation failed; refusing to generate verifier:")
        for err in access_validation.errors:
            print(f"  - {err}")
        sys.exit(1)

    script = generate_verify_script(changes, canonical, version="research-v1", access_report=access_report)
    out_path = os.path.join(build_dir, "evolved_verify.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"Verify script written to: {out_path}")
    print(f"Paste in ZMK Studio console after applying to check all keys.")


if __name__ == "__main__":
    main()
