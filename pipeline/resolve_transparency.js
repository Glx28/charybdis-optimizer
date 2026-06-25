const { readBuild, writeBuild } = require("./lib/io");
const { LAYER_CONTEXTS, isTransparent, isNone, ALL_COLS, ALL_ROWS } = require("./lib/constants");

function run(config) {
  const errors = [], warnings = [];
  const canonical = readBuild("canonical.json");
  const { layers } = canonical;

  const contexts = {};

  for (const ctx of LAYER_CONTEXTS) {
    const resolved = {};
    const noneBlocks = [];

    for (const y of ALL_ROWS) {
      for (const x of ALL_COLS) {
        if (y >= 4) {
          const thumbKeys = y === 4 ? [3,4,5,7,8] : [4,5,7];
          if (!thumbKeys.includes(x)) continue;
        }
        const coord = `${x}:${y}`;
        let found = null;
        let sourceLayer = null;
        let fellThrough = false;
        let throughLayers = [];

        for (const layerIdx of ctx.stack) {
          const layer = layers[String(layerIdx)];
          if (!layer) continue;
          const binding = layer.keys[coord];
          if (!binding) continue;

          if (isTransparent(binding.behavior)) {
            throughLayers.push(layerIdx);
            fellThrough = true;
            continue;
          }
          if (isNone(binding.behavior)) {
            found = { ...binding, blocked: true };
            sourceLayer = layerIdx;
            noneBlocks.push({ coord, context: ctx.name, layer: layerIdx, detail: `None on L${layerIdx} blocks fall-through` });
            break;
          }
          found = binding;
          sourceLayer = layerIdx;
          break;
        }

        if (found) {
          resolved[coord] = {
            source_layer: sourceLayer,
            behavior: found.behavior,
            parameter: found.parameter || "",
            label: found.label || "",
            modifiers: found.modifiers || [],
            fell_through: fellThrough,
            through_layers: throughLayers,
            blocked: !!found.blocked,
          };
        }
      }
    }

    contexts[ctx.name] = {
      stack: ctx.stack,
      thumb_busy: ctx.thumbBusy,
      resolved,
      none_blocks: noneBlocks,
    };
  }

  const output = { timestamp: new Date().toISOString(), contexts };

  writeBuild("resolved_layout.json", output);
  return { success: true, output, errors, warnings };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  const ctxNames = Object.keys(result.output.contexts);
  console.log(`Resolved ${ctxNames.length} contexts: ${ctxNames.join(", ")}`);
  for (const [name, ctx] of Object.entries(result.output.contexts)) {
    const keys = Object.keys(ctx.resolved).length;
    const ft = Object.values(ctx.resolved).filter((r) => r.fell_through).length;
    const blocks = ctx.none_blocks.length;
    console.log(`  ${name}: ${keys} keys, ${ft} fall-through, ${blocks} None blocks`);
  }
}
