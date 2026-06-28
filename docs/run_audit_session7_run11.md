# Run 11 Post-Mortem — Violations Frozen at 5,402

## Run Metadata
- **Config:** 5000 pop, 10,000 gens (reached gen 2600 before external kill)
- **Duration:** 11,845s (~3.3 hours)
- **Gen time:** 4.5s (degraded from 2.4s — vcache hit 52%)
- **best_weighted:** eff=-15,904 viol=5,429
- **best_violations:** eff=-12,697 viol=5,402
- **best_effort:** eff=-21,875 viol=8,896

## Critical Problem: Violations Frozen

Violations dropped from 5,459 (gen 0) to 5,402 (gen 2600) — only 57 points in 2,600 generations. For comparison, previous 100-gen runs dropped violations from 1,800 → 50.

### Violation trajectory:
| Gen | Violations | Change from prev |
|-----|-----------|-----------------|
| 0 | 5,459 | — |
| 100 | 5,418 | -41 |
| 500 | 5,414 | -4 |
| 1000 | 5,410 | -4 |
| 1900 | 5,406 | -4 |
| 2300 | 5,402 | -4 |
| 2600 | 5,402 | 0 |

The violations decrease by exactly 4 every ~500 gens — one penalty component resolves, then nothing. This is a **fixed violation floor**, not a convergence issue.

## What's Causing the Frozen Violations

The `evaluate_full` breakdown shows `violations: 7,554.9` as a single aggregate number with no sub-component breakdown. To identify the source, I analyzed the best_violations genome directly:

### Layout State (best_violations, viol=5,402)
- **Assigned:** 323/559 (58%) — 236 positions empty
- **L0 thumbs:** All filled correctly — coach holds, MB1, spacebar, return enter, leftalt. **This fix is working.**
- **Empty eff=0 positions:** 2 (non-L0)
- **Empty eff≤2.0 positions:** 26
- **Empty eff≤3.0 positions:** 100
- **Mouse:** MB1 on L0, MB2 on L1, MB3 on L2, MB4-5 on L5. **MB2-3 separated from MB1 across 3 layers.**
- **Ctrl+Z:** eff=3.5 on L3 (improved from 5.5! The importance parity boost is working)
- **Duplicates:** coach_base 5x, coach_travel_toggle 3x, coach_game_lock 2x, momentary_layer_layer::6 2x

### Root Cause Hypothesis

The violation score is 5,402 with violations_weight=50.0, so the raw violation amount is 5,402/50 = **108.0 raw violation units**. This likely comes from:

1. **Empty prime position penalty (30 × position_waste_weight = 150 effort, but also violation?)** — 26 empty positions at eff≤2.0. If these contribute to violations, they'd add 26 × some_amount.

2. **L0 thumb structural penalty (80.0 per bad key)** — All L0 thumbs are correctly filled, so this should be 0. Unless the evaluator's `l0_thumb_worthy` classification doesn't match what's actually on the thumbs.

3. **Structural capability duplicates** — "target=0 mode=exit_to_base count=6 excess=3" has been present since gen 0 in every run. These 3 excess exit keys may contribute a fixed violation that can never be resolved because the optimizer can't remove structural keys.

4. **Group splits** — MB2 on L1, MB3 on L2, MB1 on L0. If mouse buttons are in a group with group_split penalty, this creates violations.

5. **Cross-layer duplicates** — coach_base appears 5x. If these trigger cross_layer_duplicate or structural_duplicate penalties, that's 4 excess × some weight.

**The coding agent needs to decompose the violation score into its sub-components to identify exactly which penalties create the floor.**

## What Works

1. **L0 thumbs perfect** — all 6 mutable positions filled with structural keys (coach holds, MB1, leftalt)
2. **Ctrl+Z moved to eff=3.5** (was eff=5.5 for 7 runs) — importance parity boost worked
3. **Win_directions 100%** from gen 0
4. **Arrows 100%** from gen 0
5. **Clipboard 100%** from gen 0
6. **imp_eff_corr improved** to +0.028 (best ever, nearly zero)
7. **Effort** strong at -21,875 (best_effort)
8. **Structural** 100% valid every gen

## What Doesn't Work

1. **Violations frozen at ~5,400** — 2,600 gens with no convergence
2. **f_keys_high=0%** — was 99% in the previous run. The f_keys_high group is completely broken despite being marked protected
3. **MB scattered across L0/L1/L2/L5** — mouse buttons on 4 different layers
4. **236 empty positions** — only 323/559 assigned. The optimizer is leaving positions empty rather than filling them
5. **Gen time degraded** — 4.5s/gen (was 2.4s) due to 52% vcache hit
6. **Adjacency positive** (+9,606 at gen 2600)

