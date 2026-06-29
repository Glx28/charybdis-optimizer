# Kimi Agent Prompt: Improve Charybdis Usage Logger for Optimizer

## Your Task

Improve the AHK usage logger in `charybdis-tools` so that it captures data that is maximally useful for the layout optimizer in `charybdis-optimizer`. The optimizer reads your logs via `build/usage_stats.json` (produced by `pipeline/aggregate_usage.js`). Your job is to make the logger richer, more precise, and more actionable for the optimizer's fitness functions.

## Context

### What the Logger Currently Captures

The logger is `charybdis-tools/ahk/charybdis_helpers.ahk`. It writes to `runtime/shortcut_usage.jsonl` with event types:

- `shortcut` — modifier+key combos (Ctrl+A, Alt+Tab, etc.)
- `functional` — bare keys (Esc, arrows, Enter, etc.) with hold duration
- `layer_key` — keys pressed while on a non-L0 layer
- `typing_counter` — aggregated Space/Backspace/Enter counts
- `mouse` — MB1-MB5 clicks with modifier, count
- `scroll` — Wheel direction with ticks, modifier
- `modifier_tap` — modifier pressed+released without combo (tap detection)
- `app_focus` — app switch events with previous app duration
- `layer_session` — keys pressed during a layer session, duration
- `startup` — logger init

The `prev`/`gap_ms` fields track 2-key sequences. The `repeat_count` field tracks repeated key presses.

### What the Optimizer Needs (from `usage_stats.json`)

The optimizer's `aggregate_usage.js` reads the JSONL and produces:

- `shortcuts[keys].count` — per-shortcut usage count
- `shortcuts[keys].apps` — which apps use each shortcut
- `shortcuts[keys].by_layer` — which layers each shortcut is used on
- `sequences["A -> B"]` — 2-key sequences with avg gap_ms
- `chains["A -> B -> C"]` — 2-5 key chains within same app, within 10s
- `workflows["A -> B -> C"]` — repeated 3-5 key subsequences, count ≥ 3, within 15s, same app
- `layer_sessions[layer]` — session count, avg duration, common keys
- `layer_switch_activations` — how many times each layer was activated
- `hold_heavy[keys]` — keys held ≥ 500ms (avg hold time)
- `modifier_taps` — modifier tap counts
- `mouse_clicks` — per-button, per-app, per-modifier
- `scroll_events` — per-app, per-direction
- `app_time_seconds` — time spent per app (from `charybdis_events.jsonl` + `app_focus`)
- `blind_spots` — high-importance shortcuts the user never uses in apps they spend time in

### What the Optimizer's Fitness Factors Actually Use

1. **Effort Factor** — `shortcuts.count` weighted by importance. Wants high-count shortcuts on low-effort positions.
2. **Adjacency Factor** — `sequences` and `chains`. Wants A→B sequence pairs close together. Wants 2-5 key chains clustered.
3. **Workflow Coherence** — `workflows`. Wants 3-5 key repeated patterns on the same layer.
4. **App Coherence** — `by_app`, `shortcuts.apps`. Wants same-app shortcuts on the same layer.
5. **Cross-Layer Duplicate** — `by_layer_shortcut`. Wants shortcuts used on multiple layers to be placed on the highest-usage layers.
6. **Violation Factor** — `layer_switch_activations`, `layer_sessions`. Wants layer content to match actual usage.
7. **Trackball Proximity** — `mouse_clicks`. Wants mouse-related shortcuts near the trackball. **Currently the logger only captures mouse clicks, not trackball interaction patterns.**
8. **Learning Curve** — `shortcuts.count` over time. Wants to know which shortcuts are newly learned vs. habitual.
9. **Dynamic Groups** — `chains`, `sequences`. Discovers implicit groups from usage patterns.
10. **Blind Spots** — `blind_spots`. Identifies shortcuts the user SHOULD be using but isn't.

## What to Improve

Focus on the following gaps. These are the highest-impact improvements for the optimizer.

### 1. Trackball & Mouse Gesture Data (HIGH IMPACT)

The optimizer has a `trackball_proximity` factor that rewards mouse shortcuts near the trackball, but the logger only captures discrete clicks. It doesn't know:

