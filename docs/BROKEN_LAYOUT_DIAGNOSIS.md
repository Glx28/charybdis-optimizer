# Broken Layout Diagnosis — Scratch Run 2026-06-27

## The Problem
The overnight scratch run produces layouts with effort=5,153 / violations=-1,866 that look numerically excellent but are **physically unusable** — 5 of 10 layers have no exit key, causing soft-locks.

## Broken Layers

| Layer | Method | Entry Paths | Has Exit? | Status |
|-------|--------|-------------|-----------|--------|
| L1 | momentary | momentary only | thumb release | OK |
| L2 | momentary_or_locked | momentary + **lock** (coach_mouse_lock) | **none** | **SOFT-LOCK** |
| L3 | momentary | momentary only | thumb release | OK |
| L4 | momentary | momentary only | thumb release | OK |
| L5 | toggled | **toggle** from L10 | **none** | **SOFT-LOCK** |
| L6 | toggled | **14 toggle entries** from L2/L5/L9/L10 + 1 momentary | **none** | **SOFT-LOCK** |
| L7 | locked | lock from L10 | coach_base (fixed/immutable) | OK |
| L8 | toggled | **toggle** from L2 + momentary | **none** | **SOFT-LOCK** |
| L9 | toggled | **toggle** from L2 | **none** | **SOFT-LOCK** |
| L10 | toggled | toggle from L3 | coach_base + coach_travel_off | OK |

## Where coach_base IS Placed
- L7: 4× (fixed/immutable, not from genome)
- L10: 1× at (9,0) effort=3.5
- L10: coach_travel_off at (0,3) effort=3.0

**That's it.** Only L7 and L10 have exit keys. L2, L5, L6, L8, L9 are all missing.

## Empty Capacity (room exists for coach_base!)
- L2: 6 empty slots
- L5: 22 empty slots
- L6: 30 empty slots
- L8: 28 empty slots
- L9: 41 empty slots

There are **127 empty positions** on the broken layers. The optimizer CHOSE not to place coach_base there.

## Root Cause Analysis

### The math says it should work
- `_toggled_base_violation` = 5,000 per missing exit
- `violations` weight = 50.0
- Total penalty: 5 layers × 5,000 × 50.0 = **1,250,000** violations
- Best violations in the run is **-1,866** — the penalty should dwarf any benefit of not placing coach_base

### So why doesn't it work?

**The penalty IS being applied but the SELECTION doesn't act on it properly.** Looking at the Pareto front: `pf=2971 eff=[5153,31152] viol=[-1866,4955]`. The violations range goes up to 4,955 — there are solutions with violations but they're on the Pareto front because they have lower effort.

The real issue is **the best-violations solution (-1,866) also lacks exits.** This means:

1. **No genome in the entire population has coach_base on all required layers.** The toggled_base_violation for 5 missing layers = 1,250,000. But the violations objective shows -1,866. This means the violations from toggled_base ARE NOT BEING COUNTED. 

2. **Possible cause: the `_toggled_base_violation` checks `self.toggled_layer_indices`** — if this dict doesn't include L2/L5/L6/L8/L9, those layers won't get the 5000 penalty. Need to verify that `toggled_layer_indices` is correctly populated.

3. **Possible cause: the scratch run uses `config_scratch.json`** which may have different `violations` weight or the `_toggled_base_violation` may read a different weight key.

4. **Possible cause: the validation in `_batch_access_penalties` catches invalid access and sets `HARD_INVALID_FITNESS`** — but if the cache key doesn't change when coach_base is removed (because coach_base is NOT a capability SID in `_cap_sid_set`), then the validation result may be stale/wrong.

**CRITICAL CHECK:** Is `coach_base` in `_cap_sid_set`? If not, removing/adding coach_base doesn't change the cache fingerprint, so the cached validation result is STALE — it may say "valid" when coach_base was present and keep saying "valid" after coach_base is removed.

## Fixes Needed (for Codex)

### Fix 1: Verify coach_base IS a capability SID
In `fitness.py _init_capability_cache()`, check that coach_base, coach_travel_off, coach_recover_base are included in `_cap_sid_set`. The `shortcut_capability()` function in `layer_access.py` checks `behavior_l in ("coach_base", "coach_recover_base", "coach_travel_off")` and returns an `AccessCapability` — so they SHOULD be capability SIDs. But verify the test position used in `_init_capability_cache` doesn't filter them out:

```python
# Current code tests with self.positions[:1] — a single position
for s in self.pool:
    for p in self.positions[:1]:
        cap = shortcut_capability(s, p)
        if cap:
            self._cap_sid_set.add(s.sid)
            break
```

The issue: `shortcut_capability` uses `pos.layer` as the `source` layer. If positions[:1] is L0, then coach_base on L0 produces capability (source=0, target=0, mode=exit_to_base) — this IS a capability. But what if the test misses it? Log `_cap_sid_set` and verify coach_base SID (277) is in it.

### Fix 2: Make toggled_base_violation a HARD constraint, not soft
Instead of 5000 penalty (which gets balanced against other objectives), make missing exits on toggled/locked layers return `HARD_INVALID_FITNESS`. No layout should ever be considered valid without exits on all non-momentary layers.

In `evaluate_batch_gpu()`, after the existing `_toggled_base_violation` GPU computation:
```python
# If any toggled layer lacks coach_base, this genome is INVALID — hard reject
if toggled_base_viol.any():
    # Set effort and violations to HARD_INVALID_FITNESS for affected genomes
```

### Fix 3: Validate the cache fingerprint includes coach_base
The `_t_is_cap_sid` tensor must include coach_base (SID 277), coach_travel_off, coach_recover_base. If these change position in the genome, the cache key MUST change. If coach_base is missing from `_cap_sid_set`, the entire validation cache is silently wrong.

### Fix 4: Add runtime assertion
In `_batch_access_penalties`, after computing validations, add:
```python
# Sanity check: no valid layout should lack exits on toggled layers
for i, val in enumerate(validations):
    if val.valid:
        for layer in analyzer.exit_required_layers:
            if layer in val.reachable_layers:
                has_exit = any(c.source == layer and c.target == 0 for c in val.capabilities)
                assert has_exit, f"Genome {i}: L{layer} reachable but no exit — cache bug?"
```

## Test Data
- Genome source: `build/evolution_scratch_results.json` (best-violations solution)
- coach_base SID: 277
- coach_base NOT in frozen_l0_sids (correct — it's not on L0 in the locked area)
- 17 stale SIDs in genome (pool size changed between runs?)
- Pareto front: 2971 solutions, effort range [5153, 31152], violations range [-1866, 4955]
