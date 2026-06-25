const fs = require("fs");
const path = require("path");
const { readBuild, writeBuild } = require("./lib/io");
const {
  effort, hand, LAYER_NAMES, LAYER_ACCESS, LAYER_CONTEXTS, LAYER_APP_CONTEXT,
  COACH_BEHAVIORS, STRUCTURAL_BEHAVIORS, THUMB_HAND, THUMB_POSITIONS,
  isTransparent, isNone,
} = require("./lib/constants");

const SKIP_LAYERS = new Set([0, 6, 7, 8]);
const MAX_SWAPS_PER_LAYER = 5;
const MIN_EFFORT_DELTA = 2;
const CONJUNCTION_BONUS = 1.5;

const KEY_GROUPS = [
  { name: "arrows", params: ["LeftArrow", "RightArrow", "UpArrow", "DownArrow"] },
  { name: "arrows_ctrl", params: ["LeftArrow", "RightArrow", "UpArrow", "DownArrow"], mods: /ctrl/i },
  { name: "page_nav", params: ["Home", "End", "PageUp", "PageDown"] },
  { name: "f_keys_low", params: ["F1", "F2", "F3", "F4", "F5", "F6"] },
  { name: "f_keys_high", params: ["F7", "F8", "F9", "F10", "F11", "F12"] },
  { name: "f_keys_ext", params: ["F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24"] },
  { name: "clipboard", params: ["C", "V", "X", "Z", "Y"], mods: /ctrl/i },
  { name: "mouse_buttons", behaviors: ["Mouse Key Press"] },
  { name: "bt_profiles", behaviors: ["Bluetooth"] },
  { name: "number_row", params: ["1 and Bang", "2 and At", "3 and Hash", "4 and Dollar", "5 and Percent"] },
  { name: "taskbar", params: ["1 and Bang", "2 and At", "3 and Hash", "4 and Dollar", "5 and Percent"], mods: /gui/i },
];

function isStructural(binding) {
  if (!binding) return false;
  const b = binding.behavior || "";
  if (COACH_BEHAVIORS.has(b)) return true;
  if (STRUCTURAL_BEHAVIORS.has(b)) return true;
  if (/mouse key press/i.test(b)) return true;
  if (/bluetooth|output selection|studio unlock|reset|bootloader/i.test(b)) return true;
  const p = (binding.parameter || "").toLowerCase();
  if (/spacebar|return enter|leftshift|rightshift|leftalt|rightalt|leftctrl|rightctrl/i.test(p)
      && (binding.modifiers || []).length === 0) return true;
  return false;
}

function getKeyGroup(binding) {
  if (!binding) return null;
  const b = binding.behavior || "";
  const p = (binding.parameter || "").toUpperCase();
  const mods = (binding.modifiers || []).join(" ");

  for (const group of KEY_GROUPS) {
    if (group.behaviors && group.behaviors.some(gb => b.toLowerCase().includes(gb.toLowerCase()))) {
      return group.name;
    }
    if (group.params) {
      const paramMatch = group.params.some(gp => p.includes(gp.toUpperCase()));
      if (paramMatch) {
        if (group.mods) {
          if (group.mods.test(mods)) return group.name;
        } else {
          return group.name;
        }
      }
    }
  }
  return null;
}

function adjacentCoords(x1, y1, x2, y2) {
  const dx = Math.abs(x1 - x2);
  const dy = Math.abs(y1 - y2);
  if (x1 <= 5 && x2 >= 7) return false;
  if (x1 >= 7 && x2 <= 5) return false;
  return dx <= 1 && dy <= 1 && (dx + dy) > 0;
}

function distance(x1, y1, x2, y2) {
  if ((x1 <= 5 && x2 >= 7) || (x1 >= 7 && x2 <= 5)) return 99;
  return Math.abs(x1 - x2) + Math.abs(y1 - y2);
}

