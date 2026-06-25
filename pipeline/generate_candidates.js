const { readBuild, writeBuild } = require("./lib/io");
const {
  effort, hand, LEFT_COLS, RIGHT_COLS, FINGER_ROWS, THUMB_ROWS,
  LAYER_NAMES, LAYER_ACCESS, LAYER_CONTEXTS, LAYER_APP_CONTEXT,
  COACH_BEHAVIORS, STRUCTURAL_BEHAVIORS, THUMB_POSITIONS, THUMB_HAND,
  isTransparent, isNone,
} = require("./lib/constants");

const FREQ_WEIGHTS = { constant: 10, high: 6, medium: 3, low: 1, rare: 0.2 };

function isStructural(binding) {
  if (!binding) return false;
  const b = binding.behavior || "";
  if (COACH_BEHAVIORS.has(b)) return true;
  if (STRUCTURAL_BEHAVIORS.has(b)) return true;
  if (/mouse key press/i.test(b)) return true;
  if (/bluetooth|output selection|studio unlock|reset|bootloader/i.test(b)) return true;
  const p = (binding.parameter || "").toLowerCase();
  if (/spacebar|return enter/i.test(p) && (binding.modifiers || []).length === 0) return true;
  return false;
}

function isThumbAvailable(layerNum, x, y) {
  if (y < 4) return true;
  const access = LAYER_ACCESS[layerNum];
  if (!access) return true;

  if (access.key && access.key.x === x && access.key.y === y) return false;

  const isMomentary = access.method === "momentary";
  if (isMomentary && access.thumb && THUMB_HAND[x] === access.thumb) return false;

  return true;
}

function findFreeSlots(canonical) {
  const freeSlots = {};
  for (const [layerId, layerData] of Object.entries(canonical.layers)) {
    const layerNum = Number(layerId);
    const free = [];
    for (const [coord, binding] of Object.entries(layerData.keys)) {
      if (!isTransparent(binding.behavior)) continue;
      const [x, y] = coord.split(":").map(Number);
      if (!isThumbAvailable(layerNum, x, y)) continue;
      free.push({
        coord, x, y,
        effort: effort(x, y),
        hand: hand(x),
        isThumb: y >= 4,
      });
    }
    free.sort((a, b) => a.effort - b.effort);
    freeSlots[layerId] = free;
  }
  return freeSlots;
}

function assignKeysToSlots(shortcuts, slots) {
  const sortedShortcuts = [...shortcuts].sort((a, b) => b.importance - a.importance);
  const sortedSlots = [...slots].sort((a, b) => a.effort - b.effort);
  const assignments = [];
  const usedSlots = new Set();

  for (const shortcut of sortedShortcuts) {
    let bestSlot = null;
    for (const slot of sortedSlots) {
      if (usedSlots.has(slot.coord)) continue;
      bestSlot = slot;
      break;
    }
    if (!bestSlot) break;
    usedSlots.add(bestSlot.coord);
    assignments.push({
      ...bestSlot,
      shortcut,
      from: "Transparent",
      to: `Key Press: ${shortcut.keys}`,
      label: shortcut.label,
      action: shortcut.action,
    });
  }
  return assignments;
}

function getLayerRelevantShortcuts(layerNum, unmappedGaps, scores) {
  const ctx = LAYER_APP_CONTEXT[layerNum];
  if (!ctx) return [];

  const allowedAppIds = new Set(ctx.apps);

  // Collect shortcuts from allowed apps that are unmapped and high-freq
  const relevant = [];
  for (const app of scores.apps) {
    if (!allowedAppIds.has(app.id)) continue;
    for (const s of app.shortcuts) {
      if (s.mapped) continue;
      if (s.freq_weight < 3) continue;

      // For dedicated layers (L5, L9, L10), accept all shortcuts from the app
      // For shared layers (L1-L4), require multi-modifier or layer-appropriate modifiers
      const isDedicated = [5, 9, 10].includes(layerNum);
      if (!isDedicated) {
        if (layerNum === 3 && !s.keys.split("+").some(k => /^win$/i.test(k))) continue;
        if (layerNum === 1 || layerNum === 2) {
          if (s.keys.split("+").filter(k => /^(Ctrl|Shift|Alt|Win)$/i.test(k)).length < 1) continue;
        }
      }

      relevant.push({
        app: app.id, keys: s.keys, action: s.action,
        frequency: s.frequency, importance: s.importance,
        modifiers: s.keys.split("+").filter(k => /^(Ctrl|Shift|Alt|Win)$/i.test(k)).sort(),
        base_key: s.keys.split("+").pop(),
        label: s.action.split(" ").map(w => w.slice(0, 3)).join("").slice(0, 5),
        category: s.category || "general",
      });
    }
  }

  relevant.sort((a, b) => b.importance - a.importance);
  return relevant;
}

