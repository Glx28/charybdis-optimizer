# Charybdis Keymap Baseline Report
Generated: 2026-06-25T09:02:40.735Z

## Summary

| Metric | Value |
|--------|-------|
| Total keys | 616 |
| Active layers | 10 |
| Apps tracked | 13 |
| Total app shortcuts | 532 |
| Shortcuts mapped | 462 (87%) |
| Workflows tested | 28 |
| Workflows passing | 28/28 |
| Sync mismatches | 6 |
| Layer contexts | 15 |

## App Coverage

| App | Weight | Shortcuts | Mapped | Coverage | Efficiency |
|-----|--------|-----------|--------|----------|------------|
| Microsoft Teams | 1 | 44 | 36 | 82% | 62% |
| Windows 11 | 1 | 52 | 46 | 88% | 65% |
| Browser (Chrome/Edge) | 0.95 | 89 | 69 | 78% | 59% |
| Visual Studio Code | 0.9 | 76 | 66 | 87% | 60% |
| M-Files Desktop Client | 0.85 | 37 | 35 | 95% | 69% |
| M-Files Admin | 0.85 | 17 | 16 | 94% | 64% |
| Microsoft Outlook | 0.7 | 30 | 29 | 97% | 72% |
| Microsoft Excel | 0.5 | 58 | 52 | 90% | 61% |
| File Explorer | 0.45 | 31 | 23 | 74% | 60% |
| Windows Terminal / PowerShell | 0.4 | 26 | 22 | 85% | 63% |
| Microsoft Word | 0.3 | 29 | 26 | 90% | 71% |
| Microsoft PowerPoint | 0.2 | 27 | 27 | 100% | 71% |
| Discord | 0.2 | 16 | 15 | 94% | 63% |

## High-Frequency Unmapped Shortcuts

| Importance | App | Shortcut | Action | Frequency |
|-----------|-----|----------|--------|-----------|
| 8.5 | M-Files Desktop Client | Alt+Enter | Properties / metadata card | constant |
| 6.0 | Microsoft Teams | Ctrl+3 | Teams/channels | high |
| 6.0 | Microsoft Teams | Ctrl+4 | Calendar | high |
| 5.7 | Browser (Chrome/Edge) | Alt+Right | Forward | high |
| 5.7 | Browser (Chrome/Edge) | H | Go back in history | high |
| 5.7 | Browser (Chrome/Edge) | J | Previous tab | high |
| 5.7 | Browser (Chrome/Edge) | K | Next tab | high |
| 5.4 | Visual Studio Code | Ctrl+J | Toggle bottom panel | high |
| 5.4 | Visual Studio Code | Ctrl+Shift+Z | Redo | high |
| 5.4 | Visual Studio Code | Alt+Right | Navigate forward | high |
| 5.4 | Visual Studio Code | Alt+Click | Add cursor at position | high |
| 5.4 | Visual Studio Code | Ctrl+Alt+Up | Add cursor above | high |
| 5.4 | Visual Studio Code | Ctrl+Alt+Down | Add cursor below | high |
| 5.1 | M-Files Admin | Alt+Enter | Properties | high |
| 3.0 | Microsoft Excel | Ctrl+Shift++ | Insert cells/rows/columns | high |
| 2.7 | File Explorer | Alt+Right | Forward | high |
| 2.7 | File Explorer | Ctrl+Click | Select multiple (non-adjacent) | high |
| 2.7 | File Explorer | Shift+Click | Select range | high |

## Layer Map

### Layer 0: Base QWERTY

    Esc    1      2      3      4      5       │  6      7      8      9      0      BkSp      y0
    Tab    Q      W      E      R      T       │  Y      U      I      O      P      å         y1
    Shft   A      S      D      F      G       │  H      J      K      L      ø      æ         y2
    Ctrl   Z      X      C      V      B       │  N      M      ,      .      /      \         y3

### Layer 1: Navigation

    F1     H      F      F4     F11    F6      │  F7     F8     F9     F10    F11    F12       y0
    Code   F5     F6     F7     F8     V       │  ←      BkSp   F2     3 PD   End    BkSp      y1
    Shft   ←      F3     Scroll Speed  Delete  │  Search ↓      ↑      →      →      Home      y2
    Ctrl   F9     F10    F5     F12    9 PU    │  C      CmdPal [      ]      \      -         y3

