# Handoff: 100-Gen Validation Run Analysis

## Structural Fixes: CONFIRMED WORKING
- structural: 5000/5000 valid (100%) — every genome has valid exits
- stale SIDs: 0 — pool validation working
- missing_exits: [] — all layers covered (L2, L5, L6, L8, L9, L10)
- coach_base placed on L2, L5, L6, L9, L10; coach_travel_off on L8

## Critical Performance Bug: ensure_structural_exits is 50x Too Slow

**URGENT FIX NEEDED.** `vary` time exploded from 600ms to 27,000-31,000ms per generation.

**Cause:** `ensure_structural_exits()` is called for EVERY offspring genome (5000× per gen) in `vary_population_gpu()` at line 765-772. It runs `shortcut_capability()` on every position of every exit-required layer = `5000 × 6 layers × 56 positions = 1.68M` string-matching capability checks per gen.

**Fix options (pick one):**
1. **Cache capability SIDs** — precompute `exit_sid_set = {sid for sid in pool if shortcut_capability(s, any_position).target == 0}` once at init. Then `ensure_structural_exits` just checks `if any(genome[p.gene_idx] in exit_sid_set for p in layer_pos)` — O(56) set lookups vs 56 string matches.
2. **Run ensure_structural_exits only on GPU-mutated genomes that changed capability positions** — most mutations don't touch coach_base. Only re-check if a capability SID was moved.
3. **Move exit validation into the GPU batch** — check `t_g == coach_base_sid` per layer in a single tensor op for all 5000 genomes simultaneously.
4. **Protect coach_base in operators** — add coach_base SIDs to the protected set so operators can't remove them. Then ensure_structural_exits never needs to repair, just verify once at seeding.

Option 4 is the cleanest: protect structural keys in operators, verify once at seed, skip per-gen repair entirely.

## Layout Quality Issues Found

### Issue 1: ALL Mouse Buttons Missing
**No mouse buttons placed anywhere.** MB1 (imp=45), MB2 (imp=35), MB3 (imp=20), MB4/5 (imp=12) — all unplaced. This is a critical failure on a trackball keyboard with no physical mouse.

**Cause:** Mouse buttons are in the pool but their `category` might be filtered, or the `missing_important` penalty doesn't catch them because they're `base_key` category. Check if `t_very_high_imp_sids` / `t_high_imp_sids` include mouse button SIDs.

**Also:** MB1 is in `open_l0_keys` config but scratch mode uses `"open_l0_keys": []` — so MB1's L0 position is frozen. The optimizer can still place MB1-5 on other layers but chose not to. The `mouse_accessibility` bonus should drive this, but it's apparently not strong enough or not being computed correctly in the new code.

### Issue 2: Right Arrow on L0 Replaced coach_l1_hold
Position (4,4) on L0 — one of the 6 open mutable L0 positions — has `rightarrow` instead of the expected `coach_l1_hold`. **Wait — coach_l1_hold IS at (3,4).** The scratch config has `open_l0_keys: []` meaning ALL L0 is frozen except empty positions. So the open L0 positions are wherever L0 had empty slots, and the optimizer filled (4,4) with rightarrow.

This may be OK — rightarrow at imp=30 on a thumb position is reasonable if coach_l1_hold is already elsewhere. But a single arrow without the group is questionable.

### Issue 3: Low-Importance Keys on Home Row
L4 has Alt+P (imp=0.5), Ctrl+Shift+1 (imp=0.1), Alt+Shift+Down (imp=0.6) on effort=0.0 home row positions. The position_waste penalty should catch this but either:
- The penalty is too weak relative to the benefit of filling positions
- L4 has few shortcuts to place, so low-imp keys fill the remaining home row spots

**Fix:** The position waste penalty `max(0, 4 - imp) * max(0, 2 - effort) * 0.5` at effort=0: `(4 - 0.1) * (2 - 0) * 0.5 = 3.9`. That's a small penalty. Consider increasing the multiplier from 0.5 to 2.0, or making effort=0 positions even more expensive for low-imp keys.

### Issue 4: Scroll Toggle Placed but Arrows Partly Ungrouped
Scroll toggle (Momentary Layer 6) correctly placed on L1 and L2 at (3,2) — great, home row, easy access.

But arrows: 3 on L2 (left hand thumb area + y=3) and 1 on L0. The L2 arrows are leftarrow(3,4), downarrow(4,4), uparrow(3,3) — these are on left thumb + one row up. Rightarrow is missing from L2. The group is split.

**Fix:** group_split weight is 50 but may need the group placement to prefer keeping all 4 together even if it means worse individual positions.

### Issue 5: 31% Population Diversity
Only 1558/5000 unique genomes at gen 20. This is very low — healthy is 70%+. The structural exit repair may be forcing too much convergence (all genomes get the same coach_base placements, reducing diversity).

**Fix:** Vary the coach_base placement position in seeding — don't always place it at the same effort-optimal slot. Randomize among the top 3-5 candidates per layer.

## Metrics Summary (Gen 20)
```
effort=30,573  adj=1,222  viol=-2,162
structural: 100% valid
sid_health: clean
diversity: 31% unique (too low)
position_quality: imp_eff_corr=0.115 (weak — should be negative: high imp on low effort)
timing: 29s/gen (should be 3-5s — ensure_structural_exits bug)
```

## Priority Fixes for Codex
1. **URGENT: Fix ensure_structural_exits performance** — 27s→<100ms by protecting structural keys in operators
2. **Mouse buttons not placed** — verify mouse_accessibility scoring works, check if MB SIDs are in importance tiers
3. **Position waste multiplier** — increase from 0.5 to 2.0 for effort=0 positions
4. **Diversity too low** — randomize coach_base placement positions in seeding
5. **imp_eff_corr should be negative** — currently 0.115 (positive = high-imp keys on HIGH effort positions = wrong). The effort model may need the quadratic scaling adjusted for the new 0-based home row values