- Which shortcuts are used *while* the user is actively using the mouse (simultaneous keyboard+mouse)
- Whether the user reaches from the trackball to the keyboard or vice versa
- Trackball button usage (MB1, MB2, MB3) vs. keyboard shortcuts that complement mouse work
- Mouse movement patterns (e.g., moving from trackball to a specific key cluster)

**What to add to the logger:**
- `mouse_session` event type: when the user starts using the mouse (clicks/scroll), track which keyboard shortcuts they use within the same 5-second window. Log as: `{"type": "mouse_session", "started_with": "MB1", "keyboard_shortcuts": ["Ctrl+C", "Ctrl+V"], "duration_ms": 4200, "app": "msedge.exe"}`
- Add a `proximity_hint` field to mouse events: when a keyboard shortcut is used within 2 seconds of a mouse click, log `{"type": "shortcut", "keys": "Ctrl+C", "mouse_context": "MB1", "ms_since_mouse": 450, ...}`
- This lets the optimizer learn: "Ctrl+C and Ctrl+V are often used right after MB1" → they should be near the trackball.

### 2. Error & Correction Detection (HIGH IMPACT)

The optimizer wants to know which shortcuts are hard to use (high error rate = should be on easier positions or a different layer). Currently the logger has no error detection.

**What to add:**
- Detect `shortcut → Backspace` pattern within 2 seconds: this means the shortcut probably didn't do what the user expected (wrong target, wrong layer, etc.). Log as: `{"type": "correction", "attempted": "Ctrl+V", "corrected_with": "Backspace", "gap_ms": 340, "app": "code.exe"}`
- Detect `wrong_layer_sequence`: when the user presses a key on L0, then immediately switches to a non-L0 layer and presses the same key (or similar key), it means they were on the wrong layer. Log as: `{"type": "wrong_layer_correction", "attempted_on_layer": "0", "keys": "Ctrl+F", "switched_to": "1", "corrected_keys": "Ctrl+F", "gap_ms": 280}`
- Detect `modifier_error`: when a modifier is held but the combo fails (no key pressed within 500ms, or the user presses Backspace/Delete/Escape). Log as: `{"type": "modifier_error", "modifier": "Ctrl", "followed_by": "Backspace", "duration_ms": 520}`

These will feed into a new optimizer factor (or improve existing ViolationFactor) that penalizes high-error shortcuts on hard-to-reach positions.

### 3. Layer Transition Efficiency (HIGH IMPACT)

The optimizer's `ViolationFactor._thumb_occupancy()` and `WorkflowCoherenceFactor` need to know whether the user is efficiently using layers. Currently the logger only captures `layer_session` (keys pressed while on a layer) but doesn't know:

- Whether the user switched to the right layer immediately or tried multiple layers
- Layer "switching cost" — time spent bouncing between layers
- Which layer access method was used (momentary hold vs. toggle vs. lock)

**What to add:**
- `layer_transition` event: log every layer switch with entry method. `{"type": "layer_transition", "from": "0", "to": "1", "method": "momentary", "duration_ms": 0, "keys_on_target": 3, "app": "code.exe"}`
  - `method`: `"momentary"` (hold thumb), `"toggle"` (tap to lock), `"lock"` (coach lock key), `"return"` (back to base)
  - `duration_ms`: how long the user stayed on the target layer
  - `keys_on_target`: how many keys were pressed while on the target layer
- `layer_bounce` detection: when the user switches A→B→A within 1 second, log `{"type": "layer_bounce", "layers": ["0", "1", "0"], "total_ms": 800, "app": "code.exe"}`. This indicates wrong layer selection.
- `layer_sticky` detection: when the user stays on a layer for >10 seconds and uses many keys, log `{"type": "layer_sticky", "layer": "1", "duration_ms": 15000, "keys_pressed": 42, "app": "code.exe"}`. This suggests the layer is being used as a "home" for a specific app/workflow.

These will feed into `layer_switch_activations` and `layer_sessions` in the aggregator, and the optimizer can use them to:
- Reward "sticky" layers (good: user stays on layer and works efficiently)
- Penalize "bouncy" layers (bad: user keeps switching back — wrong layer content)
- Prefer momentary access for short sessions, toggle for long sessions

