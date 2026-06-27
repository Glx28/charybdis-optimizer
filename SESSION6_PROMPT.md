# Session 6: Fix Layout Quality — Scoring, Penalties, and Realism

## Mission

The Charybdis keyboard layout optimizer produces layouts that pass all technical constraints but make bad real-world decisions. Fix the scoring and penalty system so generated layouts are actually usable on a real split keyboard.

## Critical Problems Found from Real Keyboard Testing

### Problem 1: Locked-Area Keys Duplicated
Escape is already at position (0,0) on L0 in the frozen/locked area. The optimizer placed Escape AGAIN on L0 at position (7,5) — one of only 6 open L0 thumb positions. This is a critical waste: it duplicates a key that's already on the same layer, occupying a prime mutable position with something the user already has.

The broader rule: **keys in the locked/frozen area of L0 should NEVER be duplicated anywhere**. They are already placed by the user in optimal positions. Duplicating them — on the same layer or any other layer — wastes positions that high-value shortcuts need. The frozen L0 area contains letters, numbers, punctuation, and structural keys. Only the 6 open L0 positions (coach holds, MB1, leftalt) are mutable.

**Root cause:** The fitness function has `_l0_key_displacement_violation` which penalizes L0-only keys appearing on non-L0 layers, but it doesn't penalize duplicating frozen L0 keys ON L0 itself (in the open positions) or on other layers. The `_duplicate_violations` penalty catches same-layer duplicates but doesn't know which keys are in the frozen area vs the open area.

**Fix needed:** 
1. Build a set of SIDs that are assigned in the frozen L0 positions (the ~50 locked positions). These are "already-have" keys.
2. In both GPU and CPU scoring: any mutable position (anywhere, any layer) that holds an "already-have" SID gets a heavy penalty — proportional to `(50 + importance * 5)`. This is similar to `_l0_key_displacement_violation` but covers ALL layers including L0 open positions.
3. Exception: structural/capability SIDs (coach_base, layer switches) which may legitimately appear on multiple layers.

### Problem 2: Ungrouped Arrow/Navigation Keys
Down arrow placed solo at position (4,5) without the rest of the arrow group. Arrow keys are nearly useless alone — you need Up/Down/Left/Right together. The group placement scoring exists but is too weak relative to individual placement effort.

**Root cause:** `group_split` weight is 20.0 and `group_placement` weight is 2.0. The optimizer can get a better effort score by scattering group members across good individual positions rather than keeping them together in slightly worse positions.

**Fix needed:** Increase `group_split` weight significantly (40-60). Also ensure the `move_group` operator runs frequently enough to keep groups together. The GPU operators skip group checking — verify that the `batch_swap_within_layer` GPU operator doesn't break groups by swapping a group member away from its group.

### Problem 3: Wasteful Base-Return Keys on Momentary Layers
A `momentary_layer` key (return to L0) was placed on L1 in prime real estate. On momentary layers, releasing the thumb holding key ALREADY returns to L0 — an explicit "go to L0" key is redundant. The fitness function apparently rewards having more "exit paths" from layers, but on momentary layers the thumb release IS the exit.

**Root cause:** The `_toggled_base_violation` penalty gives a 5000-point penalty per toggled layer without a `coach_base`. But momentary layers don't need `coach_base` — they auto-return on release. The optimizer may be over-rewarding `coach_base` placement even on momentary layers. Check `LAYER_ACCESS` in `representation.py` — layers with method "momentary" should NOT get bonus for having `coach_base`.

**Fix needed in `fitness.py`:**
1. In the `momentary_redundancy` penalty or a new penalty: penalize `coach_base`/`coach_recover_base`/`to_layer 0` keys on layers with `LAYER_ACCESS` method "momentary" — they're redundant.
2. In `mouse_accessibility` or `group_placement`: do NOT reward `coach_base` on momentary layers.
3. The `_toggled_base_violation` is correct — only toggled/locked layers need explicit exits. Verify it doesn't also check momentary layers.

### Problem 4: Effort Model and Position Value

**ALREADY FIXED in this session:** The effort model in `representation.py` was updated from the old model (which treated thumbs as worst positions) to match real-world ergonomics. The new model:

```python
ROW_COMFORT = {0: 3.5, 1: 1.0, 2: 0.0, 3: 1.0, 4: 1.5, 5: 2.5}
COL_EFFORT  = {0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 7: 2, 8: 0, 9: 0, 10: 0, 11: 0, 12: 2}
```

Home row inner columns (y=2, x=1-4/8-11) = effort 0.0 (best). See `docs/position_value_model.md` for the full breakdown.

**Still needed — position waste penalty:** Low-importance shortcuts (imp < 4) on low-effort positions (effort < 2) should get a penalty. A rarely-used key sitting on home row is a waste. Add to both GPU and CPU paths:
```
waste = max(0, 4 - importance) * max(0, 2 - effort) * 0.5
```
This pushes low-value keys off prime real estate without affecting high-value placements.

### Problem 5: Apply Script Exports Only Changes
`analyze_results.py --export` generates `evolved_apply.js` with only the CHANGED keys from the current layout. This is fragile — if the base layout changes, the apply script becomes inconsistent. 

