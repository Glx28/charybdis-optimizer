# Charybdis Keymap Baseline Report
Generated: 2026-06-27T02:45:13.709Z

## Summary

| Metric | Value |
|--------|-------|
| Total keys | 659 |
| Active layers | 12 |
| Apps tracked | 13 |
| Total app shortcuts | 532 |
| Shortcuts mapped | 473 (89%) |
| Workflows tested | 28 |
| Workflows passing | 28/28 |
| Sync mismatches | 16 |
| Layer contexts | 15 |

## App Coverage

| App | Weight | Shortcuts | Mapped | Coverage | Efficiency |
|-----|--------|-----------|--------|----------|------------|
| Microsoft Teams | 1 | 44 | 43 | 98% | 67% |
| Windows 11 | 1 | 52 | 42 | 81% | 58% |
| Browser (Chrome/Edge) | 0.95 | 89 | 73 | 82% | 58% |
| Visual Studio Code | 0.9 | 76 | 69 | 91% | 60% |
| M-Files Desktop Client | 0.85 | 37 | 36 | 97% | 69% |
| M-Files Admin | 0.85 | 17 | 16 | 94% | 62% |
| Microsoft Outlook | 0.7 | 30 | 29 | 97% | 71% |
| Microsoft Excel | 0.5 | 58 | 49 | 84% | 57% |
| File Explorer | 0.45 | 31 | 24 | 77% | 58% |
| Windows Terminal / PowerShell | 0.4 | 26 | 22 | 85% | 62% |
| Microsoft Word | 0.3 | 29 | 27 | 93% | 69% |
| Microsoft PowerPoint | 0.2 | 27 | 27 | 100% | 68% |
| Discord | 0.2 | 16 | 16 | 100% | 64% |

## High-Frequency Unmapped Shortcuts

| Importance | App | Shortcut | Action | Frequency |
|-----------|-----|----------|--------|-----------|
| 9.0 | Visual Studio Code | Ctrl+` | Toggle terminal | constant |
| 8.5 | M-Files Desktop Client | Alt+Enter | Properties / metadata card | constant |
| 6.0 | Windows 11 | Win+Down | Minimize / restore | high |
| 6.0 | Windows 11 | Win+V | Clipboard history | high |
| 6.0 | Windows 11 | Win+3 | Open/switch pinned app 3 | high |
| 5.7 | Browser (Chrome/Edge) | Ctrl+Shift+Tab | Previous tab | high |
| 5.7 | Browser (Chrome/Edge) | H | Go back in history | high |
| 5.7 | Browser (Chrome/Edge) | J | Previous tab | high |
| 5.7 | Browser (Chrome/Edge) | K | Next tab | high |
| 5.4 | Visual Studio Code | Alt+Click | Add cursor at position | high |
| 5.4 | Visual Studio Code | F3 | Find next | high |
| 5.1 | M-Files Admin | Alt+Enter | Properties | high |
| 3.0 | Microsoft Excel | Ctrl+Shift++ | Insert cells/rows/columns | high |
| 2.7 | File Explorer | Ctrl+Click | Select multiple (non-adjacent) | high |
| 2.7 | File Explorer | Shift+Click | Select range | high |

## Layer Map

### Layer 0: Base QWERTY

    Esc    1      2      3      4      5       │  6      7      8      9      0      BkSp      y0
    Tab    Q      W      E      R      T       │  Y      U      I      O      P      å         y1
    Shft   A      S      D      F      G       │  H      J      K      L      ø      æ         y2
    Ctrl   Z      X      C      V      B       │  N      M      ,      .      /      \         y3

### Layer 1: Navigation

    Win+B  ·      F      Ctrl+1 Win+I  Ctrl+Shift+G  │  ·      Ctrl+O ·      ·      ·      ·         y0
    Code   Alt+F12 Win+Tab Ctrl+Shift+W Shift+Alt+Right V       │  Ctrl+Shift+E Ctrl+Shift+H Win+R  Ctrl+Shift+C Ctrl+Up ·         y1
    Ctrl+G leftarrow_combo Ctrl+Shift+U Scroll Speed  f2      │  Search ↓      ↑      →      Ctrl+End Win+Up    y2
    ·      ·      f5     ·      Up     Ctrl+Shift+A  │  C      Ctrl+K coach_game_lock ·      Shift+Alt+Down ·         y3

### Layer 2: Mouse QoL

    Snip   f9     Desktop f10    Ctrl+Shift+G Scroll  │  ·      Ctrl+2 ·      Ctrl+F ·      ·         y0
    Win+E  Ctrl+Shift+K Close  Enter  F5     Zoom In  │  Win    Enter  Ctrl+S minus  f6     Cut       y1
    MB4    Ctrl+H MB2    MB3    Ctrl+I Ctrl+6  │  Ctrl+C f4     coach_travel_toggle coach_base f5     Scroll    y2
    ·      ·      Shift+Alt+A Ctrl+G Ctrl+Shift+E Paste   │  Shift+Alt+Down pageup ·      Undo   Speed  Ctrl+Shift+Enter    y3

### Layer 3: Window/App

    ·      ·      equal  Emoji  QSett  Notif   │  TskCy  ·      Ctrl+P BT?    left bracket_combo ·         y0
    BT1    f17    ·      →      Win+M  Lang    │  TskMg  Ctrl+Shift+V ·      f16    Ctrl+Shift+K Shift+F8    y1
    Ctrl+U ·      Ctrl+G 1      4      5       │  Search ·      Ctrl+/ ;      Ctrl+Shift+H Ctrl+Shift+E    y2
    Ctrl+O ·      ·      Voice  S      ·       │  Tab    Ctrl+Y BT3    Ctrl+R Ctrl+Tab Ctrl+Shift+N    y3

### Layer 4: System/BT

    BT0    BT1    BT2    BT3    BT4    ·       │  Ctrl+Shift+X f6     ·      Studio Unlock Ctrl+Enter Bootloader    y0
    Ctrl+G Ctrl+O F15    F16    F14    return enter  │  Ctrl+S end    ·      Ctrl+L delete Ctrl+U    y1
    Backspace F19    F20    F21    Ctrl+I right bracket  │  ·      leftshift left bracket f12    f5     Share     y2
    Excel  Shift+Alt+Up DMS    Ctrl+D Tab    F22     │  Ctrl+Shift+V home   f11    f7     Hangup Accept    y3

### Layer 5: Code/IDE

    ·      ·      Stop   ·      GoSym  ·       │  Ctrl+Shift+H Ctrl+G Win+Ctrl+D Explr  ·      ·         y0
    Wrap   Ctrl+Shift+F f18    Win+Ctrl+Right InsUp  Ctrl+Shift+`  │  ·      ·      Ctrl+W f1     backslash ·         y1
    Ctrl+N Save   Ctrl+J Sett   DelLn  Ctrl+Shift+S  │  ·      ·      Ctrl+L ·      coach_travel_toggle ·         y2
    ·      PstNF  ·      NTerm  Ext    f8      │  ·      ·      ·      keypad 3 ·      ·         y3

