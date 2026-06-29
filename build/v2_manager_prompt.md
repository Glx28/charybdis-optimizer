# MANAGER AGENT: RUN CHARYBDIS V2 EVOLUTION (ALL CRASHES FIXED — VERIFIED)

## Your Task

Start the v2 evolution run and let it run continuously. **Three previous crashes have been fixed and the code was verified with a 5-generation test run.** Report back at milestones. Do NOT stop the run unless the process crashes with a Python exception.

## Start Command

```bash
cd charybdis-optimizer-v2
uv run python run_evolution.py ../build
```

## Previous Crashes (All Fixed)

1. **Pickle error** — `_eval_one` was a local function. **Fixed** — moved to module level.
2. **`numpy.typing` import in workers** — Windows spawn doesn't inherit venv. **Fixed** — `_setup_mp_env()` sets `PYTHONPATH` for child processes.
3. **`torch.compile` / Triton crash on GTX 1070** — Triton requires CUDA capability >= 7.0, GTX 1070 is 6.1. **Fixed** — `SurrogateTrainer._can_compile()` checks CUDA capability before attempting `torch.compile`. GTX 1070 runs in eager mode (still fast).
4. **Score mismatch in multiprocessing** — Workers were missing `usage_data`, `layer_to_indices`, `dynamic_groups`. **Fixed** — all layout data passed to workers.

## Verification Done

A **5-generation test run** completed successfully:
- Startup: 50 samples, 10 epochs, surrogate R² = 0.87
- Evolution: 5 gens in 5.9s with pop=50
- No crashes, no exceptions
- Results saved correctly
- `torch.compile` correctly skipped for GTX 1070

## What Changed

- **GPU surrogate** — GTX 1070, CUDA 12.1, eager mode (torch.compile skipped for old GPUs)
- **Multiprocessing exact eval** — Full layout data passed to workers, PYTHONPATH set for venv
- **Initial training** — 1000 samples by default, auto-retrain if R² < 0.85
- **Seed injection** — Genome 0 is pre-seeded layout
- **Unbuffered output** — Real-time progress
- **Checkpoint cleanup** — Only last 5 kept

## Expected Speed

- **Startup**: ~70-120s (1000 samples + surrogate training on GPU)
- **Per generation**: ~3-5s with pop=1000
- **1000 generations**: ~50-80 minutes
- **10000 generations**: ~8-14 hours

## What to Report

### 1. Initial startup (first 5 minutes)
First 20 lines. Should show:
```
CHARYBDIS V2 EVOLUTION
Loading data from ../build...
  Positions: 616, Shortcuts: 295
  Mutable: 512
  Pre-seeded assignments: 303
Generating 1000 random layouts for surrogate training...
Evaluating exact fitness...
  Done in ...s (...ms per layout)
Training surrogate (... params) on cuda...
  Surrogate R^2 = ...
Running evolution: pop=1000, gens=10000
```

Expected:
- Surrogate R² ≥ 0.90 (or auto-retrain to 1000 samples/60 epochs if R² < 0.85)
- Exact eval of 1000 samples takes ~60-120s with parallel CPU
- If startup takes > 3 minutes, report it

### 2. First 100 generations (critical check)
After gen 100, run:
```bash
cd charybdis-optimizer-v2
uv run python -c "import json; r=json.load(open('../build/v2_checkpoint_gen100.json')); print('Best raw viol:', r['best_exact'].get('raw_violations', 'N/A')); print('Best norm viol:', r['best_exact']['violations'])"
```

**Expected**: Raw violations should be **below 10M** by gen 100 (seed was 11.1M). If still above 10M, report it.

### 3. Every 1000 generations
Share last 5 lines of pymoo output (the `Gen | n_eval | f1 | f2 | f3 | n_nds | eps` table).

### 4. Every 2000 generations
```bash
cd charybdis-optimizer-v2
uv run python -c "import json; r=json.load(open('../build/v2_evolution_results.json')); print('Best raw viol:', r['best_exact'].get('raw_violations', 'N/A')); print('Best norm viol:', r['best_exact']['violations']); print('R2:', r.get('surrogate_r2_history',[])[-1])"
```

Also check for checkpoint files:
```bash
ls -la C:/Users/nos/charybdis-optimizer/build/v2_checkpoint_gen*.json 2>/dev/null | tail -3
```

## DO NOT STOP FOR

- `n_nds` near 1000 — normal for 3-objective MOO.
- `eps` at 0 — evolution may be exploring.
- Slow improvement — expected; evolution takes time.
- Run taking hours — 10000 gens = ~14 hours. Normal.
- Output showing "exact eval" lines every 50 gens — normal.
- Surrogate retraining lines every 200 gens — normal.
- "torch.compile skipped" message — normal for GTX 1070.
- "Surrogate R² below gate, retraining" — normal if initial R² < 0.85.

## ONLY Stop If

- Python exception with traceback (capture last 20 lines)
- Process exits with non-zero code
- Machine out of memory/disk
- Machine restart needed

If it crashes, capture the full traceback and report it. Do not attempt to fix the code.

## Current Seed Numbers

- **Raw seed fitness**: effort=1612, adj=-82422, viol=11114715
- **Normalized seed fitness**: effort≈0.81, adj≈-0.82, viol≈1.11
- **group_split at seed**: ~3762
- **Target**: Raw violations below 5M.

## Files

- Code: `charybdis-optimizer-v2/`
- Data: `build/canonical.json`, `build/app_shortcut_scores.json`, `build/usage_stats.json`
- Output: `build/v2_evolution_results.json`
- Checkpoints: `build/v2_checkpoint_gen*.json` (only last 5 kept)
- Performance report: `build/v2_perf_report.json` (after run completes)
- Config: `charybdis-optimizer-v2/config/__init__.py` (built-in defaults, do not modify)

## Bottom Line

**Start the run now. The code was verified with a 5-generation test run that completed successfully.** All three crashes are fixed. The GPU surrogate works in eager mode. Multiprocessing exact eval is correct. Let it cook. Report every 1000 gens. Do NOT stop for normal evolution behavior.
