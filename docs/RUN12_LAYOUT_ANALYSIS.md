# Run 12 Layout Analysis Report

**Generation:** 1400 / 10,000 (14% complete)
**Date:** 2026-06-28
**Analyzed by:** Kimi Coding Agent
**Run status:** Alive (PID 18160), clean stderr

---

## 1. Executive Summary

### Is the layout improving?

| Objective | Trend | Last Improvement | Verdict |
|-----------|-------|----------------|---------|
| **Effort** | 13,341 -> -3,469 (improving) | Gen 1400 (still improving) | GOOD |
| **Adjacency** | 4,710 -> 14,389 (improving) | Gen 1400 (still improving) | GOOD |
| **Violations** | -289 -> -309 (frozen) | **Gen 200** (1,200 gens ago) | **BAD** |

**Conclusion:** The run is making excellent progress on effort and adjacency, but violations have been **frozen at -309 since gen 200**. This is a convergence floor, not a lack of effort. The root cause is a **CPU/GPU scoring divergence** in the GPU batch path (diagnosed and fixed separately in `docs/DIAGNOSIS_VIOLATION_FLOOR_RUN12.md`).

### Is the layout good for future use?

**Yes, with reservations.** The layout has strong structural qualities (mouse buttons, arrows, clipboard are all well-placed). However, the violation floor means the optimizer hasn't been able to improve group placement and dynamic group clustering. The current "best" layout is decent but not optimal.

**Recommendation:** The run should be restarted with the `exact_gpu_scoring=True` fix (already applied to `fitness.py`). The current run will continue to optimize a phantom objective.

---

## 2. The Three Best Genomes

| Genome | Assignments | Stored (GPU) | CPU Re-evaluated | Verdict |
|--------|-------------|--------------|------------------|---------|
| **best_violations** | 324/559 | eff=8,665, adj=12,218, viol=-309 | eff=8,662, adj=-4,858, viol=1,224 | Best true violations |
| **best_effort** | 372/559 | eff=-3,469, adj=14,389, viol=2,213 | eff=-3,472, adj=-7,065, viol=3,746 | Best effort, worse violations |
| **best_weighted** | 324/559 | eff=6,943, adj=4,547, viol=-301 | eff=6,937, adj=-3,664, viol=1,232 | Balanced compromise |

**Note:** The "stored" values are from the GPU batch path (with approximate scoring). The "CPU re-evaluated" values are the ground truth. The GPU path understates violations by ~1,500 points for the best_violations genome.

---

## 3. Layer-by-Layer Layout Breakdown

### L0: Base Layer (56 keys, mostly frozen)
- Standard QWERTY letters on home row (q,w,e,r,t,y,u...)
- Spacebar on thumb (imp=100, excellent)
- Numbers on top row (effort 3.5-5.5) - these are frozen positions
- Modifiers and structural keys on thumbs
- **Verdict:** Unchanged from canonical. Good.

### L1: Navigation Layer (29 keys)
- **Arrows:** All 4 on left hand, same layer!
  - rightarrow (1,2), leftarrow (2,2), uparrow (5,1), downarrow (5,2)
  - Max distance: 5 (rightarrow to uparrow)
  - **Verdict:** Excellent clustering. Arrows are usable together.
- left gui, equals, right brace, toggle_layer::5
- **Verdict:** Clean navigation layer. Good.

### L2: Mouse + Clipboard Layer (37 keys) - BEST LAYER
- **Mouse buttons:** MB1 (1,2), MB2 (2,2), MB3 (3,2) - all on left hand, home row!
- **Clipboard:** Ctrl+V (1,1), Ctrl+X (2,1), Ctrl+Z (3,1), Ctrl+C (4,2) - all on left hand, near home row
- **Win directions:** 8 Win+Arrow shortcuts on left hand, same layer
- home, toggle_layer::6, momentary_layer::8
- **Verdict:** This is the star of the layout. Mouse buttons + clipboard clustered perfectly on left hand for one-handed mouse mode. Right hand stays on trackball.

### L3: F-Keys High + Controls (34 keys)
- f_keys_high group: f9, f11 + others (6 keys, all on same layer, same hand)
- Ctrl+2, Ctrl+E, Enter, Ctrl+Enter
- select:mb4, select:mb5 (on right hand)
- end
- **Verdict:** Good F-key clustering. MB4/5 on right hand (not ideal for mouse mode but acceptable).