### Layer 2: Mouse QoL

    Snip   Task View Desktop Next Tab Prev Tab Scroll  │  Next Tab Desktop Del    Prev Tab Sel All Task View    y0
    Esc    Alt+Tab Close  Enter  BkSp   Zoom In  │  Win    Enter  Refresh BkSp   Alt+Tab Cut       y1
    Copy   MB1    MB2    MB3    MB4    MB5     │  Mouse Key Press Mouse Key Press Mouse Key Press Mouse Key Press Mouse Key Press Scroll    y2
    Esc    Undo   Close  Zoom Out Sel All Paste   │  Copy   Redo   Paste  Undo   Speed  Close Win    y3

### Layer 3: Window/App

    Emoji  ←      →      Emoji  QSett  Notif   │  TskCy  SysTr  Copilot Acces  ←      Emoji     y0
    MinAll ␣      V      →      →      Lang    │  TskMg  `      ↓      Lock   Settings Run       y1
    Snip   3      2      1      4      5       │  Search F4     ←      Mouse Lock Speed  Game      y2
    ClipH  →      ↑      Voice  S      D       │  Tab    D      Tab    Explorer CmdPal Power     y3

### Layer 4: System/BT

    Bluetooth Bluetooth Bluetooth Bluetooth Bluetooth Bluetooth  │  Output Selection Output Selection Output Selection Studio Unlock Reset  Bootloader    y0
    Ctrl+G Ctrl+O F15    F16    F14    F18     │  F17    Ctrl+K Ctrl+S Ctrl+L Ctrl+B Ctrl+U    y1
    ·      F19    F20    F21    ·      F23     │  F13    Hand   Ctrl+E Ctrl+P Ctrl+R Share     y2
    Excel  F24    DMS    Ctrl+D Ctrl+I F22     │  Mute   Camera Ctrl+W Ctrl+N Hangup Accept    y3

### Layer 5: Code/IDE

    Hover  SelNx  Stop   StpOv  GoSym  StpOt   │  BkPt   Rstr   Cmnt   Explr  NewFl  Fmt       y0
    Wrap   LnUp   LnDn   CpDn   InsUp  InsLn   │  Split  Open   Debug  SelAl  Peek   GoLn      y1
    Rename Save   Brkt   Sett   DelLn  Term    │  Ind    CmdP   Probs  StpIn  SrchF  Git       y2
    Close  PstNF  BlkCm  NTerm  Ext    Rename  │  Close  Outd   SelLn  RplFl  NxtPr  PrvPr     y3

### Layer 7: Game/RPG

    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y0
    ·      9 PU   ↑      3 PD   ·      ·       │  ·      ·      3 PD   ↑      9 PU   ·         y1
    ·      ←      ↓      →      Z      ·       │  ·      Z      ←      ↓      →      ·         y2
    ·      X      C      Shft   Esc    ·       │  ·      Esc    Shft   C      X      ·         y3

### Layer 8: Speed/Travel

    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y0
    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y1
    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y2
    ·      ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y3

### Layer 9: M-Files/DMS

    Refresh ·      ·      ·      ·      ·       │  ·      ·      ·      ·      ·      ·         y0
    Back   WfSt   Asgn   Rename Fav    List    │  Print  ·      Search ·      ·      ·         y1
    Search Save   ChkIn  ChkOt  ·      Icon    │  Refresh ·      Back   Hist   Rel    UndCO     y2
    Rename DLoad  Open   CpLnk  Notif  Group   │  Vault  ·      ·      ·      ·      ·         y3

### Layer 10: Excel

    ShftEnt SelAll Copy   Cut    AutoSum ShowFml  │  F2 Edit =      Ctrl+Up Ctrl+Dn PasteSp GoTo      y0
    ShftTab Sel←   Sel→   Sel↑   Sel↓   InsTime  │  Insert SelRow InsDate SelHome Redo   FillRt    y1
    Find   SelCol F4 $Ref Ctrl+Home SelEnd Ctrl+End  │  PrevSht Paste  NextSht Undo   Save   Bold      y2
    HideRow Replace Delete NumFmt CurFmt PctFmt  │  FmtCell FillDn UnhideR HideCol GenFmt ArrFml    y3

## App Efficiency (weighted accessibility)

```
  Microsoft Teams      █████████████████████░░░░░░░░░░░░ 62%
  Windows 11           ██████████████████████░░░░░░░░░░░ 65%
  Browser (Chrome/Edge ████████████████████░░░░░░░░░░░░░ 59%
  Visual Studio Code   ████████████████████░░░░░░░░░░░░░ 60%
  M-Files Desktop Clie ███████████████████████░░░░░░░░░░ 69%
  M-Files Admin        █████████████████████░░░░░░░░░░░░ 64%
  Microsoft Outlook    ████████████████████████░░░░░░░░░ 72%
  Microsoft Excel      ████████████████████░░░░░░░░░░░░░ 61%
  File Explorer        ████████████████████░░░░░░░░░░░░░ 60%
  Windows Terminal / P █████████████████████░░░░░░░░░░░░ 63%
  Microsoft Word       ████████████████████████░░░░░░░░░ 71%
  Microsoft PowerPoint ████████████████████████░░░░░░░░░ 71%
  Discord              █████████████████████░░░░░░░░░░░░ 63%
```

## Layer Access Paths

- **L0** (Base QWERTY) → **L1** (Navigation) via momentary at x3,y4
- **L0** (Base QWERTY) → **L4** (System/BT) via momentary at x7,y4
- **L0** (Base QWERTY) → **L3** (Window/App) via momentary at x8,y4
- **L0** (Base QWERTY) → **L2** (Mouse QoL) via momentary at x5,y5
- **L1** (Navigation) → **L5** (Code/IDE) via toggle at x0,y1
- **L1** (Navigation) → **L6** (Scroll) via momentary at x3,y2
- **L1** (Navigation) → **L8** (Speed/Travel) via toggle at x4,y2
- **L2** (Mouse QoL) → **L6** (Scroll) via momentary at x5,y0
- **L2** (Mouse QoL) → **L6** (Scroll) via toggle at x12,y2
- **L2** (Mouse QoL) → **L8** (Speed/Travel) via momentary at x11,y3
- **L3** (Window/App) → **L2** (Mouse QoL) via lock at x10,y2
- **L3** (Window/App) → **L8** (Speed/Travel) via toggle at x11,y2
- **L3** (Window/App) → **L7** (Game/RPG) via lock at x12,y2
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

- **L2** (Mouse QoL): 3 exits ✓
  - 5:4: coach_base (Base)
  - 7:4: coach_base (Base)
  - 8:4: coach_base (Base)
- **L7** (Game/RPG): 4 exits ✓
  - 3:4: coach_base (Exit Base)
  - 5:4: coach_base (Exit Base)
  - 7:4: coach_base (Exit Base)
  - 8:4: coach_base (Exit Base)
- **L8** (Speed/Travel): 2 exits ✓
  - 7:4: coach_travel_off (Exit Travel)
  - 8:4: coach_travel_off (Exit Travel)

## Ergonomic Notes

No constraint violations.

## File Sync Status

CSV rows: 616, Apply keys: 616
Matched: 616, Mismatches: 6, Aliases: 0

### Mismatches

- `2:0:0`: parameter — CSV: "Print Screen" vs Apply: "Keyboard PrintScreen"
- `2:5:1`: parameter — CSV: "Equal" vs Apply: "Keyboard Equals and Plus"
- `3:4:4`: modifiers — CSV: "L GUI" vs Apply: "Left GUI"
- `10:4:0`: parameter — CSV: "Equal and Plus" vs Apply: "Keyboard Equals and Plus"
- `10:8:0`: parameter — CSV: "Equal and Plus" vs Apply: "Keyboard Equals and Plus"
- `10:7:1`: parameter — CSV: "Equal and Plus" vs Apply: "Keyboard Equals and Plus"
