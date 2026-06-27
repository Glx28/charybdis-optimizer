# Fix Usage Data Aggregation for Keyboard Layout Optimizer

## Mission

The Charybdis keyboard layout optimizer uses `build/usage_stats.json` to weight shortcut importance by real usage. The raw logger (`../charybdis-tools/runtime/shortcut_usage.jsonl`) captures rich data — 7097 events including mouse clicks by layer, scroll by layer, arrow key usage, layer session durations — but the aggregation pipeline (`pipeline/aggregate_usage.js`) only extracts 25 shortcuts into `usage_stats.json`. Critical non-locked-area keys (mouse buttons, scroll, arrows, navigation, layer switches) are underrepresented or missing entirely.

The optimizer needs accurate usage data for these keys because they're the ones it's PLACING — the locked L0 keys (letters, numbers) don't need usage data since they can't move.

## What the Raw Logger Already Captures (7097 events, 1 day)

The AHK logger at `../charybdis-tools/runtime/shortcut_usage.jsonl` logs these event types:

| Type | Count | What it captures |
|------|-------|-----------------|
| `typing_counter` | 2743 | Bare key presses (Space, Backspace) with counts, app, layer |
| `mouse` | 1404 | MB1-5 clicks with app, layer, modifier state |
| `scroll` | 703 | Scroll direction, ticks, app, layer |
| `shortcut` | 656 | Modifier+key combos (Ctrl+C etc) with app, layer, gap_ms |
| `modifier_tap` | 459 | Standalone modifier press (Ctrl, Alt) with layer |
| `app_focus` | 391 | App switches with duration |
| `layer_key` | 302 | Key presses on non-L0 layers (the most valuable data!) |
| `functional` | 237 | Navigation keys on L0 (arrows, Tab, Esc, Delete, PgDn) |
| `layer_session` | 197 | Layer activation with duration_ms, keys_pressed |
| `startup` | 4 | Logger init |

## What the Aggregator Currently Produces (usage_stats.json)

```json
{
  "shortcuts": { ... },        // 25 entries — ONLY modifier shortcuts, missing bare keys
  "mouse_clicks": { ... },     // 3 buttons — missing per-layer breakdown
  "scroll_events": { ... },    // 2 apps — missing layer info, no total count
  "layer_sessions": { ... },   // 4 layers — OK but lacks duration distribution
  "by_layer_shortcut": { ... }, // exists but sparsely populated
  "blind_spots": [ ... ]       // 137 items — good
}
```

## What's Missing (Critical for Optimizer)

### 1. Arrow/Navigation key usage — NOT aggregated
The `functional` events show:
- Right arrow: 73 uses/day
- Down arrow: 72 uses/day  
- Left arrow: 47 uses/day
- Up arrow: 34 uses/day
- Escape: 7 uses/day (already on L0 — should reduce its importance elsewhere)
- Delete: 2 uses/day
- PgDn: 1 use/day

These are `type: "functional"` events with `keys` field. The aggregator doesn't merge them into `shortcuts`. They should be — they're the SAME keys the optimizer places on layers.

### 2. Mouse button per-layer breakdown — NOT aggregated
Raw data shows:
- MB1: 1146 on L0, 220 on L2, 27 on L1
- MB2: 28 on L0, 22 on L2
- MB3: 25 on L2, 1 on L0
- MB4: 9 on L2, 1 on L0
- MB5: 3 on L2

The aggregator only stores total per-button counts. The optimizer needs per-layer mouse data to know which layer benefits most from mouse buttons (L2 is the mouse layer — MB3/4/5 are almost exclusively used there).

### 3. Scroll usage — NOT properly aggregated
Raw data shows:
- 3842 total scroll ticks across all apps
- By layer: L0=1933, L1=1657, L2=252
- By app: claude=1780, msedge=1004, Codex=951

The aggregator only stores per-app up/down counts. The optimizer needs:
- Total scroll events per day (to weight the scroll toggle key importance)
- Per-layer scroll usage (to know which layers users scroll on)
- The scroll toggle activation is a Momentary Layer 6 — the logger should track when L6 is activated

### 4. Layer-specific key usage — PARTIALLY aggregated
`layer_key` events show what the user presses on each layer:
- L2: Space(85), Backspace(55), Enter(30), Alt+Tab(30), Ctrl+V(12), Ctrl+C(9)...
- L1: Down(3), Ctrl+Shift+J(2), F6(1)...
- L3: Backspace(3), Escape(1)
- L4: Ctrl+Shift+H(1)

This is the most valuable data for the optimizer — it shows what shortcuts the user ACTUALLY uses on each layer. The aggregator has `by_layer_shortcut` but it's sparsely populated and doesn't include `layer_key` or `functional` events.

### 5. Typing counter — NOT used for importance
`typing_counter` events show:
- Space: 2242/day
- Backspace: 859/day

These are locked L0 keys so they don't directly affect placement, BUT they inform importance weighting for the L0 frozen-area duplicate penalty (don't duplicate Space on other layers — it's critical on L0).

### 6. Layer session quality data
Layer sessions track activation count and duration but not:
- Which layer switch key was used to activate the layer
- Whether the user found what they needed (did they press a shortcut, or immediately return?)
- Average keys pressed per session (currently in raw data but not well-aggregated)

## What to Fix

### In the aggregator (`pipeline/aggregate_usage.js`):