function bindingKey(binding) {
  if (!binding) return null;
  const p = (binding.parameter || "").toUpperCase();
  const mods = (binding.modifiers || []).map(m => {
    if (/gui/i.test(m)) return "Win";
    if (/ctrl/i.test(m)) return "Ctrl";
    if (/shift/i.test(m)) return "Shift";
    if (/alt/i.test(m)) return "Alt";
    return m;
  }).sort();
  const modStr = mods.join("+");
  const base = p.split(" ")[0].replace(/^KEYBOARD\s*/i, "");
  return modStr ? `${modStr}+${base}` : base;
}

function buildConjunctionPairs(appScores) {
  const pairs = new Map();

  function addPair(k1, k2, weight) {
    if (k1 === k2) return;
    const key = [k1, k2].sort().join("|");
    pairs.set(key, (pairs.get(key) || 0) + weight);
  }

  for (const app of appScores.apps) {
    const byCategory = {};
    for (const s of app.shortcuts) {
      if (!s.mapped) continue;
      const cat = s.category || "general";
      if (!byCategory[cat]) byCategory[cat] = [];
      byCategory[cat].push(s);
    }

    for (const [, shortcuts] of Object.entries(byCategory)) {
      for (let i = 0; i < shortcuts.length; i++) {
        for (let j = i + 1; j < shortcuts.length; j++) {
          const weight = Math.min(shortcuts[i].importance, shortcuts[j].importance) * 0.3;
          addPair(shortcuts[i].keys, shortcuts[j].keys, weight);
        }
      }
    }
  }

  // Workflow-derived conjunctions: consecutive steps on the same layer
  try {
    const workflowDir = path.join(__dirname, "workflows");
    if (fs.existsSync(workflowDir)) {
      for (const file of fs.readdirSync(workflowDir).filter(f => f.endsWith(".json"))) {
        const wf = JSON.parse(fs.readFileSync(path.join(workflowDir, file), "utf-8"));
        const pressSteps = (wf.steps || []).filter(s => s.action === "press");
        for (let i = 0; i < pressSteps.length - 1; i++) {
          const a = pressSteps[i], b = pressSteps[i + 1];
          if (a.layer === b.layer) {
            const keyA = a.shortcut_keys || a.desc;
            const keyB = b.shortcut_keys || b.desc;
            if (keyA && keyB) addPair(keyA, keyB, (wf.weight || 0.5) * 5);
          }
        }
      }
    }
  } catch (e) { /* workflows optional */ }

  return pairs;
}

function lookupImportance(binding, appScores) {
  if (!binding || isTransparent(binding.behavior) || isNone(binding.behavior)) return 0;
  if (isStructural(binding)) return Infinity;

  const param = (binding.parameter || "").toUpperCase();
  const mods = (binding.modifiers || []).map(m => {
    if (/gui/i.test(m)) return "Win";
    if (/ctrl/i.test(m)) return "Ctrl";
    if (/shift/i.test(m)) return "Shift";
    if (/alt/i.test(m)) return "Alt";
    return m;
  }).sort();
  const modStr = mods.join("+");

  let bestImportance = 0;
  for (const app of appScores.apps) {
    for (const s of app.shortcuts) {
      if (!s.mapped) continue;
      const sMods = s.keys.split("+").filter(k => /^(Ctrl|Shift|Alt|Win)$/i.test(k)).sort().join("+");
      const sBase = s.keys.split("+").pop().toUpperCase();
      if (sMods === modStr && param.includes(sBase)) {
        bestImportance = Math.max(bestImportance, s.importance);
      }
    }
  }

  if (bestImportance === 0) bestImportance = 1;
  return bestImportance;
}

function countDuplicatesOnLayer(binding, layerKeys) {
  if (!binding || isTransparent(binding.behavior)) return 0;
  const p = (binding.parameter || "").toUpperCase();
  const b = (binding.behavior || "").toLowerCase();
  const mods = (binding.modifiers || []).sort().join(",");
  let count = 0;
  for (const [, other] of Object.entries(layerKeys)) {
    if (isTransparent(other.behavior)) continue;
    const op = (other.parameter || "").toUpperCase();
    const ob = (other.behavior || "").toLowerCase();
    const om = (other.modifiers || []).sort().join(",");
    if (b === ob && p === op && mods === om) count++;
  }
  return count - 1;
}

