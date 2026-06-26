#!/usr/bin/env node
const { readBuild } = require("./lib/io");
const { LAYER_NAMES } = require("./lib/constants");

try {
  const canonical = readBuild("canonical.json");
  const sync = readBuild("sync_report.json");
  const workflows = readBuild("workflow_results.json");
  const appScores = readBuild("app_shortcut_scores.json");
  const graph = readBuild("layer_graph.json");

  const w = console.log;
  w("\n" + "═".repeat(60));
  w("  CHARYBDIS KEYMAP DASHBOARD — v2.5");
  w("═".repeat(60));

  w(`\n  Layout: ${canonical.sources.csv.rowCount} keys, ${Object.keys(canonical.layers).length} layers`);
  w(`  Active layers: ${Object.keys(canonical.layers).filter(l => Object.values(canonical.layers[l].keys).some(k => !/transparent|none/i.test(k.behavior))).length}`);
  w(`  Reachable: ${graph.reachability.from_base.map(l => "L" + l).join(" ")}`);

  w("\n  ┌─ APP COVERAGE ─────────────────────────────────┐");
  w("  │ App              │ Mapped │ Total │ Coverage     │");
  w("  ├──────────────────┼────────┼───────┼──────────────┤");
  for (const app of appScores.apps) {
    const bar = "█".repeat(Math.round(app.coverage_pct / 5)) + "░".repeat(20 - Math.round(app.coverage_pct / 5));
    w(`  │ ${app.name.slice(0, 16).padEnd(16)} │ ${String(app.mapped).padStart(6)} │ ${String(app.total_shortcuts).padStart(5)} │ ${bar} ${app.coverage_pct}% │`);
  }
  w(`  ├──────────────────┼────────┼───────┼──────────────┤`);
  w(`  │ ${"TOTAL".padEnd(16)} │ ${String(appScores.summary.total_mapped).padStart(6)} │ ${String(appScores.summary.total_shortcuts).padStart(5)} │ ${"█".repeat(Math.round(appScores.summary.overall_coverage_pct / 5))}${"░".repeat(20 - Math.round(appScores.summary.overall_coverage_pct / 5))} ${appScores.summary.overall_coverage_pct}% │`);
  w("  └──────────────────┴────────┴───────┴──────────────┘");

  w("\n  ┌─ WORKFLOWS ─────────────────────────────────────┐");
  for (const r of workflows.results) {
    w(`  │ ${r.pass ? "✓" : "✗"} ${r.name.slice(0, 45).padEnd(45)} e=${String(r.total_effort).padStart(3)} │`);
  }
  w(`  │ ${"".padEnd(45)} tot=${String(workflows.summary.total_weighted_effort.toFixed(0)).padStart(3)} │`);
  w("  └─────────────────────────────────────────────────┘");

  w("\n  ┌─ SYNC & ANALYSIS ─────────────────────────────┐");
  w(`  │ CSV↔Apply: ${sync.summary.matched} matched, ${sync.diffs.length} mismatches               │`);
  w(`  │ Workflow refs: ${String(sync.workflow_refs.valid).padStart(2)}/${String(sync.workflow_refs.total).padStart(2)} valid                          │`);
  try {
    const cross = readBuild("cross_app_analysis.json");
    w(`  │ Universal shortcuts: ${cross.summary.universal_count} (${cross.summary.universal_mapped} mapped)         │`);
    w(`  │ Shortcut conflicts: ${(cross.shortcut_conflicts||[]).length} (same key, diff action)   │`);
  } catch {}
  w("  └────────────────────────────────────────────────┘");

  w("\n  ┌─ LAYER MAP ────────────────────────────────────┐");
  for (const [l, data] of Object.entries(canonical.layers)) {
    const active = Object.values(data.keys).filter(k => !/transparent|none/i.test(k.behavior)).length;
    if (active === 0) continue;
    const name = (LAYER_NAMES[l] || data.role || "").slice(0, 20);
    const bar = "█".repeat(Math.min(30, Math.round(active / 2)));
    w(`  │ L${l.padEnd(2)} ${name.padEnd(20)} ${String(active).padStart(2)} keys ${bar.padEnd(30)} │`);
  }
  w("  └────────────────────────────────────────────────┘");

  w("\n" + "═".repeat(60) + "\n");
} catch (e) {
  console.error("Dashboard error — run the pipeline first: node pipeline/run_pipeline.js");
  console.error(e.message);
}
