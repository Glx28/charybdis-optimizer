#!/usr/bin/env node
// Applies candidate keymaps to CSV and apply_every_key.js
const fs = require("fs");
const path = require("path");
const { parseCsv, csvSplit } = require("./lib/csv");
const { SIBLING_ZMK } = require("./lib/io");

const CSV_PATH = path.join(SIBLING_ZMK, "layout/keybindings_explained.csv");
const APPLY_PATH = path.join(SIBLING_ZMK, "scripts/zmk-studio/apply_every_key.js");

// ═══════════════════════════════════════════════════
// ALL CANDIDATE CHANGES
// ═══════════════════════════════════════════════════

const CHANGES = [];

// --- L1 x0,y1: game_lock → Code layer toggle ---
CHANGES.push({
  layer: 1, x: 0, y: 1,
  csv: { visual_label: "Code", behavior: "Toggle Layer", parameter: "Layer::5", purpose: "v2.2: Toggle Code/IDE layer (Layer 5). Replaces duplicate game lock (game lock remains on L3 x12,y2).", usage_notes: "Hold Nav + tap to toggle Code layer on/off." },
  apply: { behavior: "Toggle Layer", label: "Code", parameter: "5", rationale: "v2.2: Toggle Code/IDE layer. Game lock still on L3 x12,y2.", full_reapply_v22: true },
});

// --- L4 x2,y3: free slot → M-Files layer toggle ---
CHANGES.push({
  layer: 4, x: 2, y: 3,
  csv: { visual_label: "DMS", behavior: "Toggle Layer", parameter: "Layer::9", purpose: "v2.2: Toggle M-Files/DMS layer (Layer 9). Uses freed F-key slot.", usage_notes: "Hold System + tap to toggle M-Files layer on/off." },
  apply: { behavior: "Toggle Layer", label: "DMS", parameter: "9", rationale: "v2.2: Toggle M-Files/DMS layer.", full_reapply_v22: true },
});

// --- L3 y0: Fill top row with window extras (10 keys, x0 stays transparent) ---
const L3_Y0 = [
  { x: 1, label: "TskMg", keys: "Ctrl+Shift+Esc", action: "Task Manager", param: "Escape", mods: "L Ctrl,L Shift" },
  { x: 2, label: "Emoji", keys: "Win+.", action: "Emoji picker", param: "Period and GreaterThan", mods: "L GUI" },
  { x: 3, label: "Proj", keys: "Win+P", action: "Project / display", param: "P", mods: "L GUI" },
  { x: 4, label: "QSett", keys: "Win+A", action: "Quick Settings", param: "A", mods: "L GUI" },
  { x: 5, label: "Notif", keys: "Win+N", action: "Notifications", param: "N", mods: "L GUI" },
  { x: 7, label: "TskCy", keys: "Win+T", action: "Cycle taskbar", param: "T", mods: "L GUI" },
  { x: 8, label: "SysTr", keys: "Win+B", action: "System tray", param: "B", mods: "L GUI" },
  { x: 9, label: "Cast", keys: "Win+K", action: "Connect / Cast", param: "K", mods: "L GUI" },
  { x: 10, label: "Acces", keys: "Win+U", action: "Accessibility", param: "U", mods: "L GUI" },
  { x: 11, label: "Emoji", keys: "Win+;", action: "Emoji picker (alt)", param: "SemiColon and Colon", mods: "L GUI" },
];
for (const k of L3_Y0) {
  CHANGES.push({
    layer: 3, x: k.x, y: 0,
    csv: { visual_label: k.label, behavior: "Key Press", parameter: k.param, modifiers: k.mods, purpose: `v2.2: ${k.keys} — ${k.action}. Fills empty L3 y0.`, usage_notes: `Sends ${k.mods.replace(/,/g,"+")}+${k.param}.` },
    apply: { behavior: "Key Press", label: k.label, parameter: `Keyboard ${k.param}`, modifiers: k.mods.split(",").map(m=>m.trim()), rationale: `v2.2: ${k.keys} ${k.action} — fills L3 y0.`, full_reapply_v22: true },
  });
}

