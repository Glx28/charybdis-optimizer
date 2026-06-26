const { readBuild, writeBuild, ensureBuildDir } = require("./lib/io");
const { LAYER_NAMES, effort, LEFT_COLS, RIGHT_COLS } = require("./lib/constants");
const fs = require("fs");
const path = require("path");

function tryReadBuild(name) {
  try { return readBuild(name); } catch { return null; }
}

function run(config) {
  const canonical = tryReadBuild("canonical.json");
  if (!canonical) { return { skipped: true, reason: "canonical.json not found in build/" }; }
  const sync = tryReadBuild("sync_report.json") || {};
  const resolved = tryReadBuild("resolved_layout.json") || {};
  const graph = tryReadBuild("layer_graph.json") || {};
  const ergo = tryReadBuild("ergonomic_scores.json") || {};
  const workflows = tryReadBuild("workflow_results.json") || {};
  const appScores = tryReadBuild("app_shortcut_scores.json") || {};

  const lines = [];
  const w = (s) => lines.push(s);

  w("# Charybdis Keymap Baseline Report");
  w(`Generated: ${new Date().toISOString()}\n`);

  // Summary
  w("## Summary\n");
  w(`| Metric | Value |`);
  w(`|--------|-------|`);
  w(`| Total keys | ${canonical.sources.csv.rowCount} |`);
  w(`| Active layers | ${Object.keys(canonical.layers).filter(l => {const k=canonical.layers[l].keys; return Object.values(k).some(b => !/transparent|none/i.test(b.behavior));}).length} |`);
  w(`| Apps tracked | ${appScores.summary.total_apps} |`);
  w(`| Total app shortcuts | ${appScores.summary.total_shortcuts} |`);
  w(`| Shortcuts mapped | ${appScores.summary.total_mapped} (${appScores.summary.overall_coverage_pct}%) |`);
  w(`| Workflows tested | ${workflows.summary.total_workflows} |`);
  w(`| Workflows passing | ${workflows.summary.passed}/${workflows.summary.total_workflows} |`);
  w(`| Sync mismatches | ${sync.summary.diffs} |`);
  w(`| Layer contexts | ${Object.keys(resolved.contexts).length} |`);
  w("");

  // Per-app coverage
  w("## App Coverage\n");
  w("| App | Weight | Shortcuts | Mapped | Coverage | Efficiency |");
  w("|-----|--------|-----------|--------|----------|------------|");
  for (const app of appScores.apps) {
    w(`| ${app.name} | ${app.user_weight} | ${app.total_shortcuts} | ${app.mapped} | ${app.coverage_pct}% | ${app.efficiency_pct}% |`);
  }
  w("");

  // Unmapped high-frequency
  w("## High-Frequency Unmapped Shortcuts\n");
  const allUnmapped = [];
  for (const app of appScores.apps) {
    for (const s of app.shortcuts) {
      if (!s.mapped && s.freq_weight >= 6) {
        allUnmapped.push({ app: app.name, keys: s.keys, action: s.action, freq: s.frequency, importance: s.importance });
      }
    }
  }
  allUnmapped.sort((a, b) => b.importance - a.importance);
  if (allUnmapped.length) {
    w("| Importance | App | Shortcut | Action | Frequency |");
    w("|-----------|-----|----------|--------|-----------|");
    for (const u of allUnmapped.slice(0, 20)) {
      w(`| ${u.importance.toFixed(1)} | ${u.app} | ${u.keys} | ${u.action} | ${u.freq} |`);
    }
  } else {
    w("All high-frequency shortcuts are mapped.");
  }
  w("");

  // Layer map
  w("## Layer Map\n");
  for (const [layerId, layerData] of Object.entries(canonical.layers)) {
    const active = Object.values(layerData.keys).filter(k => !/transparent|none/i.test(k.behavior));
    const total = Object.keys(layerData.keys).length;
    if (active.length === 0) continue;

    w(`### Layer ${layerId}: ${layerData.name || layerData.role}\n`);

    for (const y of [0,1,2,3]) {
      const left = LEFT_COLS.map(x => {
        const k = layerData.keys[`${x}:${y}`];
        if (!k || /transparent/i.test(k.behavior)) return "·";
        if (/none/i.test(k.behavior)) return "—";
        return k.label || k.visual_label || "?";
      });
      const right = RIGHT_COLS.map(x => {
        const k = layerData.keys[`${x}:${y}`];
        if (!k || /transparent/i.test(k.behavior)) return "·";
        if (/none/i.test(k.behavior)) return "—";
        return k.label || k.visual_label || "?";
      });
      const padL = left.map(s => s.padEnd(6)).join(" ");
      const padR = right.map(s => s.padEnd(6)).join(" ");
      w(`    ${padL}  │  ${padR}    y${y}`);
    }
    w("");
  }

  // Efficiency bars
  w("## App Efficiency (weighted accessibility)\n");
  w("```");
  for (const app of appScores.apps) {
    const bar = "█".repeat(Math.round(app.efficiency_pct / 3)) + "░".repeat(33 - Math.round(app.efficiency_pct / 3));
    w(`  ${app.name.slice(0, 20).padEnd(20)} ${bar} ${app.efficiency_pct}%`);
  }
  w("```\n");

  // Layer access paths
  w("## Layer Access Paths\n");
  const graphData = readBuild("layer_graph.json");
  for (const edge of graphData.edges.filter(e => e.from === 0 || e.from <= 4)) {
    const fromName = LAYER_NAMES[edge.from] || `L${edge.from}`;
    const toName = LAYER_NAMES[edge.to] || `L${edge.to}`;
    w(`- **L${edge.from}** (${fromName}) → **L${edge.to}** (${toName}) via ${edge.mechanism} at x${edge.key.x},y${edge.key.y}`);
  }
  w("");

  // Workflow results
  w("## Workflow Simulation Results\n");
  w("| Workflow | Effort | Weight | Weighted | Pass |");
  w("|----------|--------|--------|----------|------|");
  for (const r of workflows.results) {
    w(`| ${r.name} | ${r.total_effort} | ${r.weight} | ${r.weighted_score.toFixed(1)} | ${r.pass ? "✓" : "✗"} |`);
  }
  w(`\nTotal weighted effort: ${workflows.summary.total_weighted_effort.toFixed(1)}`);
  w("");

  // Layer graph
  w("## Layer Access Graph\n");
  w(`Reachable from base: ${graph.reachability.from_base.map(l => `L${l}`).join(", ")}`);
  w(`Unreachable: ${graph.reachability.unreachable.length ? graph.reachability.unreachable.map(l => `L${l}`).join(", ") : "none"}\n`);

  w("### Exit paths for lockable/toggleable layers\n");
  for (const [layer, info] of Object.entries(graph.exit_analysis)) {
    w(`- **L${layer}** (${LAYER_NAMES[layer]}): ${info.count} exits ${info.sufficient ? "✓" : "⚠ INSUFFICIENT"}`);
    for (const e of info.exits) w(`  - ${e.coord}: ${e.behavior} (${e.label})`);
  }
  w("");

  // Ergonomic issues
  w("## Ergonomic Notes\n");
  if (ergo.constraint_violations.length) {
    w("### Constraint Violations\n");
    for (const v of ergo.constraint_violations) {
      w(`- **${v.severity}**: L${v.layer} ${v.position} (${v.label}) — ${v.detail}`);
    }
  } else {
    w("No constraint violations.");
  }
  w("");

  // Sync status
  w("## File Sync Status\n");
  w(`CSV rows: ${sync.summary.total_csv}, Apply keys: ${sync.summary.total_apply}`);
  w(`Matched: ${sync.summary.matched}, Mismatches: ${sync.diffs.length}, Aliases: ${sync.aliases.length}`);
  if (sync.diffs.length) {
    w("\n### Mismatches\n");
    for (const d of sync.diffs) {
      w(`- \`${d.key}\`: ${d.field} — CSV: "${d.csv_value}" vs Apply: "${d.apply_value}"`);
    }
  }
  w("");

  const report = lines.join("\n");
  ensureBuildDir();
  const { BUILD } = require("./lib/io");
  fs.writeFileSync(path.join(BUILD, "baseline_report.md"), report, "utf-8");
  writeBuild("baseline_report_meta.json", { timestamp: new Date().toISOString(), lines: lines.length });

  return { success: true, output: { lines: lines.length }, errors: [], warnings: [] };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  console.log(`Report generated: ${result.output.lines} lines → build/baseline_report.md`);
}
