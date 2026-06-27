# Session 6B: Performance Optimization & Algorithm Quality

## Mission

Codex is handling scoring/penalty fixes (Problems 1-5 from the layout quality review). Your job is everything else: further speed optimization, algorithm improvements, better convergence, diagnostics, and infrastructure hardening. Do NOT touch the scoring penalties that Codex is fixing (frozen-area duplication, coach_base on momentary, group_split weights, position waste penalty, apply script export). Focus on making the engine faster, smarter, and more robust.

## Context — What Was Already Done (Session 5)

The optimizer went from ~20s/gen to ~1.3s/gen through:
1. **OperatorContext** — precomputed static lookups (operators.py)
2. **7 GPU batch operators** — swap, migrate, dedup, thumb_fill, redistribute, cross_layer_dedup (operators.py)
3. **GPU uniform crossover** — replaced CPU PMX (operators.py)
4. **No-clone variation** — every offspring modified, `vary_population_gpu` orchestrator (run_evolution.py)
5. **Adaptive mutation** — n_ops 1→3 on plateau (operators.py)
6. **Fitness eval caching** — validation cached by capability-SID fingerprint (fitness.py)
7. **GPU vectorized penalties** — access_effort, demand, finger_balance, app_coherence, missing_important all via scatter ops (fitness.py)
8. **Effort model rewrite** — home row inner=0.0, thumbs=1.5-2.5 (representation.py)
9. **Mouse button importance** — MB2=35, MB3=20, MB4/5=12 (representation.py)
10. **Scroll key importance** — Momentary Layer 6 = 40.0 (only way to scroll on trackball) (representation.py)
11. **2-layer duplicate penalty** — CPU+GPU parity (fitness.py)

## Current Performance Profile

```
Eval 5000 genomes (warm cache):   377ms   (was 14,200ms)
Eval 5000 genomes (cold cache):   3,497ms
Operators (vary_population_gpu):  600ms
NSGA-II selection:                300ms
Total gen time:                   ~1,300ms (was 20,000ms)

Component breakdown (warm, 5000 genomes):
  access_penalties:      60ms   (validation cache + GPU access effort + CPU demand penalty)
  cross_layer_consist:    2ms   (scatter_reduce, was 46ms)
  duplicates:            11ms
  same_finger:            2ms
  adjacency:              2ms
  app_coherence:          2ms
  finger_balance:         1ms
  effort:                 2ms
  missing_important:      0.3ms
  GPU tensor total:      22ms
  Full eval:            377ms
```

The ~350ms gap between GPU tensor total (22ms) and full eval (377ms) is:
- numpy↔tensor conversion overhead (~80ms)
- access_penalties CPU demand loop (~60ms)
- Python list building for DEAP (~50ms)
- torch.cuda.synchronize overhead (~30ms)
- g_np construction from genomes_list (~80ms)

## Your Optimization Targets

### 1. Eliminate the genomes_list → numpy conversion (80ms)

In `evaluate_batch_gpu()` line ~880: `g_np = np.array(genomes_list, dtype=np.int64)`. This converts a Python list of 5000 lists into numpy. 

The `vary_population_gpu` already has the genomes as a tensor (`t_all`) but converts back to Python lists for DEAP. Then `evaluate_batch_gpu` converts them back to numpy/tensor. This round-trip is wasteful.

**Approach:** Pass the tensor directly from `vary_population_gpu` to `evaluate_batch_gpu` via a side channel. Store `t_all` on the OperatorContext or as a return value, and have `batch_evaluate` check for it before doing the numpy conversion. The DEAP Individual list is still needed for selection, but the tensor can be reused for eval.

### 2. Vectorize the CPU demand penalty loop (60ms)

In `_batch_access_penalties`, the demand penalty currently uses a GPU scatter_add for layer demand computation but the result is already fast. The remaining ~60ms is the validation cache lookup + cost/depth matrix construction. Profile to find the exact bottleneck within `_batch_access_penalties` and optimize.

### 3. Reduce DEAP Individual overhead (50ms)