// --- Layer 5: Code/IDE layer (44 keys + 4 exits) ---
const L5_KEYS = [
  // y2 HOME — most used
  { x:1,y:2, label:"Save", param:"S", mods:"L Ctrl", action:"Save" },
  { x:2,y:2, label:"SelNx", param:"D", mods:"L Ctrl", action:"Select next occurrence" },
  { x:3,y:2, label:"Cmnt", param:"ForwardSlash and QuestionMark", mods:"L Ctrl", action:"Toggle comment" },
  { x:4,y:2, label:"DelLn", param:"K", mods:"L Ctrl,L Shift", action:"Delete line" },
  { x:5,y:2, label:"Term", param:"Grave Accent and Tilde", mods:"L Ctrl", action:"Toggle terminal" },
  { x:7,y:2, label:"Open", param:"P", mods:"L Ctrl", action:"Quick open file" },
  { x:8,y:2, label:"CmdP", param:"P", mods:"L Ctrl,L Shift", action:"Command palette" },
  { x:9,y:2, label:"GoLn", param:"G", mods:"L Ctrl", action:"Go to line" },
  { x:10,y:2, label:"GoSym", param:"O", mods:"L Ctrl,L Shift", action:"Go to symbol" },
  { x:11,y:2, label:"SrchF", param:"F", mods:"L Ctrl,L Shift", action:"Search across files" },
  { x:12,y:2, label:"Git", param:"G", mods:"L Ctrl,L Shift", action:"Source control" },
  // y1 UPPER — editing
  { x:1,y:1, label:"LnUp", param:"UpArrow", mods:"L Alt", action:"Move line up" },
  { x:2,y:1, label:"LnDn", param:"DownArrow", mods:"L Alt", action:"Move line down" },
  { x:3,y:1, label:"CpDn", param:"DownArrow", mods:"L Shift,L Alt", action:"Copy line down" },
  { x:4,y:1, label:"InsLn", param:"Return Enter", mods:"L Ctrl", action:"Insert line below" },
  { x:5,y:1, label:"InsUp", param:"Return Enter", mods:"L Ctrl,L Shift", action:"Insert line above" },
  { x:7,y:1, label:"Outd", param:"Left Brace", mods:"L Ctrl", action:"Outdent" },
  { x:8,y:1, label:"Ind", param:"Right Brace", mods:"L Ctrl", action:"Indent" },
  { x:9,y:1, label:"Brkt", param:"Backslash and Pipe", mods:"L Ctrl,L Shift", action:"Jump to bracket" },
  { x:10,y:1, label:"SelAl", param:"L", mods:"L Ctrl,L Shift", action:"Select all occurrences" },
  { x:11,y:1, label:"Peek", param:"F12", mods:"L Alt", action:"Peek definition" },
  { x:12,y:1, label:"Probs", param:"M", mods:"L Ctrl,L Shift", action:"Problems panel" },
  // y3 BOTTOM — panels, formatting, multi-cursor
  { x:1,y:3, label:"PstNF", param:"V", mods:"L Ctrl,L Shift", action:"Paste no formatting" },
  { x:2,y:3, label:"BlkCm", param:"A", mods:"L Shift,L Alt", action:"Block comment" },
  { x:3,y:3, label:"Explr", param:"E", mods:"L Ctrl,L Shift", action:"Explorer panel" },
  { x:4,y:3, label:"Ext", param:"X", mods:"L Ctrl,L Shift", action:"Extensions panel" },
  { x:5,y:3, label:"Side", param:"B", mods:"L Ctrl", action:"Toggle sidebar" },
  { x:7,y:3, label:"Panel", param:"J", mods:"L Ctrl", action:"Toggle bottom panel" },
  { x:8,y:3, label:"Split", param:"Backslash and Pipe", mods:"L Ctrl", action:"Split editor" },
  { x:9,y:3, label:"SelLn", param:"L", mods:"L Ctrl", action:"Select line" },
  { x:10,y:3, label:"RplFl", param:"H", mods:"L Ctrl,L Shift", action:"Replace in files" },
  { x:11,y:3, label:"NxtPr", param:"F8", mods:"", action:"Next problem" },
  { x:12,y:3, label:"PrvPr", param:"F8", mods:"L Shift", action:"Prev problem" },
  // y0 TOP — debug, less frequent
  { x:1,y:0, label:"Debug", param:"F5", mods:"", action:"Start/continue debug" },
  { x:2,y:0, label:"Stop", param:"F5", mods:"L Shift", action:"Stop debugging" },
  { x:3,y:0, label:"StpOv", param:"F10", mods:"", action:"Step over" },
  { x:4,y:0, label:"StpIn", param:"F11", mods:"", action:"Step into" },
  { x:5,y:0, label:"StpOt", param:"F11", mods:"L Shift", action:"Step out" },
  { x:7,y:0, label:"BkPt", param:"F9", mods:"", action:"Toggle breakpoint" },
  { x:8,y:0, label:"Rstr", param:"F5", mods:"L Ctrl,L Shift", action:"Restart debug" },
  { x:9,y:0, label:"Sett", param:"Comma and LessThan", mods:"L Ctrl", action:"Settings" },
  { x:10,y:0, label:"NTerm", param:"Grave Accent and Tilde", mods:"L Ctrl,L Shift", action:"New terminal" },
  { x:11,y:0, label:"NewFl", param:"N", mods:"L Ctrl", action:"New file" },
  { x:12,y:0, label:"Fmt", param:"F", mods:"L Ctrl,L Shift", action:"Format document" },
];
for (const k of L5_KEYS) {
  const modsArr = k.mods ? k.mods.split(",").map(m => m.trim()) : [];
  CHANGES.push({
    layer: 5, x: k.x, y: k.y,
    csv: { visual_label: k.label, behavior: k.mods ? "Key Press" : "Key Press", parameter: k.param, modifiers: k.mods, purpose: `v2.2: Code/IDE — ${k.action}.`, usage_notes: `Sends ${k.mods ? k.mods.replace(/,/g,"+")+"+" : ""}${k.param}.` },
    apply: { behavior: "Key Press", label: k.label, parameter: `Keyboard ${k.param}`, modifiers: modsArr.length ? modsArr : undefined, rationale: `v2.2: Code/IDE layer — ${k.action}.`, full_reapply_v22: true },
  });
}
// L5 exits
for (const pos of [{x:3,y:4},{x:5,y:4},{x:7,y:4},{x:8,y:4}]) {
  CHANGES.push({
    layer: 5, x: pos.x, y: pos.y,
    csv: { visual_label: "Base", behavior: "coach_base", parameter: "", purpose: "Exit Code layer to base.", usage_notes: "Coach beacon: exit to base (Ctrl+Alt+Shift+F22)." },
    apply: { behavior: "coach_base", label: "Base", rationale: "v2.2: Exit Code/IDE layer to base.", full_reapply_v22: true },
  });
}

