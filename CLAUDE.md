# Charybdis Optimizer — Layout Evolution Pipeline

13-module Node.js analysis pipeline + Python DEAP/pyribs evolutionary optimizer for the Charybdis split keyboard layout.

## Quick Start

```bash
# Run the full analysis pipeline
node pipeline/run_pipeline.js

# Run evolutionary optimization (requires Python + DEAP)
python evolve/run_evolution.py build

# Install Python deps
pip install -r evolve/requirements.txt
# Optional GPU acceleration (GTX 1070)
pip install torch --index-url https://download.pytorch.org/whl/cu121
# Optional Quality-Diversity
pip install "pyribs[visualize]"
```

## Structure

- `pipeline/` — 13-module Node.js pipeline (analysis, scoring, candidate generation, reporting)
  - `run_pipeline.js` — entry point
  - `lib/` — shared utilities (CSV parsing, IO, constants)
- `evolve/` — Python DEAP evolutionary optimizer
  - `config.json` — population size, generations, 12 fitness weights
  - `fitness.py` — 12-factor fitness function (effort, adjacency, violations, finger balance, etc.)
  - `representation.py` — layout genome encoding
  - `operators.py` — crossover/mutation operators
  - `run_evolution.py` — main entry point
- `app-keybindings/` — 18 app shortcut definition JSONs (browser, teams, vscode, excel, etc.)
- `workflows/` — 28 workflow simulation JSONs
- `build/` — pipeline output (mostly gitignored)
  - `canonical.json` — current layout snapshot (pipeline input)
  - `app_shortcut_scores.json` — scored shortcut corpus

## Input Data

- `build/canonical.json` comes from ZMK Studio export: `../charybdis-zmk-config/config/charybdis.json`
- `build/usage_stats.json` comes from AHK usage tracker: `../charybdis-tools/runtime/shortcut_usage.jsonl`

The pipeline's `aggregate_usage.js` module reads the usage JSONL. Pass `--runtime-path` to override the default path.

## Config

`evolve/config.json` controls: `pop_size`, `n_generations`, and 12 fitness weights. The fitness function in `fitness.py` evaluates: effort, adjacency, violations, finger balance, same-finger penalty, thumb utilization, cross-layer consistency, trackball proximity, app transition, learning curve, Norwegian awareness, ZMK Studio compatibility.

## Key Constraints

- Multi-app shortcuts: a shortcut used by 3+ apps gets scored once per app (not averaged away)
- Layer context: fitness respects which layer a key lives on
- GPU/CPU alignment: PyTorch batch fitness must match CPU single-eval results exactly

## Sibling Repos

All repos live in the same parent directory.
- `../charybdis-zmk-config` — ZMK firmware config, keymap, layout CSV, ZMK Studio scripts
- `../charybdis-coach` — Browser-based interactive keyboard layout coach
- `../charybdis-tools` — Windows AHK helper, trackball benchmarks, PowerShell scripts, runtime logs
