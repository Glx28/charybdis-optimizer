const { readBuild, writeBuild } = require("./lib/io");
const { ROW_COMFORT, COL_EFFORT, FINGER_MAP, LAYER_NAMES, LAYER_CONTEXTS, hand, effort, LEFT_COLS, RIGHT_COLS, THUMB_ROWS } = require("./lib/constants");

function run(config) {
  const errors = [], warnings = [];
  const resolved = readBuild("resolved_layout.json");
  const graph = readBuild("layer_graph.json");

  const positionScores = {};
  const positions = [];
  for (const y of [0,1,2,3,4,5]) {
    const cols = y >= 4 ? (y === 4 ? [3,4,5,7,8] : [4,5,7]) : [...LEFT_COLS, ...RIGHT_COLS];
    for (const x of cols) {
      const e = effort(x, y);
      const pos = {
        x, y, hand: hand(x), finger: FINGER_MAP[x] || "unknown",
        row_type: { 0: "top", 1: "upper", 2: "home", 3: "bottom", 4: "thumb", 5: "thumb2" }[y],
        base_effort: e,
        is_trackball_adjacent: hand(x) === "right" && y >= 4,
      };
      positionScores[`${x}:${y}`] = pos;
      positions.push(pos);
    }
  }

  const contextScores = {};
  for (const ctx of LAYER_CONTEXTS) {
    const ctxData = resolved.contexts[ctx.name];
    if (!ctxData) continue;

    const available = [];
    const unreachable = [];
    const highEffort = [];

    for (const [coord, binding] of Object.entries(ctxData.resolved)) {
      const [x, y] = coord.split(":").map(Number);
      const pos = positionScores[coord];
      if (!pos) continue;

      let reachable = true;
      let extraPenalty = 0;

      if (ctx.thumbBusy && y >= 4) {
        const thumbHand = ctx.thumbBusy;
        const keyHand = hand(x);
        if (keyHand === thumbHand) {
          reachable = false;
          unreachable.push({ coord, label: binding.label, reason: `${thumbHand} thumb busy holding layer` });
        }
      }

      if (ctx.thumbBusy && y < 4) {
        const thumbHand = ctx.thumbBusy;
        const keyHand = hand(x);
        if (keyHand === thumbHand) {
          extraPenalty += 0.5;
        }
      }

      if (reachable) {
        const totalEffort = pos.base_effort + extraPenalty;
        available.push({ coord, label: binding.label, effort: totalEffort });
        if (totalEffort >= 6) {
          highEffort.push({ coord, label: binding.label, effort: totalEffort, behavior: binding.behavior });
        }
      }
    }

    contextScores[ctx.name] = {
      stack: ctx.stack,
      thumb_busy: ctx.thumbBusy,
      available_count: available.length,
      unreachable,
      high_effort: highEffort,
    };
  }

  const constraintViolations = [];
  const canonical = readBuild("canonical.json");
  for (const [layerId, layerData] of Object.entries(canonical.layers)) {
    for (const [coord, binding] of Object.entries(layerData.keys)) {
      const [x, y] = coord.split(":").map(Number);
      if (/reset|bootloader/i.test(binding.behavior) && y === 2) {
        constraintViolations.push({
          rule: "dangerous_not_home_row", layer: Number(layerId),
          position: coord, label: binding.label,
          severity: "error", detail: `${binding.label} on home row y2 — easy to hit accidentally`,
        });
      }
    }
  }

  const layerSummaries = {};
  for (const ctx of LAYER_CONTEXTS) {
    const sc = contextScores[ctx.name];
    if (!sc) continue;
    const efforts = sc.high_effort.length ? sc.high_effort.map((h) => h.effort) : [0];
    layerSummaries[ctx.name] = {
      available: sc.available_count,
      unreachable: sc.unreachable.length,
      avg_high_effort: efforts.reduce((a, b) => a + b, 0) / efforts.length,
    };
  }

  const output = {
    timestamp: new Date().toISOString(),
    position_scores: positionScores,
    context_scores: contextScores,
    constraint_violations: constraintViolations,
    layer_summaries: layerSummaries,
  };

  writeBuild("ergonomic_scores.json", output);
  if (constraintViolations.filter((v) => v.severity === "error").length) {
    errors.push(`${constraintViolations.filter((v) => v.severity === "error").length} hard constraint violation(s)`);
  }
  return { success: true, output, errors, warnings };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  console.log("Physical model built.");
  for (const [ctx, summary] of Object.entries(result.output.layer_summaries)) {
    console.log(`  ${ctx}: ${summary.available} available, ${summary.unreachable} unreachable`);
  }
  if (result.output.constraint_violations.length) {
    console.log("Constraint violations:");
    for (const v of result.output.constraint_violations) console.log(`  ${v.severity}: L${v.layer} ${v.position} ${v.label} — ${v.detail}`);
  }
}