// --- Layer 9: M-Files/DMS layer (22 keys + 4 exits) ---
const L9_KEYS = [
  // y2 HOME — core doc ops
  { x:1,y:2, label:"ChkOt", param:"E", mods:"L Ctrl", action:"Check out" },
  { x:2,y:2, label:"ChkIn", param:"E", mods:"L Ctrl,L Shift", action:"Check in" },
  { x:3,y:2, label:"Save", param:"S", mods:"L Ctrl", action:"Save" },
  { x:4,y:2, label:"New", param:"N", mods:"L Ctrl", action:"New object" },
  { x:5,y:2, label:"Open", param:"O", mods:"L Ctrl", action:"Open document" },
  { x:7,y:2, label:"Props", param:"Return Enter", mods:"L Alt", action:"Properties / metadata" },
  { x:8,y:2, label:"CpLnk", param:"C", mods:"L Ctrl,L Shift", action:"Copy object link" },
  { x:9,y:2, label:"Info", param:"I", mods:"L Ctrl", action:"Object info" },
  { x:10,y:2, label:"Hist", param:"H", mods:"L Ctrl,L Shift", action:"Version history" },
  { x:11,y:2, label:"Rel", param:"K", mods:"L Ctrl", action:"Add relationship" },
  { x:12,y:2, label:"UndCO", param:"U", mods:"L Ctrl,L Shift", action:"Undo checkout" },
  // y1 UPPER — workflow, search
  { x:1,y:1, label:"WfSt", param:"W", mods:"L Ctrl,L Shift", action:"Change workflow state" },
  { x:2,y:1, label:"Asgn", param:"A", mods:"L Ctrl,L Shift", action:"Assign to user" },
  { x:3,y:1, label:"ASrch", param:"F", mods:"L Ctrl,L Shift", action:"Advanced search" },
  { x:4,y:1, label:"Fav", param:"M", mods:"L Ctrl", action:"Add to favorites" },
  { x:5,y:1, label:"DLoad", param:"D", mods:"L Ctrl,L Shift", action:"Download copy" },
  { x:7,y:1, label:"Print", param:"P", mods:"L Ctrl", action:"Print" },
  { x:8,y:1, label:"Vault", param:"G", mods:"L Ctrl", action:"Go to vault" },
  // y3 BOTTOM — views
  { x:1,y:3, label:"List", param:"1 and Bang", mods:"L Ctrl", action:"List view" },
  { x:2,y:3, label:"Icon", param:"2 and At", mods:"L Ctrl", action:"Icon view" },
  { x:3,y:3, label:"Group", param:"G", mods:"L Ctrl,L Shift", action:"Group by" },
  { x:4,y:3, label:"Notif", param:"F5", mods:"L Ctrl,L Shift", action:"Send notification" },
];
for (const k of L9_KEYS) {
  const modsArr = k.mods ? k.mods.split(",").map(m => m.trim()) : [];
  CHANGES.push({
    layer: 9, x: k.x, y: k.y,
    csv: { visual_label: k.label, behavior: "Key Press", parameter: k.param, modifiers: k.mods, purpose: `v2.2: M-Files — ${k.action}.`, usage_notes: `Sends ${k.mods.replace(/,/g,"+")}+${k.param}.` },
    apply: { behavior: "Key Press", label: k.label, parameter: `Keyboard ${k.param}`, modifiers: modsArr, rationale: `v2.2: M-Files/DMS layer — ${k.action}.`, full_reapply_v22: true },
  });
}
// L9 exits
for (const pos of [{x:3,y:4},{x:5,y:4},{x:7,y:4},{x:8,y:4}]) {
  CHANGES.push({
    layer: 9, x: pos.x, y: pos.y,
    csv: { visual_label: "Base", behavior: "coach_base", parameter: "", purpose: "Exit M-Files layer to base.", usage_notes: "Coach beacon: exit to base (Ctrl+Alt+Shift+F22)." },
    apply: { behavior: "coach_base", label: "Base", rationale: "v2.2: Exit M-Files/DMS layer to base.", full_reapply_v22: true },
  });
}

