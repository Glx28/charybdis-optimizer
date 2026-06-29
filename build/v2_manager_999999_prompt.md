# MANAGER AGENT: RUN CHARYBDIS V2 — 999,999 GENERATION LONG RUN

## Your Task

Start the v2 evolution run with **999,999 generations** and let it run continuously. This is a long run (expected ~8-9 days at 0.77s/gen). Report back at milestones. **Do NOT stop the run unless the process crashes with a Python exception.**

## Start Command

```bash
cd charybdis-optimizer-v2
uv run python run_evolution.py ../build
```

## What Codex Changed (Major Speed Improvements)

1. **Numba batch exact evaluator** — 100 layouts in 0.06s (was ~7s). 170x faster. Verified parity with CPU oracle (max diff 5e-07).
2. **Smaller surrogate** — 2.56M params (was 10.2M). predict(1000) in 0.015s.
3. **Faster defaults** — n_initial=500, epochs=30, exact_eval_every=100, batch=5, checkpoint_interval=500.
4. **R² fallback guardrail** — If initial R² < gate, auto-retrain with 1000 samples/60 epochs. Verified: recovered to R²=0.9897.
5. **O(n) cycle crossover** — Faster genetic operator.
6. **Duplicate elimination off** — Saves time; NSGA2 handles diversity.
7. **Perf stats** — `build/v2_perf_report.json` after each run shows timing breakdowns.

## Measured Speed (Verified by Codex)

- **20 gens, pop=1000: 15.4s total** = **0.77s per generation**
- **Exact eval batch of 5: 0.038s**
- **Surrogate predict(1000): 0.015s**
- **Startup** (500 samples + 30 epochs): ~10-30s
- **999,999 gens estimated**: ~214 hours = **~8.9 days**

## Expected Output

Startup (~10-30s):
```
CHARYBDIS V2 EVOLUTION
  torch=2.5.1+cu121, cuda=True
  CUDA device: NVIDIA GeForce GTX 1070
  Numba available: True
Loading data from ../build...
  Positions: 616, Shortcuts: 238
  Mutable: 512
  Pre-seeded assignments: 303
  Numba exact evaluator enabled (parity max diff=...).
  Seed fitness (raw): effort=1612, adj=-41662, viol=9219908
Generating 500 random layouts for surrogate training...
Evaluating exact fitness...
  Done in ...s (...ms per layout)
Training surrogate (2.56M params) on cuda...
  Surrogate R^2 = 0.98+
Running evolution: pop=1000, gens=999999
```

Per-generation output (pymoo table):
```
n_gen  |  n_eval  | n_nds  |      eps      |   indicator
```

## What to Report

### 1. Initial startup (first 5 minutes)
Capture first 20 lines. Confirm:
- `Numba exact evaluator enabled` — if not, report it
- `cuda=True` — GPU is active
- Surrogate R² ≥ 0.95 — if below 0.90, report it (fallback will trigger automatically)
- `Running evolution: pop=1000, gens=999999` — correct config

### 2. First 100 generations (critical check)
After ~2 minutes (100 gens × 0.77s), run:
```bash
cd charybdis-optimizer-v2
uv run python -c "import json; r=json.load(open('../build/v2_checkpoint_gen100.json')); print('Best raw viol:', r['best_exact'].get('raw_violations', 'N/A')); print('Best norm viol:', r['best_exact']['violations'])"
```

**Expected**: Raw violations should be **below 9M** by gen 100 (seed was 9.2M). If still above 9.2M, the seed injection may not be working — report it.

### 3. Every 1000 generations
Share last 5 lines of pymoo output.

### 4. Every 10,000 generations
Run diagnostic:
```bash
cd charybdis-optimizer-v2
uv run python -c "import json; r=json.load(open('../build/v2_evolution_results.json')); print('Best raw viol:', r['best_exact'].get('raw_violations', 'N/A')); print('Best norm viol:', r['best_exact']['violations']); print('R2:', r.get('surrogate_r2_history',[])[-1]); print('Gens:', r.get('generation'))"
```

Also check perf report:
```bash
cd charybdis-optimizer-v2
uv run python -c "import json; p=json.load(open('../build/v2_perf_report.json')); print('Per-gen avg:', p.get('per_gen_avg', 'N/A'), 's'); print('Exact eval avg:', p.get('exact_eval_avg', 'N/A'), 's')"
```

### 5. Every 50,000 generations (milestone)
Check if checkpoints exist and have valid data:
```bash
ls -la C:/Users/nos/charybdis-optimizer/build/v2_checkpoint_gen*.json 2>/dev/null | tail -5
```

## DO NOT STOP FOR

- `n_nds` near 1000 — normal for 3-objective MOO.
- `eps` at 0 — evolution may be exploring.
- Slow improvement — expected; 999,999 gens is a long run.
- Run taking days — **8-9 days is expected for 999,999 gens**.
- Output showing "exact eval" lines every 100 gens — normal (exact_eval_every=100).
- "Surrogate R² below gate, retraining" — normal; fallback guardrail is working.
- "Checkpoint gen ..." every 500 gens — normal.
- Checkpoints accumulating — only last 5 kept.

## ONLY Stop If

- Python exception with traceback (capture last 20 lines)
- Process exits with non-zero code
- Machine out of memory/disk
- Machine restart needed
- GPU/driver crash (rare, but possible on long runs)

If it crashes, capture the full traceback and report it. Do not attempt to fix the code.

## Important: This is a Multi-Day Run

**999,999 generations at 0.77s/gen = ~214 hours = ~8.9 days.**

- The run will continue across system sleeps/hibernates as long as Python stays running.
- If the machine restarts, the run is lost. You would need to restart from scratch.
- Checkpoints are saved every 500 gens, but there is no resume-from-checkpoint feature yet.
- If the user wants to pause/resume, they should know: **pausing = losing progress**. No resume feature exists.

## Current Seed Numbers

- **Raw seed fitness**: effort=1612, adj=-41662, viol=9219908
- **Normalized seed fitness**: effort≈83.6, adj≈-39.5, viol≈22.6
- **group_split at seed**: ~3762
- **Target**: Raw violations below 4M (less than half of seed). Below 1M would be excellent.

## Files

- Code: `charybdis-optimizer-v2/`
- Data: `build/canonical.json`, `build/app_shortcut_scores.json`, `build/usage_stats.json`
- Output: `build/v2_evolution_results.json` (after run completes or is killed)
- Checkpoints: `build/v2_checkpoint_gen*.json` (only last 5 kept)
- Performance report: `build/v2_perf_report.json` (after run completes)
- Config: `charybdis-optimizer-v2/config/__init__.py` (fast defaults, do not modify)

## Bottom Line

**Start the run now.** The code has been verified: 20 gens in 15.4s, Numba exact eval is 170x faster, surrogate is GPU-accelerated, R² fallback guardrail works. This is a **8-9 day run**. Let it cook. Report at 1000-gen intervals. Do NOT stop for normal evolution behavior. If the machine needs to restart, warn the user that progress will be lost.
