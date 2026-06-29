# Violation Floor Diagnosis — Run 12 (Gen ~1200)

**Date:** 2026-06-28
**Diagnosed by:** Kimi Coding Agent
**Files changed:** `evolve/fitness.py` (1 line)
**Tests run:** Unit tests, CPU/GPU parity, compile check

---

## 1. Empty Position Math (The Question the Manager Asked)

| Metric | Value |
|--------|-------|
| Total mutable positions | 559 |
| Prime positions (eff ≤ 1.5, non-L0, non-frozen) | **243** |
| Pool size (unique shortcuts) | **316** |
| Structural keys in pool | 15 |
| High-importance shortcuts (≥ 3.0) | 251 |

**Verdict:** Pool size (316) > Prime positions (243). In theory, ALL prime positions can be filled with pool entries. The `empty_prime` penalty (150 per empty prime slot) is **NOT a structural/inevitable floor**. It is a penalty that evolution can resolve by placing shortcuts on prime positions.

**However**, the actual best genome in Run 12 has **10 empty prime positions**, contributing 1,500 to the `position_waste` effort penalty (not violation). This is a small, fixable number.

---

## 2. The Actual Violation Floor in Run 12

### What the Log Shows

From `build/run_logs/scratch_20260628_123511.out.log` (latest gen = 1200):

| Gen | Best Violation | Mean Violation | Max Violation |
|-----|---------------|----------------|---------------|
| 0 | -289 | 10,267 | 14,584 |
| 100 | -305 | 477 | 868 |
| 200 | **-309** | 705 | 1,012 |
| 400 | **-309** | 684 | 967 |
| 600 | **-309** | 683 | 955 |
| 800 | **-309** | 781 | 1,055 |
| 900 | **-309** | 775 | 1,052 |
| 1000 | **-309** | 829 | 1,047 |
| 1100 | **-309** | 854 | 1,037 |
| 1200 | **-309** | 854 | 1,037 |

**Key observation:** The best violation has been frozen at **-309** for **1,000+ generations** (gen 200 through gen 1200). The mean violation fluctuates around 750–850.

### Violation Breakdown of the `best_violations` Genome (GPU-evaluated, as stored in interim)

Loaded from `build/evolution_scratch_results_interim.json`:
- **Stored fitness:** effort=10620.45, adj=12331.00, viol=-309.07
- **Assignments:** 324 positions filled, 316 unique SIDs

**CPU evaluation of the SAME genome (reconstructed evaluator):**
- `group_split`: 1,116.67 (PENALTY, not bonus)
- `momentary_redundancy`: 107.60
- `total`: **1,224.27**

**GPU batch evaluation of the SAME genome:**
- `total`: **-309.07** (matches stored run value)

**CPU vs GPU divergence: 1,533.34 violation points**

This is a massive CPU/GPU divergence. The GPU path says the genome is excellent (viol=-309). The CPU path says it's mediocre (viol=1224).

---

## 3. Root Cause: Non-Exact GPU Scoring (`exact_gpu_scoring=False`)

The `fitness.py` evaluator has two GPU paths:

1. **Exact GPU path** (`exact_gpu_scoring=True`): Mirrors CPU logic exactly, including per-layer same-hand clustering for spatial groups, neighbor checks, and max-distance checks for completeness bonuses.

2. **Non-exact GPU path** (`exact_gpu_scoring=False`, the **current default**): A fast approximation that:
   - Counts group members per layer but **ignores hand split** when computing `best_layer_count`
   - Applies the completeness bonus **once per group** instead of **per layer**
   - **Does not check max-distance** for completeness
   - Skips neighbor-isolation penalties

For genomes with spatial groups (e.g., arrows) split across hands on the same layer, the non-exact GPU path:
- Thinks the group is complete (`best_layer_count = 4`)
- Gives a bonus of `-12` raw per group
- While the CPU correctly sees the group is split and applies a **penalty** of `+20` raw per layer

With weight 50, the difference per group per layer is **1,600 points**. This is the source of the 1,533 divergence.

**Why the official parity test passed:** `evaluate_cpu_gpu_parity.py` already sets `exact_gpu_scoring=True` (line 95). The parity test was validating the exact path, but the actual run was using the approximate path.

---