### 4. Hesitation Detection (MEDIUM IMPACT)

The optimizer wants to know which shortcuts are "muscle memory" (fast, consistent) vs. "still learning" (slow, hesitant). This feeds into the Learning Curve factor.

**What to add:**
- `sequence_timing` event: for known 2-key sequences (e.g., Ctrl+C → Ctrl+V), track the gap_ms over time. If the gap increases from ~200ms to ~800ms, the user is hesitating. Log the full distribution, not just the average.
- `shortcut_confidence` field: for each shortcut, track the coefficient of variation (CV = std/mean) of its execution time. Low CV = muscle memory. High CV = still learning. Log as: `{"type": "shortcut_confidence", "keys": "Ctrl+Shift+P", "avg_gap_ms": 1200, "cv": 0.45, "sample_count": 12}`

This is a new data type. The aggregator would need to be updated to produce `shortcut_confidence` data, and the optimizer's `LearningCurveFactor` can use it to penalize placing low-confidence shortcuts on hard positions.

### 5. Contextual App State (MEDIUM IMPACT)

The optimizer's `AppCoherenceFactor` wants same-app shortcuts on the same layer, but apps have different modes. VS Code has "editing mode", "debug mode", "terminal mode". The logger doesn't know which mode the user is in.

**What to add:**
- `app_context` event: infer context from recent shortcuts. For example:
  - `Ctrl+Shift+P` → `"context": "command_palette"`
  - `Ctrl+Shift+F5` → `"context": "debugging"`
  - `Ctrl+`` → `"context": "terminal"`
  - `Ctrl+K, Ctrl+S` → `"context": "settings"`
- This is heuristic. Map a small set of known "context indicator" shortcuts to context labels. If no indicator, context is `"general"`.
- Log as: `{"type": "app_context", "app": "code.exe", "context": "debugging", "inferred_from": "Ctrl+Shift+F5", "ts": "..."}`
- The aggregator then produces `by_context` data, and the optimizer can group shortcuts by context within an app, not just by app.

**Implementation note**: Start with a hardcoded map of 20-30 common "context indicator" shortcuts for the 5 most-used apps (VS Code, Browser, Terminal, Excel, Teams). Don't try to be exhaustive.

### 6. Hand/Finger Data (if ZMK beacon provides it) (MEDIUM IMPACT)

The optimizer evaluates finger balance and same-finger penalty, but the logger doesn't know which hand or finger was used. If the ZMK beacon sends key coordinates (x, y, layer), the logger can infer hand from position.

**What to add:**
- If the `charybdis_state.json` beacon includes `lastKey.x` and `lastKey.y`, map these to `hand` (left/right) using the layout CSV. Left half = left hand, right half = right hand.
- Add `hand` field to `shortcut` and `functional` events: `{"type": "shortcut", "keys": "Ctrl+A", "hand": "left", ...}`
- This feeds into the aggregator's `by_hand` data, and the optimizer's `FingerBalanceFactor` can weight actual hand usage, not just assume 50/50.

**Check first**: Does `charybdis_state.json` include `lastKey.x` and `lastKey.y`? If yes, implement. If not, skip.

### 7. Shortcut Success/Failure (MEDIUM IMPACT)

The logger doesn't know if a shortcut actually worked. Some shortcuts open dialogs, some do nothing in certain contexts, some are silently ignored.

**What to add:**
- Heuristic failure detection: if a shortcut is followed by the same shortcut again within 1 second, it likely failed the first time. Log as: `{"type": "shortcut_retry", "keys": "Ctrl+P", "gap_ms": 450, "app": "code.exe"}`
- Heuristic "no-op" detection: if a shortcut is followed by a completely different shortcut within 500ms (e.g., `Ctrl+F` → `Ctrl+H`), it might mean the first shortcut didn't open the expected dialog. Log as: `{"type": "shortcut_noop_hint", "attempted": "Ctrl+F", "followed_by": "Ctrl+H", "gap_ms": 320, "app": "code.exe"}`
- These are NOT definitive failure signals, but they are strong hints. The optimizer can use them as weak signals in the ViolationFactor.

### 8. Learning Curve Tracking (MEDIUM IMPACT)

The optimizer has a `LearningCurveFactor` that penalizes changes from the reference layout. But it doesn't know which shortcuts the user is actively learning vs. which ones are already mastered.

**What to add:**
- `shortcut_velocity` event: track how many times a NEW shortcut (first seen in last 7 days) is used per day. Log as: `{"type": "shortcut_velocity", "keys": "Ctrl+Shift+Alt+T", "first_seen_days_ago": 2, "uses_today": 5, "uses_yesterday": 1, "uses_2days_ago": 0}`
- The aggregator maintains a rolling window. The optimizer uses this to:
  - Reward placing high-velocity (newly learned) shortcuts on easy positions
  - Penalize changing positions of high-velocity shortcuts (they're being actively learned)
  - Allow changing positions of low-velocity shortcuts (they're either mastered or forgotten)

**Implementation note**: The logger writes raw events. The aggregator (`aggregate_usage.js`) computes velocity. But the logger needs to include `first_seen` timestamp for each shortcut so the aggregator can compute velocity.

## What NOT to Do

- **Don't rewrite everything**. The logger is 1800 lines of AHK v2. Make targeted additions.
- **Don't break existing events**. The `shortcut`, `functional`, `mouse`, `scroll`, `layer_session`, `app_focus`, `modifier_tap`, `typing_counter` event types must remain backward-compatible. The aggregator (`aggregate_usage.js`) depends on them.
- **Don't add events that can't be reliably detected**. If an event type is unreliable (>20% false positives), skip it or make it opt-in via a config flag.
- **Don't change the JSONL format dramatically**. The aggregator reads line-by-line JSON. Each line must be a self-contained JSON object. Add new fields to existing event types, or add new event types.

## Your Plan

1. **Read the current logger** (`charybdis-tools/ahk/charybdis_helpers.ahk`) and understand the event buffering system (`BufferEvent`, `FlushEventBuffer`, `EventBuffer`).
2. **Read the aggregator** (`charybdis-optimizer/pipeline/aggregate_usage.js`) to understand how it processes the JSONL.
3. **Read the optimizer's fitness factors** (`charybdis-optimizer-v2/fitness/factors/*.py`) to understand what data they actually use.
4. **Implement improvements in priority order**:
   - P0: Trackball/mouse gesture data (Item 1)
   - P0: Error & correction detection (Item 2)
   - P0: Layer transition efficiency (Item 3)
   - P1: Hesitation detection (Item 4)
   - P1: Contextual app state (Item 5)
   - P1: Hand/finger data (Item 6) — only if ZMK beacon provides coordinates
   - P1: Shortcut success/failure (Item 7)
   - P1: Learning curve tracking (Item 8)
5. **Update the aggregator** (`aggregate_usage.js`) to process the new event types and produce new fields in `usage_stats.json`.
6. **Test**: Run the logger for a few minutes, generate some events, then run `node pipeline/aggregate_usage.js` to verify the new fields appear in `usage_stats.json`.
7. **Report**: What you changed, what new data is now available, and how the optimizer can use it.

## Files to Modify

- `charybdis-tools/ahk/charybdis_helpers.ahk` — main logger
- `charybdis-optimizer/pipeline/aggregate_usage.js` — aggregator (update to process new events)

## Files to Read (for reference)

- `charybdis-tools/runtime/shortcut_usage_pre_run7_20260628.jsonl` — sample log data
- `charybdis-optimizer/build/usage_stats.json` — current aggregated output
- `charybdis-optimizer-v2/fitness/factors/*.py` — what the optimizer uses
- `charybdis-optimizer-v2/core/loader.py` — how `UsageData` is loaded

## Success Criteria

- The logger produces new event types that the aggregator can process.
- `usage_stats.json` contains new fields that the optimizer can use.
- Existing events (`shortcut`, `mouse`, `layer_session`, etc.) are unchanged and backward-compatible.
- The AHK script still compiles and runs without errors.
- The aggregator still runs successfully on old logs (backward-compatible).

## Start

Begin by reading `charybdis_helpers.ahk` (lines 370-450 for `LogShortcutUsage` and event buffering, lines 746-800 for `LogEventWithRepeatAndSequence`, lines 806-890 for mouse/scroll callbacks). Then read `aggregate_usage.js` to understand the full pipeline. Then implement.