// ═══════════════════════════════════════════════════
// APPLY TO CSV
// ═══════════════════════════════════════════════════
function applyToCsv() {
  const text = fs.readFileSync(CSV_PATH, "utf-8");
  const lines = text.split(/\r?\n/);
  const header = lines[0];
  let changed = 0;

  for (const change of CHANGES) {
    const target = `"${change.layer}",`;
    const coordMatch = `"${change.x}","${change.y}"`;
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].startsWith(target)) continue;
      const fields = csvSplit(lines[i]);
      if (fields[2] === String(change.x) && fields[3] === String(change.y)) {
        const c = change.csv;
        const layerRole = fields[1];
        const newLine = `"${change.layer}","${layerRole}","${change.x}","${change.y}","${c.visual_label}","${c.behavior}","${c.parameter || ""}","${c.modifiers || ""}","${c.purpose}","${c.usage_notes}"`;
        lines[i] = newLine;
        changed++;
        break;
      }
    }
  }

  // Update layer roles for L5 and L9
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].startsWith('"5",')) {
      lines[i] = lines[i].replace(/"Reserved[^"]*"/, '"Code/IDE layer (VS Code shortcuts)"');
    }
    if (lines[i].startsWith('"9",')) {
      lines[i] = lines[i].replace(/"Reserved[^"]*"/, '"M-Files/DMS document management"');
    }
  }

  fs.writeFileSync(CSV_PATH, lines.join("\r\n"), "utf-8");
  return changed;
}