## 4. Fix Applied

**File:** `evolve/fitness.py`
**Line 39:**

```python
# Before:
self.exact_gpu_scoring = bool(config.get("exact_gpu_scoring", config.get("exact_gpu_adjacency", False)))

# After:
self.exact_gpu_scoring = bool(config.get("exact_gpu_scoring", config.get("exact_gpu_adjacency", True)))
```

This changes the **default** from `False` to `True`. Configs that explicitly set `exact_gpu_scoring` are unaffected. Configs that omit it (like `config_scratch.json`) now use exact scoring.

**Why this is the right fix:**
- The non-exact GPU path is systematically wrong for the very genomes the optimizer finds most interesting (those with complete groups).
- The exact path has negligible performance impact on a GTX 1070 (the parity test runs instantly).
- The `_config_hash` function only hashes `frozen_layers` and `weights`, so this change does **not** invalidate existing checkpoints.

---

## 5. Validation Results

### Unit Tests
```bash
cd evolve && python -m unittest test_fitness test_layer_access -v
```
**Result:** 62 passed, 1 skipped (skipped test is normal — `evolution_results.json` not present).

### CPU/GPU Parity Test
```bash
cd evolve && python evaluate_cpu_gpu_parity.py ../build
```
**Result:** `max_abs_diff effort=0.25 adjacency=0.01 violations=0.00`

### Compile Check
```bash
cd .. && python -m py_compile evolve/*.py
```
**Result:** No errors.

### Exact vs Approximate Comparison (custom diagnostic)

| Mode | CPU Viol | GPU Viol | Diff |
|------|----------|----------|------|
| `exact_gpu_scoring=False` (old default) | 1,224.27 | -309.07 | **1,533.34** |
| `exact_gpu_scoring=True` (new default) | 1,224.27 | 1,224.27 | **0.00** |

---

## 6. What This Means for Run 12

### The Current Running Process
- Run 12 is alive at gen ~1200 with PID 18160.
- The running process loaded `fitness.py` at startup. It **will NOT** pick up the code change automatically.
- The run has been optimizing for GPU violations using the **approximate** path. The "best" genome (viol=-309 on GPU) is actually viol=1224 on CPU.

### Options for the Manager
1. **Let the run continue:** It will keep optimizing the wrong objective, but it won't crash. The final result will be a genome that looks good on GPU but is mediocre on CPU.
2. **Restart the run:** Kill the process, let it pick up the checkpoint with the new code. The run will resume from gen 1200 and start optimizing the correct objective. The best violation will likely jump from -309 to ~1224 (the true CPU value), but then it can actually improve from there.
3. **Wait for next checkpoint:** The run saves a checkpoint every 100 gens. If the Manager wants to restart at the next checkpoint (gen 1300), that's also an option.

**Recommendation:** Restart the run. The current trajectory is optimizing a phantom objective. Better to start optimizing the real one now.

---

## 7. The "Old" Violation Floor (~5,400)

The handoff mentions a floor of ~5,400 from previous runs. Run 12's fixes (exit_to_base exempt, L0 thumb freeze, etc.) already resolved this. The current floor at -309 is a **different artifact** — it's the GPU approximation making the genome look better than it actually is.

Once the run restarts with `exact_gpu_scoring=True`, the "floor" at -309 will disappear. The true violation score will be around 1,200+ for the current best genome. The optimizer will then have room to actually improve violations by:
- Better placing dynamic groups (discovered from usage sequences and chains)
- Reducing momentary_redundancy penalties
- Improving group_split bonuses through better same-layer, same-hand clustering

---

## 8. Files Changed

| File | Change | Lines |
|------|--------|-------|
| `evolve/fitness.py` | Default `exact_gpu_scoring` changed from `False` to `True` | 1 line (line 39) |

---

## 9. Diagnostic Scripts Created

These scripts are for the Manager's reference and can be deleted after review:

- `evolve/diagnose_violations.py` — Empty position math + violation breakdown (general)
- `evolve/diagnose_violations_exact.py` — Exact run reproduction for stored genome
- `evolve/test_exact_gpu.py` — CPU vs GPU with exact/approximate comparison
- `evolve/test_parity_approx.py` — Parity test with approximate scoring (would fail)

---

*End of report.*
