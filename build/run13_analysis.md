# Run 13 Gen 0 Seed — Physical Layout & Human Performance Analysis

## Executive Summary

Run 13 was killed at generation 0, but its **seed genome is remarkably strong**:
- **Violations: -1314.8** (vs Run 12's best evolved -309)
- **Group integrity: 100%** across all 5 static groups (arrows, clipboard, f-keys, win-directions)
- **Structural validity: 100%** — all layer access/exit paths work
- **324/559 positions assigned** (58%)

However, **human usability has significant issues** that would cause real-world fatigue and confusion. This report identifies those issues and extracts actionable lessons for v2.

---

## 1. Physical Layout Analysis

### Layer Distribution

| Layer | Name | Keys | Left | Right | Thumbs | Assessment |
|-------|------|------|------|-------|--------|------------|
| 0 | Base QWERTY | 56 | 29 | 27 | 8 | Full — good |
| 1 | Navigation | 30 | 16 | 14 | 3 | Underutilized |
| 2 | Mouse QoL | 36 | 22 | 14 | 4 | Heavy left load |
| 3 | Window/App | 36 | 19 | 17 | 4 | Balanced |
| 4 | System/BT | 28 | 15 | 13 | 3 | Balanced |
| 5 | Code/IDE | 27 | 14 | 13 | 3 | Balanced |
| 6 | Scroll | 27 | 15 | 12 | 3 | Balanced |
| 8 | Speed/Travel | 28 | 14 | 14 | 4 | Perfectly balanced |
| 9 | M-Files/DMS | 26 | 14 | 12 | 2 | Slightly left-heavy |
| 10 | Excel | 30 | 17 | 13 | 2 | Left-heavy |

**Issue**: Layers 2 and 10 are left-heavy. Layer 1 (Navigation) is underutilized at only 30 keys when it should be one of the most active layers.

### Key Cluster Placement

#### ✅ **Excellent Clustering**
- **Clipboard (Ctrl+C/V/X/Z)**: All 4 keys on **Layer 2**, with 2 adjacent pairs
  - (1,1), (2,1), (3,1), (4,2) — tight cluster on left hand, home row area
  - This is perfect: copy/paste/cut/undo are all accessible on the same layer, near each other

- **Window Management**: 5 of 6 keys on **Layer 2**
  - (2,0), (4,0), (5,1), (5,2), (9,3) — mostly clustered on left hand
  - Win+Left/Right/Up/Down are near each other

- **Mouse Workflow**: Pre-seeded on Layer 2 left hand
  - (1,3), (2,0), (3,0), (4,0), (4,5), (5,1), (5,2), (5,3) — 8 keys clustered

#### ⚠️ **Scattered Clusters (Human Usability Problem)**
- **Arrow Keys**: 34 keys across **9 different layers!**
  - This is the single biggest usability issue. A human cannot remember which layer has which arrow.
  - Only Layer 2 has a decent cluster (8 keys, 4 adjacent pairs)
  - All other layers have 1-6 arrow keys with poor adjacency

- **F-Keys**: 22 keys across **8 layers**
  - No layer has more than 5 F-keys
  - Layer 4 has 5 but no adjacency
  - Layer 10 has 4 with 2 adjacent pairs (best cluster)

- **Browser Navigation**: 11 keys across **6 layers**
  - Ctrl+Tab, Ctrl+Shift+Tab, Ctrl+T, Ctrl+W, etc. are scattered
  - Layer 8 has 2 adjacent pairs (best)

- **VS Code Shortcuts**: 14 keys across **6 layers**
  - Command palette, file explorer, terminal, etc. all on different layers
  - No layer has more than 4 VS Code keys

- **Teams Shortcuts**: 9 keys across **5 layers**
  - Layer 1 has 4 but no adjacency
  - Layer 3 has 3 with 2 adjacent pairs (good sub-cluster)

---

## 2. Daily Human Workflow Simulation

### Scenario A: Typing & Basic Editing (Layer 0 only)
- **Base layer**: 56 keys fully populated with QWERTY + thumb access keys
- **Thumb cluster**: Spacebar, Enter, layer coaches, Alt
- **Assessment**: ✅ Excellent. No layer switching needed.

### Scenario B: Copy-Paste Workflow
- **Sequence**: Ctrl+C → Ctrl+V → Ctrl+Z (if mistake)
- **Current layout**: All on Layer 2, clustered at (1,1)-(4,2)
- **Assessment**: ✅ Excellent. One layer switch to L2, then all keys are adjacent.

### Scenario C: Window Management (Win+ arrows)
- **Sequence**: Win+Left → Win+Right → Win+Up
- **Current layout**: Win+Left/Right/Up on Layer 2, Win+Down on Layer 6
- **Assessment**: ⚠️ **Problem**. 3 of 4 are on Layer 2, but Win+Down is on Layer 6.
  - User switches to L2, snaps left, snaps right, then must switch to L6 for down.
  - Layer access cost: L2=4.5, L6=2.5 → total access cost = 7.0 for this workflow

### Scenario D: Code Editing (VS Code)
- **Sequence**: Ctrl+Shift+P (command palette) → Ctrl+P (quick open) → Ctrl+` (terminal)
- **Current layout**:
  - Ctrl+Shift+P on Layer 2 (3,4)
  - Ctrl+P on Layer 3 (9,3)
  - Ctrl+` on Layer 8 (9,1)
- **Assessment**: ❌ **Critical Problem**. Three different layers for three core coding shortcuts.
  - Layer switches: L0→L2 (cost 4.5) → L0→L3 (cost 1.5) → L0→L8 (cost 2.5)
  - Total access cost: 8.5 + mental context switching overhead
  - This would be extremely frustrating for a developer.

### Scenario E: Browser Navigation
- **Sequence**: Ctrl+Tab (next tab) → Ctrl+Shift+Tab (prev tab) → Ctrl+T (new tab)
- **Current layout**:
  - Ctrl+Tab on Layer 2 (5,3)
  - Ctrl+Shift+Tab on Layer 1 (10,3)
  - Ctrl+T on Layer 3 (3,3)
- **Assessment**: ❌ **Critical Problem**. Three different layers for basic tab navigation.
  - Layer 1 access cost: 1.5 (good)
  - But Ctrl+Tab on L2 (cost 4.5) and Ctrl+T on L3 (cost 1.5)
  - Total access cost: 7.5

### Scenario F: Arrow Key Navigation
- **Sequence**: Up → Down → Left → Right
- **Current layout**: Arrows on 9 different layers
- **Assessment**: ❌ **Severe Problem**. A human cannot use arrow keys reliably.
  - The "arrows" group has 34 entries because many shortcuts contain "Up", "Down", etc. in their names
  - But even the actual directional arrows (Up, Down, Left, Right) are scattered
  - Layer 2 has the best arrow cluster: (1,3), (2,0), (3,0), (4,0), (4,5), (5,1), (5,2), (5,3)
  - But this mixes actual arrow keys with arrow-containing shortcuts (e.g., "Win+Left", "Alt+Down")

---

## 3. Thumb Cluster Analysis (Critical for Human Use)

The thumb cluster has **36 assignments** across all layers. This is the most physically constrained area of the keyboard.

### Layer 0 Thumb Keys (Base)
| Coord | Key | Effort | Assessment |
|-------|-----|--------|------------|
| (3,4) | coach_l1_hold | 4.5 | ✅ Layer access — correct placement |
| (4,4) | Spacebar | 4.5 | ✅ Essential — correct placement |
| (4,5) | Momentary L6 | 4.5 | ✅ Layer access — correct placement |
| (5,4) | LeftAlt | 4.5 | ⚠️ Alt is a modifier, should be easily accessible |
| (5,5) | coach_l2_hold | 4.5 | ✅ Layer access — correct placement |
| (7,4) | coach_l4_hold | 4.5 | ✅ Layer access — correct placement |
| (7,5) | Return/Enter | 4.5 | ✅ Essential — correct placement |
| (8,4) | coach_l3_hold | 4.5 | ✅ Layer access — correct placement |

**Assessment**: Base layer thumb is well-configured with 8 keys: 5 layer coaches + Space + Enter + Alt.

### Layer 2 Thumb Keys (Mouse QoL)
| Coord | Key | Effort | Assessment |
|-------|-----|--------|------------|
| (3,4) | Down | 4.5 | ⚠️ Arrow key on thumb — awkward |
| (4,4) | Ctrl+Shift+Q | 4.5 | ❌ New meeting (Teams) — should not be on thumb |
| (4,5) | Win+Shift+Right | 4.5 | ❌ Move to right monitor — thumb is wrong place |
| (8,4) | Ctrl+9 | 4.5 | ❌ Hide selected rows (Excel) — not thumb-worthy |

**Assessment**: Layer 2 thumb is overloaded with non-essential shortcuts. The thumb should be reserved for:
- Layer access keys
- High-frequency actions (Space, Enter, Backspace)
- Mouse clicks (if this is the mouse layer)

### Layer 3 Thumb Keys (Window/App)
| Coord | Key | Effort | Assessment |
|-------|-----|--------|------------|
| (3,4) | Ctrl+Shift+End | 4.5 | ❌ Select to last cell — not thumb-worthy |
| (4,4) | Ctrl+Shift+Home | 4.5 | ❌ Select to A1 — not thumb-worthy |
| (5,4) | F10 | 4.5 | ⚠️ Menu key — acceptable but not ideal |
| (8,4) | Win+K | 4.5 | ❌ Connect/Cast — not thumb-worthy |

**Assessment**: Layer 3 thumb has 4 keys, all of which are low-frequency. This is thumb waste.

### Layer 8 Thumb Keys (Speed/Travel)
| Coord | Key | Effort | Assessment |
|-------|-----|--------|------------|
| (3,4) | Ctrl+; | 4.5 | ❌ Insert date (Excel) — not thumb-worthy |
| (4,4) | Ctrl+Shift+! | 4.5 | ❌ Number format (Excel) — not thumb-worthy |
| (8,4) | Win+T | 4.5 | ⚠️ Cycle taskbar — borderline |

**Assessment**: Layer 8 thumb has Excel formatting shortcuts. These should be on finger keys, not thumb.

### Layer 9 Thumb Keys (M-Files/DMS)
| Coord | Key | Effort | Assessment |
|-------|-----|--------|------------|
| (3,4) | Page Down | 4.5 | ⚠️ Acceptable for thumb |
| (4,4) | Page Up | 4.5 | ⚠️ Acceptable for thumb |
| (8,4) | Ctrl+F6 | 4.5 | ❌ Previous section — not thumb-worthy |

**Assessment**: Layer 9 thumb has Page Up/Down which are reasonable for thumb, but Ctrl+F6 is not.

### Layer 10 Thumb Keys (Excel)
| Coord | Key | Effort | Assessment |
|-------|-----|--------|------------|
| (3,4) | Win+M | 4.5 | ❌ Minimize all — not thumb-worthy |
| (4,4) | Win+Ctrl+F4 | 4.5 | ❌ Close desktop — not thumb-worthy |
| (8,4) | Win+P | 4.5 | ❌ Project mode — not thumb-worthy |

**Assessment**: Layer 10 thumb has Windows system shortcuts. These should be on finger keys.

### Layer 4 Thumb Keys (System/BT)
| Coord | Key | Effort | Assessment |
|-------|-----|--------|------------|
| (3,4) | Alt+Shift+- | 4.5 | ❌ Split pane horizontal — not thumb-worthy |
| (4,4) | Alt+Shift++ | 4.5 | ❌ Split pane vertical — not thumb-worthy |
| (8,4) | Page Down | 4.5 | ⚠️ Acceptable |

**Assessment**: Layer 4 thumb has terminal split commands. Terminal power users might appreciate this, but it's niche.

**Thumb Cluster Summary**:
- **Total thumb keys**: 36 across all layers
- **Base layer**: 8 keys, all appropriate
- **Other layers**: 28 keys, many are inappropriate for thumb
- **Problem**: Thumb is being used for low-frequency, complex shortcuts (Ctrl+Shift+Q, Win+Shift+Right, Ctrl+9, etc.)
- **Recommendation**: Limit thumb to 4 keys per layer: layer access + 1-2 high-frequency shortcuts

---

## 4. Modifier Distribution (Critical for Cognitive Load)

### Ctrl+ Combos: 116 shortcuts across 9 layers

| Layer | Count | Examples | Assessment |
|-------|-------|----------|------------|
| 1 | 12 | Ctrl+N, Ctrl+Tab | Navigation — good theme |
| 2 | 10 | Ctrl+V, Ctrl+C | Clipboard — good theme |
| 3 | 15 | Ctrl+7, Ctrl+S | Window/App — acceptable |
| 4 | 10 | Ctrl+Shift+>, Ctrl+Shift+< | Formatting — acceptable |
| 5 | 10 | Ctrl+Alt+Up | Code — acceptable |
| 6 | 18 | Ctrl+Q, Ctrl+Shift+Tab | Scroll/Nav — getting scattered |
| 8 | 15 | Ctrl+W, Ctrl+R | Browser/Speed — acceptable |
| 9 | 18 | Ctrl+Shift+Left | M-Files — too many |
| 10 | 8 | Ctrl+\\, Ctrl+Shift+_ | Excel — acceptable |

**Problem**: Ctrl+ combos are on 9 layers. A human cannot remember which layer has which Ctrl+ shortcut.
- **Cognitive load**: High. User must remember "Ctrl+Tab is on L1, Ctrl+V is on L2, Ctrl+S is on L3..."
- **Layer switching cost**: Every Ctrl+ shortcut requires a layer switch unless the user is already on that layer.
- **Recommendation**: Consolidate Ctrl+ combos to 3-4 layers max, with clear themes:
  - L1: Navigation Ctrl+ (Tab, T, W, R)
  - L2: Editing Ctrl+ (C, V, X, Z, A)
  - L3: App-specific Ctrl+ (S, N, O, P)
  - L8: Browser Ctrl+ (W, R, T, Tab)

### Alt+ Combos: 25 shortcuts across 8 layers

**Problem**: Alt+ shortcuts are scattered across 8 layers. Alt is a common modifier (Alt+Tab, Alt+F4, Alt+arrow). Having Alt+ shortcuts on 8 layers means the user can never rely on muscle memory for Alt+ combos.

### Win+ Combos: 38 shortcuts across 7 layers

**Problem**: Win+ shortcuts are on 7 layers. Windows management shortcuts should be consolidated to 1-2 layers (L2 and L3).

---

## 5. Same-Finger & Finger Balance Analysis

### Same-Finger Penalty: 74.1

This is **relatively high**. The penalty is distributed across:
- Thumb cluster (most severe — 36 keys on thumb positions)
- Left pinky (Ctrl+ combos on left hand)
- Right index (arrow keys and navigation)

### Finger Balance: 199.2

This indicates **uneven load distribution**. The left hand is doing significantly more work than the right hand, especially on:
- Layer 2: 22 left vs 14 right (Mouse QoL — should be more balanced)
- Layer 10: 17 left vs 13 right (Excel — left hand overloaded with formatting)

### Trackball Proximity: 112.7

Mouse-related shortcuts are reasonably close to the trackball position, but could be improved.

---

## 6. Learning Curve: 0.0

The learning curve metric is **0.0**, which is suspicious. This suggests either:
1. The metric is not being computed correctly
2. The layout is somehow perfectly learnable (impossible for 324 shortcuts)
3. The learning curve factor is disabled or broken in this run

**For v2**: The learning curve must be a real, non-zero metric. A layout with 324 shortcuts across 10 layers requires significant learning time.

---

## 7. Critical Issues for Real Human Use

### 🔴 **CRITICAL: Modifier Scattering**
- Ctrl+/Alt+/Win+ combos are on 7-9 layers each
- **Human impact**: User cannot develop muscle memory. Every shortcut requires conscious layer identification.
- **Example**: "I need Ctrl+Tab. Is it on L1, L2, L6, or L8?"

### 🔴 **CRITICAL: Arrow Key Scattering**
- Arrow keys (and arrow-containing shortcuts) on 9 layers
- **Human impact**: Arrow navigation is fundamental. Scattering arrows destroys usability.
- **Recommendation**: All true arrow keys (Up, Down, Left, Right) should be on ONE layer, in a 2x2 cluster.

### 🔴 **CRITICAL: Thumb Overload**
- 36 shortcuts on thumb cluster across all layers
- Many are low-frequency, complex shortcuts (Ctrl+Shift+Q, Win+Shift+Right)
- **Human impact**: Thumb fatigue, missed keys, accidental presses
- **Recommendation**: Max 4 thumb keys per layer. Base layer gets 8 (layer coaches + essentials). Other layers get 4 max.

### 🟡 **MAJOR: Layer Role Ambiguity**
- Layer 2 has: clipboard, window management, mouse, some arrows, some browser nav, some VS Code
- **Human impact**: "What is Layer 2 for?" — too many themes
- **Recommendation**: Enforce strict layer themes:
  - L1: Navigation (arrows, page up/down, home/end, tab switching)
  - L2: Mouse + Clipboard (MB1-3, scroll, Ctrl+C/V/X/Z)
  - L3: Window Management (Win+arrows, minimize, maximize, snap)
  - L5: Code/IDE (VS Code, terminal, IDE shortcuts)
  - L8: Browser (tab nav, bookmarks, refresh, find)
  - L9: M-Files (DMS-specific)
  - L10: Excel (spreadsheet-specific)

### 🟡 **MAJOR: F-Key Scattering**
- 22 F-keys across 8 layers
- **Human impact**: F-keys are used for function shortcuts (F5=refresh, F11=fullscreen). Hard to find.
- **Recommendation**: All F-keys on one layer (L1 or L4), in a single row.

### 🟡 **MAJOR: Layer 1 Underutilized**
- Layer 1 (Navigation) has only 30 keys but should be heavily used
- **Human impact**: Navigation is fundamental. Underutilization means other layers are overloaded.
- **Recommendation**: Move all arrow keys, page up/down, home/end, tab switching to L1. Target: 45+ keys.

### 🟢 **MINOR: High-Effort Base Keys**
- Escape at (0,0) effort=5.5 (far left corner)
- 5 and 6 keys at effort=5.5
- **Human impact**: Minor — these are standard QWERTY positions
- **Acceptable**: Base layer follows QWERTY, so this is expected

---

## 8. What Works Well (Preserve in v2)

1. **Clipboard Clustering on L2**: All 4 clipboard keys adjacent — excellent
2. **Window Management on L2**: 5 of 6 keys clustered — good
3. **Mouse Pre-seeding on L2**: 8 mouse keys on left hand — excellent for trackball users
4. **Structural Validity**: 100% — all layers have proper access/exit paths
5. **Group Integrity**: 100% — static groups are perfectly preserved
6. **Base Layer**: 56 keys fully populated with standard QWERTY + thumb access
7. **Layer 8 Balance**: Perfect 14/14 left/right split

---

## 9. Lessons for v2

### 9.1 Fitness Function Improvements

| Issue | v1 Status | v2 Recommendation |
|-------|-----------|-------------------|
| Modifier scattering | Not penalized | Add **modifier consolidation penalty**: -500 per modifier type on >4 layers |
| Arrow scattering | Partial (group_split) | Add **arrow consolidation requirement**: all arrow keys must be on same layer, adjacent |
| Thumb overload | Not penalized | Add **thumb limit penalty**: >4 thumb keys per layer = -50 per excess |
| Layer role ambiguity | Partial (layer_demand) | Add **theme coherence bonus**: +100 if layer has >70% keys from single theme |
| F-key scattering | Not penalized | Add **F-key consolidation**: all F-keys on same layer |
| Same-finger penalty | Weak (74.1 is high but not penalized enough) | Strengthen thumb same-finger penalty by 3× |
| Finger balance | Weak (199.2 is unbalanced) | Add **hand balance penalty** if left/right ratio > 1.5:1 |
| Learning curve | Broken (0.0) | Fix and weight learning curve properly |

### 9.2 Pre-seeding Improvements

| v1 Pre-seeding | v2 Improvement |
|----------------|----------------|
| Static groups (arrows, clipboard, etc.) | ✅ Keep — excellent results (-1400 group_split) |
| Dynamic groups (discovered from usage) | ✅ Keep — but add **theme enforcement** |
| Mouse workflow on L2 left hand | ✅ Keep — excellent for trackball |
| Structural exits | ✅ Keep — 100% validity |
| Greedy importance fill | ⚠️ **Replace with theme-aware fill**: don't just fill by importance, fill by layer theme |

### 9.3 Configuration Changes for v2

```yaml
# v2 config additions
fitness:
  # New penalties
  modifier_consolidation:
    enabled: true
    max_layers_per_modifier: 4  # Ctrl+ on max 4 layers
    penalty_per_excess_layer: -100
  
  arrow_consolidation:
    enabled: true
    required_layer: 1  # All arrows on L1
    adjacency_required: true
    penalty: -500
  
  thumb_limits:
    enabled: true
    max_per_layer: 4
    base_layer_max: 8
    penalty_per_excess: -50
  
  theme_coherence:
    enabled: true
    min_theme_pct: 0.70
    bonus: 100
  
  f_key_consolidation:
    enabled: true
    required_layer: 4  # All F-keys on L4
    penalty: -200
  
  finger_balance:
    max_hand_ratio: 1.5
    penalty: -20
  
  same_finger:
    thumb_weight: 3.0  # 3× penalty for thumb same-finger
```

### 9.4 Layer Theme Definitions (v2)

| Layer | Theme | Expected Shortcuts | Target Keys |
|-------|-------|-------------------|-------------|
| 0 | Base | QWERTY, numbers, layer access | 56 (fixed) |
| 1 | Navigation | Arrows, PgUp/PgDn, Home/End, Tab switching, F-keys | 45+ |
| 2 | Mouse + Clipboard | MB1-3, scroll, Ctrl+C/V/X/Z, Win+arrows (window snap) | 40+ |
| 3 | Window/App | Alt+Tab, Win+Tab, taskbar switching, app switching | 35+ |
| 4 | System/BT | Bluetooth, media, volume, brightness, system settings | 30+ |
| 5 | Code/IDE | VS Code, terminal, IDE shortcuts, debugging | 35+ |
| 6 | Scroll | Scroll up/down, zoom, pan, M-Files scroll | 30+ |
| 8 | Browser | Tab nav, bookmarks, refresh, find, history | 35+ |
| 9 | M-Files | DMS-specific: check-in/out, metadata, search | 30+ |
| 10 | Excel | Spreadsheet: formatting, formulas, navigation, cells | 35+ |

---

## 10. Conclusion

Run 13's gen 0 seed is **structurally excellent** but **human-unfriendly** in its current form. The algorithm optimized for:
- ✅ Group clustering (group_split = -1400)
- ✅ Structural validity (100%)
- ✅ Violation minimization (viol = -1314)

But it failed to optimize for:
- ❌ Modifier consolidation (Ctrl+ on 9 layers)
- ❌ Arrow consolidation (arrows on 9 layers)
- ❌ Thumb ergonomics (36 thumb keys, many inappropriate)
- ❌ Layer theme coherence (layers have mixed purposes)
- ❌ Cognitive load / learnability

**v2 must add these human-centric constraints to the fitness function.** The current v2 fitness only has 7 factors (effort, adjacency, finger_balance, same_finger, violations, thumb_utilization, trackball_proximity). It needs:
1. **Modifier consolidation factor**
2. **Arrow consolidation factor**
3. **Theme coherence factor**
4. **Thumb ergonomics factor** (not just utilization, but appropriateness)
5. **Learning curve factor** (fix the broken metric)
6. **Hand balance factor** (strengthen from current weak implementation)

**The v2 rewrite has a strong foundation. These 6 additional factors will make it human-usable.**
