const { readBuild, writeBuild } = require("./lib/io");
const { LAYER_NAMES, COACH_BEHAVIORS, isTransparent, isNone, hand } = require("./lib/constants");

function run(config) {
  const errors = [], warnings = [];
  const canonical = readBuild("canonical.json");
  const { layers } = canonical;

  const nodes = {};
  const edges = [];
  const exitAnalysis = {};

  for (const [layerId, layerData] of Object.entries(layers)) {
    const activeKeys = Object.values(layerData.keys).filter((k) => !isTransparent(k.behavior) && !isNone(k.behavior)).length;
    nodes[layerId] = { name: LAYER_NAMES[layerId] || layerData.role, type: layerId === "0" ? "base" : "overlay", active_keys: activeKeys };
  }

  for (const [layerId, layerData] of Object.entries(layers)) {
    for (const [coord, binding] of Object.entries(layerData.keys)) {
      const [x, y] = coord.split(":").map(Number);
      const b = binding.behavior.toLowerCase();

      if (/coach_l(\d)_hold/.test(b)) {
        const targetLayer = b.match(/coach_l(\d)_hold/)[1];
        edges.push({
          from: Number(layerId), to: Number(targetLayer),
          key: { x, y }, mechanism: "momentary", behavior: binding.behavior,
          thumb_occupied: { hand: hand(x), position: coord },
          reversible: true, reverse_mechanism: "release",
        });
      }

      if (/coach_mouse_lock/.test(b)) {
        edges.push({
          from: Number(layerId), to: 2,
          key: { x, y }, mechanism: "lock", behavior: binding.behavior,
          thumb_occupied: null,
          reversible: false, exit_required: true,
        });
      }

      if (/coach_game_lock/.test(b)) {
        edges.push({
          from: Number(layerId), to: 7,
          key: { x, y }, mechanism: "lock", behavior: binding.behavior,
          thumb_occupied: null,
          reversible: false, exit_required: true,
        });
      }

      if (/coach_travel_toggle/.test(b)) {
        edges.push({
          from: Number(layerId), to: 8,
          key: { x, y }, mechanism: "toggle", behavior: binding.behavior,
          thumb_occupied: null,
          reversible: true, reverse_mechanism: "toggle_again_or_exit",
        });
      }

      if (/^toggle layer$/i.test(binding.behavior)) {
        const target = Number(String(binding.parameter).replace(/^Layer::/, "")) || 0;
        edges.push({
          from: Number(layerId), to: target,
          key: { x, y }, mechanism: "toggle", behavior: binding.behavior,
          thumb_occupied: null,
          reversible: true, reverse_mechanism: "toggle_again",
        });
      }

      if (/^momentary layer$/i.test(binding.behavior)) {
        const target = Number(String(binding.parameter).replace(/^Layer::/, "")) || 0;
        edges.push({
          from: Number(layerId), to: target,
          key: { x, y }, mechanism: "momentary", behavior: binding.behavior,
          thumb_occupied: { hand: hand(x), position: coord },
          reversible: true, reverse_mechanism: "release",
        });
      }

      if (/^to layer$/i.test(binding.behavior)) {
        const target = Number(String(binding.parameter).replace(/^Layer::/, "")) || 0;
        edges.push({
          from: Number(layerId), to: target,
          key: { x, y }, mechanism: "to_layer", behavior: binding.behavior,
          thumb_occupied: null,
          reversible: false, exit_required: target !== 0,
        });
      }
    }
  }

  for (const lockLayer of [2, 7, 8]) {
    const layerData = layers[String(lockLayer)];
    if (!layerData) continue;
    const exits = [];
    for (const [coord, binding] of Object.entries(layerData.keys)) {
      if (/coach_base|coach_travel_off/i.test(binding.behavior)) {
        exits.push({ coord, behavior: binding.behavior, label: binding.label });
      }
    }
    exitAnalysis[lockLayer] = {
      exits, count: exits.length,
      sufficient: exits.length >= 2,
    };
    if (exits.length < 2) {
      (exits.length === 0 ? errors : warnings).push(`Layer ${lockLayer} (${LAYER_NAMES[lockLayer]}) has only ${exits.length} exit(s)`);
    }
  }

  const reachableFromBase = new Set([0]);
  const queue = [0];
  while (queue.length) {
    const current = queue.shift();
    for (const edge of edges) {
      if (edge.from === current && !reachableFromBase.has(edge.to)) {
        reachableFromBase.add(edge.to);
        queue.push(edge.to);
      }
    }
  }
  const unreachable = Object.keys(layers).map(Number).filter((l) => !reachableFromBase.has(l));

  const output = {
    timestamp: new Date().toISOString(),
    nodes, edges, exit_analysis: exitAnalysis,
    reachability: {
      from_base: [...reachableFromBase].sort((a, b) => a - b),
      unreachable,
    },
  };

  writeBuild("layer_graph.json", output);
  return { success: true, output, errors, warnings };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  const { reachability, exit_analysis, edges } = result.output;
  console.log(`Layer graph: ${edges.length} edges, reachable from base: [${reachability.from_base.join(",")}], unreachable: [${reachability.unreachable.join(",")}]`);
  for (const [layer, info] of Object.entries(exit_analysis)) {
    console.log(`  L${layer} exits: ${info.count} ${info.sufficient ? "✓" : "⚠ INSUFFICIENT"}`);
  }
  if (result.warnings.length) console.log(`Warnings: ${result.warnings.join("; ")}`);
  if (result.errors.length) console.log(`ERRORS: ${result.errors.join("; ")}`);
}
