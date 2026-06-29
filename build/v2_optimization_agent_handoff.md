# V2 OPTIMIZATION AGENT — CONTINUOUS IMPROVEMENT HANDOFF

## Your Base Directory

**`C:\Users\nos\charybdis-optimizer\charybdis-optimizer-v2`**

All work happens here. Do not modify v1 code (`charybdis-optimizer/`). Do not modify the manager's running process directly unless it's crashed.

## Current Situation

A manager agent (Claude) is running a long evolution job:
```bash
cd charybdis-optimizer-v2 && uv run python run_evolution.py ../build
```

This is a **999,999 generation run** with pop=1000. Expected duration: **8-9 days** at ~0.77s per generation. The manager reports every 1000 generations.

Your job is to **continuously improve the optimizer** while the run proceeds. Monitor the run, analyze performance, find bottlenecks, and apply optimizations that make the layout better or the code faster. **Do not stop the run unless you find a bug that causes crashes.**

## What You Must Read First

Before touching any code, read these files to understand the current state:

1. **`config/__init__.py`** — Current defaults (pop=1000, n_initial=500, epochs=30, etc.)
2. **`run_evolution.py`** — Main entry point. Has perf stats, profiling, `--profile-fast` flag.
3. **`fitness/batch_evaluator.py`** — Numba-compiled batch exact evaluator. This is where most fitness computation happens.
4. **`fitness/evaluator.py`** — Composable evaluator that wires all factors.
5. **`evolution/surrogate.py`** — Surrogate model + trainer. CUDA auto-detect, AMP, optional torch.compile.
6. **`evolution/__init__.py`** — NSGA2 operators (sampling, crossover, mutation, repair).
7. **`fitness/factors/*.py`** — All 8 fitness factors.
8. **`core/__init__.py`** — Data structures: Position, Shortcut, Layout, LayerAccess, FitnessResult.
9. **`core/loader.py`** — Data loading, pre-seeding, dynamic group discovery.
10. **`build/v2_perf_report.json`** — Performance data from the last run.
11. **`build/v2_checkpoint_gen*.json`** — Latest checkpoint (best genome, fitness scores).

## How to Monitor the Current Run

### 1. Check if the run is alive
```bash
cd charybdis-optimizer-v2
# Check if Python process is running
ps aux | grep run_evolution 2>/dev/null || tasklist /FI "IMAGENAME eq python.exe"
```

### 2. Read latest output
```bash
tail -50 C:/Users/nos/charybdis-optimizer/build/v2_evolution_results.json 2>/dev/null
# Or check the log file if one exists
```

### 3. Read latest checkpoint
```bash
cd charybdis-optimizer-v2
uv run python -c "
import json, glob
cks = sorted(glob.glob('../build/v2_checkpoint_gen*.json'))
if cks:
    r = json.load(open(cks[-1]))
    print('Checkpoint:', cks[-1])
    print('Gen:', r['generation'])
    print('Best exact viol:', r['best_exact']['violations'])
    print('Best raw viol:', r['best_exact'].get('raw_violations', 'N/A'))
"
```

### 4. Read performance report
```bash
cd charybdis-optimizer-v2
uv run python -c "
import json
p = json.load(open('../build/v2_perf_report.json'))
for k, v in p.get('events', {}).items():
    print(f'{k}: {v[\"total_seconds\"]:.2f}s total, {v[\"avg_seconds\"]:.3f}s avg, {v[\"count\"]} calls')
"
```

## Your Optimization Areas

### TIER 1: SPEED (Always look for these)

**Goal: Reduce per-generation time from ~0.77s to <0.5s.**

#### 1.1 Surrogate Inference Speed
- The surrogate is already GPU (0.015s per 1000 layouts). But can it be faster?
- Check: `python -c "import torch; from evolution.surrogate import ...; measure predict() time"`
- Try: `torch.jit.trace()` the model for static graph optimization.
- Try: Reduce embedding_dim from 32 to 16 (smaller model, less memory bandwidth).
- Try: `torch.set_float32_matmul_precision('high')` for faster GEMM on Tensor Cores.

