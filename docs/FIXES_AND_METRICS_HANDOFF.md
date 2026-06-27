# Fixes, Metrics Enhancements & General Improvements Handoff

## Critical Bugs (must fix before next run)

### Bug 1: Pool Size Mismatch / Stale SIDs
**Current pool size is 327 but evolved genomes contain SIDs 327-341** (17 stale SIDs). The overnight scratch run was evolving with pool size 342 (from an earlier build), but the current `build_shortcut_pool` produces 327 shortcuts. This means:
- Checkpoints from the overnight run are incompatible with current pool
- Any genome with SID >= 327 will crash CPU eval (`pool[sid]` IndexError)
- GPU eval silently treats stale SIDs as valid (sentinel clamps them)
- Results file contains invalid genomes

**Fix:** 
- Add pool size validation when loading checkpoints — reject if `config_hash` or pool size doesn't match
- Add SID range validation in `evaluate_batch_gpu` and `evaluate`: clamp or reject SIDs >= pool_size
- When resuming, re-run `build_shortcut_pool` and compare size — if different, warn and start fresh
- Store `pool_size` in checkpoint metadata

### Bug 2: L2 Missing from toggled_layer_indices
`toggled_layer_indices` only includes layers where `LAYER_ACCESS[layer]["method"]` is `"toggled"` or `"locked"`. **L2 is `momentary_or_locked` — it's excluded.** But L2 can be LOCKED via `coach_mouse_lock`, meaning it needs a `coach_base` exit when in locked mode.

**Current toggled_layer_indices:** `{5, 6, 8, 9, 10}` — **L2 is missing**

**Fix:** In `fitness.py` where `toggled_layer_indices` is built, include `"momentary_or_locked"`:
```python
# Current (broken):
if info.get("method") in ("toggled", "locked"):

# Fixed:
if info.get("method") in ("toggled", "locked", "momentary_or_locked"):
```