// ═══════════════════════════════════════════════════
// APPLY TO APPLY_EVERY_KEY.JS
// ═══════════════════════════════════════════════════
function applyToScript() {
  const text = fs.readFileSync(APPLY_PATH, "utf-8");
  const match = text.match(/window\.CHARYBDIS_FINAL_LAYOUT\s*=\s*(\{[\s\S]*?\n\})\s*;/);
  if (!match) throw new Error("Could not extract layout from apply script");
  const layout = new Function(`return ${match[1]}`)();
  let changed = 0;

  for (const change of CHANGES) {
    const key = layout.keys.find(k => k.layer === change.layer && k.x === change.x && k.y === change.y);
    if (!key) { console.warn(`Key not found: L${change.layer} x${change.x} y${change.y}`); continue; }
    const a = change.apply;
    key.behavior = a.behavior;
    key.label = a.label;
    if (a.parameter !== undefined) key.parameter = a.parameter;
    else delete key.parameter;
    if (a.modifiers && a.modifiers.length) key.modifiers = a.modifiers;
    else delete key.modifiers;
    key.rationale = a.rationale;
    key.apply_batch = true;
    if (a.full_reapply_v22) key.full_reapply_v22 = true;
    changed++;
  }

  // Update version
  layout.version = "v2.2-code-mfiles-layers";
  layout.policy = layout.policy.replace(/v2\.\d[^.]*\./, "v2.2.") +
    " v2.2 adds Code/IDE layer (L5, 44 shortcuts), M-Files/DMS layer (L9, 22 shortcuts), and fills L3 y0 with window extras.";

  const newJson = JSON.stringify(layout, null, 2);
  const newText = text.replace(/window\.CHARYBDIS_FINAL_LAYOUT\s*=\s*\{[\s\S]*?\n\}\s*;/, `window.CHARYBDIS_FINAL_LAYOUT = ${newJson}\n;`);
  fs.writeFileSync(APPLY_PATH, newText, "utf-8");
  return changed;
}

// ═══════════════════════════════════════════════════
// RUN
// ═══════════════════════════════════════════════════
console.log(`Applying ${CHANGES.length} changes...`);
const csvChanged = applyToCsv();
console.log(`CSV: ${csvChanged} lines updated`);
const applyChanged = applyToScript();
console.log(`Apply script: ${applyChanged} keys updated`);
console.log(`\nTotal: ${CHANGES.length} candidate changes applied.`);
console.log("Changes by layer:");
const byLayer = {};
for (const c of CHANGES) { byLayer[c.layer] = (byLayer[c.layer] || 0) + 1; }
for (const [l, n] of Object.entries(byLayer).sort((a,b) => a[0]-b[0])) {
  console.log(`  L${l}: ${n} keys`);
}
