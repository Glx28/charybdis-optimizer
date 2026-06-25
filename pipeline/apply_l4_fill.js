#!/usr/bin/env node
// Fill L4 right half with cross-app power shortcuts
const fs = require("fs");
const path = require("path");
const { parseCsv, csvSplit } = require("./lib/csv");
const { ROOT } = require("./lib/io");

const CSV_PATH = path.join(ROOT, "layout/keybindings_explained.csv");
const APPLY_PATH = path.join(ROOT, "scripts/zmk-studio/apply_every_key.js");

// L4 right half: y1 (x7-x12), y2 (x7-x12), y3 (x7-x12) = 18 slots
// L4 left: x0,y2 + x0,y3 + x3-x5,y3 = 5 more slots
// Right thumb holds L4 → LEFT hand fully free, right fingers work

const CHANGES = [
  // === RIGHT HALF y2 (HOME ROW) — most used cross-app shortcuts ===
  { layer:4, x:7, y:2, label:"Ctrl+S", param:"S", mods:"L Ctrl", action:"Save (universal)" },
  { layer:4, x:8, y:2, label:"Ctrl+N", param:"N", mods:"L Ctrl", action:"New (file/chat/tab)" },
  { layer:4, x:9, y:2, label:"Ctrl+P", param:"P", mods:"L Ctrl", action:"Print / Quick Open" },
  { layer:4, x:10, y:2, label:"Ctrl+O", param:"O", mods:"L Ctrl", action:"Open file" },
  { layer:4, x:11, y:2, label:"Ctrl+R", param:"R", mods:"L Ctrl", action:"Reply / Refresh / Run" },
  { layer:4, x:12, y:2, label:"Ctrl+W", param:"W", mods:"L Ctrl", action:"Close tab/window" },

  // === RIGHT HALF y1 (UPPER) — app navigation & Teams (57% usage) ===
  { layer:4, x:7, y:1, label:"Ctrl+E", param:"E", mods:"L Ctrl", action:"Search (Teams/Outlook/Explorer)" },
  { layer:4, x:8, y:1, label:"Ctrl+K", param:"K", mods:"L Ctrl", action:"Quick switcher / Insert link" },
  { layer:4, x:9, y:1, label:"Ctrl+G", param:"G", mods:"L Ctrl", action:"Go to (line/page/vault)" },
  { layer:4, x:10, y:1, label:"Ctrl+B", param:"B", mods:"L Ctrl", action:"Bold / Toggle sidebar" },
  { layer:4, x:11, y:1, label:"Ctrl+I", param:"I", mods:"L Ctrl", action:"Italic / Object info" },
  { layer:4, x:12, y:1, label:"Ctrl+U", param:"U", mods:"L Ctrl", action:"Underline / Upload" },

  // === RIGHT HALF y3 (BOTTOM) — Teams meetings + common combos ===
  { layer:4, x:7, y:3, label:"Mute", param:"M", mods:"L Ctrl,L Shift", action:"Teams mute toggle" },
  { layer:4, x:8, y:3, label:"Camera", param:"O", mods:"L Ctrl,L Shift", action:"Teams camera toggle" },
  { layer:4, x:9, y:3, label:"Share", param:"E", mods:"L Ctrl,L Shift", action:"Teams screen share" },
  { layer:4, x:10, y:3, label:"Hand", param:"K", mods:"L Ctrl,L Shift", action:"Teams raise hand" },
  { layer:4, x:11, y:3, label:"Hangup", param:"H", mods:"L Ctrl,L Shift", action:"Teams end call" },
  { layer:4, x:12, y:3, label:"Accept", param:"A", mods:"L Ctrl,L Shift", action:"Teams accept call" },

  // === LEFT y3 free slots — more Ctrl combos ===
  { layer:4, x:3, y:3, label:"Ctrl+D", param:"D", mods:"L Ctrl", action:"Duplicate / Delete / Bookmark" },
  { layer:4, x:4, y:3, label:"Ctrl+L", param:"L", mods:"L Ctrl", action:"Address bar / Select line" },
];

function applyToCsv() {
  const text = fs.readFileSync(CSV_PATH, "utf-8");
  const lines = text.split(/\r?\n/);
  let changed = 0;
  for (const c of CHANGES) {
    const target = `"${c.layer}",`;
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].startsWith(target)) continue;
      const fields = csvSplit(lines[i]);
      if (fields[2] === String(c.x) && fields[3] === String(c.y)) {
        const role = fields[1];
        lines[i] = `"${c.layer}","${role}","${c.x}","${c.y}","${c.label}","Key Press","${c.param}","${c.mods}","v2.3: L4 power shortcut — ${c.action}.","Sends ${c.mods.replace(/,/g,"+")}+${c.param}."`;
        changed++;
        break;
      }
    }
  }
  fs.writeFileSync(CSV_PATH, lines.join("\r\n"), "utf-8");
  return changed;
}

function applyToScript() {
  const text = fs.readFileSync(APPLY_PATH, "utf-8");
  const match = text.match(/window\.CHARYBDIS_FINAL_LAYOUT\s*=\s*(\{[\s\S]*?\n\})\s*;/);
  if (!match) throw new Error("Could not extract layout");
  const layout = new Function(`return ${match[1]}`)();
  let changed = 0;
  for (const c of CHANGES) {
    const key = layout.keys.find(k => k.layer === c.layer && k.x === c.x && k.y === c.y);
    if (!key) continue;
    key.behavior = "Key Press";
    key.label = c.label;
    key.parameter = `Keyboard ${c.param}`;
    key.modifiers = c.mods.split(",").map(m => m.trim());
    key.rationale = `v2.3: L4 power shortcut — ${c.action}.`;
    key.apply_batch = true;
    key.full_reapply_v23 = true;
    changed++;
  }
  layout.version = "v2.3-l4-power-shortcuts";
  const newJson = JSON.stringify(layout, null, 2);
  const newText = text.replace(/window\.CHARYBDIS_FINAL_LAYOUT\s*=\s*\{[\s\S]*?\n\}\s*;/, `window.CHARYBDIS_FINAL_LAYOUT = ${newJson}\n;`);
  fs.writeFileSync(APPLY_PATH, newText, "utf-8");
  return changed;
}

console.log(`Applying ${CHANGES.length} L4 power shortcuts...`);
const csvChanged = applyToCsv();
console.log(`CSV: ${csvChanged} lines updated`);
const applyChanged = applyToScript();
console.log(`Apply script: ${applyChanged} keys updated`);
