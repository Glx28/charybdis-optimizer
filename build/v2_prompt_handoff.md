# PROMPT: Start v2 Evolution Runs

Paste this into a new Claude session to continue work on the Charybdis v2 optimizer.

---

## CONTEXT

You are managing the Charybdis keyboard layout optimizer. Run 13 died at gen 0. A complete v2 rewrite was built and is ready to run. **Your job is to run v2 evolution, evaluate results, and iterate.**

## FILES

- **v2 code**: `charybdis-optimizer-v2/` (self-contained, 10 tests pass)
- **Data**: `build/canonical.json`, `build/app_shortcut_scores.json`, `build/usage_stats.json`
- **Config**: `build/config_v2.yaml`
- **Handoff docs**: `build/v2_manager_handoff.md` (detailed), `build/run13_analysis.md` (Run 13 analysis)

## IMMEDIATE TASKS

### 1. Verify v2 Works
```bash
cd charybdis-optimizer-v2
py -m pytest tests/test_v2.py -v
py run_evolution.py ../build
```
Expected: 10 tests pass, evolution completes in ~15s with surrogate R² > 0.90.

### 2. Run First Serious v2 Evolution
```bash
# Edit config for a real run
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

# Run
cd charybdis-optimizer-v2
py run_evolution.py ../build
```

### 3. Save Results
v2 currently only prints to stdout. Capture output:
```bash
cd charybdis-optimizer-v2
py run_evolution.py ../build | tee ../build/v2_run_$(date +%Y%m%d_%H%M%S).log
```

## WHAT v2 DOES

v2 optimizes for **workflows**, not app categories. It knows:
- **Thumb occupancy**: which thumb is occupied for each layer (e.g., L1 = left thumb held, so left thumb shortcuts on L1 are unreachable)
- **Usage patterns**: reads `usage_stats.json` to reward placing cross-app shortcuts used together on the same layer
- **Workflow coherence**: penalizes splitting `Ctrl+C → Alt+Tab → Ctrl+V` across 3 layers

## KNOWN LIMITATIONS

1. **Empty genome start** — v2 starts with no shortcuts assigned. v1's seed was violations = -1314. If v2 results are worse, port `build_scratch_genome()` from `evolve/representation.py` (v1) into v2.
2. **No results save format** — need to add JSON output to `run_evolution.py`.
3. **No GPU batch exact eval** — surrogate is fast but exact eval is CPU-only.
4. **No pre-seeding of static groups** — arrows, clipboard, F-keys clustering not enforced.

## KEY METRICS TO TRACK

- `violations` (lower is better) — baseline empty genome = ~6270
- `workflow_coherence` (lower is better) — baseline = ~3364
- `effort` (lower is better) — baseline = 0 (empty)
- `adjacency` (higher is better) — baseline = 0 (empty)
- Surrogate R² (should be > 0.90)

## IF RESULTS ARE NOT GOOD

Priority order for porting from v1:
1. Pre-seeding (`evolve/representation.py` line 897: `build_scratch_genome()`)
2. Static group repair (`evolve/representation.py` line 345: `repair_seeded_groups()`)
3. Dynamic group discovery (`evolve/representation.py`: `discover_dynamic_groups()`)
4. GPU batch exact eval (`evolve/fitness.py`: `GPUFitnessEvaluator`)

## GOAL

Get v2 to produce layouts with violations < -500 (ideally approaching v1's -1314 seed) while respecting thumb occupancy and workflow coherence. Then compare with v1's best evolved results and iterate.

---

Run v2 now. Report back with:
1. Best violations score
2. Pareto front size
3. Surrogate R²
4. Whether thumb occupancy was respected in the best genome
5. Whether known workflows (Ctrl+C → Alt+Tab → Ctrl+V) are on the same layer
