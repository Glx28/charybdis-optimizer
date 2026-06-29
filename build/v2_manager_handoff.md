# CLAUDE MANAGER HANDOFF — Start v2 Runs

## TL;DR

Run 13 died at gen 0. v2 is built, tested, and ready. **Run it now.**

```bash
cd charybdis-optimizer-v2
py run_evolution.py ../build
```

---

## Current State

| What | Status | Location |
|------|--------|----------|
| v1 Run 13 | DEAD at gen 0 | `build/evolution_scratch_checkpoint.npz` (seed only) |
| v1 code | Backed up | `charybdis-optimizer/` (original) |
| v2 code | **READY** | `charybdis-optimizer-v2/` |
| Tests | 10/10 pass | `charybdis-optimizer-v2/tests/test_v2.py` |
| Data files | Shared | `build/canonical.json`, `build/app_shortcut_scores.json`, `build/usage_stats.json` |

---

## What v2 Does Better

v2 optimizes for **workflows**, not app categories. Key insight from Run 13 analysis: users don't care about "modifier themes" on layers — they care that when they're doing specific work (e.g., "Claude + coding + browser"), all the shortcuts they need are on accessible layers with minimal effort.

v2 fitness factors (8 total):
1. **Effort** — low-effort positions for high-importance shortcuts
2. **Adjacency** — related shortcuts close together (same-app + cross-app usage-aware)
3. **Finger balance** — even left/right hand load
4. **Same-finger** — penalize overusing one finger
5. **Violations** — duplicates, L0 displacement, missing important, **thumb occupancy**
6. **Workflow coherence** — penalize splitting multi-step workflows across layers
7. **Thumb utilization** — reward using thumb cluster appropriately
8. **Trackball proximity** — mouse shortcuts near trackball

**Thumb occupancy**: The v2 knows which thumb is occupied for each layer:
- Left thumb occupied: L1, L2, L6, L8 (momentary access from L0)
- Right thumb occupied: L3, L4 (momentary access from L0)
- Thumbs free: L5, L7, L9, L10 (toggle access — no hold required)
- **Penalty**: placing shortcuts on occupied thumbs = unreachable while layer is active

**Workflow coherence**: Reads `build/usage_stats.json` (123 sequences, 565 chains, 81 workflows). Cross-app shortcuts used together (e.g., `Ctrl+C → Alt+Tab → Ctrl+V`) get bonuses for being on the same layer.

---

## How to Run

### Step 1: Verify Environment
```bash
cd charybdis-optimizer-v2
py -m pytest tests/test_v2.py -v
```
Expected: 10 passed in ~10-15s.

### Step 2: Quick Test Run (15 seconds)
```bash
cd charybdis-optimizer-v2
py run_evolution.py ../build
```
Expected: 50 gens, pop=100, surrogate R² ≈ 0.95, completes in ~15s.

### Step 3: Serious Run (5-10 minutes)
Edit `build/config_v2.yaml`:
```yaml
evolution:
  pop_size: 500
  n_generations: 500
```

Run:
```bash
cd charybdis-optimizer-v2
py run_evolution.py ../build
```

For overnight runs:
```yaml
evolution:
  pop_size: 2000
  n_generations: 1000
```

### Step 4: Evaluate Results
After the run, v2 prints `Best layout: effort=X, adj=Y, viol=Z`. Lower `viol` is better. For exact evaluation:
```python
from core.loader import build_layout
from fitness.evaluator import FitnessEvaluator

layout = build_layout('../build')
evaluator = FitnessEvaluator()

# Load best genome from results and evaluate exactly
# (v2 currently doesn't save results in a standard format — see "Known Issues")
```

---

## Configuration Reference

`build/config_v2.yaml`:
```yaml
evolution:
  pop_size: 100          # Population size (500+ recommended for serious runs)
  n_generations: 50      # Generations (500+ recommended for serious runs)
  crossover_prob: 0.7    # Cycle crossover probability
  mutation_prob: 0.15    # Swap mutation probability
  seed: 42               # Random seed (None for random)

surrogate:
  enabled: true          # Enable neural surrogate (100× speedup)
  hidden_dim: 128        # Surrogate MLP hidden size
  retrain_every: 200     # Retrain surrogate every N genomes
  exact_eval_every: 50   # Exact eval every N generations
  n_initial_samples: 500 # Random layouts to train surrogate initially
  surrogate_epochs: 50   # Training epochs for surrogate

fitness:
  weights:
    effort: 1.0
    adjacency: 1.5
    finger_balance: 0.8
    same_finger: 2.0
    violations: 50.0
    workflow_coherence: 30.0
```

---

## Known Issues & Limitations

1. **v2 starts with EMPTY genome** (`-1` everywhere). No pre-seeding. The first generations are random. This is the biggest gap vs. v1 — Run 13's seed was violations = -1314, which took v1's `build_scratch_genome()` to achieve.

2. **No results save format yet**. v2 prints best scores to stdout but doesn't save `evolution_results.json` like v1. You need to capture stdout or add save logic to `run_evolution.py`.

3. **No GPU batch exact eval**. v2 surrogate is fast but exact evaluation is CPU-only. The surrogate R² = 0.95 is good but not perfect. For the final evaluation, exact eval is needed.

4. **No pre-seeding of static groups**. v1 had `repair_seeded_groups()` that kept arrows, clipboard, F-keys, win-directions clustered. v2 doesn't have this. The optimizer discovers clustering through evolution, but seeding helps.