**Fix needed:** The apply script should export ALL assigned keys across all layers, not just diffs. Check `analyze_results.py` around line 200+ where the export happens.

## Architecture Overview

### Key Files
- `evolve/fitness.py` — 2500+ lines. `evaluate_batch_gpu()` (~650 lines) is the GPU batch scoring. `_violation_score()` (~50 lines) is CPU single-genome violations. Individual penalty methods: `_group_split_violations`, `_duplicate_violations`, `_missing_important_penalty`, `_cross_layer_duplicate_penalty`, `_momentary_redundancy_penalty`, `_toggled_base_violation`, `_l0_key_displacement_violation`.
- `evolve/operators.py` — OperatorContext class + 10 CPU operators + 7 GPU batch operators + GPU crossover.
- `evolve/representation.py` — `LAYER_ACCESS` dict (line ~25) defines which layers are momentary/toggled/locked. `KEY_GROUPS` (line ~64) defines protected groups (arrows, clipboard, mouse_buttons, etc.). `Position` and `Shortcut` dataclasses.
- `evolve/layer_access.py` — `LayerAccessAnalyzer.validate()` checks layer reachability and exit paths. `AccessValidation` dataclass with `access_depths`.
- `evolve/config.json` — normal run weights (25+ weights for effort, violations, etc.)
- `evolve/config_scratch.json` — scratch run weights.
- `evolve/run_evolution.py` — `vary_population_gpu()`, generation loop, seeding, verbose logging.
- `evolve/analyze_results.py` — layout analysis + export to apply script.

### Current Fitness Weights (config.json)
```json
"violations": 50.0,
"group_split": 20.0,        // TOO LOW — groups get scattered
"group_placement": 2.0,     // TOO LOW — group quality not rewarded enough
"duplicate": 40.0,
"cross_layer_duplicate": 25.0,
"momentary_redundancy": 5.0, // Doesn't catch coach_base on momentary
"missing_important": 50.0,
"unassignment": 50.0
```

### Layer Access Methods (representation.py LAYER_ACCESS)
- L0: base (always active)
- L1: momentary (held via coach_l1_hold on L0) — releases to L0 automatically
- L2: momentary_or_locked (can be held OR locked via coach_mouse_lock)
- L3: momentary (held via coach_l3_hold on L0)
- L4: momentary (held via coach_l4_hold on L0)
- L5: toggled (from L1 toggle) — NEEDS explicit exit (coach_base)
- L6: momentary or toggled (from L1/L2) — complex access
- L7: locked (game mode) — NEEDS explicit exit
- L8: toggled (travel toggle) — NEEDS explicit exit
- L9: toggled (from L4 toggle) — NEEDS explicit exit
- L10: toggled (from L4 toggle) — NEEDS explicit exit

**Key insight:** Layers 1, 3, 4 are MOMENTARY — coach_base is REDUNDANT on them. Layers 5, 7, 8, 9, 10 are toggled/locked — coach_base is REQUIRED on them.

### Position Grid
The Charybdis is a 3x6+thumb split keyboard:
- x=0-5 left hand, x=7-12 right hand (x=6 is the split gap)
- y=0-3 main key rows (4 rows × 6 columns × 2 hands = 48 main keys per layer)
- y=4-5 thumb cluster — **only 8 physical thumb positions total** (5 left: x=3-5 y=4, x=4-5 y=5; 3 right: x=7-8 y=4, x=7 y=5)
- `is_thumb` = True for y>=4
- Effort model (ALREADY UPDATED): home row inner (y=2, x=1-4/8-11) = 0.0, adjacent rows = 1.0, outer columns add +2.0, top row = 3.5+. See `docs/position_value_model.md`.
- L0 is mostly frozen (letters, numbers). Only 6 L0 positions are open for mutation (coach holds, MB1, leftalt)

### Genome Encoding
- Integer array of length 559 (all mutable positions across 10 layers)
- Each gene = SID (shortcut ID, 0-341) or -1 (empty)
- Pool has 342 shortcuts (app shortcuts + base keys)
- Each shortcut has: `sid`, `keys`, `importance` (0-10), `app`, `apps`, `base_key`, `modifiers`, `category`

### Performance State
- eval 5000 genomes warm: 377ms (was 14,200ms — 37x faster)
- operators/gen: 600ms
- total gen time: ~1.3s (was 20s)
- All 23 tests pass, GPU/CPU parity max_diff=0.06

## What to Fix (Priority Order)

### 1. Penalize duplication of frozen/locked-area keys
In `evaluate_batch_gpu()` and `_violation_score()`: build a set of SIDs assigned in frozen L0 positions (the ~50 locked positions where the user placed letters, numbers, Esc, etc). Any MUTABLE position (on ANY layer, including the 6 open L0 positions) that holds one of these frozen-area SIDs gets a heavy penalty: `(50 + importance * 5)`. Exception: capability SIDs (`_cap_sid_set`) which serve structural purposes across layers.