### Bug 3: Validation Cache Allows Invalid Layouts Through
The `_batch_access_penalties` cache uses capability-SID fingerprints. When `coach_base` (SID 277) moves or disappears, the fingerprint DOES change (verified — it's in `_cap_sid_set`). However:

- The cached validation was computed with a DIFFERENT genome that HAD coach_base
- The cache key includes ALL positions (559 × int16 = 1118 bytes per key)
- Two genomes that differ only in non-capability positions get different cache keys even though they have identical layer access

This means the cache is CORRECT but has low hit rates, and the toggled_base penalty IS applied. The real issue is Bug 2 (L2 excluded) combined with the GPU batch path not calling `access_analyzer.validate()` for every genome in the fast path.

**Verification needed:** The GPU `_toggled_base_violation` tensor computation matches CPU. Check if the GPU path uses `self.toggled_layer_indices` (which excludes L2) or a different set.

### Bug 4: GPU/CPU Fitness Divergence for Stale SIDs
CPU `evaluate()` crashes on `pool[sid]` for SID >= 327. GPU `evaluate_batch_gpu()` silently handles it (sentinel clamping). This means the GPU path produces finite fitness for genomes that the CPU path would reject as HARD_INVALID. The saved result fitness `{effort: 22269, viol: -1145}` is GPU-only — CPU gives `HARD_INVALID_FITNESS` for the same genome.

**Fix:** In GPU batch path, add SID range validation:
```python
invalid_sids = (t_g >= S) & (t_g != S)  # SIDs above pool size that aren't sentinel
if invalid_sids.any():
    # Mark those genomes as invalid
```

## Scoring Adjustments

### Issue 5: toggled_base_violation Too Weak as Soft Penalty
Even with the penalty working (20,000 raw × 30 weight = 600,000 violations for 4 missing layers), the optimizer still produced layouts without exits. The multi-objective NSGA-II allows solutions with high violations on the Pareto front if they have low effort.

**Fix:** Make missing exits a HARD constraint, not a soft penalty:
```python
# In evaluate_batch_gpu, after toggled_base_viol computation:
has_missing_exit = (toggled_base_viol > 0)
e[has_missing_exit] = HARD_INVALID_FITNESS
v[has_missing_exit] = HARD_INVALID_FITNESS
```
This ensures NO genome without exits survives selection. coach_base on toggled layers is not optional — it's structural.

### Issue 6: coach_base Importance vs Position Waste Conflict
coach_base has importance=12. The new position_waste penalty penalizes imp<4 keys on eff<2 positions. coach_base at imp=12 is above this threshold. But if coach_base ends up on a high-effort position, the effort score pushes against it. 

Consider: coach_base importance should be context-dependent — on toggled layers it's CRITICAL (no importance score captures "prevents soft-lock"), on momentary layers it's REDUNDANT (the momentary_redundancy penalty handles this). The toggled_base HARD constraint (Issue 5) is the correct fix — don't rely on importance to place structural keys.

### Issue 7: Scratch Config violations Weight Too Low
`config_scratch.json` has `violations: 30.0` vs normal's `50.0`. This was intentional to allow more exploration, but it also weakens ALL violation penalties including structural ones (toggled_base, group_split, duplicates). 

**Fix:** Keep violations at 30 for exploratory balance BUT make toggled_base a hard constraint (Issue 5) so structural integrity doesn't depend on weight tuning.

## Metrics & Logging Enhancements

### Metric 1: Layer Exit Coverage
At each verbose checkpoint, log how many toggled/locked layers have exit keys:
```
exit_coverage: 2/6 layers have coach_base (L7[fixed], L10) — MISSING: L2,L5,L6,L8,L9
```
This immediately flags structural problems without waiting for the full layout analysis.

### Metric 2: Structural Validity Rate
What percentage of the population passes `access_analyzer.validate()`? Currently we track feasibility (violations below threshold) but not structural validity. A population where 0% of genomes have valid layer access is fundamentally broken regardless of fitness scores.
```
structural: 0/8000 valid access (0%) — ALL genomes lack L2 exit
```

### Metric 3: SID Range Health
Log if any genome contains SIDs outside the pool range:
```
sid_health: 17 stale SIDs detected (pool=327, max_sid_in_pop=341)
```

### Metric 4: coach_base Distribution
How many coach_base keys are in the population, and on which layers:
```
coach_base: avg=1.2/genome, layers={L10:95%, L5:3%, L9:2%}
```

### Metric 5: Group Integrity
For each KEY_GROUP, what percentage of the population has the group fully together:
```
groups: arrows=67% intact, clipboard=45% intact, mouse_buttons=89% intact
```

### Metric 6: Position Value Utilization
Are high-effort positions being used for high-importance keys? Compute correlation:
```
position_quality: imp-effort corr=-0.72 (good — high imp keys on low effort positions)
```

## General Improvements

### Improvement 1: Checkpoint Pool Size Validation
Store `pool_size` and `pool_hash` in checkpoint. On resume, compare with current pool — if different, reject checkpoint and start fresh rather than silently evolving with stale SIDs.

### Improvement 2: Runtime Layer Access Validation Sampling  
Every N generations (e.g., every 100), validate a sample of 50 genomes from the population with `access_analyzer.validate()`. If 0% are valid, log a WARNING and consider resetting the population. This catches the "all genomes are structurally broken" failure mode early.

### Improvement 3: Seed Structural Keys First
In `seed_population_scratch`, ensure coach_base is placed on ALL toggled/locked layers BEFORE random shortcut placement. This makes the initial population structurally valid so evolution starts from a viable state.

### Improvement 4: Operator Protection for Structural Keys
The GPU batch operators can remove coach_base from a layer by swapping or migrating it away. Add coach_base to the protected SID set for layers where it's the ONLY exit key. This prevents operators from breaking structural integrity.

### Improvement 5: Toggle Layer 6 Flooding
L6 has 14 `toggle_layer_layer::6` entries across L2/L5/L9/L10. This is because `toggle_layer_layer::6` is a capability SID that the optimizer scatters everywhere (it's useful for reaching L6). But having 14 copies is wasteful. Consider:
- Adding a "structural duplication" penalty for layer-switch keys that appear more than 2-3 times
- Or: treat toggle_layer keys as group members that should cluster, not scatter

### Improvement 6: Pareto Front Validation Filter
When saving interim/final results, filter the Pareto front to ONLY include genomes that pass `access_analyzer.validate()`. Currently the best-violations solution can be structurally invalid (as we found). The analysis/export already checks this, but the saved JSON doesn't.

### Improvement 7: Multi-Run Cross-Pollination
The normal run produces genomes refined from the current layout (structurally valid, high learning curve). The scratch run produces genomes from nothing (may lack structural keys). Cross-seeding: inject top 5% of normal-run elites into scratch population, and vice versa. This ensures structural genes from the normal run help the scratch run.

## Test Data for Verification
```
Pool size: 327 (current), was 342 (overnight run)
coach_base SID: 277
coach_travel_off SID: 320
toggled_layer_indices (current): {5, 6, 8, 9, 10} — MISSING L2
Broken layers in overnight result: L2, L5, L6, L8, L9
Stale SIDs in overnight result: 327-341 (15 unique values, 17 occurrences)
CPU eval of best scratch genome: HARD_INVALID_FITNESS (validation fails on L2)
GPU eval of best scratch genome: effort=22269 viol=-1145 (stale cache + no L2 check)
```
