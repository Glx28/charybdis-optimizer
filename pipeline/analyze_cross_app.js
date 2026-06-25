const fs = require("fs");
const path = require("path");
const { readBuild, writeBuild } = require("./lib/io");

function run(config) {
  const appScores = readBuild("app_shortcut_scores.json");

  // Aggregate: which key combos appear across the most apps and at highest frequency?
  const comboMap = new Map();
  for (const app of appScores.apps) {
    for (const s of app.shortcuts) {
      const key = s.keys;
      if (!comboMap.has(key)) comboMap.set(key, { keys: key, apps: [], total_importance: 0, mapped: false, best_effort: null });
      const entry = comboMap.get(key);
      entry.apps.push({ app: app.id, action: s.action, frequency: s.frequency, importance: s.importance });
      entry.total_importance += s.importance;
      if (s.mapped) { entry.mapped = true; if (s.best_match) entry.best_effort = Math.min(entry.best_effort || 99, s.best_match.effort); }
    }
  }

  const combos = [...comboMap.values()].sort((a, b) => b.total_importance - a.total_importance);

  // Universal shortcuts (appear in 3+ apps)
  const universal = combos.filter(c => c.apps.length >= 3);
  const universalMapped = universal.filter(c => c.mapped);
  const universalUnmapped = universal.filter(c => !c.mapped);

  // App-specific shortcuts (appear in only 1 app)
  const appSpecific = combos.filter(c => c.apps.length === 1);

  // Top 30 most important shortcuts across all apps
  const top30 = combos.slice(0, 30);

  // Modifier frequency analysis
  const modFreq = {};
  for (const c of combos) {
    const parts = c.keys.split("+").filter(p => /^(Ctrl|Shift|Alt|Win)$/i.test(p));
    const modKey = parts.sort().join("+") || "none";
    modFreq[modKey] = (modFreq[modKey] || 0) + c.total_importance;
  }

  // Conflict detection: same shortcut, different actions across apps
  const conflicts = [];
  for (const [key, combo] of comboMap) {
    if (combo.apps.length < 2) continue;
    const actions = new Set(combo.apps.map(a => a.action.toLowerCase()));
    if (actions.size > 1) {
      conflicts.push({
        keys: combo.keys,
        app_count: combo.apps.length,
        actions: combo.apps.map(a => ({ app: a.app, action: a.action })),
      });
    }
  }

  const output = {
    timestamp: new Date().toISOString(),
    summary: {
      total_unique_combos: combos.length,
      universal_count: universal.length,
      universal_mapped: universalMapped.length,
      universal_unmapped: universalUnmapped.length,
      app_specific_count: appSpecific.length,
    },
    top30_most_important: top30.map(c => ({
      keys: c.keys, importance: c.total_importance, app_count: c.apps.length,
      mapped: c.mapped, best_effort: c.best_effort,
      apps: c.apps.map(a => `${a.app}:${a.frequency}`).join(", "),
    })),
    universal_unmapped: universalUnmapped.map(c => ({
      keys: c.keys, importance: c.total_importance, app_count: c.apps.length,
      apps: c.apps.map(a => `${a.app}:${a.action}`).join(", "),
    })),
    modifier_importance: Object.entries(modFreq).sort((a, b) => b[1] - a[1]).map(([mod, imp]) => ({ modifier: mod, total_importance: imp })),
    shortcut_conflicts: conflicts.slice(0, 20),
  };

  writeBuild("cross_app_analysis.json", output);
  return { success: true, output, errors: [], warnings: [] };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  const s = result.output.summary;
  console.log(`\nCross-App Analysis: ${s.total_unique_combos} unique combos, ${s.universal_count} universal (${s.universal_mapped} mapped, ${s.universal_unmapped} unmapped)\n`);

  console.log("TOP 20 MOST IMPORTANT SHORTCUTS (across all apps):");
  for (const c of result.output.top30_most_important.slice(0, 20)) {
    const status = c.mapped ? `✓ effort=${c.best_effort}` : "✗ UNMAPPED";
    console.log(`  ${c.importance.toFixed(1).padStart(5)} ${c.keys.padEnd(20)} ${c.app_count} apps  ${status}`);
  }

  if (result.output.universal_unmapped.length) {
    console.log(`\nUNIVERSAL UNMAPPED (${result.output.universal_unmapped.length}):`);
    for (const c of result.output.universal_unmapped.slice(0, 10)) {
      console.log(`  ${c.importance.toFixed(1).padStart(5)} ${c.keys.padEnd(20)} ${c.app_count} apps: ${c.apps}`);
    }
  }

  console.log("\nMODIFIER IMPORTANCE RANKING:");
  for (const m of result.output.modifier_importance.slice(0, 8)) {
    console.log(`  ${m.total_importance.toFixed(1).padStart(6)} ${m.modifier}`);
  }
}
