const { readBuild, writeBuild } = require("./lib/io");
const { paramsMatch, modifiersMatch, normalizeParam } = require("./lib/normalize");

function run(config) {
  const errors = [], warnings = [];
  const canonical = readBuild("canonical.json");
  const { layers, apply_keys, workflow_apps } = canonical;

  const diffs = [];
  let matched = 0, csvOnly = 0, applyOnly = 0;

  const csvByKey = new Map();
  for (const [layerId, layerData] of Object.entries(layers)) {
    for (const [coord, binding] of Object.entries(layerData.keys)) {
      const [x, y] = coord.split(":").map(Number);
      csvByKey.set(`${layerId}:${x}:${y}`, binding);
    }
  }

  const applyByKey = new Map();
  for (const k of apply_keys) {
    applyByKey.set(`${k.layer}:${k.x}:${k.y}`, k);
  }

  for (const [key, csvBinding] of csvByKey) {
    const applyBinding = applyByKey.get(key);
    if (!applyBinding) {
      if (!/transparent|none/i.test(csvBinding.behavior)) {
        diffs.push({ key, field: "existence", csv_value: csvBinding.behavior, apply_value: "(missing)", severity: "info" });
      }
      csvOnly++;
      continue;
    }

    if (csvBinding.behavior.toLowerCase() !== applyBinding.behavior.toLowerCase()) {
      if (/coach_/i.test(csvBinding.behavior) && /coach_/i.test(applyBinding.behavior)) {
        diffs.push({ key, field: "behavior", csv_value: csvBinding.behavior, apply_value: applyBinding.behavior, severity: "mismatch" });
      } else if (/transparent|none/i.test(csvBinding.behavior) !== /transparent|none/i.test(applyBinding.behavior)) {
        diffs.push({ key, field: "behavior", csv_value: csvBinding.behavior, apply_value: applyBinding.behavior, severity: "mismatch" });
      }
    }

    if (csvBinding.parameter && applyBinding.parameter) {
      if (!paramsMatch(csvBinding.parameter, applyBinding.parameter)) {
        const severity = normalizeParam(csvBinding.parameter).toUpperCase() === normalizeParam(applyBinding.parameter).toUpperCase() ? "alias" : "mismatch";
        diffs.push({ key, field: "parameter", csv_value: csvBinding.parameter, apply_value: applyBinding.parameter, severity });
      }
    }

    if (!modifiersMatch(csvBinding.modifiers, applyBinding.modifiers)) {
      diffs.push({ key, field: "modifiers", csv_value: csvBinding.modifiers.join(","), apply_value: (applyBinding.modifiers || []).join(","), severity: "mismatch" });
    }

    matched++;
  }

  for (const [key] of applyByKey) {
    if (!csvByKey.has(key)) { applyOnly++; }
  }

  const workflowRefs = { total: 0, valid: 0, broken: [] };
  for (const [appId, app] of Object.entries(workflow_apps)) {
    for (const ref of (app.refs || [])) {
      workflowRefs.total++;
      const parsed = parseCharybdisRef(ref.charybdis);
      if (parsed.length === 0) {
        workflowRefs.broken.push({ app: appId, shortcut: ref.keys, charybdis: ref.charybdis, issue: "Could not parse reference" });
      } else {
        let anyValid = false;
        for (const p of parsed) {
          const csvKey = csvByKey.get(`${p.layer}:${p.x}:${p.y}`);
          if (csvKey) anyValid = true;
        }
        if (anyValid) workflowRefs.valid++;
        else workflowRefs.broken.push({ app: appId, shortcut: ref.keys, charybdis: ref.charybdis, issue: "Referenced position not found in CSV" });
      }
    }
  }

  const mismatches = diffs.filter((d) => d.severity === "mismatch");
  if (mismatches.length > 0) {
    warnings.push(`${mismatches.length} sync mismatch(es) between CSV and apply script`);
  }
  if (workflowRefs.broken.length > 0) {
    warnings.push(`${workflowRefs.broken.length} broken workflow reference(s)`);
  }

  const output = {
    timestamp: new Date().toISOString(),
    summary: { total_csv: csvByKey.size, total_apply: applyByKey.size, matched, diffs: diffs.length, csv_only: csvOnly, apply_only: applyOnly },
    diffs: diffs.filter((d) => d.severity === "mismatch"),
    aliases: diffs.filter((d) => d.severity === "alias"),
    workflow_refs: workflowRefs,
  };

  writeBuild("sync_report.json", output);
  return { success: true, output, errors, warnings };
}

function parseCharybdisRef(ref) {
  if (!ref) return [];
  const results = [];
  const layerMatch = ref.match(/L(\d+)/);
  if (!layerMatch) return [];
  const layer = layerMatch[1];
  const posMatches = ref.matchAll(/x(\d+),\s*y(\d+)/g);
  for (const m of posMatches) {
    results.push({ layer: Number(layer), x: Number(m[1]), y: Number(m[2]) });
  }
  if (results.length === 0) {
    results.push({ layer: Number(layer), x: -1, y: -1 });
  }
  return results;
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  const s = result.output.summary;
  console.log(`Sync: ${s.matched} matched, ${s.diffs} diffs (${result.output.diffs.length} mismatches, ${result.output.aliases.length} aliases), ${s.csv_only} CSV-only, ${s.apply_only} apply-only`);
  console.log(`Workflows: ${result.output.workflow_refs.valid}/${result.output.workflow_refs.total} valid refs`);
  if (result.warnings.length) console.log(`Warnings: ${result.warnings.join("; ")}`);
  if (result.output.diffs.length) {
    console.log("Mismatches:");
    for (const d of result.output.diffs) console.log(`  ${d.key}: ${d.field} — CSV="${d.csv_value}" vs Apply="${d.apply_value}"`);
  }
}