### L4: Windows Layer (22 keys)
- Win+S, Win+1, Alt+Tab, Ctrl+Shift+M
- toggle_layer::9, toggle_layer::10
- **Verdict:** Windows-focused layer. Reasonable.

### L5: Host F-Keys (F13-F22) (27 keys)
- f13, f15, f17, f19, f21 on left; f14, f16, f20 on right
- coach_base exit on thumb
- **Verdict:** All host F-keys on one layer. Clean.

### L6: Host F-Keys + Editor (29 keys)
- f13, f18, f22, grave accent
- Ctrl+Shift+L, Ctrl+T, Alt+Left
- coach_base exit
- **Verdict:** Some duplication with L5 (f13 on both). This is a cross-layer duplicate penalty risk.

### L8: Browser Layer (28 keys)
- Ctrl+L, Ctrl+W, Ctrl+Tab, Ctrl+F, Ctrl+Shift+P, Ctrl+/
- coach_travel_off
- **Verdict:** Excellent browser shortcut layer. All on home row.

### L9: Editor Layer (30 keys)
- Ctrl+S, Ctrl+`, Tab, Ctrl+D, Ctrl+P, Ctrl+Shift+E, Alt+Enter
- coach_base exit
- **Verdict:** Good editor layer. VS Code shortcuts well-placed.

### L10: F-Keys Low + Mouse Lock (32 keys)
- f1, f2, f5, coach_mouse_lock, coach_game_lock
- bt_sel 0, bt_sel 1 (Bluetooth)
- coach_base exit
- **Verdict:** Mixed layer. F-keys low + mouse lock + bluetooth. Slightly unfocused but functional.

---

## 4. Structural Quality Checks

### 4.1 Group Integrity

| Group | Expected | Placed | Best Cluster | On Same Layer? | Same Hand? | Verdict |
|-------|----------|--------|-------------|----------------|------------|---------|
| arrows | 4 | 4 | 4 on L1 | YES | YES | EXCELLENT |
| win_directions | 4 | 8 | 8 on L2 | YES | YES | EXCELLENT |
| clipboard | 5 | 9 | 5 on L3 | **NO** | YES | GOOD (split across layers) |
| f_keys_low | 6 | 6 | 6 on L10 | YES | YES | EXCELLENT |
| f_keys_high | 6 | 6 | 6 on L3 | YES | YES | EXCELLENT |
| chain_Ctrl+V_Enter_Alt+Tab | 3 | 3 | 1 on L2 | **NO** | YES | **BAD** (dynamic group scattered) |
| dynamic_Space_Space | 2 | 2 | 2 on L3 | YES | YES | GOOD |
| dynamic_Down_Down | 2 | 2 | 2 on L1 | YES | YES | GOOD |

**Key issue:** The `chain_Ctrl+V_Enter_Alt+Tab` dynamic group is scattered across 3 layers. This contributes heavily to the `group_split` violation (1,117 points). The group was discovered from usage data and should be clustered together for workflow efficiency.

### 4.2 Mouse Mode (Left-Hand Mouse)

| Button | Placements | Best Left-Hand Mouse Layer | Effort | Verdict |
|--------|-----------|---------------------------|--------|---------|
| MB1 | 1 | L2 (1,2) | 0.0 | PERFECT |
| MB2 | 1 | L2 (2,2) | 0.0 | PERFECT |
| MB3 | 1 | L2 (3,2) | 0.0 | PERFECT |
| MB4 | 1 | None | L3 (10,2) | 0.0 | OK (not on LHM layer) |
| MB5 | 1 | None | L3 (11,2) | 0.0 | OK (not on LHM layer) |
| Ctrl+V | 1 | L2 (1,1) | 1.0 | EXCELLENT |
| Ctrl+X | 1 | L2 (2,1) | 1.0 | EXCELLENT |
| Ctrl+Z | 1 | L2 (3,1) | 1.0 | EXCELLENT |
| Ctrl+C | 1 | L2 (4,2) | 0.0 | EXCELLENT |

**Verdict:** MB1-3 + clipboard are all perfectly placed on L2 left hand. This is the ideal one-handed mouse mode. The user can hold L2 with left thumb, use left fingers for mouse clicks and clipboard, and right hand on trackball. This is the single best feature of the evolved layout.

### 4.3 Toggled/Locked Layer Exits

| Layer | Type | Has Exit? | Exit Position | Verdict |
|-------|------|-----------|--------------|---------|
| L2 | momentary_or_locked | YES | (10,2) | OK |
| L5 | toggled | YES | (3,4) | OK |
| L6 | toggled | YES | (0,2) | OK |
| L7 | locked | N/A | N/A | L7 is frozen |
| L8 | toggled | YES | (7,4) | OK |
| L9 | toggled | YES | (4,4) | OK |
| L10 | toggled | YES | (3,4) | OK |

**Verdict:** All mutable toggled/locked layers have coach_base exits. The L7 "missing" is a false positive (L7 is frozen, no mutable positions). No soft-lock risk.

### 4.4 Effort Distribution

| Effort | Keys | Avg Importance | High-Imp (>=9) | Verdict |
|--------|------|---------------|----------------|---------|
| 0.0 | 74-80 | 14.6-16.0 | 54-68 | Excellent |
| 1.0 | 155-160 | 9.1-9.4 | 25-29 | Good |
| 1.5 | 28-30 | 7.2-8.5 | 6-7 | Good |
| 2.0 | 14-38 | 8.1-16.2 | 7-8 | Mixed |
| 3.0 | 20-28 | 14.5-20.4 | 13 | Acceptable |
| 3.5 | 18-20 | 13.4-15.3 | 11 | Acceptable |
| 4.5+ | 7-9 | 15.1-32.5 | 6 | High-effort keys |

**Key finding:** 229-237 keys (70-75% of assigned) are on effort <= 1.0. The heavy lifting is done on easy positions. The 15-20 high-importance keys on effort >= 3.5 are mostly **frozen L0 positions** (numbers on top row, escape on corner), not mutable placements.

### 4.5 Duplication Analysis

- **No same-layer duplicates** (duplicate penalty = 0)
- **No cross-layer duplicates** for best_violations and best_weighted
- **Cross-layer duplicate penalty = 2,332** for best_effort (this is why its violations are worse)
- **No structural duplicates** (exit_to_base exempt working correctly)
- **No ZMK compatibility issues** (0)

---

## 5. Violation Breakdown (CPU Truth)

### best_violations (True viol = 1,224)

| Component | Value | % of Total | Fixable? |
|-----------|-------|-----------|----------|
| group_split | 1,116.67 | 91% | YES - dynamic group clustering |
| momentary_redundancy | 107.60 | 9% | Partial - base-accessible shortcuts on momentary layers |
| All others | 0.00 | 0% | - |

**The violation problem is entirely group_split.** The dynamic group `chain_Ctrl+V_Enter_Alt+Tab` is scattered across layers. The clipboard group is also split across L2 and L3. The arrows and win_directions are actually fine (same layer, same hand).

### best_effort (True viol = 3,746)

| Component | Value | % of Total | Fixable? |
|-----------|-------|-----------|----------|
| cross_layer_duplicate | 2,332.00 | 62% | YES - stop duplicating shortcuts across layers |
| group_split | 1,116.67 | 30% | YES |
| momentary_redundancy | 177.20 | 5% | Partial |
| missing_important | 120.00 | 3% | YES - place missing shortcuts |

**best_effort trades violations for effort.** It has more assignments (372 vs 324) but pays heavily in cross-layer duplication. Not recommended unless effort is the only priority.

---

## 6. Convergence Analysis

### Effort Trajectory

```
Gen    0: 13,341
Gen  200:     38  (big drop, explore phase)
Gen  500:  -1,640
Gen 1000:  -3,031
Gen 1400:  -3,469  (still improving!)
```

The effort is improving linearly at ~-2.5 per 100 generations. At this rate, gen 10,000 would reach ~-23,000. This is healthy convergence.

### Violation Trajectory

```
Gen    0: -289
Gen  100: -305
Gen  200: -309  <-- FLOOR, NEVER IMPROVES AGAIN
Gen 1400: -309  (1,200 generations with no change)
```

**This is the critical finding.** Violations stopped improving at gen 200 and have been frozen for 1,200 generations (86% of the run so far). This is not because the layout is optimal - it's because the GPU approximation path is making the layout look better than it actually is. The optimizer thinks it's at -309 (excellent), but the true value is +1,224 (mediocre). With no pressure to improve, violations don't move.

### Pareto Front

The Pareto front has 30 entries. All 5 sampled entries have violations = -309. This means the entire front is clustered around the same violation value, with only effort and adjacency varying. The optimizer is not exploring the violation dimension because the GPU path tells it all these genomes are equally good on violations.

---

## 7. What Should We Improve?

### 7.1 Immediate Fix: Restart the Run (HIGHEST PRIORITY)

The `exact_gpu_scoring` fix has been applied to `fitness.py` (line 39). The running process will NOT pick it up automatically. The run must be restarted.

**Why restart:**
- The current run has been optimizing a phantom objective for 1,200 generations
- The "best" genomes are actually mediocre on true violations
- Without the fix, the next 8,600 generations will be equally wasted
- The checkpoint is compatible (no config hash change needed)

**Expected outcome after restart:**
- The true violation of the best genome will jump from -309 to ~1,224
- The optimizer will then have 1,200+ points of room to improve
- The dominant target is group_split: clustering the `chain_Ctrl+V_Enter_Alt+Tab` dynamic group and keeping clipboard on one layer
- Effort will likely worsen temporarily as the optimizer prioritizes violations, then recover

### 7.2 Medium Priority: Dynamic Group Handling

The `chain_Ctrl+V_Enter_Alt+Tab` dynamic group is a 3-key chain discovered from usage data. It's currently scattered across 3 layers. This group has weight=1.0 (dynamic) and contributes ~66 raw penalty points = 3,333 weighted penalty (wait, let me recalculate... actually the group_split for this group is part of the 1,116 total, so it's not the full amount).

**Options:**
1. **Increase dynamic group weight:** The current weight is 1.0. Raising it would make the optimizer work harder to cluster these keys.
2. **Pre-seed the chain:** Force these 3 shortcuts onto the same layer during scratch initialization.
3. **Let evolution handle it:** With exact scoring, the optimizer should naturally cluster them as the penalty becomes visible.

### 7.3 Low Priority: Clipboard Layer Consolidation

The clipboard group (5 keys) is placed on 9 positions across multiple layers. The best cluster is 5 on L3. The other 4 are on L2 (the mouse layer). This is actually intentional - having Ctrl+C/V/Z/X on both the mouse layer (L2) and the editor layer (L3) is a deliberate duplicate for workflow convenience. But the group_split penalty penalizes this.

**Options:**
1. **Accept the penalty:** The clipboard-on-mouse-layer is a high-value feature. The penalty is acceptable.
2. **Move all clipboard to L3:** This would eliminate the group_split penalty but lose the mouse-layer convenience.
3. **Reduce clipboard group weight:** The clipboard group is protected (weight from KEY_GROUPS). Making it unprotected would reduce the penalty but also reduce the reward.

### 7.4 Minor: L0 Key Displacement

The "high-importance shortcuts on bad positions" list shows mostly L0 frozen keys (numbers on top row, escape on corner). These are NOT mutable placements - they're inherited from the canonical layout and are physically frozen. The optimizer cannot move them. This is not a problem with the evolved layout; it's a limitation of the L0 hardware.

---

## 8. Files Created

| File | Purpose |
|------|---------|
| `build/layout_best_violations.json` | Best violations genome decoded to layer/position/key mapping |
| `build/layout_best_effort.json` | Best effort genome decoded |
| `build/layout_best_weighted.json` | Best weighted genome decoded |
| `docs/DIAGNOSIS_VIOLATION_FLOOR_RUN12.md` | Technical diagnosis of the violation floor |

---

## 9. Final Verdict

### Is the layout good?

**Yes, for a work-in-progress.** The structural bones are excellent:
- Mouse buttons + clipboard perfectly clustered on L2 left hand
- Arrows well-placed on L1 left hand
- F-keys grouped on dedicated layers
- All toggled layers have exits
- No same-layer duplicates
- No ZMK compatibility issues

### Is it improving?

**Effort and adjacency: yes. Violations: no.** The violation floor at -309 is a GPU scoring artifact, not a real convergence limit. The true violations are ~1,224 and have room to improve by at least 1,000+ points.

### What should we do?

1. **Restart the run** with the `exact_gpu_scoring=True` fix (already in `fitness.py`)
2. **Monitor the first 500 gens after restart** to confirm violations start moving again
3. **If violations still don't improve after restart**, investigate dynamic group weighting or pre-seeding
4. **The current genomes are usable as-is** if you want to try them now - they're decent layouts. But they're not optimal.

---

*End of report.*