function conjunctionNeighborScore(key, targetX, targetY, layerKeys, conjunctionPairs) {
  const keyStr = bindingKey(key);
  if (!keyStr) return 0;

  let score = 0;
  for (const [coord, binding] of Object.entries(layerKeys)) {
    if (isTransparent(binding.behavior) || isNone(binding.behavior)) continue;
    const neighborStr = bindingKey(binding);
    if (!neighborStr) continue;

    const pairKey = [keyStr, neighborStr].sort().join("|");
    const pairWeight = conjunctionPairs.get(pairKey);
    if (!pairWeight) continue;

    const [nx, ny] = coord.split(":").map(Number);
    const dist = distance(targetX, targetY, nx, ny);
    if (dist <= 2) {
      score += pairWeight / Math.max(dist, 1);
    }
  }
  return score;
}

function run(config) {
  const errors = [], warnings = [];
  const canonical = readBuild("canonical.json");
  const appScores = readBuild("app_shortcut_scores.json");
  const conjunctionPairs = buildConjunctionPairs(appScores);
  const proposals = [];

  for (const [layerId, layerData] of Object.entries(canonical.layers)) {
    const layerNum = Number(layerId);
    if (SKIP_LAYERS.has(layerNum)) continue;

    const access = LAYER_ACCESS[layerNum];
    const isMomentary = access?.method === "momentary";
    const busyThumb = isMomentary ? access?.thumb : null;

    const keys = [];
    const allGroupMembers = new Map();

    for (const [coord, binding] of Object.entries(layerData.keys)) {
      const [x, y] = coord.split(":").map(Number);
      if (y >= 4 && busyThumb && THUMB_HAND[x] === busyThumb) continue;
      if (isTransparent(binding.behavior) || isNone(binding.behavior)) continue;
      if (isStructural(binding)) continue;

      const importance = lookupImportance(binding, appScores);
      if (importance === Infinity) continue;

      const group = getKeyGroup(binding);
      const dupes = countDuplicatesOnLayer(binding, layerData.keys);

      const entry = {
        coord, x, y, effort: effort(x, y),
        label: binding.label || binding.parameter || "?",
        behavior: binding.behavior,
        parameter: binding.parameter,
        modifiers: binding.modifiers,
        importance,
        group,
        duplicates: dupes,
      };

      if (group) {
        if (!allGroupMembers.has(group)) allGroupMembers.set(group, []);
        allGroupMembers.get(group).push(entry);
      }

      keys.push(entry);
    }

    if (keys.length < 2) continue;

    // Build protected group coords (flood-fill cluster detection)
    const protectedGroupCoords = new Set();
    for (const [, members] of allGroupMembers) {
      if (members.length < 2) continue;
      const visited = new Set();
      for (let i = 0; i < members.length; i++) {
        if (visited.has(i)) continue;
        const cluster = [i];
        visited.add(i);
        let changed = true;
        while (changed) {
          changed = false;
          for (let j = 0; j < members.length; j++) {
            if (visited.has(j)) continue;
            for (const ci of cluster) {
              if (adjacentCoords(members[ci].x, members[ci].y, members[j].x, members[j].y)) {
                cluster.push(j);
                visited.add(j);
                changed = true;
                break;
              }
            }
          }
        }
        if (cluster.length >= 2) {
          for (const ci of cluster) protectedGroupCoords.add(members[ci].coord);
        }
      }
    }

    for (const key of keys) {
      key.adjustedImportance = key.importance;
      if (key.duplicates > 0) {
        key.adjustedImportance *= 0.7;
      }
      if (protectedGroupCoords.has(key.coord)) {
        key.protected = true;
      }
    }

    const movableKeys = keys.filter(k => !k.protected);
    movableKeys.sort((a, b) => b.adjustedImportance - a.adjustedImportance);

    let layerSwaps = 0;
    const movedCoords = new Set();

    for (const key of movableKeys) {
      if (layerSwaps >= MAX_SWAPS_PER_LAYER) break;
      if (movedCoords.has(key.coord)) continue;

      let bestTarget = null;
      let bestScore = 0;

      for (const other of keys) {
        if (other.coord === key.coord) continue;
        if (movedCoords.has(other.coord)) continue;
        if (other.protected) continue;

        const effortDelta = key.effort - other.effort;
        if (effortDelta < MIN_EFFORT_DELTA) continue;
        if (key.adjustedImportance <= other.adjustedImportance) continue;

        const conjBonus = conjunctionNeighborScore(key, other.x, other.y, layerData.keys, conjunctionPairs) * CONJUNCTION_BONUS;
        const score = effortDelta + conjBonus;

        if (score > bestScore) {
          bestScore = score;
          bestTarget = { ...other, conjBonus };
        }
      }

      // Also check transparent positions (including thumb slots)
      for (const [coord, binding] of Object.entries(layerData.keys)) {
        if (movedCoords.has(coord)) continue;
        if (!isTransparent(binding.behavior)) continue;
        const [x, y] = coord.split(":").map(Number);
        if (y >= 4 && busyThumb && THUMB_HAND[x] === busyThumb) continue;
        const e = effort(x, y);
        const effortDelta = key.effort - e;
        if (effortDelta < MIN_EFFORT_DELTA) continue;

        const conjBonus = conjunctionNeighborScore(key, x, y, layerData.keys, conjunctionPairs) * CONJUNCTION_BONUS;
        const score = effortDelta + conjBonus;

        if (score > bestScore) {
          bestScore = score;
          bestTarget = { coord, x, y, effort: e, label: "(transparent)", importance: 0, adjustedImportance: 0, conjBonus };
        }
      }

      if (bestTarget && bestScore >= MIN_EFFORT_DELTA) {
        const conjNote = bestTarget.conjBonus > 0 ? ` +conj ${bestTarget.conjBonus.toFixed(1)}` : "";
        proposals.push({
          layer: layerNum,
          layer_name: LAYER_NAMES[layerNum] || `Layer ${layerNum}`,
          type: isTransparent((layerData.keys[bestTarget.coord] || {}).behavior) ? "move_to_empty" : "swap",
          key_a: { coord: key.coord, x: key.x, y: key.y, label: key.label, importance: key.adjustedImportance, effort: key.effort },
          key_b: { coord: bestTarget.coord, x: bestTarget.x, y: bestTarget.y, label: bestTarget.label, importance: bestTarget.adjustedImportance || 0, effort: bestTarget.effort },
          effort_delta: key.effort - bestTarget.effort,
          conjunction_bonus: bestTarget.conjBonus || 0,
          total_score: bestScore,
          reason: `${key.label} (imp ${key.adjustedImportance.toFixed(1)}) effort ${key.effort}→${bestTarget.effort} (save ${key.effort - bestTarget.effort}${conjNote})`,
        });
        movedCoords.add(key.coord);
        movedCoords.add(bestTarget.coord);
        layerSwaps++;
      }
    }
  }

  proposals.sort((a, b) => b.total_score - a.total_score);

  const output = {
    timestamp: new Date().toISOString(),
    total_proposals: proposals.length,
    conjunction_pairs_count: conjunctionPairs.size,
    proposals,
  };

  writeBuild("reorganize_proposals.json", output);

  return {
    success: true,
    output: { summary: `${proposals.length} swap proposals (${conjunctionPairs.size} conjunction pairs)` },
    errors, warnings,
  };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  const p = JSON.parse(require("fs").readFileSync("scripts/keymap-optimizer/build/reorganize_proposals.json", "utf8"));
  console.log(`\nReorganize: ${p.total_proposals} proposals (${p.conjunction_pairs_count} conjunction pairs)\n`);
  for (const prop of p.proposals) {
    const conj = prop.conjunction_bonus > 0 ? ` [conj +${prop.conjunction_bonus.toFixed(1)}]` : "";
    console.log(`  L${prop.layer} ${prop.type}: ${prop.reason}${conj}`);
  }
}