function run(config) {
  const errors = [], warnings = [];
  const canonical = readBuild("canonical.json");
  const scores = readBuild("app_shortcut_scores.json");
  const resolved = readBuild("resolved_layout.json");

  let reorgProposals = { proposals: [] };
  try { reorgProposals = readBuild("reorganize_proposals.json"); } catch (e) { /* optional */ }

  const candidates = [];
  const freeSlots = findFreeSlots(canonical);

  // Collect ALL unmapped high-frequency shortcuts for summary
  const allUnmapped = [];
  for (const app of scores.apps) {
    for (const s of app.shortcuts) {
      if (!s.mapped && s.freq_weight >= 3) {
        allUnmapped.push({
          app: app.id, keys: s.keys, action: s.action,
          frequency: s.frequency, importance: s.importance,
          modifiers: s.keys.split("+").filter(k => /^(Ctrl|Shift|Alt|Win)$/i.test(k)).sort(),
          base_key: s.keys.split("+").pop(),
          label: s.action.split(" ").map(w => w.slice(0, 3)).join("").slice(0, 5),
        });
      }
    }
  }
  allUnmapped.sort((a, b) => b.importance - a.importance);

  // Candidate A: Baseline
  candidates.push({
    id: "baseline",
    name: "Current Layout (No Changes)",
    description: "Keep the current layout unchanged. Reference point.",
    changes: [], rationale: "Baseline for comparison.",
    new_layers: [], estimated_coverage_change: "0%", risk: "none",
  });

  // Candidate B: Context-aware fill across active layers (including thumb positions)
  const activeFillLayers = [1, 2, 3, 4, 5, 9, 10];
  const allFillChanges = [];
  const layerFillDetails = [];

  for (const layerNum of activeFillLayers) {
    const layerFree = freeSlots[String(layerNum)] || [];
    if (layerFree.length === 0) continue;

    const fingerFree = layerFree.filter(s => !s.isThumb);
    const thumbFree = layerFree.filter(s => s.isThumb);

    const relevantShortcuts = getLayerRelevantShortcuts(layerNum, allUnmapped, scores);
    if (relevantShortcuts.length === 0 && fingerFree.length === 0 && thumbFree.length === 0) continue;

    // Assign to finger slots first, then thumb slots — all from same layer-appropriate pool
    const allSlots = [...fingerFree, ...thumbFree];
    const assignments = assignKeysToSlots(relevantShortcuts.slice(0, allSlots.length), allSlots);

    const fingerAssigned = assignments.filter(a => !a.isThumb).length;
    const thumbAssigned = assignments.filter(a => a.isThumb).length;

    for (const a of assignments) {
      allFillChanges.push({
        layer: layerNum,
        layer_name: LAYER_NAMES[layerNum] || `Layer ${layerNum}`,
        app_context: LAYER_APP_CONTEXT[layerNum]?.desc || "unspecified",
        ...a,
      });
    }

    if (assignments.length > 0 || thumbFree.length > 0) {
      layerFillDetails.push({
        layer: layerNum,
        name: LAYER_NAMES[layerNum],
        context: LAYER_APP_CONTEXT[layerNum]?.desc || "none",
        allowed_apps: LAYER_APP_CONTEXT[layerNum]?.apps || [],
        finger_free: fingerFree.length,
        finger_assigned: fingerAssigned,
        thumb_free: thumbFree.length,
        thumb_assigned: thumbAssigned,
        total_candidates_available: relevantShortcuts.length,
        sample_candidates: relevantShortcuts.slice(0, 5).map(s => `${s.app}:${s.keys} (${s.action})`),
      });
    }
  }

  if (allFillChanges.length) {
    const thumbChanges = allFillChanges.filter(c => c.isThumb);
    candidates.push({
      id: "fill_free_slots",
      name: `Fill ${allFillChanges.length} Free Slots (${thumbChanges.length} thumb) Across Active Layers`,
      description: `Context-aware assignment: each layer gets shortcuts only from its relevant apps. ${thumbChanges.length} thumb positions filled. Layer details below.`,
      changes: allFillChanges,
      layer_details: layerFillDetails,
      rationale: "Layer-context filtering: L5 thumbs get VS Code, L9 thumbs get M-Files, L10 thumbs get Excel, etc. Greedy assignment: highest-importance shortcuts get lowest-effort positions.",
      new_layers: [],
      estimated_coverage_change: `+${allFillChanges.length} shortcuts`,
      risk: "low — only fills transparent slots with layer-appropriate shortcuts",
    });
  }

  // Candidate C: Reorganization swaps
  if (reorgProposals.proposals && reorgProposals.proposals.length > 0) {
    const conjSwaps = reorgProposals.proposals.filter(p => p.conjunction_bonus > 0);
    candidates.push({
      id: "reorganize_existing",
      name: `Reorganize ${reorgProposals.proposals.length} Existing Keys (${conjSwaps.length} with adjacency bonus)`,
      description: `Move ${reorgProposals.proposals.length} keys to better positions. ${conjSwaps.length} swaps also improve workflow adjacency (related shortcuts closer together).`,
      changes: reorgProposals.proposals.map(p => ({
        layer: p.layer, type: p.type,
        key_a: p.key_a, key_b: p.key_b,
        effort_delta: p.effort_delta,
        conjunction_bonus: p.conjunction_bonus,
        total_score: p.total_score,
        reason: p.reason,
      })),
      rationale: "Frequency-effort optimization + conjunction scoring: most-used shortcuts get easiest positions, frequently-paired shortcuts stay near each other.",
      new_layers: [],
      estimated_coverage_change: "Same coverage, better efficiency + adjacency",
      risk: "medium — changes muscle memory for relocated keys",
    });
  }

  // Summary
  const totalFree = Object.entries(freeSlots).reduce((sum, [, slots]) => sum + slots.length, 0);
  const thumbFree = Object.entries(freeSlots).reduce((sum, [, slots]) => sum + slots.filter(s => s.isThumb).length, 0);

  const output = {
    timestamp: new Date().toISOString(),
    analysis: {
      total_unmapped_high_freq: allUnmapped.filter(g => g.importance >= 6).length,
      total_free_slots: totalFree,
      total_free_thumb_slots: thumbFree,
      free_per_layer: Object.entries(freeSlots).map(([l, slots]) => ({
        layer: Number(l), name: LAYER_NAMES[l] || `Layer ${l}`,
        free_total: slots.length,
        free_finger: slots.filter(s => !s.isThumb).length,
        free_thumb: slots.filter(s => s.isThumb).length,
        x0_free: slots.filter(s => s.x === 0).length,
        layer_context: LAYER_APP_CONTEXT[Number(l)]?.desc || "none",
      })),
      reorg_proposals: reorgProposals.proposals?.length || 0,
      layer_fill_details: layerFillDetails,
    },
    candidates,
  };

  writeBuild("candidates.json", output);
  return { success: true, output, errors, warnings };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  console.log("\n" + "═".repeat(70));
  console.log("CANDIDATE KEYMAPS GENERATED");
  console.log("═".repeat(70));

  const a = result.output.analysis;
  console.log(`\nAnalysis: ${a.total_unmapped_high_freq} unmapped high-freq, ${a.total_free_slots} free slots (${a.total_free_thumb_slots} thumb)`);
  console.log("\nFree per layer:");
  for (const l of a.free_per_layer.filter(l => l.free_total > 0)) {
    console.log(`  L${l.layer} ${l.name}: ${l.free_total} (finger: ${l.free_finger}, thumb: ${l.free_thumb}, x0: ${l.x0_free}) — ${l.layer_context}`);
  }

  if (a.layer_fill_details?.length) {
    console.log("\nLayer-context fill details:");
    for (const d of a.layer_fill_details) {
      console.log(`  L${d.layer} ${d.name}: ${d.finger_assigned}/${d.finger_free} finger + ${d.thumb_assigned}/${d.thumb_free} thumb filled`);
      console.log(`    Context: ${d.context}`);
      console.log(`    Apps: ${d.allowed_apps.join(", ")} (${d.total_candidates_available} candidates)`);
      if (d.sample_candidates.length) {
        console.log(`    Sample: ${d.sample_candidates.slice(0, 3).join(", ")}`);
      }
    }
  }

  if (a.reorg_proposals) console.log(`\nReorganization: ${a.reorg_proposals} swap proposals`);

  for (const c of result.output.candidates) {
    const thumbCount = (c.changes || []).filter(ch => ch.isThumb).length;
    const thumbNote = thumbCount > 0 ? ` (${thumbCount} thumb)` : "";
    console.log(`\n─── ${c.id}: ${c.name} ───`);
    console.log(`  Changes: ${c.changes.length}${thumbNote}, Coverage: ${c.estimated_coverage_change}, Risk: ${c.risk}`);
  }
  console.log("═".repeat(70));
}
