# Position Value Model — Charybdis Split Keyboard

## Overview

The Charybdis is a 3x6+3 split keyboard (6 columns per hand, 4 rows + 2-3 thumb keys). Position value is determined by how easily a finger can reach a key from the home row resting position.

## Grid Layout

```
LEFT HAND                          RIGHT HAND
x: 0   1   2   3   4   5     7   8   9  10  11  12
   ─── ─── ─── ─── ─── ───   ─── ─── ─── ─── ─── ───
y0: .   .   .   .   .   .     .   .   .   .   .   .    ← top row (reach up)
y1: .   .   .   .   .   .     .   .   .   .   .   .    ← upper home
y2: .   .   .   .   .   .     .   .   .   .   .   .    ← HOME ROW (fingers rest here)
y3: .   .   .   .   .   .     .   .   .   .   .   .    ← bottom row (curl down)
y4:             .   .   .     .       .                ← thumb cluster (3+4+5 L, 7+8 R)
y5:                 .   .     .                        ← thumb outer (4+5 L, 7 R)
```

Column x=6 does not exist (split gap between hands).

**Only 8 physical thumb positions exist** (5 left: x=3-5 y=4, x=4-5 y=5; 3 right: x=7-8 y=4, x=7 y=5). These repeat across 10 layers = 80 mutable thumb positions total.

## Position Value Tiers (best → worst)

### Tier 1 — Home row, inner columns (BEST)
**y=2, x=1-4 (left) and x=8-11 (right)**

These are where fingers naturally rest. Zero movement needed. Any high-importance shortcut should live here.

Effort: ~1.0

### Tier 2 — Adjacent rows, inner columns  
**y=1 and y=3, x=1-4 (left) and x=8-11 (right)**

One row up or down from home — a small curl or extension. Still very easy.

Effort: ~2.0

### Tier 3 — Home row, outer columns
**y=2, x=0, x=5 (left) and x=7, x=12 (right)**

Home row but at the edges — pinky stretch (x=0, x=12) or index overreach (x=5, x=7). More effort than inner columns.

Effort: ~3.0

### Tier 4 — Thumb cluster (FREE thumb only)
**y=4-5, but only positions where the thumb is NOT holding a layer key**

Thumbs are strong and fast, but on momentary layers one thumb is busy holding the layer switch. The FREE thumb (opposite hand from the hold key) has excellent positions. The BUSY thumb positions are unreachable during momentary layer use.

Effort: ~2.0 (free thumb), ~6.0+ (busy thumb / outer thumb)

### Tier 5 — Adjacent rows, outer columns
**y=1 and y=3, x=0, x=5 (left) and x=7, x=12 (right)**

Edge columns + row movement = double penalty. Pinky reaching up/down, or index overreaching up/down.

Effort: ~4.0

### Tier 6 — Top row, inner columns
**y=0, x=1-4 (left) and x=8-11 (right)**

Full extension upward from home. Reachable but slow and awkward for frequent use.

Effort: ~4.5

### Tier 7 — Top row, outer columns (WORST)
**y=0, x=0, x=5 (left) and x=7, x=12 (right)**

Maximum reach: top row + edge column. Reserved for rarely-used keys.

Effort: ~6.0

## Implementation

In `representation.py`:
```python
ROW_COMFORT = {0: 3.5, 1: 1.0, 2: 0.0, 3: 1.0, 4: 1.5, 5: 2.5}
COL_EFFORT  = {0: 2,   1: 0,   2: 0,   3: 0,   4: 0,   5: 2,
               7: 2,   8: 0,   9: 0,  10: 0,  11: 0,  12: 2}

effort(x, y) = ROW_COMFORT[y] + COL_EFFORT[x]
```

## Effort Matrix

```
         x=0  x=1  x=2  x=3  x=4  x=5    x=7  x=8  x=9  x=10 x=11 x=12
y=0:     5.5  3.5  3.5  3.5  3.5  5.5    5.5  3.5  3.5  3.5  3.5  5.5
y=1:     3.0  1.0  1.0  1.0  1.0  3.0    3.0  1.0  1.0  1.0  1.0  3.0
y=2:     2.0  0.0  0.0  0.0  0.0  2.0    2.0  0.0  0.0  0.0  0.0  2.0  ← HOME
y=3:     3.0  1.0  1.0  1.0  1.0  3.0    3.0  1.0  1.0  1.0  1.0  3.0
y=4:                    1.5  1.5  3.5    3.5  1.5                        ← thumb (8 keys)
y=5:                         2.5  4.5    4.5                             ← thumb outer (3 keys)
```

Thumb effort is further adjusted by `thumb_busy_extra` in `fitness.py` which adds +5.0 when the same-hand thumb is holding a layer key (making busy-thumb positions effectively effort 6.5-9.5).

**Left thumb positions:** x=3,4 y=4 (1.5), x=5 y=4 (3.5), x=4 y=5 (2.5), x=5 y=5 (4.5)
**Right thumb positions:** x=7 y=4 (3.5), x=8 y=4 (1.5), x=7 y=5 (4.5)

## Implications for the Optimizer

1. **High-importance shortcuts** (imp >= 7) should land on Tier 1-2 positions (effort <= 2.0). The fitness function should penalize them quadratically on high-effort positions.

2. **Low-importance shortcuts** (imp < 4) on Tier 1-2 positions are a WASTE. Add a "position waste" penalty: `penalty = (4 - importance) * max(0, 2.0 - effort) * 2.0`. This pushes junk off prime real estate.

3. **Group keys** (arrows, clipboard) should prefer Tier 2-3 positions where they can cluster on the same hand with adequate space, rather than being scattered across Tier 1 positions.

4. **Thumb positions** must account for which thumb is free. On L1 (held by left coach_l1_hold), right thumb positions are free/easy. On L2 (held by left coach_l2_hold), right thumb is free. The `thumb_busy_extra` effort already exists in fitness.py but may not be aggressive enough.

5. **Layer switch keys** (coach holds) should prefer thumb positions (Tier 4) since thumbs are natural for hold-and-press patterns. This is already biased via `layer_switch_penalty` weight.
