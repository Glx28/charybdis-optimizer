# Codex Handoff: Lessons from the 2964-Gen Scratch Run

## Run Summary
- **Config:** 8000 pop, scratch mode, all session 5+6 optimizations active
- **Duration:** ~4.5 hours across 2 launches (crashed at gen 900, resumed to gen 2964)
- **Early stop:** plateau 400 at gen 2964
- **Best fitness:** effort=4,949, violations=-1,987
- **Outcome:** Numerically excellent but structurally broken (5 layers without exits)
- **Root causes identified and fixed by Codex:** L2 exit, hard constraints, stale SIDs, seeding

This handoff focuses on **what else we learned** that the structural fix doesn't cover.

## Issue 1: Diversity Injection Spam
From gen ~2600 to gen 2964, the diversity injection fired EVERY generation:
```
Injected 400 fresh genomes at plateau 346
Injected 400 fresh genomes at plateau 347
Injected 400 fresh genomes at plateau 348
...
```

**Problem:** The injection threshold is `plateau >= 150` and it fires every gen after that. With 400 fresh genomes per gen (5% of 8000), the population is constantly disrupted but never improves. The fresh genomes are random (via `migrate_shortcut` from scratch) — they're structurally invalid under the new hard constraints, so they immediately get `HARD_INVALID_FITNESS` and waste evaluation budget.

**Fix needed:**
1. Inject only ONCE per plateau milestone, not every gen. E.g., inject at plateau=150, then again at plateau=300, not every gen from 150 onward.
2. Fresh injected genomes must be structurally valid — run `ensure_structural_exits()` on each injected genome before inserting.
3. Consider reducing injection to 2-3% (not 5%) to avoid destabilizing the population.
4. After injection, DON'T reset plateau_count — let the optimizer prove it can improve. If it can't improve even with injection, early-stop is the right outcome.

```python
# Current (broken):
if plateau_count >= 150:
    inject 5%  # fires EVERY gen from 150 onward

# Fixed:
if plateau_count in (150, 250, 350):  # specific milestones only
    inject 2%
    # ensure_structural_exits on each injected genome
```

## Issue 2: Crash at Gen 900 (Silent Death)
The first launch died silently at gen 900 — no error in stderr, no Python traceback. Process just disappeared.

**Likely cause:** CUDA OOM during a large tensor allocation. The GTX 1070 has 8GB VRAM. With 8000 pop, the `evaluate_batch_gpu` allocates ~500MB for the main genome tensor + per-component temporaries. If the validation cache grows large or a tensor op fragments VRAM, an unhandled OOM can kill the process.

**Fix needed:**
1. Wrap the generation loop body in a try/except for `torch.cuda.OutOfMemoryError` — on OOM, call `torch.cuda.empty_cache()`, save checkpoint, and retry the generation.
2. Log VRAM usage at each verbose checkpoint: `torch.cuda.memory_allocated()` and `torch.cuda.max_memory_allocated()`.
3. Consider periodically clearing the validation cache (it grew to 45,000+ entries = significant memory).

## Issue 3: Cache Hit Rate Decay
Cache hit rate dropped steadily during the run:
```
Gen    0: hit=80%
Gen  300: hit=57%
Gen  600: hit=49%
Gen  900: hit=37%
Gen 1500: hit=37-40%  (stabilized but low)
```

**Problem:** In exploit phase, the population becomes more diverse (hamming distance grew from 94 to 250) because crossover creates unique capability fingerprints. Each unique fingerprint = cache miss = full `access_analyzer.validate()` call (0.9ms each). At 40% hit rate with 8000 pop, that's ~4,800 misses × 0.9ms = 4.3s per eval.