1. **Merge `functional` events into `shortcuts`** — arrow keys, Tab, Esc, Delete, PgDn/PgUp are shortcuts that the optimizer places. They need the same `count`, `apps`, `by_layer`, `per_day` structure as modifier shortcuts.

2. **Merge `layer_key` events into `by_layer_shortcut`** — these show actual key usage on non-L0 layers. Currently `by_layer_shortcut` is sparsely populated.

3. **Add `mouse_by_layer`** to usage_stats — per-button per-layer counts. Structure: `{"MB1": {"0": 1146, "1": 27, "2": 220}, "MB2": {"0": 28, "2": 22}, ...}`

4. **Add `scroll_total`** — total scroll ticks per day, and `scroll_by_layer` — per-layer scroll counts. This lets the optimizer weight the scroll toggle key (Momentary Layer 6, importance 40).

5. **Add `layer_switch_activations`** — how many times each layer switch key was pressed (coach_l1_hold, coach_l2_hold, etc). Derived from `layer_session` events + the layer number.

6. **Improve `layer_sessions`** — add `avg_keys_per_session` (sessions with 0 keys = user activated layer but found nothing useful = bad layout signal).

### In the optimizer (`evolve/fitness.py`):

7. **Use `mouse_by_layer`** for per-shortcut usage boost — the usage_boost for MB3 should reflect its total real usage (26×/day), not just its static importance. The per-layer data informs `by_layer_shortcut` so the optimizer knows these buttons ARE used, regardless of which layer they end up on after evolution.

8. **Use `scroll_total`** for scroll key importance boosting — if user scrolls 3842 ticks/day, the scroll toggle key (Momentary Layer 6) should get a massive usage boost. Scrolling is one of the most frequent actions — the key that enables it should be weighted accordingly.

9. **Use `layer_switch_activations`** for coach hold importance — if coach_l1_hold is activated 165×/day vs coach_l4_hold 4×/day, their importance should reflect actual usage. This doesn't constrain which layer they switch TO (layers are mutable), but it tells the optimizer which switch keys the user relies on most.

## File Locations

- **Raw events:** `../charybdis-tools/runtime/shortcut_usage.jsonl` (JSONL, one event per line)
- **Aggregator:** `pipeline/aggregate_usage.js` (Node.js, reads JSONL → writes usage_stats.json)
- **Aggregated output:** `build/usage_stats.json`
- **Optimizer usage:** `evolve/fitness.py` lines 25-120 (reads usage_stats in `__init__`)
- **Pipeline entry:** `pipeline/run_pipeline.js` (runs aggregate_usage as one of 13 modules)

## Event Format Reference

```jsonl
{"type":"mouse","app":"msedge.exe","button":"MB1","count":1,"layer":"0","ts":"..."}
{"type":"scroll","app":"claude.exe","direction":"down","layer":"1","ticks":2,"ts":"..."}
{"type":"functional","app":"claude.exe","keys":"Right","layer":"0","ts":"..."}
{"type":"layer_key","app":"claude.exe","keys":"Space","layer":"2","ts":"..."}
{"type":"shortcut","app":"claude.exe","keys":"Ctrl+V","layer":"0","gap_ms":500,"ts":"..."}
{"type":"typing_counter","app":"claude.exe","count":5,"keys":"Space","layer":"0","ts":"..."}
{"type":"layer_session","app":"claude.exe","layer":"1","duration_ms":3250,"keys_pressed":[],"ts":"..."}
{"type":"modifier_tap","app":"claude.exe","key":"Ctrl","layer":"1","ts":"..."}
{"type":"app_focus","app":"claude.exe","prev_app":"msedge.exe","prev_duration_ms":26906,"ts":"..."}
```

## Important Context: Layer Identity is Dynamic

The optimizer treats layers as mutable containers — **layer identity is emergent, not fixed**. A layer that's currently "mouse mode" might become "navigation + mouse" or something else entirely after evolution. The usage data should inform the optimizer about WHAT the user does (clicks, scrolls, uses shortcuts) and WHERE (which layer), but should NOT hardcode assumptions like "L2 must be mouse layer."

What the data SHOULD express:
- "The user scrolls 3842 ticks/day" → scroll toggle key needs high importance
- "MB3 is used 25× on the current L2" → mouse buttons have real usage on whatever layer they end up on
- "The user activates L1 165 times/day vs L4 only 4 times" → L1 access key is more valuable

What the data should NOT express:
- "L2 is the mouse layer" → the optimizer decides layer roles
- "Mouse buttons must go on L2" → the optimizer places them based on effort + usage + accessibility scoring
- Fixed layer-to-function mappings → layers are flexible

The aggregator should track usage by layer number (since that's what the logger sees), but the optimizer's fitness function interprets this as "shortcuts currently on layer X get this usage boost" — if evolution moves those shortcuts to layer Y, the usage boost follows the shortcut, not the layer.

## What NOT to Change
- Don't modify the AHK logger itself — it's already capturing everything we need
- Don't change the JSONL format — it's working and accumulating data
- Don't break existing usage_stats.json consumers (fitness.py reads specific keys)
- Keep backward compatibility: new fields are additive, don't rename existing ones
- Don't add any layer-role assumptions to the aggregator (no "mouse layer" concept)

## Test
After changes, run:
```bash
node pipeline/run_pipeline.js
```
Then verify `build/usage_stats.json` contains the new fields. The optimizer will automatically pick them up on next evolution run.