#### 1.2 pymoo Overhead
- pymoo's NSGA2 selection, crossover, mutation, repair are pure Python/NumPy on CPU.
- Profile: `python -m cProfile -o profile.stats run_evolution.py ../build` and analyze.
- Check `pstats` for which function takes the most time per generation.
- If `eliminate_duplicates` is the bottleneck (it's currently False), that's good.
- If `CycleCrossover._do` or `SwapMutation._do` is slow, optimize those loops.

#### 1.3 Numba Batch Evaluator Speed
- `fitness/batch_evaluator.py` is the hot path. Check if Numba is actually compiling.
- Look for `NUMBA_DEBUG=1` output or compile times.
- Try: `njit(parallel=True, cache=True, fastmath=True)` for the batch functions.
- Try: Reduce precision to float32 everywhere (some operations might be float64).
- Try: Pre-compute more lookup tables to avoid repeated computations in the batch loop.

#### 1.4 Data Transfer Overhead
- Check if numpy arrays are being copied between CPU and GPU unnecessarily.
- The surrogate predict should accept torch tensors directly, not numpy arrays.
- Check: does `predict()` do `torch.tensor(layouts + 1, ...)` every call? If so, pre-allocate the +1 buffer.

#### 1.5 Checkpoint I/O Speed
- Checkpoints save full JSON every 500 gens. With 1000 individuals × 616 positions = 616K integers, that's ~5MB per checkpoint.
- Try: Use pickle or np.savez instead of JSON for the genome array.
- Try: Save only the best genome, not the full Pareto front.
- Try: Increase checkpoint_interval to 1000 or 2000.

#### 1.6 Exact Eval Batch Frequency
- Current: exact_eval_every=100, exact_eval_batch=5. Each batch is 0.038s.
- Amortized: 0.038s / 100 = 0.00038s per gen. Tiny.
- But if exact_eval_batch grows, or if the surrogate needs retraining, exact eval time spikes.
- Try: exact_eval_every=200, exact_eval_batch=10. Less frequent but more samples per eval.
- Try: Skip exact eval entirely after gen 10000 (surrogate is good enough by then).

#### 1.7 Memory Pressure
- Check: `nvidia-smi` or `torch.cuda.memory_summary()` to see if GPU memory is full.
- If GPU memory is full, the surrogate model might be spilling to system memory.
- Try: Reduce batch_size in DataLoader to free up GPU memory for the model.
- Try: `torch.cuda.empty_cache()` between generations if memory is growing.

#### 1.8 System Resource Usage
- Check: `htop` or Windows Task Manager to see CPU/GPU utilization.
- If CPU is at 100% and GPU is at 10%, the bottleneck is on CPU (pymoo operators or Numba).
- If GPU is at 100% and CPU is at 10%, the bottleneck is surrogate inference.
- If both are low, the bottleneck is I/O or sequential logic.
- **Goal: Maximize GPU utilization. If GPU < 50%, the CPU is the bottleneck.**

### TIER 2: LAYOUT QUALITY (Monitor and improve)

**Goal: Get raw violations below 1M (currently seed is 9.2M).**

#### 2.1 Analyze the Best Genome
- Load the best genome from the latest checkpoint.
- Evaluate it with all factors and print the breakdown.
- Find which factor is the dominant penalty.

```python
cd charybdis-optimizer-v2
uv run python -c "
from core.loader import build_layout
from fitness.evaluator import FitnessEvaluator
from fitness.factors.violation import ViolationFactor
import json, glob

layout = build_layout('../build')
cks = sorted(glob.glob('../build/v2_checkpoint_gen*.json'))
if cks:
    r = json.load(open(cks[-1]))
    g = r['best_exact']['genome']
    layout = layout.clone_with(genome=[int(x) for x in g])

evaluator = FitnessEvaluator(reference_layout=layout)
result = evaluator.evaluate(layout)
print('Objectives:', result.objectives)
print('Factor scores:')
for k, v in result.factor_scores.items():
    print(f'  {k}: {v:.2f}')

vf = ViolationFactor()
print('Violation breakdown:')
print(f'  duplicate: {vf._duplicate_penalty(layout):.2f}')
print(f'  l0_displacement: {vf._l0_displacement(layout):.2f}')
print(f'  missing_important: {vf._missing_important(layout):.2f}')
print(f'  cross_layer_dup: {vf._cross_layer_duplicate(layout):.2f}')
print(f'  group_split: {vf._group_split(layout):.2f}')
print(f'  thumb_occupancy: {vf._thumb_occupancy(layout):.2f}')
"
```

#### 2.2 Tune Objective Weights
- The weights in `config/__init__.py` determine how much each factor matters.
- If `violations` is the dominant penalty but not improving, increase its weight.
- If `group_split` is the bottleneck, increase the `group_split` sub-weight in `ViolationFactor`.
- If `app_coherence` is too strong/weak, adjust its weight.
- **Test weight changes by running a 100-gen test and comparing the final violations.**

```python
# Quick test: run 100 gens with new weights, compare violations
# Create a test config, run, check results, delete config
```

#### 2.3 Fix Group Preservation
- If `group_split` > 2000 after 1000 gens, the static group preservation is not working.
- Check: `fitness/factors/violation.py` — `KEY_GROUPS` and `_group_split()`.
- Try: Add a group repair operator that moves group members to the same layer.
- Try: Increase `group_split` weight in `ViolationFactor.sub_weights`.

#### 2.4 Fix Thumb Occupancy
- If `thumb_occupancy` > 100 after 1000 gens, too many shortcuts are on occupied thumbs.
- Check: `fitness/factors/violation.py` — `_thumb_occupancy()` and layer occupancy map.
- Verify: `layer_access` data is correct. L1/L2/L6/L8 should have left thumb occupied, L3/L4 right thumb occupied.
- Try: Increase `thumb_occupancy` penalty weight.

#### 2.5 Address Blind Spots
- 104 high-importance shortcuts are never used. Check `build/usage_stats.json` → `blind_spots`.
- If these shortcuts are truly unused, reduce their importance in the corpus.
- If the logger is missing them, fix the logger (in `charybdis-tools/ahk/`).
- Try: Add a `usage_informed_importance` that discounts unused shortcuts.

#### 2.6 Improve Pre-Seeding
- The current `build_scratch_genome()` in `core/loader.py` does greedy assignment.
- Try: Use usage data to weight which shortcuts get pre-seeded first (most-used first).
- Try: Seed static groups (arrows, clipboard, F-keys) together on the same layer from the start.

### TIER 3: GPU UTILIZATION (Push the GTX 1070 harder)

**Goal: GPU > 80% utilization during evolution.**

#### 3.1 Surrogate Batch Size
- The surrogate predicts one generation (1000 layouts) at a time. Can we batch multiple generations?
- If we could predict 2-3 generations ahead, we'd double GPU utilization.
- But pymoo evaluates one generation at a time. This is a structural limitation.

#### 3.2 Exact Eval on GPU
- The Numba batch evaluator is CPU-only. Can we move it to GPU?
- Option A: Rewrite the batch evaluator in CUDA using CuPy or Numba's CUDA backend.
- Option B: Use `torch.jit.script` to compile the fitness factors to GPU kernels.
- Option C: Use `jax` instead of Numba for GPU JIT compilation.
- **This is a major rewrite. Only do it if profiling shows exact eval is the bottleneck.**

#### 3.3 Mixed Precision
- Current: `mixed_precision=True` in surrogate. Check if FP16 is actually used.
- GTX 1070 has FP16 but it's slow. FP32 might be faster on this card.
- Try: `mixed_precision=False` and compare speeds.

#### 3.4 Parallel Exact Eval on GPU
- If we have multiple exact eval batches to run (e.g., during retraining), run them in parallel on GPU streams.
- `torch.cuda.Stream()` allows concurrent kernel execution.
- But this only helps if we have multiple independent batches.

### TIER 4: ALGORITHM IMPROVEMENTS (Try new approaches)

#### 4.1 Better Selection Pressure
- If `n_nds` hits 1000/1000 consistently, all individuals are Pareto-optimal. No selection pressure.
- Try: Reduce to 2 objectives (merge adjacency + violations into one).
- Try: Use weighted sum instead of NSGA2 for single-objective optimization.
- Try: Add a diversity metric (crowding distance) to maintain selection pressure.

#### 4.2 Local Search
- After every 1000 gens, run hill-climbing from the best individual.
- Try: Swap two random positions, accept if fitness improves. Repeat 1000 times.
- This could find local optima that NSGA2 misses.

#### 4.3 Adaptive Mutation Rate
- If `eps` is low for 100+ gens, increase `mutation_prob` temporarily to escape local optima.
- If `eps` is high, decrease mutation rate to fine-tune.
- Implement: `mutation_prob = base_rate * (1 + eps_factor)` where eps_factor depends on recent improvement.

#### 4.4 Crossover Operator
- Current: CycleCrossover (O(n)). Try: PMX (Partially Mapped Crossover) or OrderCrossover for permutations.
- Some crossover operators preserve adjacency better than others.
- Test: Run 100 gens with each crossover, compare final violations.

#### 4.5 Surrogate Quality
- If `evolved_surrogate_accuracy_history` shows R² dropping below 0.80, the surrogate is misleading the optimizer.
- Try: Increase `n_initial_samples` to 1000 or 2000 for better initial training.
- Try: Increase `surrogate_epochs` to 100 for more training.
- Try: Use a larger hidden_dim (256 or 512) if the model is underfitting.
- Try: Use a different architecture (e.g., transformer instead of MLP).

## How to Test Changes Safely

### 1. Always run the test suite first
```bash
cd charybdis-optimizer-v2
uv run python -m pytest tests/ -v
# Must be 10 passed before any changes
```

### 2. Use a temporary config for quick tests
```bash
cd charybdis-optimizer-v2
cat > ../build/config_test.yaml << 'EOF'
evolution:
  pop_size: 100
  n_generations: 20
  crossover_prob: 0.7
  mutation_prob: 0.15
  seed: 42
surrogate:
  enabled: true
  hidden_dim: 128
  embedding_dim: 32
  batch_size: 256
  compile: true
  mixed_precision: true
  retrain_every: 200
  exact_eval_every: 100
  n_initial_samples: 100
  surrogate_epochs: 10
  min_r2: 0.90
exact_eval:
  batch_size: 5
  use_numba: true
  parity_tolerance: 1e-4
fitness:
  weights:
    effort: 1.0
    adjacency: 1.5
    finger_balance: 0.8
    same_finger: 2.0
    violations: 50.0
    workflow_coherence: 30.0
    learning_curve: 0.5
    app_coherence: 5.0
    trackball_proximity: 2.0
output:
  build_dir: "build"
  checkpoint_interval: 500
  verbose: true
profiling:
  enabled: false
EOF
# Run with test config
uv run python -u run_evolution.py ../build --config ../build/config_test.yaml
# Or: uv run python -u run_evolution.py ../build --profile-fast
# Then delete the test config
rm ../build/config_test.yaml
```

### 3. Profile before and after
```bash
cd charybdis-optimizer-v2
# Baseline
uv run python -u run_evolution.py ../build --profile-fast
# Save the perf report
# After changes
uv run python -u run_evolution.py ../build --profile-fast
# Compare v2_perf_report.json before and after
```

### 4. Verify correctness
- If you changed fitness factors, verify the Numba parity test still passes:
```python
from fitness.batch_evaluator import BatchExactEvaluator
# Run parity test
```
- If you changed the surrogate, verify R² > 0.90 after training.
- If you changed operators, verify the genome is still valid (no duplicates where not allowed, frozen positions preserved).

## Reporting Rules

### Report to the user IMMEDIATELY if:
1. You found a crash-causing bug in the running code (don't stop the run, but warn the user).
2. The run has crashed or exited unexpectedly.
3. GPU utilization is < 20% for 1000+ gens (major bottleneck found).
4. You made a change that improved speed by > 20% or improved best violations by > 10%.

### Report at the end of each optimization session:
1. What you changed.
2. How you tested it.
3. Before/after numbers (speed, violations, R², etc.).
4. What you plan to try next.

### Do NOT report:
- Minor tweaks that had no measurable effect (< 5% improvement).
- Failed experiments (keep them in your notes but don't bother the user).
- Theoretical ideas that haven't been tested yet.

## Priority Order (Do These First)

1. **Profile the current run** — `python -m cProfile` or `py-spy` to find the real bottleneck.
2. **Tune weights** — If violations aren't dropping fast enough, try different weight combinations.
3. **Optimize surrogate** — torch.compile (if RTX), smaller embedding, jit.trace.
4. **Optimize Numba evaluator** — parallel=True, cache=True, precompute more lookups.
5. **Reduce I/O** — pickle checkpoints, less frequent saves.
6. **Group repair** — If group_split is the bottleneck, add a repair operator.
7. **Adaptive mutation** — If evolution stalls, increase mutation rate.
8. **Local search** — After 10000 gens, hill-climb from the best.

## Quick Commands Reference

```bash
# Run tests
cd charybdis-optimizer-v2 && uv run python -m pytest tests/ -v

# Profile fast run (20 gens)
cd charybdis-optimizer-v2 && uv run python -u run_evolution.py ../build --profile-fast

# Check GPU
cd charybdis-optimizer-v2 && uv run python -c "import torch; print(torch.cuda.get_device_name(0)); print(torch.cuda.is_available())"

# Check latest checkpoint
cd charybdis-optimizer-v2 && uv run python -c "import json, glob; cks=sorted(glob.glob('../build/v2_checkpoint_gen*.json')); print(cks[-1]) if cks else print('none')"

# Check perf report
cd charybdis-optimizer-v2 && uv run python -c "import json; p=json.load(open('../build/v2_perf_report.json')); print(p)"

# Check if run is alive
ps aux | grep run_evolution || tasklist /FI "IMAGENAME eq python.exe"

# Analyze best layout
cd charybdis-optimizer-v2 && uv run python -c "
from core.loader import build_layout
from fitness.evaluator import FitnessEvaluator
import json, glob
layout = build_layout('../build')
cks = sorted(glob.glob('../build/v2_checkpoint_gen*.json'))
if cks:
    r = json.load(open(cks[-1]))
    g = r['best_exact']['genome']
    layout = layout.clone_with(genome=[int(x) for x in g])
    result = FitnessEvaluator(reference_layout=layout).evaluate(layout)
    print('Objectives:', result.objectives)
    for k, v in result.factor_scores.items():
        print(f'  {k}: {v:.2f}')
"

# Run with custom config (for testing)
cd charybdis-optimizer-v2 && cat > ../build/config_test.yaml << 'YAML'
... (see above) ...
YAML && uv run python -u run_evolution.py ../build && rm ../build/config_test.yaml
```

## Bottom Line

**Your mission: Make the optimizer faster and better while the run proceeds.**

- Monitor the run without interfering.
- Profile, find bottlenecks, fix them.
- Test every change with a 20-gen test run before declaring it good.
- Report significant improvements to the user.
- Keep the code stable — the 999,999-gen run must not be interrupted.
- Work from `charybdis-optimizer-v2/`. Read the files. Profile. Optimize. Repeat.