**Fix options:**
1. **Coarser cache key:** Instead of hashing ALL 559 positions (where non-cap SIDs are -1), hash only the ~33 positions that actually hold capability SIDs. Two genomes with the same coach_hold/toggle/momentary placements have identical layer access regardless of shortcut differences.
2. **Cache eviction:** LRU eviction instead of bulk deletion at 50,000 entries. Keep the 10,000 most recently used.
3. **Structural validation bypass:** Once the population is 100% structurally valid (which the hard constraint guarantees after gen 0), skip the full `access_analyzer.validate()` and only compute access costs/depths. The validate() call is mostly checking reachability/exits — if those can't change (because structural keys are protected), the result is always "valid."

## Issue 4: Phase Thresholds vs Actual Convergence
The run reached exploit phase at gen 800 (scratch threshold). But it was still making good progress at that point (effort dropping from 11,534 to 4,949 between gen 750-2964). The exploit operator distribution heavily favors `swap_within_layer` (1010/gen) over `migrate_shortcut` (555/gen), which is appropriate for refinement but may be too early.

**Observation:** The run went: explore (0-150) → balanced (150-800) → exploit (800-2964). It spent 2164 gens in exploit, with most improvement happening in the first 500 gens of exploit. The last 1600 gens were mostly plateau with injection spam.

**Suggestion:** Consider adaptive phase based on improvement rate, not fixed gen thresholds. If violations are still dropping >1% per 50 gens, stay in balanced. Only switch to exploit when improvement rate < 0.1% per 50 gens.

## Issue 5: Toggle Layer 6 Flooding
The broken layout had **14 copies of `toggle_layer_layer::6`** scattered across L2, L5, L9, L10. This is because the optimizer found that placing toggle_layer_6 keys costs almost nothing (they're capability SIDs, exempt from many penalties) but adds layer connectivity.

**Problem:** 14 toggle keys to the same layer is wasteful — you only need 1-2 per source layer. The `structural_duplicate` weight (10.0 in config) may not be strong enough.

**Fix:** The structural_duplicate penalty should scale quadratically for capability SIDs appearing more than 3× per target layer. Having 2 ways to reach L6 from L2 is fine. Having 7 is waste.

## Issue 6: Same-Finger Penalty Dominates Effort
Throughout the run, `same_finger_penalty` was consistently 2000-3000 — by far the largest effort component. `finger_balance` was 100-200, `thumb_utilization` 40-70. This suggests the same-finger penalty is either too aggressive or the conjunction pairs create unavoidable same-finger conflicts.

**Check:** Are there conjunction pairs that force two shortcuts onto the same finger because no other placement satisfies both effort and adjacency? The same_finger weight is 2.5 in scratch config — may need reduction to 1.5-2.0 if it's blocking good layouts.

## Issue 7: Low Assignment Rate
The final layout had only 366/559 positions assigned (65%). With 327 shortcuts and 559 positions, theoretical max is 327/559 = 58%. So 366 exceeds pool size — some duplicates exist. But 193 positions are empty, which is expected.

**Not a bug** — just confirms that the pool is smaller than the position count. Consider whether unused positions should have a different cost model (empty positions on high-effort spots = fine, empty positions on home row = wasteful).

## Metrics to Watch in 100-Gen Validation Run
1. **Gen 0: structural=100%** — all genomes valid (confirms seeding fix)
2. **Gen 0: no stale SIDs** — sid_health clean
3. **Gen 10: exit_coverage=all layers** — coach_base on L2/L5/L6/L8/L9/L10
4. **Gen 25: violations dropping** — confirms hard constraint isn't blocking evolution
5. **Gen 50: groups intact >70%** — arrows, clipboard together
6. **Gen 100: effort < 50,000** — reasonable scratch convergence
7. **No diversity injection spam** — plateau should be natural, not forced

## Files Reference
- Overnight logs: `build/run_logs/scratch_overnight_20260627_052949.out.log` (gen 0-900) and `scratch_overnight_resume_20260627_101339.out.log` (gen 900-2964)
- Results: `build/evolution_scratch_results.json`
- Diagnosis docs: `docs/BROKEN_LAYOUT_DIAGNOSIS.md`, `docs/FIXES_AND_METRICS_HANDOFF.md`
