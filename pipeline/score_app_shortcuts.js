const fs = require("fs");
const path = require("path");
const { readBuild, writeBuild } = require("./lib/io");
const { effort, hand, LAYER_CONTEXTS } = require("./lib/constants");
const { normalizeParam, normalizeModifiers } = require("./lib/normalize");

const FREQ_WEIGHTS = { constant: 10, high: 6, medium: 3, low: 1, rare: 0.2 };

function loadAppKeybindings() {
  const dir = path.join(__dirname, "..", "app-keybindings");
  const indexPath = path.join(dir, "index.json");
  if (!fs.existsSync(indexPath)) return { apps: [], weights: FREQ_WEIGHTS };
  const index = JSON.parse(fs.readFileSync(indexPath, "utf-8"));
  const apps = [];
  for (const entry of (index.apps || [])) {
    const filePath = path.join(dir, entry.file);
    if (!fs.existsSync(filePath)) continue;
    const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    data._user_weight = entry.user_weight || 1.0;
    apps.push(data);
  }
  return { apps, weights: index.frequency_weights || FREQ_WEIGHTS };
}

function parseShortcutKeys(keys) {
  const parts = keys.split("+").map((p) => p.trim());
  const mods = [];
  let baseKey = null;
  for (const p of parts) {
    if (/^(Ctrl|Shift|Alt|Win|Meta)$/i.test(p)) mods.push(p);
    else baseKey = p;
  }
  return { modifiers: mods.sort(), base_key: baseKey };
}

function findShortcutOnLayout(shortcut, resolved, canonical) {
  const matches = [];
  const parsed = shortcut.modifiers
    ? { modifiers: shortcut.modifiers.sort(), base_key: shortcut.base_key }
    : parseShortcutKeys(shortcut.keys);

  if (!parsed.base_key || /^Click$/i.test(parsed.base_key)) return matches;

  const BASE_KEY_ALIASES = {
    "`": ["GRAVE ACCENT AND TILDE", "GRAVE"],
    "/": ["FORWARDSLASH AND QUESTIONMARK", "FORWARDSLASH"],
    "\\": ["BACKSLASH AND PIPE", "BACKSLASH"],
    ";": ["SEMICOLON AND COLON", "SEMICOLON"],
    "'": ["LEFT APOS AND DOUBLE", "APOSTROPHE"],
    ",": ["COMMA AND LESSTHAN", "COMMA"],
    ".": ["PERIOD AND GREATERTHAN", "PERIOD"],
    "-": ["DASH AND UNDERSCORE", "MINUS"],
    "=": ["EQUAL AND PLUS", "EQUAL"],
    "[": ["LEFT BRACE", "LEFT BRACKET"],
    "]": ["RIGHT BRACE", "RIGHT BRACKET"],
    "BACKSPACE": ["DELETE"],
    "ESC": ["ESCAPE"],
    "ESCAPE": ["ESCAPE"],
    "ENTER": ["RETURN ENTER", "RETURN"],
    "SPACE": ["SPACEBAR"],
    "TAB": ["TAB"],
    "HOME": ["HOME"],
    "END": ["END"],
    "PAGEUP": ["PAGEUP", "9 AND PAGEUP"],
    "PAGEDOWN": ["PAGEDOWN", "3 AND PAGEDN"],
    "DELETE": ["DELETE FORWARD"],
    "UP": ["UPARROW"], "DOWN": ["DOWNARROW"], "LEFT": ["LEFTARROW"], "RIGHT": ["RIGHTARROW"],
    "PAUSE": ["PAUSE"],
  };
  for (let i = 1; i <= 24; i++) BASE_KEY_ALIASES[`F${i}`] = [`F${i}`];
  for (let i = 0; i <= 9; i++) BASE_KEY_ALIASES[String(i)] = [`${i} AND`];
  for (const ch of "ABCDEFGHIJKLMNOPQRSTUVWXYZ") BASE_KEY_ALIASES[ch] = [ch];

  for (const ctx of LAYER_CONTEXTS) {
    const ctxData = resolved.contexts[ctx.name];
    if (!ctxData) continue;

    for (const [coord, binding] of Object.entries(ctxData.resolved)) {
      if (binding.blocked) continue;
      if (!/key press/i.test(binding.behavior)) continue;

      const paramNorm = normalizeParam(binding.parameter).toUpperCase();
      const baseNorm = parsed.base_key.toUpperCase();

      let paramMatch = false;
      if (paramNorm === baseNorm) paramMatch = true;
      else if (paramNorm.includes(baseNorm) && baseNorm.length >= 2) paramMatch = true;
      else {
        const aliases = BASE_KEY_ALIASES[baseNorm] || BASE_KEY_ALIASES[parsed.base_key] || [];
        for (const alias of aliases) {
          if (paramNorm === alias.toUpperCase() || paramNorm.includes(alias.toUpperCase())) {
            paramMatch = true;
            break;
          }
        }
      }

      if (!paramMatch) continue;

      const bindingMods = (binding.modifiers || []).map((m) => {
        if (/gui/i.test(m)) return "Win";
        if (/ctrl/i.test(m)) return "Ctrl";
        if (/shift/i.test(m)) return "Shift";
        if (/alt/i.test(m)) return "Alt";
        return m;
      }).sort();

      const shortcutMods = parsed.modifiers.map((m) => {
        if (/^win$/i.test(m)) return "Win";
        return m.charAt(0).toUpperCase() + m.slice(1).toLowerCase();
      }).sort();

      if (bindingMods.join("|") !== shortcutMods.join("|")) continue;

      const [x, y] = coord.split(":").map(Number);
      matches.push({
        context: ctx.name,
        layer_stack: ctx.stack,
        thumb_busy: ctx.thumbBusy,
        coord, x, y,
        effort: effort(x, y),
        fell_through: binding.fell_through,
        source_layer: binding.source_layer,
      });
    }
  }

  return matches;
}

