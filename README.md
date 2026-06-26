# Charybdis Optimizer

13-module Node.js analysis pipeline + Python DEAP/pyribs evolutionary optimizer for the Charybdis split keyboard layout. Evolves shortcut placement across 11 layers using a 12-factor fitness function.

## Quick Start

```powershell
# Run the analysis pipeline (Node.js, no install needed)
node pipeline/run_pipeline.js

# Run evolutionary optimization (requires Python + DEAP)
pip install -r evolve/requirements.txt
python evolve/run_evolution.py build
```

## Fresh Setup

See [charybdis-tools bootstrap](https://github.com/Glx28/charybdis-tools) for one-command setup of all repos.

For the optimizer specifically:

```powershell
pip install -r evolve/requirements.txt

# Optional: GPU acceleration (CUDA 12.1, tested on GTX 1070)
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Optional: Quality-Diversity search
pip install "pyribs[visualize]"
```

## What's Here

```
pipeline/                      # 13-module Node.js analysis pipeline
  run_pipeline.js              # Entry point (run single module: --module=score_app_shortcuts)
  parse_sources.js             # Parse canonical.json + keybindings CSV
  score_app_shortcuts.js       # Score shortcut-to-position fitness
  simulate_workflows.js        # Simulate real workflows across apps
  generate_report.js           # Generate layout change report
  lib/                         # Shared utilities (CSV, IO, constants)

evolve/                        # Python DEAP evolutionary optimizer
  run_evolution.py             # Main entry point
  config.json                  # Population size, generations, 12 fitness weights
  fitness.py                   # 12-factor fitness (effort, adjacency, violations, finger balance, ...)
  representation.py            # Layout genome encoding
  operators.py                 # Crossover/mutation operators
  export_zmk.py                # Genome -> ZMK Studio apply script
  generate_verify.py           # Generate verify script from apply script

app-keybindings/               # 18 app shortcut definition JSONs
workflows/                     # 28 workflow simulation JSONs

build/                         # Pipeline output (mostly gitignored)
  canonical.json               # Current layout snapshot (synced from zmk-config)
  app_shortcut_scores.json     # Scored shortcut corpus
  evolved_apply.js             # Paste in ZMK Studio console to apply evolved layout
  evolved_verify.js            # Paste after apply to verify all changes
  zmk_studio_behaviors.json    # Reference: all 34 ZMK Studio behaviors and their controls
  zmk_studio_enumerate_behaviors.js  # Script to re-enumerate Studio behaviors

sync_repos.ps1                 # One-command sync of layout data across all 4 repos
```

## Applying an Evolved Layout

1. Run evolution: `python evolve/run_evolution.py build`
2. Generate scripts: `cd evolve && python export_zmk.py ../build`
3. Connect keyboard via USB, open [zmk.studio](https://zmk.studio/)
4. Paste `build/evolved_apply.js` in console
5. Paste `build/evolved_verify.js` to confirm
6. Save in ZMK Studio
7. Sync all repos:
   ```powershell
   powershell -ExecutionPolicy Bypass -File sync_repos.ps1 -CommitMessage "feat: apply evolved layout" -Push
   ```

## Fitness Function

The 12-factor fitness evaluates: effort, adjacency, violations, finger balance, same-finger penalty, thumb utilization, cross-layer consistency, trackball proximity, app transition cost, learning curve, Norwegian awareness, ZMK Studio compatibility.

Configured in `evolve/config.json`. Population 5000, 5000 generations.

## Sibling Repos

| Repo | Purpose |
|------|---------|
| [charybdis-zmk-config](https://github.com/Glx28/zmk-config-charybdis-beacons) | ZMK firmware config, layout CSV (source of truth) |
| [charybdis-coach](https://github.com/Glx28/charybdis-coach) | Interactive keyboard layout coach |
| [charybdis-optimizer](https://github.com/Glx28/charybdis-optimizer) (this repo) | Analysis pipeline + evolutionary optimizer |
| [charybdis-tools](https://github.com/Glx28/charybdis-tools) | Windows AHK helpers, beacon, usage logging, bootstrap |