The frozen-area SID set can be precomputed once at evaluator init from `current_genome` and the `frozen_l0` position set. Both GPU and CPU paths must get the same penalty for parity.

### 2. Penalize coach_base on momentary layers  
In `evaluate_batch_gpu()` and `_momentary_redundancy_penalty()`: if a position is on a momentary layer (L1, L3, L4) and holds coach_base/coach_recover_base/coach_travel_off, add a penalty. These keys waste positions on layers that auto-return.

### 3. Increase group integrity
- Raise `group_split` weight from 20 to 50 in config.json
- Raise `group_placement` weight from 2.0 to 5.0
- Verify that the GPU `batch_swap_within_layer` operator doesn't break groups — it skips `find_group_at()` checks. The protected_mask covers protected-SID members, but non-protected groups (like F-keys) might get scattered.

### 4. Position waste penalty
Add a new penalty component: for assigned positions with effort <= 2 (easy reach), penalize if the shortcut importance is low (< 4). Formula: `penalty += max(0, 4 - importance) * max(0, 2.0 - effort) * 0.5` for each such position. This pushes low-value keys off prime real estate.

Both GPU and CPU must implement this identically.

### 5. Fix apply script to export all keys
In `analyze_results.py`, the `--export` path should write ALL assigned positions to `evolved_apply.js`, not just changes from the current layout. This ensures the script is self-contained and consistent.

### 6. Validate effort model change
**ALREADY DONE in previous session:** `representation.py` ROW_COMFORT and COL_EFFORT were updated to match real-world ergonomics (see `docs/position_value_model.md`). Home row inner columns (y=2, x=1-4/8-11) = effort 0.0 (best). Thumbs = effort 1.5-2.5 (good). Top row edges = effort 5.5 (worst). All tests and parity must be re-verified since this shifts ALL effort calculations.

## Test Commands
```bash
cd evolve
python -m unittest test_fitness test_layer_access -v
python evaluate_cpu_gpu_parity.py ../build
python -c "import py_compile, pathlib; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('.').glob('*.py')]"
```

## Run Commands  
```bash
# Quick test (200 pop, 20 gens, verbose)
# Add to config.json: "generations": 20, "pop_size": 200, "checkpoint_interval": 10, "verbose_logging": true

# Normal run
python run_evolution.py ../build

# Scratch run
python run_evolution.py ../build --scratch

# Analyze best result
python analyze_results.py ../build --export
```

## Already Implemented (previous session)
- **Effort model rewrite** — `representation.py` ROW_COMFORT/COL_EFFORT updated. Home row inner = 0.0, thumbs = 1.5-2.5.
- **Mouse button importance** — MB2 raised 15→35, MB3 8→20, MB4/MB5 5→12 (no physical mouse, trackball keyboard).
- **Backspace added** to BASE_KEY_IMPORTANCE at 35.0 (was missing).
- **Scroll key (Momentary Layer 6)** — importance raised to 40.0 (was 15.0). This is the ONLY way to scroll on the trackball keyboard. Fixed key_id lookup in `_base_key_and_importance()` so per-layer-key importance entries like `momentary_layer_layer::6` are checked before the generic `momentary layer` fallback.
- **Combo key importance** — `_combo` keys are the same physical key WITH modifiers (e.g., Shift+period=colon on Norwegian input). øæå are ALREADY on L0 locked area (semicolon=ø at x=11 y=2, left_apos=æ at x=12 y=2, left_brace=å at x=12 y=1). The `_combo` versions (semicolon_combo, left_brace_combo etc.) are modifier+key behaviors that get placed on non-L0 layers. Explicit importance values set in PUNCTUATION_IMPORTANCE override the auto-calculated 0.6× fallback.
- **Combo navigation** — Shift+arrow combos (selection shortcuts) added at 18.0 importance.
- **2-layer duplicate penalty** — CPU+GPU parity.
- **All scatter optimizations** — missing_important, finger_balance, app_coherence, cross_layer_consistency.
- **Position value documentation** — `docs/position_value_model.md` with actual 8 thumb positions mapped.

## Logger Recommendation
The usage logger in `../charybdis-tools` should track these non-locked essential keys to get real usage data:
- Mouse buttons (MB1-5) — click counts, frequency, which apps
- Arrow keys — individual vs group usage patterns
- Home/End/PageUp/PageDown — navigation frequency
- F-keys — which F-keys are actually used and how often
- Combo keys (Shift+key) — Norwegian char frequency (Ø, Å, Æ usage)
- Tab/Enter/Escape/Backspace — frequency per app
This data feeds into `build/usage_stats.json` which boosts importance scores dynamically.

## Critical Rules
- NEVER freeze, protect, or manually patch layouts. Fix the algorithm.
- CPU and GPU fitness scoring must produce identical results (max_abs_diff < 1.0 on `evaluate_cpu_gpu_parity.py`).
- All 23 tests must pass.
- Keep the verbose_logging infrastructure (config flag) — it's invaluable for debugging.
- Changes to GPU `evaluate_batch_gpu()` MUST have matching changes in CPU `_violation_score()` / individual penalty methods.
- Measure before/after with `profile_evolution.py ../build`.