function run(config) {
  const errors = [], warnings = [];
  const resolved = readBuild("resolved_layout.json");
  const canonical = readBuild("canonical.json");
  const { apps, weights } = loadAppKeybindings();

  if (apps.length === 0) {
    warnings.push("No app keybinding files found");
    const emptyOutput = { timestamp: new Date().toISOString(), summary: { total_apps: 0, total_shortcuts: 0, total_mapped: 0, total_unmapped: 0, overall_coverage_pct: 0 }, apps: [] };
    writeBuild("app_shortcut_scores.json", emptyOutput);
    return { success: true, output: emptyOutput, errors, warnings };
  }

  const appResults = [];
  let totalShortcuts = 0, totalMapped = 0, totalUnmapped = 0;

  for (const app of apps) {
    const appId = app.id;
    const userWeight = app._user_weight;
    const shortcuts = [];
    let appMapped = 0, appUnmapped = 0, appWeightedScore = 0, appWeightedMax = 0;

    for (const cat of (app.categories || [])) {
      for (const s of (cat.shortcuts || [])) {
        totalShortcuts++;
        const freq = s.frequency || "medium";
        const freqWeight = weights[freq] || 3;
        const importance = freqWeight * userWeight;

        const matches = findShortcutOnLayout(s, resolved, canonical);
        const bestMatch = matches.length
          ? matches.reduce((a, b) => a.effort < b.effort ? a : b)
          : null;

        const mapped = matches.length > 0;
        if (mapped) { appMapped++; totalMapped++; } else { appUnmapped++; totalUnmapped++; }

        const accessScore = bestMatch ? Math.max(0, 10 - bestMatch.effort) : 0;
        const weightedAccess = accessScore * importance;
        const maxPossible = 10 * importance;
        appWeightedScore += weightedAccess;
        appWeightedMax += maxPossible;

        shortcuts.push({
          keys: s.keys,
          action: s.action,
          category: cat.name,
          frequency: freq,
          freq_weight: freqWeight,
          importance,
          mapped,
          match_count: matches.length,
          best_match: bestMatch ? {
            context: bestMatch.context,
            coord: bestMatch.coord,
            effort: bestMatch.effort,
            layer: bestMatch.source_layer,
          } : null,
          access_score: accessScore,
          weighted_access: weightedAccess,
        });
      }
    }

    shortcuts.sort((a, b) => b.importance - a.importance);

    const unmappedHighFreq = shortcuts.filter((s) => !s.mapped && s.freq_weight >= 6);

    appResults.push({
      id: appId,
      name: app.name,
      user_weight: userWeight,
      total_shortcuts: shortcuts.length,
      mapped: appMapped,
      unmapped: appUnmapped,
      coverage_pct: shortcuts.length ? Math.round((appMapped / shortcuts.length) * 100) : 0,
      weighted_score: appWeightedScore,
      weighted_max: appWeightedMax,
      efficiency_pct: appWeightedMax ? Math.round((appWeightedScore / appWeightedMax) * 100) : 0,
      unmapped_high_frequency: unmappedHighFreq.map((s) => ({ keys: s.keys, action: s.action, frequency: s.frequency })),
      shortcuts,
    });
  }

  appResults.sort((a, b) => b.user_weight - a.user_weight);

  const output = {
    timestamp: new Date().toISOString(),
    summary: {
      total_apps: apps.length,
      total_shortcuts: totalShortcuts,
      total_mapped: totalMapped,
      total_unmapped: totalUnmapped,
      overall_coverage_pct: totalShortcuts ? Math.round((totalMapped / totalShortcuts) * 100) : 0,
    },
    apps: appResults,
  };

  writeBuild("app_shortcut_scores.json", output);
  return { success: true, output, errors, warnings };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  const s = result.output.summary;
  console.log(`\nApp Keybinding Corpus: ${s.total_apps} apps, ${s.total_shortcuts} shortcuts, ${s.overall_coverage_pct}% mapped to Charybdis\n`);
  for (const app of result.output.apps) {
    console.log(`  ${app.name} (weight ${app.user_weight}): ${app.mapped}/${app.total_shortcuts} mapped (${app.coverage_pct}%), efficiency ${app.efficiency_pct}%`);
    if (app.unmapped_high_frequency.length) {
      console.log(`    High-freq unmapped:`);
      for (const u of app.unmapped_high_frequency.slice(0, 5)) {
        console.log(`      ${u.keys} — ${u.action} [${u.frequency}]`);
      }
    }
  }
}