The `creator.Individual(row.tolist())` call at the end of `vary_population_gpu` creates 5000 Python list objects. Consider:
- Using numpy arrays as Individual backing (Individual subclass of np.ndarray)
- Deferring Individual creation until after eval (eval doesn't need Individual, just raw genomes)
- Caching the numpy array and only creating Individuals for selection

### 4. Seeding GPU acceleration (13-15s → target 3-5s)

`seed_population` and `seed_population_scratch` call CPU operators 50-300× per genome in Python loops. For 8000 genomes that's ~250s of CPU work.

**Approach:** Use `batch_migrate_shortcut` GPU operator for the initial placement pass. Instead of calling `migrate_shortcut` 200× per genome sequentially, do 200 rounds of `batch_migrate_shortcut` on all 8000 genomes simultaneously. Each round places one shortcut per genome. 200 rounds × 8000 genomes in GPU batch vs 200 × 8000 sequential CPU calls.

### 5. Diversity injection on plateau

When `plateau_count > 100`, the adaptive mutation increases intensity (n_ops 2→3) but doesn't inject fresh genetic material. Add:
- Replace 5-10% of population with fresh random genomes (via `migrate_shortcut` from scratch)
- Or: inject elites from the other run mode (normal seeds from scratch results, scratch from normal)
- Reset plateau_count after injection so it doesn't re-trigger immediately

In `run_evolution.py` generation loop, after the `plateau_intensity` update:
```python
if plateau_count == 150 and plateau_count > last_injection:
    n_inject = pop_size // 20  # 5%
    for i in random.sample(range(pop_size), n_inject):
        fresh = copy.copy(current_genome)
        for _ in range(random.randint(20, 50)):
            fresh = migrate_shortcut(fresh, ctx)
        population[i] = creator.Individual(fresh)
        del population[i].fitness.values
    last_injection = plateau_count
    print(f"  Injected {n_inject} fresh genomes at plateau {plateau_count}")
```

### 6. Phase threshold tuning

Current phase boundaries:
- Normal: explore < 200, balanced 200-1000, exploit > 1000
- Scratch: explore < 300, balanced 300-1500, exploit > 1500

With 1.3s/gen, 200 gens takes ~4.3 minutes. The 300-gen test runs showed the normal run was STILL in explore phase at gen 200 (it never reached balanced before the run ended). Consider:
- Shortening explore to 100 gens (normal) / 150 gens (scratch)
- Balanced to 100-500 / 150-800
- This lets the algorithm transition to refinement faster

### 7. Cross-layer consistency scoring improvement

The `cross_layer_consistency` rewards same SID at same physical (x,y) across layers. But it doesn't consider whether this is actually useful. Having Ctrl+C at the same position on 3 different layers IS useful (muscle memory). Having a random F-key at the same position across layers is noise.

Weight the bonus by shortcut importance and usage:
```python
cl_bonus += same_coord.float() * count.float() * pw * imp_per_sid * 0.5
```

### 8. Better convergence logging

The verbose logging currently shows per-checkpoint stats. Add:
- **Cache hit rate** per checkpoint: `hits / (hits + misses)` for the validation cache
- **Operator success rate**: for GPU operators, what % of genomes were actually modified (vs no-op due to no valid candidates)
- **Pareto front size and spread**: how many non-dominated solutions, their effort/violation ranges
- **Diversity metric**: average hamming distance between random genome pairs (not just unique count)

### 9. Checkpoint efficiency

Checkpoints save the entire population as JSON lists — at 5000 × 559 ints, that's ~20MB per checkpoint. Consider:
- Saving as numpy `.npz` (compressed, ~2MB)
- Or: only save the Pareto front + best 100 individuals + population stats (not all 5000)
- Resume from partial checkpoint by re-seeding the rest

## Key Files

- `evolve/operators.py` — OperatorContext, GPU batch operators, `batch_crossover_gpu`, `GPU_OP_MAP`
- `evolve/run_evolution.py` — `vary_population_gpu`, `vary_population`, `seed_population`, `seed_population_scratch`, generation loop, `_batch_access_penalties` call
- `evolve/fitness.py` — `evaluate_batch_gpu` (~lines 872-1524), `_batch_access_penalties` (~lines 1526-1640)
- `evolve/representation.py` — `ROW_COMFORT`, `COL_EFFORT`, `BASE_KEY_IMPORTANCE`, `PUNCTUATION_IMPORTANCE`, `KEY_GROUPS`, `LAYER_ACCESS`
- `evolve/profile_evolution.py` — profiling script
- `evolve/config.json` / `evolve/config_scratch.json` — weights and settings

## Test Commands
```bash
cd evolve
python -m unittest test_fitness test_layer_access -v           # 23 tests must pass
python evaluate_cpu_gpu_parity.py ../build                      # max_abs_diff < 1.0
python profile_evolution.py ../build                            # timing comparison
python -c "import py_compile, pathlib; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('.').glob('*.py')]"
```

## Critical Rules
- Do NOT modify scoring penalties (fitness weights, violation logic, group_split, position waste) — Codex is handling those in a separate worktree.
- CPU and GPU fitness scoring must produce identical results (parity test).
- All 23 tests must pass after changes.
- Measure before/after with profiling.
- The verbose_logging infrastructure (config flag `verbose_logging: true`) must keep working.
- Norwegian keyboard layout: semicolon=ø, left_apos=æ, left_brace=å on L0. Input language is Norwegian.
- Only 8 physical thumb positions (5 left, 3 right). Scroll = Momentary Layer 6 (importance 40).
- No physical mouse — trackball only. MB1-3 are essential daily-use buttons.

## Quick Smoke Test
```bash
# Set config.json: "generations": 20, "pop_size": 500, "checkpoint_interval": 10, "verbose_logging": true
python run_evolution.py ../build
# Should complete in < 60s, all gens logged, no errors
```
