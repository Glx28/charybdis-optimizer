#!/usr/bin/env node
const { ensureBuildDir, writeBuild } = require("./lib/io");

const MODULES = [
  { name: "parse_sources", path: "./parse_sources", fatal: true },
  { name: "aggregate_usage", path: "./aggregate_usage", fatal: false },
  { name: "validate_sync", path: "./validate_sync", fatal: false },
  { name: "resolve_transparency", path: "./resolve_transparency", fatal: false },
  { name: "build_layer_graph", path: "./build_layer_graph", fatal: false },
  { name: "physical_model", path: "./physical_model", fatal: false },
  { name: "simulate_workflows", path: "./simulate_workflows", fatal: false },
  { name: "score_app_shortcuts", path: "./score_app_shortcuts", fatal: false },
  { name: "reorganize_layout", path: "./reorganize_layout", fatal: false },
  { name: "generate_candidates", path: "./generate_candidates", fatal: false },
  { name: "evolve_layout", path: "./evolve_layout", fatal: false },
  { name: "analyze_cross_app", path: "./analyze_cross_app", fatal: false },
  { name: "generate_report", path: "./generate_report", fatal: false },
];

function run() {
  const singleModule = process.argv.find((a) => a.startsWith("--module="))?.split("=")[1];
  const verbose = process.argv.includes("--verbose");
  ensureBuildDir();

  const results = {};
  let allErrors = [], allWarnings = [];
  let halted = false;

  const modulesToRun = singleModule
    ? MODULES.filter((m) => m.name === singleModule)
    : MODULES;

  if (singleModule && modulesToRun.length === 0) {
    console.error(`Unknown module: ${singleModule}. Available: ${MODULES.map((m) => m.name).join(", ")}`);
    process.exit(1);
  }

  console.log("═".repeat(70));
  console.log("CHARYBDIS KEYMAP OPTIMIZER PIPELINE");
  console.log("═".repeat(70));

  for (const mod of modulesToRun) {
    if (halted) {
      results[mod.name] = { status: "skipped", reason: "previous fatal error" };
      continue;
    }

    const startTime = Date.now();
    console.log(`\n▸ ${mod.name}...`);

    try {
      const module = require(mod.path);
      const result = module.run({});
      const elapsed = Date.now() - startTime;

      results[mod.name] = {
        status: result.success ? "ok" : "failed",
        elapsed_ms: elapsed,
        errors: result.errors || [],
        warnings: result.warnings || [],
      };

      allErrors.push(...(result.errors || []).map((e) => `[${mod.name}] ${e}`));
      allWarnings.push(...(result.warnings || []).map((w) => `[${mod.name}] ${w}`));

      if (result.success) {
        console.log(`  ✓ ${mod.name} (${elapsed}ms)`);
        if (verbose && result.output?.summary) {
          console.log(`    ${JSON.stringify(result.output.summary)}`);
        }
      } else {
        console.log(`  ✗ ${mod.name} FAILED (${elapsed}ms)`);
        for (const e of (result.errors || [])) console.log(`    ERROR: ${e}`);
        if (mod.fatal) {
          console.log(`  FATAL: ${mod.name} is required. Halting pipeline.`);
          halted = true;
        }
      }

      for (const w of (result.warnings || [])) console.log(`    WARN: ${w}`);

    } catch (err) {
      const elapsed = Date.now() - startTime;
      results[mod.name] = { status: "crashed", elapsed_ms: elapsed, error: err.message };
      allErrors.push(`[${mod.name}] CRASH: ${err.message}`);
      console.log(`  ✗ ${mod.name} CRASHED (${elapsed}ms): ${err.message}`);
      if (verbose) console.log(err.stack);
      if (mod.fatal) { halted = true; console.log("  FATAL: Halting pipeline."); }
    }
  }

  const summary = {
    timestamp: new Date().toISOString(),
    modules_run: Object.keys(results).length,
    passed: Object.values(results).filter((r) => r.status === "ok").length,
    failed: Object.values(results).filter((r) => r.status === "failed" || r.status === "crashed").length,
    skipped: Object.values(results).filter((r) => r.status === "skipped").length,
    total_errors: allErrors.length,
    total_warnings: allWarnings.length,
    results,
    errors: allErrors,
    warnings: allWarnings,
  };

  writeBuild("pipeline_summary.json", summary);

  console.log("\n" + "═".repeat(70));
  console.log(`PIPELINE ${halted ? "HALTED" : "COMPLETE"}: ${summary.passed} passed, ${summary.failed} failed, ${summary.skipped} skipped`);
  console.log(`Errors: ${allErrors.length}, Warnings: ${allWarnings.length}`);
  if (allErrors.length) { console.log("\nAll errors:"); for (const e of allErrors) console.log(`  ${e}`); }
  console.log("═".repeat(70));

  process.exit(summary.failed > 0 ? 1 : 0);
}

run();