5. **No L0 thumb protection config**. v1 had `open_l0_keys` config. v2 has a basic frozen mask but doesn't know about the 6 open L0 thumb positions.

6. **No dynamic group discovery**. v1 discovered groups from usage data (e.g., `Ctrl+C+V`, `Space+Backspace`). v2's adjacency factor captures some of this but not the explicit group repair.

---

## What to Port from v1 (Priority Order)

If results are not as good as v1's seed (-1314 violations), port these in order:

1. **Pre-seeding** (`evolve/representation.py` line 897: `build_scratch_genome()`)
   - Seeds L0 keys, structural exits, mouse workflow onto L2
   - This alone gave v1 gen 0 violations = -1314

2. **Static group repair** (`evolve/representation.py` line 345: `repair_seeded_groups()`)
   - Forces arrows, clipboard, F-keys, win-directions to cluster

3. **Dynamic group discovery** (`evolve/representation.py`: `discover_dynamic_groups()`)
   - Discovers groups from usage data and seeds them

4. **GPU batch exact eval** (`evolve/fitness.py`: `GPUFitnessEvaluator`)
   - Batch evaluate genomes on GPU for exact fitness

5. **L0 thumb protection** (`evolve/run_evolution.py`: `open_l0` config)
   - Only mutate 6 specific L0 thumb positions, protect rest

6. **Learning curve factor** (`evolve/fitness.py`)
   - v1 had this, v2 doesn't

7. **Cross-layer duplicate (usage-weighted)** (`evolve/fitness.py` lines 100-127)
   - v1 penalized duplicates more on layers with actual usage

---

## Files & Architecture

```
charybdis-optimizer-v2/
├── core/
│   ├── __init__.py          # Position, Shortcut, Layout, LayerAccess, FitnessResult
│   └── loader.py            # Loads canonical.json, app_shortcut_scores.json, usage_stats.json
├── fitness/
│   ├── __init__.py          # FitnessFactor base class
│   ├── evaluator.py         # Wires all 8 factors into 3 MO objectives
│   └── factors/
│       ├── effort.py
│       ├── adjacency.py     # Usage-aware cross-app adjacency
│       ├── finger_balance.py
│       ├── same_finger.py
│       ├── violation.py     # Thumb occupancy + duplicates + L0 displacement
│       ├── workflow_coherence.py  # NEW: penalizes workflow splits
│       ├── thumb_utilization.py
│       └── trackball_proximity.py
├── evolution/
│   ├── __init__.py          # CycleCrossover, SwapMutation, LayoutRepair, create_algorithm
│   └── surrogate.py         # LayoutSurrogate, SurrogateTrainer, SurrogateManager
├── config/
│   └── __init__.py          # YAML config loader with defaults
├── export.py
├── run_evolution.py         # Main entry point
└── tests/
    └── test_v2.py           # 10 tests, all pass
```

---

## Quick Checks for Manager

### Is v2 working?
```bash
cd charybdis-optimizer-v2
py -m pytest tests/test_v2.py -v  # 10 passed = good
py run_evolution.py ../build       # completes in ~15s = good
```

### Is thumb occupancy working?
```bash
cd charybdis-optimizer-v2
py -c "from core.loader import build_layout; l=build_layout('../build'); print('L1 occupied:', l.get_occupied_thumbs(1)); print('L5 occupied:', l.get_occupied_thumbs(5))"
```
Expected: L1 has `['left']`, L5 has `[]`.

### Is workflow coherence reading usage data?
```bash
cd charybdis-optimizer-v2
py -c "from core.loader import build_layout; l=build_layout('../build'); print('Sequences:', len(l.usage_data.sequences)); print('Chains:', len(l.usage_data.chains))"
```
Expected: 123 sequences, 565 chains.

### Is the surrogate accurate?
Watch the output of `run_evolution.py`. Surrogate R² should be > 0.90. If it's < 0.80, increase `n_initial_samples` in config.

---

## Run History (For Reference)

| Run | Status | Best Violations | Notes |
|-----|--------|-----------------|-------|
| Run 12 | Completed | -309 | Arrows/mouse well clustered, but chain scattered |
| Run 13 | **KILLED at gen 0** | -1314 (seed) | Dynamic group pre-seeding worked. Process killed. No evolved results. |
| v2 test | Completed | ~1,158,594 (empty genome baseline) | 50 gens, pop=100. Surrogate R²=0.95. First v2 run. |

---

## Immediate Action

**Run v2 with serious config NOW.**

```bash
# 1. Set config
cat > build/config_v2.yaml << 'EOF'
evolution:
  pop_size: 500
  n_generations: 500
  crossover_prob: 0.7
  mutation_prob: 0.15
  seed: 42

surrogate:
  enabled: true
  hidden_dim: 128
  retrain_every: 200
  exact_eval_every: 50
  n_initial_samples: 500
  surrogate_epochs: 50

fitness:
  weights:
    effort: 1.0
    adjacency: 1.5
    finger_balance: 0.8
    same_finger: 2.0
    violations: 50.0
    workflow_coherence: 30.0
EOF

# 2. Run
cd charybdis-optimizer-v2
py run_evolution.py ../build

# 3. Capture results
tee build/v2_run_$(date +%Y%m%d_%H%M%S).log
```

---

## Questions?

- v2 code: `charybdis-optimizer-v2/`
- v1 backup: `charybdis-optimizer/` (original, untouched)
- Data: `build/canonical.json`, `build/app_shortcut_scores.json`, `build/usage_stats.json`
- Config: `build/config_v2.yaml`
- This handoff: `build/v2_manager_handoff.md`