### Layer 6: Scroll

    ·      ·      ·      Alt+=  Ctrl+Left ·       │  ·      Ctrl+Q ·      ·      ·      ·         y0
    ·      ·      Ctrl+Space F10    Win+Shift+Left Ctrl+Right  │  Ctrl+Shift+R Alt+Right Ctrl+5 Ctrl+Shift+Left ·      ·         y1
    ·      Ctrl+Shift+Down F9     ·      Ctrl+3 Win+Space  │  ·      Ctrl+4 F5     Ctrl+Alt+Down Ctrl+Shift+Up ·         y2
    ·      ·      Ctrl+Shift++ Shift+F11 Win+Shift+Right F4      │  Ctrl+Shift+I Ctrl+Shift+T Ctrl+6 Ctrl+Shift+Right ·      ·         y3

### Layer 7: Game/RPG

    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y0
    ·      9 PU   ↑      3 PD   ·      ·       │  ·      ·      3 PD   ↑      9 PU   ·         y1
    ·      ←      ↓      →      Z      ·       │  ·      Z      ←      ↓      →      ·         y2
    ·      X      C      Shft   Esc    ·       │  ·      Esc    Shft   C      X      ·         y3

### Layer 8: Speed/Travel

    ·      ·      ·      ·      escape ·       │  ·      Shift+Space ·      ·      ·      ·         y0
    ·      ·      F11    Ctrl+Shift+S home   Win+Ctrl+Right  │  Ctrl+Shift+Esc Ctrl+Shift+Z Ctrl+- ·      ·      ·         y1
    ·      ·      Ctrl+Shift+F6 ·      left gui ·       │  Ctrl+Shift+` Alt+F4 Alt+Down Ctrl+. ·      ·         y2
    ·      ·      ·      Ctrl+Shift+B tab    Win+.   │  Win+;  Alt+Up Ctrl+Home ·      ·      ·         y3

### Layer 9: M-Files/DMS

    ·      ·      ·      ·      Ctrl+End ·       │  ·      Ctrl+Up ·      ·      ·      ·         y0
    f2     WfSt   Asgn   ·      Fav    List    │  Print  Shift+Alt+Down ·      ·      ·      ·         y1
    pageup Save   ChkIn  ·      Win+Tab Icon    │  ·      leftshift ·      Hist   Rel    UndCO     y2
    ·      DLoad  Open   CpLnk  Notif  Group   │  Vault  rightarrow_combo Ctrl+Down ·      ·      ·         y3

### Layer 10: Excel

    ShftEnt SelAll Copy   Cut    AutoSum ·       │  ·      ·      ·      Ctrl+Dn ·      Win+C     y0
    ShftTab Sel←   ·      Sel↑   ·      InsTime  │  ·      coach_mouse_lock ·      SelHome Win+B  coach_game_lock    y1
    Find   SelCol F4 $Ref ·      SelEnd ·       │  Win+L  Paste  NextSht Undo   Win+2  Win+N     y2
    HideRow Replace Delete NumFmt Ctrl+Alt+Up Ctrl+Page Down  │  ·      Win+E  ·      grave accent_combo Win+Left ·         y3

### Layer : Layer 

    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y0
    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y1
    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y2
    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y3

## App Efficiency (weighted accessibility)

```
  Microsoft Teams      ██████████████████████░░░░░░░░░░░ 67%
  Windows 11           ███████████████████░░░░░░░░░░░░░░ 58%
  Browser (Chrome/Edge ███████████████████░░░░░░░░░░░░░░ 58%
  Visual Studio Code   ████████████████████░░░░░░░░░░░░░ 60%
  M-Files Desktop Clie ███████████████████████░░░░░░░░░░ 69%
  M-Files Admin        █████████████████████░░░░░░░░░░░░ 62%
  Microsoft Outlook    ████████████████████████░░░░░░░░░ 71%
  Microsoft Excel      ███████████████████░░░░░░░░░░░░░░ 57%
  File Explorer        ███████████████████░░░░░░░░░░░░░░ 58%
  Windows Terminal / P █████████████████████░░░░░░░░░░░░ 62%
  Microsoft Word       ███████████████████████░░░░░░░░░░ 69%
  Microsoft PowerPoint ███████████████████████░░░░░░░░░░ 68%
  Discord              █████████████████████░░░░░░░░░░░░ 64%
```

## Layer Access Paths

- **L0** (Base QWERTY) → **L1** (Navigation) via momentary at x3,y4
- **L0** (Base QWERTY) → **L4** (System/BT) via momentary at x7,y4
- **L0** (Base QWERTY) → **L3** (Window/App) via momentary at x8,y4
- **L0** (Base QWERTY) → **L2** (Mouse QoL) via momentary at x5,y5
- **L1** (Navigation) → **L5** (Code/IDE) via toggle at x0,y1
- **L1** (Navigation) → **L6** (Scroll) via momentary at x3,y2
- **L1** (Navigation) → **L8** (Speed/Travel) via toggle at x4,y2
- **L1** (Navigation) → **L7** (Game/RPG) via lock at x9,y3
- **L2** (Mouse QoL) → **L6** (Scroll) via momentary at x5,y0
- **L2** (Mouse QoL) → **L8** (Speed/Travel) via toggle at x9,y2
- **L2** (Mouse QoL) → **L6** (Scroll) via toggle at x12,y2
- **L2** (Mouse QoL) → **L8** (Speed/Travel) via momentary at x11,y3
- **L4** (System/BT) → **L10** (Excel) via toggle at x0,y3
- **L4** (System/BT) → **L9** (M-Files/DMS) via toggle at x2,y3

## Workflow Simulation Results

| Workflow | Effort | Weight | Weighted | Pass |
|----------|--------|--------|----------|------|
| Full day: browse, code, M-Files, window manage, return | 77 | 1 | 77.0 | ✓ |
| Teams: search chat, reply, format, send, switch channel | 61 | 1 | 61.0 | ✓ |
| Norwegian typing: æøå, common words, punctuation | 65 | 0.9 | 58.5 | ✓ |
| Punctuation: ? - + / \ and Norwegian specials | 59 | 0.8 | 47.2 | ✓ |
| Explorer: navigate, rename, copy files, new folder | 61 | 0.75 | 45.8 | ✓ |
| Code: edit file, comment, save, debug, step through | 49 | 0.9 | 44.1 | ✓ |
| Browser+Vimium: keyboard nav, open links, scroll, tabs | 49 | 0.85 | 41.6 | ✓ |
| Code: multi-cursor edit, search files, format, commit | 49 | 0.85 | 41.6 | ✓ |
| Language switch, voice typing, Copilot launch | 58 | 0.7 | 40.6 | ✓ |
| Git: terminal, stage, commit, push (via VS Code) | 49 | 0.8 | 39.2 | ✓ |
| Copilot: select text, copy to chat, paste response back | 59 | 0.65 | 38.4 | ✓ |
| Excel: navigate, enter data, format, AutoSum | 49 | 0.75 | 36.8 | ✓ |
| M-Files daily: search, browse, check out, properties, workflow | 39 | 0.9 | 35.1 | ✓ |
| Excel: formula, format, navigate sheets, select regions | 68 | 0.5 | 34.0 | ✓ |
| Teams meeting: mute, camera, share screen, raise hand, end | 35 | 0.95 | 33.3 | ✓ |
| M-Files: search, check out, edit, check in | 39 | 0.85 | 33.1 | ✓ |
| Outlook: search, reply, compose, send | 46 | 0.7 | 32.2 | ✓ |
| Multi-monitor: snap, move to monitor, new desktop | 37 | 0.8 | 29.6 | ✓ |
| Browser: select text, copy, Alt+Tab, paste | 29 | 1 | 29.0 | ✓ |
| PowerPoint: open, present, navigate slides, end | 51 | 0.5 | 25.5 | ✓ |
| Text editing: arrows, PgUp, Home, Ctrl+F | 26 | 0.95 | 24.7 | ✓ |
| Mouse Lock → Speed toggle → Exit | 27 | 0.85 | 22.9 | ✓ |
| Window: snap left, open taskbar app, snap right | 24 | 0.9 | 21.6 | ✓ |
| Teams: join meeting, mute/unmute, share screen, leave | 29 | 0.7 | 20.3 | ✓ |
| Quick: save file, close tab, open new — via L4 power shortcuts | 21 | 0.9 | 18.9 | ✓ |
| OneNote: navigate, type notes, format, search | 30 | 0.6 | 18.0 | ✓ |
| Window: screenshot + clipboard history | 25 | 0.7 | 17.5 | ✓ |
| BT: switch profile + output | 15 | 0.5 | 7.5 | ✓ |

Total weighted effort: 975.0

## Layer Access Graph

Reachable from base: L0, L1, L2, L3, L4, L5, L6, L7, L8, L9, L10
Unreachable: none

### Exit paths for lockable/toggleable layers

- **L2** (Mouse QoL): 1 exits ⚠ INSUFFICIENT
  - 10:2: coach_base (coach_base)
- **L7** (Game/RPG): 4 exits ✓
  - 3:4: coach_base (Exit Base)
  - 5:4: coach_base (Exit Base)
  - 7:4: coach_base (Exit Base)
  - 8:4: coach_base (Exit Base)
- **L8** (Speed/Travel): 1 exits ⚠ INSUFFICIENT
  - 7:4: coach_travel_off (Exit Travel)

## Ergonomic Notes

No constraint violations.

## File Sync Status

CSV rows: 617, Apply keys: 616
Matched: 616, Mismatches: 15, Aliases: 0

### Mismatches

- `2:0:0`: parameter — CSV: "PrintScreen" vs Apply: "Keyboard PrintScreen and SysReq"
- `2:0:2`: parameter — CSV: "default_transform" vs Apply: "MB4"
- `2:2:2`: parameter — CSV: "default_transform" vs Apply: "select:MB2"
- `2:3:2`: parameter — CSV: "default_transform" vs Apply: "select:MB3"
- `2:8:3`: parameter — CSV: "9 and PageUp" vs Apply: "Keypad 9 and PageUp"
- `3:10:0`: parameter — CSV: "BT_SEL ?" vs Apply: "BT_SEL"
- `3:3:4`: parameter — CSV: "3 and PageDn" vs Apply: "Keypad 3 and PageDn"
- `5:10:3`: parameter — CSV: "3 and PageDn" vs Apply: "Keypad 3 and PageDn"
- `7:1:1`: parameter — CSV: "9 and PageUp" vs Apply: "Keypad 9 and PageUp"
- `7:3:1`: parameter — CSV: "3 and PageDn" vs Apply: "Keypad 3 and PageDn"
- `7:9:1`: parameter — CSV: "3 and PageDn" vs Apply: "Keypad 3 and PageDn"
- `7:11:1`: parameter — CSV: "9 and PageUp" vs Apply: "Keypad 9 and PageUp"
- `7:4:5`: parameter — CSV: "default_transform" vs Apply: "select:MB1"
- `7:5:5`: parameter — CSV: "default_transform" vs Apply: "select:MB2"
- `9:0:2`: parameter — CSV: "9 and PageUp" vs Apply: "Keypad 9 and PageUp"
