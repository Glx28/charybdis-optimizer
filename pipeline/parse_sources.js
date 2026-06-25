const { loadCsv } = require("./lib/csv");
const { readSource, readJson, writeBuild, ROOT, SIBLING_ZMK, sourceExists } = require("./lib/io");
const { normalizeParam, normalizeModifiers, normalizeBehavior } = require("./lib/normalize");
const { ALL_COLS, ALL_ROWS, LAYER_NAMES, hand, FINGER_MAP } = require("./lib/constants");
const path = require("path");
const fs = require("fs");
const crypto = require("crypto");

function hashContent(text) {
  return crypto.createHash("sha256").update(text).digest("hex").slice(0, 16);
}

function parseCsvSource() {
  const csvPath = "layout/keybindings_explained.csv";
  const text = readSource(csvPath);
  const rows = loadCsv(path.join(SIBLING_ZMK, csvPath));
  const layers = {};
  for (const r of rows) {
    const layer = r.layer;
    if (!layers[layer]) layers[layer] = { name: LAYER_NAMES[layer] || `Layer ${layer}`, role: r.layer_role || "", keys: {} };
    const key = `${r.x}:${r.y}`;
    layers[layer].keys[key] = {
      x: Number(r.x), y: Number(r.y),
      label: r.visual_label || "",
      behavior: normalizeBehavior(r.behavior),
      parameter: r.parameter || "",
      modifiers: normalizeModifiers(r.modifiers),
      purpose: r.purpose || "",
      usage_notes: r.usage_notes || "",
    };
  }
  return { path: csvPath, rowCount: rows.length, hash: hashContent(text), layers };
}

function parseApplySource() {
  const applyPath = "scripts/zmk-studio/apply_every_key.js";
  const text = readSource(applyPath);
  const match = text.match(/window\.CHARYBDIS_FINAL_LAYOUT\s*=\s*(\{[\s\S]*?\n\})\s*;/);
  if (!match) throw new Error("Could not extract CHARYBDIS_FINAL_LAYOUT from apply script");
  const layout = new Function(`return ${match[1]}`)();
  const keys = (layout.keys || []).map((k) => ({
    layer: Number(k.layer), x: Number(k.x), y: Number(k.y),
    behavior: normalizeBehavior(k.behavior),
    label: k.label || "",
    parameter: k.parameter || "",
    modifiers: normalizeModifiers(k.modifiers),
    rationale: k.rationale || "",
    studioSkip: !!k.studio_skip,
  }));
  return {
    path: applyPath, keyCount: keys.length,
    version: layout.version || "", hash: hashContent(text), keys,
  };
}

function parseWorkflowSources() {
  const indexPath = "apps/charybdis-coach/workflows/index.json";
  if (!sourceExists(indexPath)) return { path: indexPath, fileCount: 0, apps: {}, shortcutCount: 0 };
  const index = readJson(indexPath);
  const apps = {};
  let shortcutCount = 0;
  for (const entry of (index.apps || [])) {
    const filePath = `apps/charybdis-coach/workflows/${entry.file}`;
    if (!sourceExists(filePath)) continue;
    const data = readJson(filePath);
    const refs = [];
    for (const cat of (data.categories || [])) {
      for (const s of (cat.shortcuts || [])) {
        shortcutCount++;
        if (s.charybdis) {
          refs.push({ category: cat.name, keys: s.keys, action: s.action, charybdis: s.charybdis });
        }
      }
    }
    apps[entry.id] = { id: entry.id, name: entry.name, file: entry.file, refs };
  }
  return { path: indexPath, fileCount: Object.keys(apps).length, apps, shortcutCount };
}

function buildPhysicalGrid() {
  const positions = [];
  for (const y of ALL_ROWS) {
    for (const x of ALL_COLS) {
      if (y >= 4) {
        const thumbKeys = y === 4 ? [3,4,5,7,8] : [4,5,7];
        if (!thumbKeys.includes(x)) continue;
      }
      positions.push({
        x, y, hand: hand(x),
        zone: y >= 4 ? "thumb" : "finger",
        finger: FINGER_MAP[x] || "unknown",
        row_type: { 0: "top", 1: "upper", 2: "home", 3: "bottom", 4: "thumb", 5: "thumb2" }[y],
      });
    }
  }
  return { positions, total: positions.length };
}

function run(config) {
  const errors = [], warnings = [];
  let csv, apply, workflows;
  try { csv = parseCsvSource(); } catch (e) { errors.push(`CSV parse failed: ${e.message}`); }
  try { apply = parseApplySource(); } catch (e) { errors.push(`Apply script parse failed: ${e.message}`); }
  try { workflows = parseWorkflowSources(); } catch (e) { warnings.push(`Workflow parse failed: ${e.message}`); workflows = { path: "", fileCount: 0, apps: {}, shortcutCount: 0 }; }

  if (errors.length) return { success: false, output: null, errors, warnings };

  const output = {
    version: "1.0",
    timestamp: new Date().toISOString(),
    sources: {
      csv: { path: csv.path, rowCount: csv.rowCount, hash: csv.hash },
      apply: { path: apply.path, keyCount: apply.keyCount, version: apply.version, hash: apply.hash },
      workflows: { path: workflows.path, fileCount: workflows.fileCount, shortcutCount: workflows.shortcutCount },
    },
    physical_grid: buildPhysicalGrid(),
    layers: csv.layers,
    apply_keys: apply.keys,
    workflow_apps: workflows.apps,
  };

  writeBuild("canonical.json", output);
  return { success: true, output, errors, warnings };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  console.log(result.success ? `Parsed: ${result.output.sources.csv.rowCount} CSV rows, ${result.output.sources.apply.keyCount} apply keys, ${result.output.sources.workflows.shortcutCount} workflow shortcuts` : `FAILED: ${result.errors.join(", ")}`);
  if (result.warnings.length) console.log(`Warnings: ${result.warnings.join(", ")}`);
}