## Issues for Coding Agent

### Issue 1: Decompose Violation Score (PRIORITY: CRITICAL)

The aggregate `violations: 7,554.9` hides which sub-penalties are contributing. The coding agent needs to:

1. **Add per-component violation logging** to `evaluate_full()` or create a diagnostic function. Print each violation sub-score separately:
   - `zmk_compatibility` violations
   - `unassignment_penalty`
   - `duplicate` (same-layer)
   - `cross_layer_duplicate`
   - `structural_duplicate`
   - `group_split`
   - `missing_important`
   - `momentary_redundancy`
   - `layer_redundancy`
   - `l0_thumb_structural` (new — the 80.0 per bad key penalty)
   - `empty_prime_position` (new — the 30.0 per empty eff≤1.5 penalty)

2. **Run this diagnostic** on the best_violations genome from the interim results to identify exactly which sub-penalties create the 5,400 floor.

3. **Determine which are fixable vs structural.** For example:
   - If structural_duplicate penalties from 5x coach_base are the floor: the optimizer CAN'T remove exit keys, so this penalty is a permanent tax. Either exempt structural keys from the duplicate penalty or treat them differently.
   - If empty_prime penalties are the floor: the optimizer has 236 empty positions but only 315 pool entries. It physically can't fill them all. The penalty is penalizing an impossibility.

### Issue 2: f_keys_high = 0% (PRIORITY: HIGH)

f_keys_high was 99% at gen 0 in the previous run but 0% in this run. Something changed in the group definition, pool dedup, or protected flag handling. Check:

1. What SIDs are in the f_keys_high group?
2. Are those SIDs in the pool after dedup?
3. Is the group's `protected: true` flag being respected?
4. Did the operator protection fix (only protect if legal at position) accidentally unprotect F-keys?

### Issue 3: Empty Position Count (PRIORITY: HIGH)

323/559 assigned = 58%. With 315 pool entries and 559 positions, even if every pool entry is placed, 244 positions would be empty. Plus structural keys (coach_base, exits, layer switches) add ~20-30 more placements. So ~280-330 assignments is the theoretical max.

**The empty_prime penalty (30 × position_waste) penalizes empty eff≤1.5 positions.** But many of these positions CAN'T be filled because the pool isn't big enough. This creates a permanent violation floor.

**Fix options:**
1. Only penalize empty prime positions on layers where the optimizer has placed at least some content (if a layer has 0 assignments, empty primes aren't "waste" — the layer is just unused)
2. Cap the empty-prime penalty at the number of UNPLACED pool entries (if all pool entries are placed, further empty positions are inevitable)
3. Remove empty-prime from violations entirely and keep it as an effort penalty only (where it doesn't create a floor)

### Issue 4: Mouse Button Scattering (PRIORITY: MEDIUM)

MB1 on L0, MB2 on L1, MB3 on L2, MB4-5 on L5. The generalized mouse mode should cluster MB1-3 on the same left-hand mouse layer. Check if the new operator protections or L0 thumb structural policy interfered with mouse placement scoring.

### Issue 5: Performance Degradation (PRIORITY: LOW)

4.5s/gen with 52% vcache hit. The 50,000-entry cache isn't helping in exploit phase. Consider:
- Reducing cache to 20,000 (save memory, same hit rate)
- Or accepting 4.5s/gen for overnight runs (~12.5 hours for 10,000 gens)

## Convergence Summary

| Metric | Gen 0 | Gen 500 | Gen 2600 | Verdict |
|--------|-------|---------|----------|---------|
| effort | -9,586 | -18,304 | -21,875 | GOOD — improving |
| violations | 5,459 | 5,414 | 5,402 | **FAIL — frozen** |
| imp_eff_corr | +0.093 | — | +0.028 | GOOD — nearly zero |
| arrows | 100% | — | 100% | PASS |
| clipboard | 100% | — | 100% | PASS |
| f_keys_high | 0% | — | 0% | **FAIL — broken** |
| win_directions | 100% | — | 100% | PASS |
| Ctrl+Z | — | — | eff=3.5 | **IMPROVED** (was 5.5) |
| gen time | 3.5s | — | 4.5s | degrading |

## Do NOT Relaunch Until Fixed

The violation floor and f_keys_high=0% need to be resolved before another 10,000-gen run. The violations will never converge below ~5,400 with the current penalty structure.
