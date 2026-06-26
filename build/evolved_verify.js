/*
Charybdis optimizer layout VERIFY — research-v1
Verifies 385 evolved changes across layers [1, 2, 3, 4, 5, 6, 8, 9, 10].
Paste in ZMK Studio console AFTER applying. Does not edit or save.
*/


(async function VerifyEvolvedLayout() {
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const clean = (s) => String(s || "").trim();
  const qa = (sel) => [...document.querySelectorAll(sel)];

  const expected = [
  {
    "layer": 1,
    "x": 0,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Comma and LessThan",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+,",
    "rationale": "Optimizer (research-v1): Ctrl+, (Open settings)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F12",
    "modifiers": [],
    "label": "F12",
    "rationale": "Optimizer (research-v1): F12 (Go to definition)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Tab",
    "rationale": "Optimizer (research-v1): Ctrl+Tab (Next tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard I",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+I",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+I (Go to Inbox)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Equals and Plus",
    "modifiers": [],
    "label": "equal",
    "rationale": "Optimizer (research-v1): _base_equal (Base key: Equal and Plus)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L GUI",
      "L Shift"
    ],
    "label": "Win+Shift+Right",
    "rationale": "Optimizer (research-v1): Win+Shift+Right (Move to right monitor)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Grave Accent and Tilde",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+`",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+` (New terminal)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "spacebar",
    "rationale": "Optimizer (research-v1): _base_spacebar (Base key: Spacebar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftControl",
    "modifiers": [],
    "label": "leftcontrol",
    "rationale": "Optimizer (research-v1): _base_leftcontrol (Base key: LeftControl)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard J",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+J",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+J (Open Console)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 5,
    "y": 2,
    "behavior": "Mouse Key Press",
    "parameter": "MB1",
    "modifiers": [],
    "label": "MB1",
    "rationale": "Optimizer (research-v1): _base_select:mb1 (Base key: select:MB1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Dash and Underscore",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+-",
    "rationale": "Optimizer (research-v1): Ctrl+- (Delete cells/rows/columns)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F3",
    "modifiers": [],
    "label": "F3",
    "rationale": "Optimizer (research-v1): F3 (Find next)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [],
    "label": "left bracket",
    "rationale": "Optimizer (research-v1): _base_left bracket (Base key: Left Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Escape",
    "modifiers": [],
    "label": "Escape",
    "rationale": "Optimizer (research-v1): Escape (Close / go back)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard 5 and Percent",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+5",
    "rationale": "Optimizer (research-v1): Ctrl+5 (Calls)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 0,
    "behavior": "Mouse Key Press",
    "parameter": "MB2",
    "modifiers": [],
    "label": "MB2",
    "rationale": "Optimizer (research-v1): _base_select:mb2 (Base key: select:MB2)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [],
    "label": "return enter",
    "rationale": "Optimizer (research-v1): _base_return enter (Base key: Return Enter)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 0 and Right Bracket",
    "modifiers": [],
    "label": "right bracket_combo",
    "rationale": "Optimizer (research-v1): _base_right bracket_combo (Base key: 0 and Right Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard W",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+W",
    "rationale": "Optimizer (research-v1): Ctrl+W (Close tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 9,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard 5 and Percent",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+5",
    "rationale": "Optimizer (research-v1): Win+5 (Open/switch pinned app 5)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+S",
    "rationale": "Optimizer (research-v1): Win+S (Search)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+B",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+B (Toggle background blur)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 0,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Equals and Plus",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+=",
    "rationale": "Optimizer (research-v1): Alt+= (AutoSum)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [],
    "label": "s",
    "rationale": "Optimizer (research-v1): _base_s (Base key: S)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard 0 and Right Bracket",
    "modifiers": [],
    "label": "0",
    "rationale": "Optimizer (research-v1): _base_0 (Base key: 0 and Right Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard U",
    "modifiers": [],
    "label": "u",
    "rationale": "Optimizer (research-v1): _base_u (Base key: U)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 5 and Percent",
    "modifiers": [],
    "label": "5",
    "rationale": "Optimizer (research-v1): _base_5 (Base key: 5 and Percent)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [],
    "label": "n",
    "rationale": "Optimizer (research-v1): _base_n (Base key: N)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [],
    "label": "g",
    "rationale": "Optimizer (research-v1): _base_g (Base key: G)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 12,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Right",
    "rationale": "Optimizer (research-v1): Win+Right (Snap window right)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [],
    "label": "return enter",
    "rationale": "Optimizer (research-v1): _base_return enter (Base key: Return Enter)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 1,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard 7 and Ampersand",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+7",
    "rationale": "Optimizer (research-v1): Ctrl+7 (Switch to tab 7)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+F",
    "rationale": "Optimizer (research-v1): Alt+F (Settings menu)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 1 and Bang",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+1",
    "rationale": "Optimizer (research-v1): Win+1 (Open/switch pinned app 1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+H",
    "rationale": "Optimizer (research-v1): Win+H (Voice typing)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "Backspace",
    "rationale": "Optimizer (research-v1): Backspace (Go back / up)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 3 and Hash",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+3",
    "rationale": "Optimizer (research-v1): Ctrl+3 (Teams/channels)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L GUI",
      "L Ctrl"
    ],
    "label": "Win+Ctrl+Left",
    "rationale": "Optimizer (research-v1): Win+Ctrl+Left (Switch desktop left)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Escape",
    "modifiers": [],
    "label": "Escape",
    "rationale": "Optimizer (research-v1): Escape (Close / go back)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+P",
    "rationale": "Optimizer (research-v1): Win+P (Project / display mode)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 5,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard 6 and Caret",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+6",
    "rationale": "Optimizer (research-v1): Ctrl+6 (Files)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [],
    "label": "r",
    "rationale": "Optimizer (research-v1): _base_r (Base key: R)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Q",
    "modifiers": [],
    "label": "q",
    "rationale": "Optimizer (research-v1): _base_q (Base key: Q)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [],
    "label": "l",
    "rationale": "Optimizer (research-v1): _base_l (Base key: L)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [],
    "label": "a",
    "rationale": "Optimizer (research-v1): _base_a (Base key: A)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [],
    "label": "y",
    "rationale": "Optimizer (research-v1): _base_y (Base key: Y)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [],
    "label": "m",
    "rationale": "Optimizer (research-v1): _base_m (Base key: M)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period",
    "rationale": "Optimizer (research-v1): _base_period (Base key: Period)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "spacebar",
    "rationale": "Optimizer (research-v1): _base_spacebar (Base key: Spacebar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F",
    "modifiers": [],
    "label": "f",
    "rationale": "Optimizer (research-v1): _base_f (Base key: F)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [],
    "label": "v",
    "rationale": "Optimizer (research-v1): _base_v (Base key: V)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 2 and At",
    "modifiers": [],
    "label": "2",
    "rationale": "Optimizer (research-v1): _base_2 (Base key: 2 and At)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [],
    "label": "p",
    "rationale": "Optimizer (research-v1): _base_p (Base key: P)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard I",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+I",
    "rationale": "Optimizer (research-v1): Win+I (Settings)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+P",
    "rationale": "Optimizer (research-v1): Ctrl+P (Quick open file)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+D",
    "rationale": "Optimizer (research-v1): Ctrl+D (Select next occurrence)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Comma and LessThan",
    "modifiers": [],
    "label": "comma",
    "rationale": "Optimizer (research-v1): _base_comma (Base key: Comma and LessThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F11",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+F11",
    "rationale": "Optimizer (research-v1): Shift+F11 (Step out)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 0,
    "behavior": "Bluetooth",
    "parameter": "Clear Selected Profile",
    "modifiers": [],
    "label": "select:clear selected profile",
    "rationale": "Optimizer (research-v1): _base_select:clear selected profile (Base key: select:Clear Selected Profile)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [],
    "label": "s",
    "rationale": "Optimizer (research-v1): _base_s (Base key: S)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard SemiColon and Colon",
    "modifiers": [],
    "label": "semicolon",
    "rationale": "Optimizer (research-v1): _base_semicolon (Base key: SemiColon and Colon)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard X",
    "modifiers": [],
    "label": "x",
    "rationale": "Optimizer (research-v1): _base_x (Base key: X)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+E",
    "rationale": "Optimizer (research-v1): Ctrl+E (Search / command bar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [],
    "label": "t",
    "rationale": "Optimizer (research-v1): _base_t (Base key: T)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [],
    "label": "return enter",
    "rationale": "Optimizer (research-v1): _base_return enter (Base key: Return Enter)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [],
    "label": "g",
    "rationale": "Optimizer (research-v1): _base_g (Base key: G)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+D",
    "rationale": "Optimizer (research-v1): Alt+D (Focus address bar (alt))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 12,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [],
    "label": "b",
    "rationale": "Optimizer (research-v1): _base_b (Base key: B)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+P",
    "rationale": "Optimizer (research-v1): Alt+P (Preview pane)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 0,
    "behavior": "Bluetooth",
    "parameter": "BT_SEL 1",
    "modifiers": [],
    "label": "Bluetooth",
    "rationale": "Optimizer (research-v1): _base_bt_sel 1 (Base key: BT_SEL 1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftAlt",
    "modifiers": [],
    "label": "leftalt",
    "rationale": "Optimizer (research-v1): _base_leftalt (Base key: LeftAlt)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [],
    "label": "e",
    "rationale": "Optimizer (research-v1): _base_e (Base key: E)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 1 and Bang",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+1",
    "rationale": "Optimizer (research-v1): Win+1 (Open/switch pinned app 1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F",
    "modifiers": [],
    "label": "f",
    "rationale": "Optimizer (research-v1): _base_f (Base key: F)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [],
    "label": "c",
    "rationale": "Optimizer (research-v1): _base_c (Base key: C)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "delete",
    "rationale": "Optimizer (research-v1): _base_delete (Base key: Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 3,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftShift",
    "modifiers": [],
    "label": "leftshift",
    "rationale": "Optimizer (research-v1): _base_leftshift (Base key: LeftShift)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Escape",
    "modifiers": [],
    "label": "escape",
    "rationale": "Optimizer (research-v1): _base_escape (Base key: Escape)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [],
    "label": "y",
    "rationale": "Optimizer (research-v1): _base_y (Base key: Y)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [],
    "label": "h",
    "rationale": "Optimizer (research-v1): _base_h (Base key: H)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftControl",
    "modifiers": [],
    "label": "leftcontrol",
    "rationale": "Optimizer (research-v1): _base_leftcontrol (Base key: LeftControl)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard J",
    "modifiers": [],
    "label": "j",
    "rationale": "Optimizer (research-v1): _base_j (Base key: J)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [],
    "label": "d",
    "rationale": "Optimizer (research-v1): _base_d (Base key: D)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F4",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+F4",
    "rationale": "Optimizer (research-v1): Alt+F4 (Close window)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Left",
    "rationale": "Optimizer (research-v1): Win+Left (Snap window left)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [],
    "label": "r",
    "rationale": "Optimizer (research-v1): _base_r (Base key: R)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [],
    "label": "o",
    "rationale": "Optimizer (research-v1): _base_o (Base key: O)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [],
    "label": "left brace_combo",
    "rationale": "Optimizer (research-v1): _base_left brace_combo (Base key: Left Brace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 5,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Tab",
    "rationale": "Optimizer (research-v1): Alt+Tab (Switch apps)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Tab",
    "rationale": "Optimizer (research-v1): Win+Tab (Task View)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+G",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+G (Source control panel)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Q",
    "modifiers": [],
    "label": "q",
    "rationale": "Optimizer (research-v1): _base_q (Base key: Q)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [],
    "label": "l",
    "rationale": "Optimizer (research-v1): _base_l (Base key: L)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Up",
    "rationale": "Optimizer (research-v1): Win+Up (Maximize window)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard X",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+X",
    "rationale": "Optimizer (research-v1): Win+X (Power User menu)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period",
    "rationale": "Optimizer (research-v1): _base_period (Base key: Period)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [],
    "label": "a",
    "rationale": "Optimizer (research-v1): _base_a (Base key: A)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [],
    "label": "m",
    "rationale": "Optimizer (research-v1): _base_m (Base key: M)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Enter",
    "rationale": "Optimizer (research-v1): Alt+Enter (Properties / metadata card)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 9,
    "y": 2,
    "behavior": "Mouse Key Press",
    "parameter": "MB1",
    "modifiers": [],
    "label": "MB1",
    "rationale": "Optimizer (research-v1): _base_select:mb1 (Base key: select:MB1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F10",
    "modifiers": [],
    "label": "F10",
    "rationale": "Optimizer (research-v1): F10 (Step over)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 0,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard SemiColon and Colon",
    "modifiers": [],
    "label": "semicolon_combo",
    "rationale": "Optimizer (research-v1): _base_semicolon_combo (Base key: SemiColon and Colon)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L GUI",
      "L Shift"
    ],
    "label": "Win+Shift+S",
    "rationale": "Optimizer (research-v1): Win+Shift+S (Screenshot (Snip))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard ForwardSlash and QuestionMark",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+/",
    "rationale": "Optimizer (research-v1): Ctrl+/ (Toggle line comment)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+O",
    "rationale": "Optimizer (research-v1): Ctrl+O (Open document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F9",
    "modifiers": [],
    "label": "F9",
    "rationale": "Optimizer (research-v1): F9 (Toggle breakpoint)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "Space",
    "rationale": "Optimizer (research-v1): Space (Scroll down one screen)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 1,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F3",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+F3",
    "rationale": "Optimizer (research-v1): Shift+F3 (Find previous)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Right",
    "rationale": "Optimizer (research-v1): Ctrl+Right (Jump to right edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 1,
    "y": 2,
    "behavior": "Bluetooth",
    "parameter": "BT_SEL 0",
    "modifiers": [],
    "label": "Bluetooth",
    "rationale": "Optimizer (research-v1): _base_bt_sel 0 (Base key: BT_SEL 0)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 1,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+D",
    "rationale": "Optimizer (research-v1): Win+D (Show/hide desktop)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 2,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+Tab",
    "rationale": "Optimizer (research-v1): Shift+Tab (Outdent)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 1 and Bang",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+1",
    "rationale": "Optimizer (research-v1): Win+1 (Open/switch pinned app 1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [],
    "label": "r",
    "rationale": "Optimizer (research-v1): _base_r (Base key: R)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F24",
    "modifiers": [],
    "label": "f24",
    "rationale": "Optimizer (research-v1): _base_f24 (Base key: F24)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [],
    "label": "v",
    "rationale": "Optimizer (research-v1): _base_v (Base key: V)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+P",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+P (Command palette)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [],
    "label": "n",
    "rationale": "Optimizer (research-v1): _base_n (Base key: N)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 2,
    "behavior": "Mouse Key Press",
    "parameter": "MB1",
    "modifiers": [],
    "label": "MB1",
    "rationale": "Optimizer (research-v1): _base_select:mb1 (Base key: select:MB1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [],
    "label": "tab",
    "rationale": "Optimizer (research-v1): _base_tab (Base key: Tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Enter",
    "rationale": "Optimizer (research-v1): Alt+Enter (Properties / metadata card)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard F12",
    "modifiers": [],
    "label": "F12",
    "rationale": "Optimizer (research-v1): F12 (Go to definition)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard 4 and Dollar",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+4",
    "rationale": "Optimizer (research-v1): Ctrl+4 (Calendar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [],
    "label": "b",
    "rationale": "Optimizer (research-v1): _base_b (Base key: B)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [],
    "label": "o",
    "rationale": "Optimizer (research-v1): _base_o (Base key: O)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+D",
    "rationale": "Optimizer (research-v1): Ctrl+D (Select next occurrence)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+L",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+L (Autofill login)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard J",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+J",
    "rationale": "Optimizer (research-v1): Ctrl+J (Toggle bottom panel)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [],
    "label": "t",
    "rationale": "Optimizer (research-v1): _base_t (Base key: T)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard I",
    "modifiers": [],
    "label": "i",
    "rationale": "Optimizer (research-v1): _base_i (Base key: I)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [],
    "label": "d",
    "rationale": "Optimizer (research-v1): _base_d (Base key: D)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+.",
    "rationale": "Optimizer (research-v1): Ctrl+. (Show commands)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Space",
    "rationale": "Optimizer (research-v1): Win+Space (Switch input language)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [],
    "label": "y",
    "rationale": "Optimizer (research-v1): _base_y (Base key: Y)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [],
    "label": "h",
    "rationale": "Optimizer (research-v1): _base_h (Base key: H)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [],
    "label": "a",
    "rationale": "Optimizer (research-v1): _base_a (Base key: A)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "delete",
    "rationale": "Optimizer (research-v1): _base_delete (Base key: Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 0,
    "behavior": "Output Selection",
    "parameter": "USB Output",
    "modifiers": [],
    "label": "select:usb output",
    "rationale": "Optimizer (research-v1): _base_select:usb output (Base key: select:USB Output)",
    "optimizer_changed": true,
    "apply_batch": true,
    "studio_skip": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard ForwardSlash and QuestionMark",
    "modifiers": [],
    "label": "forwardslash",
    "rationale": "Optimizer (research-v1): _base_forwardslash (Base key: ForwardSlash and QuestionMark)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period",
    "rationale": "Optimizer (research-v1): _base_period (Base key: Period)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "spacebar",
    "rationale": "Optimizer (research-v1): _base_spacebar (Base key: Spacebar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+M",
    "rationale": "Optimizer (research-v1): Win+M (Minimize all windows)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F23",
    "modifiers": [],
    "label": "f23",
    "rationale": "Optimizer (research-v1): _base_f23 (Base key: F23)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 0,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 1 and Bang",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+1",
    "rationale": "Optimizer (research-v1): Ctrl+1 (Activity)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F16",
    "modifiers": [],
    "label": "f16",
    "rationale": "Optimizer (research-v1): _base_f16 (Base key: F16)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F21",
    "modifiers": [],
    "label": "f21",
    "rationale": "Optimizer (research-v1): _base_f21 (Base key: F21)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+Right",
    "rationale": "Optimizer (research-v1): Shift+Alt+Right (Expand selection)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+Tab",
    "rationale": "Optimizer (research-v1): Shift+Tab (Outdent)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Left",
    "rationale": "Optimizer (research-v1): Win+Left (Snap window left)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Down",
    "rationale": "Optimizer (research-v1): Alt+Down (Move line down)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F9",
    "modifiers": [],
    "label": "F9",
    "rationale": "Optimizer (research-v1): F9 (Toggle breakpoint)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Tab",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+Tab (Previous tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 1,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+E",
    "rationale": "Optimizer (research-v1): Ctrl+E (Search / command bar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftAlt",
    "modifiers": [],
    "label": "leftalt",
    "rationale": "Optimizer (research-v1): _base_leftalt (Base key: LeftAlt)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [],
    "label": "e",
    "rationale": "Optimizer (research-v1): _base_e (Base key: E)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+L",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+L (Autofill login)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [],
    "label": "Up",
    "rationale": "Optimizer (research-v1): Up (Edit last sent message)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [],
    "label": "c",
    "rationale": "Optimizer (research-v1): _base_c (Base key: C)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "delete",
    "rationale": "Optimizer (research-v1): _base_delete (Base key: Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 3,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftShift",
    "modifiers": [],
    "label": "leftshift",
    "rationale": "Optimizer (research-v1): _base_leftshift (Base key: LeftShift)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [],
    "label": "left brace",
    "rationale": "Optimizer (research-v1): _base_left brace (Base key: Left Brace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [],
    "label": "y",
    "rationale": "Optimizer (research-v1): _base_y (Base key: Y)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [],
    "label": "d",
    "rationale": "Optimizer (research-v1): _base_d (Base key: D)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "spacebar",
    "rationale": "Optimizer (research-v1): _base_spacebar (Base key: Spacebar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Comma and LessThan",
    "modifiers": [],
    "label": "comma_combo",
    "rationale": "Optimizer (research-v1): _base_comma_combo (Base key: Comma and LessThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [],
    "label": "downarrow_combo",
    "rationale": "Optimizer (research-v1): _base_downarrow_combo (Base key: DownArrow)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 4,
    "y": 5,
    "behavior": "coach_mouse_lock",
    "parameter": "",
    "modifiers": [],
    "label": "coach_mouse_lock",
    "rationale": "Optimizer (research-v1): _base_coach_mouse_lock (Base key: coach_mouse_lock)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+L",
    "rationale": "Optimizer (research-v1): Ctrl+L (Focus address bar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F20",
    "modifiers": [],
    "label": "f20",
    "rationale": "Optimizer (research-v1): _base_f20 (Base key: F20)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [],
    "label": "o",
    "rationale": "Optimizer (research-v1): _base_o (Base key: O)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F19",
    "modifiers": [],
    "label": "f19",
    "rationale": "Optimizer (research-v1): _base_f19 (Base key: F19)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+M",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+M (Toggle mute)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Equals and Plus",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl++",
    "rationale": "Optimizer (research-v1): Ctrl++ (Zoom in)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period_combo",
    "rationale": "Optimizer (research-v1): _base_period_combo (Base key: Period and GreaterThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Q",
    "modifiers": [],
    "label": "q",
    "rationale": "Optimizer (research-v1): _base_q (Base key: Q)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [],
    "label": "l",
    "rationale": "Optimizer (research-v1): _base_l (Base key: L)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [],
    "label": "a",
    "rationale": "Optimizer (research-v1): _base_a (Base key: A)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F12",
    "modifiers": [],
    "label": "F12",
    "rationale": "Optimizer (research-v1): F12 (Go to definition)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Enter",
    "rationale": "Optimizer (research-v1): Ctrl+Enter (Send (expanded mode))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period",
    "rationale": "Optimizer (research-v1): _base_period (Base key: Period)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [],
    "label": "tab",
    "rationale": "Optimizer (research-v1): _base_tab (Base key: Tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [],
    "label": "g",
    "rationale": "Optimizer (research-v1): _base_g (Base key: G)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard K",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+K",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+K (Delete line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 2 and At",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+2",
    "rationale": "Optimizer (research-v1): Win+2 (Open/switch pinned app 2)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Escape",
    "modifiers": [],
    "label": "escape",
    "rationale": "Optimizer (research-v1): _base_escape (Base key: Escape)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 9,
    "y": 3,
    "behavior": "Reset",
    "parameter": "",
    "modifiers": [],
    "label": "Reset",
    "rationale": "Optimizer (research-v1): _base_reset (Base key: default_transform:default_transform)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 0,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Z",
    "rationale": "Optimizer (research-v1): Ctrl+Z (Undo)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+C",
    "rationale": "Optimizer (research-v1): Ctrl+C (Copy)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard 9 and Left Bracket",
    "modifiers": [],
    "label": "left bracket_combo",
    "rationale": "Optimizer (research-v1): _base_left bracket_combo (Base key: 9 and Left Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 0,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Up",
    "rationale": "Optimizer (research-v1): Alt+Up (Move line up)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 10,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [],
    "label": "uparrow_combo",
    "rationale": "Optimizer (research-v1): _base_uparrow_combo (Base key: UpArrow)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [],
    "label": "s",
    "rationale": "Optimizer (research-v1): _base_s (Base key: S)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard SemiColon and Colon",
    "modifiers": [],
    "label": "semicolon",
    "rationale": "Optimizer (research-v1): _base_semicolon (Base key: SemiColon and Colon)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 10,
    "y": 3,
    "behavior": "Bluetooth",
    "parameter": "BT_SEL 3",
    "modifiers": [],
    "label": "Bluetooth",
    "rationale": "Optimizer (research-v1): _base_bt_sel 3 (Base key: BT_SEL 3)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F11",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+F11",
    "rationale": "Optimizer (research-v1): Shift+F11 (Step out)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Dash and Underscore",
    "modifiers": [],
    "label": "minus_combo",
    "rationale": "Optimizer (research-v1): _base_minus_combo (Base key: Minus)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+G",
    "rationale": "Optimizer (research-v1): Ctrl+G (Go to line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard W",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+W",
    "rationale": "Optimizer (research-v1): Ctrl+W (Close tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard 3 and Hash",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+3",
    "rationale": "Optimizer (research-v1): Ctrl+3 (Teams/channels)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 12,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard SemiColon and Colon",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+;",
    "rationale": "Optimizer (research-v1): Win+; (Emoji picker)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 12,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Down",
    "rationale": "Optimizer (research-v1): Win+Down (Minimize / restore)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [],
    "label": "tab",
    "rationale": "Optimizer (research-v1): _base_tab (Base key: Tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 1,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard X",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+X",
    "rationale": "Optimizer (research-v1): Ctrl+X (Cut)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftAlt",
    "modifiers": [],
    "label": "leftalt",
    "rationale": "Optimizer (research-v1): _base_leftalt (Base key: LeftAlt)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [],
    "label": "e",
    "rationale": "Optimizer (research-v1): _base_e (Base key: E)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 1,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+V",
    "rationale": "Optimizer (research-v1): Ctrl+V (Paste)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 2,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Y",
    "rationale": "Optimizer (research-v1): Ctrl+Y (Redo (alt))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [],
    "label": "n",
    "rationale": "Optimizer (research-v1): _base_n (Base key: N)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [],
    "label": "v",
    "rationale": "Optimizer (research-v1): _base_v (Base key: V)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "delete",
    "rationale": "Optimizer (research-v1): _base_delete (Base key: Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Right",
    "rationale": "Optimizer (research-v1): Win+Right (Snap window right)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [],
    "label": "c",
    "rationale": "Optimizer (research-v1): _base_c (Base key: C)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftShift",
    "modifiers": [],
    "label": "leftshift",
    "rationale": "Optimizer (research-v1): _base_leftshift (Base key: LeftShift)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [],
    "label": "y",
    "rationale": "Optimizer (research-v1): _base_y (Base key: Y)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+T",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+T (Reopen closed tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard J",
    "modifiers": [],
    "label": "j",
    "rationale": "Optimizer (research-v1): _base_j (Base key: J)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftControl",
    "modifiers": [],
    "label": "leftcontrol",
    "rationale": "Optimizer (research-v1): _base_leftcontrol (Base key: LeftControl)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [],
    "label": "t",
    "rationale": "Optimizer (research-v1): _base_t (Base key: T)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "spacebar",
    "rationale": "Optimizer (research-v1): _base_spacebar (Base key: Spacebar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [],
    "label": "left brace_combo",
    "rationale": "Optimizer (research-v1): _base_left brace_combo (Base key: Left Brace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L GUI",
      "L Shift"
    ],
    "label": "Win+Shift+Left",
    "rationale": "Optimizer (research-v1): Win+Shift+Left (Move to left monitor)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [],
    "label": "r",
    "rationale": "Optimizer (research-v1): _base_r (Base key: R)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [],
    "label": "o",
    "rationale": "Optimizer (research-v1): _base_o (Base key: O)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F2",
    "modifiers": [],
    "label": "F2",
    "rationale": "Optimizer (research-v1): F2 (Rename)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+D",
    "rationale": "Optimizer (research-v1): Ctrl+D (Select next occurrence)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard F14",
    "modifiers": [],
    "label": "f14",
    "rationale": "Optimizer (research-v1): _base_f14 (Base key: F14)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period_combo",
    "rationale": "Optimizer (research-v1): _base_period_combo (Base key: Period and GreaterThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Q",
    "modifiers": [],
    "label": "q",
    "rationale": "Optimizer (research-v1): _base_q (Base key: Q)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [],
    "label": "l",
    "rationale": "Optimizer (research-v1): _base_l (Base key: L)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [],
    "label": "a",
    "rationale": "Optimizer (research-v1): _base_a (Base key: A)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L GUI",
      "L Shift"
    ],
    "label": "Win+Shift+S",
    "rationale": "Optimizer (research-v1): Win+Shift+S (Screenshot (Snip))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 5,
    "behavior": "Bluetooth",
    "parameter": "BT_SEL 2",
    "modifiers": [],
    "label": "Bluetooth",
    "rationale": "Optimizer (research-v1): _base_bt_sel 2 (Base key: BT_SEL 2)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period",
    "rationale": "Optimizer (research-v1): _base_period (Base key: Period)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [],
    "label": "m",
    "rationale": "Optimizer (research-v1): _base_m (Base key: M)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 0 and Right Bracket",
    "modifiers": [],
    "label": "0",
    "rationale": "Optimizer (research-v1): _base_0 (Base key: 0 and Right Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F13",
    "modifiers": [],
    "label": "f13",
    "rationale": "Optimizer (research-v1): _base_f13 (Base key: F13)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 9,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+E",
    "rationale": "Optimizer (research-v1): Win+E (File Explorer)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Tab",
    "rationale": "Optimizer (research-v1): Ctrl+Tab (Next tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [],
    "label": "h",
    "rationale": "Optimizer (research-v1): _base_h (Base key: H)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard X",
    "modifiers": [],
    "label": "x",
    "rationale": "Optimizer (research-v1): _base_x (Base key: X)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 0,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+Down",
    "rationale": "Optimizer (research-v1): Shift+Alt+Down (Copy line down)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 6 and Caret",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+6",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+6 (Toggle details pane)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard 3 and Hash",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+3",
    "rationale": "Optimizer (research-v1): Ctrl+3 (Teams/channels)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 0,
    "y": 3,
    "behavior": "Mouse Key Press",
    "parameter": "MB5",
    "modifiers": [],
    "label": "MB5",
    "rationale": "Optimizer (research-v1): _base_select:mb5 (Base key: select:MB5)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 10,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Grave Accent and Tilde",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+`",
    "rationale": "Optimizer (research-v1): Ctrl+` (Toggle terminal)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 10,
    "y": 1,
    "behavior": "coach_travel_toggle",
    "parameter": "",
    "modifiers": [],
    "label": "coach_travel_toggle",
    "rationale": "Optimizer (research-v1): _base_coach_travel_toggle (Base key: coach_travel_toggle)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Comma and LessThan",
    "modifiers": [],
    "label": "comma",
    "rationale": "Optimizer (research-v1): _base_comma (Base key: Comma and LessThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "delete",
    "rationale": "Optimizer (research-v1): _base_delete (Base key: Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Right",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+Right (Select to right edge)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard End",
    "modifiers": [],
    "label": "end_combo",
    "rationale": "Optimizer (research-v1): _base_end_combo (Base key: End)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftShift",
    "modifiers": [],
    "label": "leftshift",
    "rationale": "Optimizer (research-v1): _base_leftshift (Base key: LeftShift)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 4 and Dollar",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+4",
    "rationale": "Optimizer (research-v1): Ctrl+4 (Calendar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+P",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+P (Command palette)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 12,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 9 and Left Bracket",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+9",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+9 (Unhide rows)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 12,
    "y": 2,
    "behavior": "coach_game_lock",
    "parameter": "",
    "modifiers": [],
    "label": "coach_game_lock",
    "rationale": "Optimizer (research-v1): _base_coach_game_lock (Base key: coach_game_lock)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Tab",
    "rationale": "Optimizer (research-v1): Ctrl+Tab (Next tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 1,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard PageDown",
    "modifiers": [],
    "label": "pagedown_combo",
    "rationale": "Optimizer (research-v1): _base_pagedown_combo (Base key: PageDown)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L GUI",
      "L Shift"
    ],
    "label": "Win+Shift+S",
    "rationale": "Optimizer (research-v1): Win+Shift+S (Screenshot (Snip))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+D",
    "rationale": "Optimizer (research-v1): Ctrl+D (Select next occurrence)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 1,
    "y": 3,
    "behavior": "Output Selection",
    "parameter": "BLE Output",
    "modifiers": [],
    "label": "select:ble output",
    "rationale": "Optimizer (research-v1): _base_select:ble output (Base key: select:BLE Output)",
    "optimizer_changed": true,
    "apply_batch": true,
    "studio_skip": true
  },
  {
    "layer": 8,
    "x": 2,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Down",
    "rationale": "Optimizer (research-v1): Win+Down (Minimize / restore)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [],
    "label": "y",
    "rationale": "Optimizer (research-v1): _base_y (Base key: Y)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard J",
    "modifiers": [],
    "label": "j",
    "rationale": "Optimizer (research-v1): _base_j (Base key: J)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Z",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+Z (Redo)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftControl",
    "modifiers": [],
    "label": "leftcontrol",
    "rationale": "Optimizer (research-v1): _base_leftcontrol (Base key: LeftControl)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [],
    "label": "b",
    "rationale": "Optimizer (research-v1): _base_b (Base key: B)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 3,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [],
    "label": "m",
    "rationale": "Optimizer (research-v1): _base_m (Base key: M)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [],
    "label": "uparrow_combo",
    "rationale": "Optimizer (research-v1): _base_uparrow_combo (Base key: UpArrow)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+T",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+T (Reopen closed tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F3",
    "modifiers": [],
    "label": "F3",
    "rationale": "Optimizer (research-v1): F3 (Find next)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [],
    "label": "s",
    "rationale": "Optimizer (research-v1): _base_s (Base key: S)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [],
    "label": "n",
    "rationale": "Optimizer (research-v1): _base_n (Base key: N)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 9 and Left Bracket",
    "modifiers": [],
    "label": "9",
    "rationale": "Optimizer (research-v1): _base_9 (Base key: 9 and Left Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard 3 and Hash",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+3",
    "rationale": "Optimizer (research-v1): Win+3 (Open/switch pinned app 3)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Backslash and Pipe",
    "modifiers": [],
    "label": "backslash_combo",
    "rationale": "Optimizer (research-v1): _base_backslash_combo (Base key: Backslash and Pipe)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Right Brace",
    "modifiers": [],
    "label": "right brace_combo",
    "rationale": "Optimizer (research-v1): _base_right brace_combo (Base key: Right Brace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftAlt",
    "modifiers": [],
    "label": "leftalt",
    "rationale": "Optimizer (research-v1): _base_leftalt (Base key: LeftAlt)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard X",
    "modifiers": [],
    "label": "x",
    "rationale": "Optimizer (research-v1): _base_x (Base key: X)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [],
    "label": "e",
    "rationale": "Optimizer (research-v1): _base_e (Base key: E)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard 5 and Percent",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+5",
    "rationale": "Optimizer (research-v1): Ctrl+5 (Calls)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 5,
    "behavior": "Mouse Key Press",
    "parameter": "MB3",
    "modifiers": [],
    "label": "MB3",
    "rationale": "Optimizer (research-v1): _base_select:mb3 (Base key: select:MB3)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F18",
    "modifiers": [],
    "label": "f18",
    "rationale": "Optimizer (research-v1): _base_f18 (Base key: F18)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 1,
    "behavior": "coach_l2_hold",
    "parameter": "",
    "modifiers": [],
    "label": "coach_l2_hold",
    "rationale": "Optimizer (research-v1): _base_coach_l2_hold (Base key: coach_l2_hold)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard U",
    "modifiers": [],
    "label": "u",
    "rationale": "Optimizer (research-v1): _base_u (Base key: U)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [],
    "label": "a",
    "rationale": "Optimizer (research-v1): _base_a (Base key: A)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard F15",
    "modifiers": [],
    "label": "f15",
    "rationale": "Optimizer (research-v1): _base_f15 (Base key: F15)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period",
    "rationale": "Optimizer (research-v1): _base_period (Base key: Period)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [],
    "label": "tab",
    "rationale": "Optimizer (research-v1): _base_tab (Base key: Tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 0 and Right Bracket",
    "modifiers": [],
    "label": "0",
    "rationale": "Optimizer (research-v1): _base_0 (Base key: 0 and Right Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [],
    "label": "v",
    "rationale": "Optimizer (research-v1): _base_v (Base key: V)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 9,
    "y": 0,
    "behavior": "Output Selection",
    "parameter": "USB Output",
    "modifiers": [],
    "label": "select:usb output",
    "rationale": "Optimizer (research-v1): _base_select:usb output (Base key: select:USB Output)",
    "optimizer_changed": true,
    "apply_batch": true,
    "studio_skip": true
  },
  {
    "layer": 8,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [],
    "label": "o",
    "rationale": "Optimizer (research-v1): _base_o (Base key: O)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "spacebar",
    "rationale": "Optimizer (research-v1): _base_spacebar (Base key: Spacebar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [],
    "label": "c",
    "rationale": "Optimizer (research-v1): _base_c (Base key: C)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 10,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+C",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+C (Inspect element)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [],
    "label": "t",
    "rationale": "Optimizer (research-v1): _base_t (Base key: T)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard J",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+J",
    "rationale": "Optimizer (research-v1): Ctrl+J (Toggle bottom panel)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard U",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+U",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+U (Mark as unread)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F4",
    "modifiers": [],
    "label": "F4",
    "rationale": "Optimizer (research-v1): F4 (Toggle absolute ref ($))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 12,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F3",
    "modifiers": [],
    "label": "F3",
    "rationale": "Optimizer (research-v1): F3 (Find next)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 2,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+T",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+T (Reopen closed tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F2",
    "modifiers": [],
    "label": "F2",
    "rationale": "Optimizer (research-v1): F2 (Rename)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+T",
    "rationale": "Optimizer (research-v1): Ctrl+T (New tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [],
    "label": "uparrow_combo",
    "rationale": "Optimizer (research-v1): _base_uparrow_combo (Base key: UpArrow)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Up",
    "rationale": "Optimizer (research-v1): Alt+Up (Move line up)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [],
    "label": "b",
    "rationale": "Optimizer (research-v1): _base_b (Base key: B)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Left",
    "rationale": "Optimizer (research-v1): Alt+Left (Back)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftControl",
    "modifiers": [],
    "label": "leftcontrol",
    "rationale": "Optimizer (research-v1): _base_leftcontrol (Base key: LeftControl)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [],
    "label": "Tab",
    "rationale": "Optimizer (research-v1): Tab (Indent / accept suggestion)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftAlt",
    "modifiers": [],
    "label": "leftalt",
    "rationale": "Optimizer (research-v1): _base_leftalt (Base key: LeftAlt)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [],
    "label": "m",
    "rationale": "Optimizer (research-v1): _base_m (Base key: M)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [],
    "label": "s",
    "rationale": "Optimizer (research-v1): _base_s (Base key: S)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Ctrl",
      "L Alt"
    ],
    "label": "Ctrl+Alt+Down",
    "rationale": "Optimizer (research-v1): Ctrl+Alt+Down (Add cursor below)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 5,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Enter",
    "rationale": "Optimizer (research-v1): Alt+Enter (Properties / metadata card)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [],
    "label": "Enter",
    "rationale": "Optimizer (research-v1): Enter (Send message)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+D",
    "rationale": "Optimizer (research-v1): Ctrl+D (Select next occurrence)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period_combo",
    "rationale": "Optimizer (research-v1): _base_period_combo (Base key: Period and GreaterThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard SemiColon and Colon",
    "modifiers": [],
    "label": "semicolon",
    "rationale": "Optimizer (research-v1): _base_semicolon (Base key: SemiColon and Colon)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [],
    "label": "e",
    "rationale": "Optimizer (research-v1): _base_e (Base key: E)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Tab",
    "rationale": "Optimizer (research-v1): Ctrl+Tab (Next tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard 2 and At",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+2",
    "rationale": "Optimizer (research-v1): Ctrl+2 (Chat)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Left GUI",
    "modifiers": [],
    "label": "left gui",
    "rationale": "Optimizer (research-v1): _base_left gui (Base key: Left GUI)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [],
    "label": "spacebar",
    "rationale": "Optimizer (research-v1): _base_spacebar (Base key: Spacebar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [],
    "label": "v",
    "rationale": "Optimizer (research-v1): _base_v (Base key: V)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Right",
    "rationale": "Optimizer (research-v1): Alt+Right (Forward)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+F",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+F (Format document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 9,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+G",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+G (Source control panel)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F10",
    "modifiers": [],
    "label": "F10",
    "rationale": "Optimizer (research-v1): F10 (Step over)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Y",
    "rationale": "Optimizer (research-v1): Ctrl+Y (Redo (alt))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 0,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Ctrl",
      "L Alt"
    ],
    "label": "Ctrl+Alt+Up",
    "rationale": "Optimizer (research-v1): Ctrl+Alt+Up (Add cursor above)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+O",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+O (Toggle camera)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F23",
    "modifiers": [],
    "label": "f23",
    "rationale": "Optimizer (research-v1): _base_f23 (Base key: F23)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 0,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard End",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+End",
    "rationale": "Optimizer (research-v1): Ctrl+End (Go to last used cell)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 10,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F22",
    "modifiers": [],
    "label": "f22",
    "rationale": "Optimizer (research-v1): _base_f22 (Base key: F22)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [],
    "label": "s",
    "rationale": "Optimizer (research-v1): _base_s (Base key: S)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard SemiColon and Colon",
    "modifiers": [],
    "label": "semicolon",
    "rationale": "Optimizer (research-v1): _base_semicolon (Base key: SemiColon and Colon)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard X",
    "modifiers": [],
    "label": "x",
    "rationale": "Optimizer (research-v1): _base_x (Base key: X)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+Enter",
    "rationale": "Optimizer (research-v1): Shift+Enter (New line in message)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Grave Accent and Tilde",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+~",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+~ (General format)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 12,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+P",
    "rationale": "Optimizer (research-v1): Ctrl+P (Quick open file)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+H",
    "rationale": "Optimizer (research-v1): Ctrl+H (Find and replace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 1,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F16",
    "modifiers": [],
    "label": "f16",
    "rationale": "Optimizer (research-v1): _base_f16 (Base key: F16)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftAlt",
    "modifiers": [],
    "label": "leftalt",
    "rationale": "Optimizer (research-v1): _base_leftalt (Base key: LeftAlt)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [],
    "label": "e",
    "rationale": "Optimizer (research-v1): _base_e (Base key: E)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 1,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+P",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+P (Command palette)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 2,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+M",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+M (Toggle mute)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [],
    "label": "d",
    "rationale": "Optimizer (research-v1): _base_d (Base key: D)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [],
    "label": "return enter",
    "rationale": "Optimizer (research-v1): _base_return enter (Base key: Return Enter)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F20",
    "modifiers": [],
    "label": "f20",
    "rationale": "Optimizer (research-v1): _base_f20 (Base key: F20)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "delete",
    "rationale": "Optimizer (research-v1): _base_delete (Base key: Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 3,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftShift",
    "modifiers": [],
    "label": "leftshift",
    "rationale": "Optimizer (research-v1): _base_leftshift (Base key: LeftShift)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [],
    "label": "left brace",
    "rationale": "Optimizer (research-v1): _base_left brace (Base key: Left Brace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F12",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+F12",
    "rationale": "Optimizer (research-v1): Alt+F12 (Peek definition)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Comma and LessThan",
    "modifiers": [],
    "label": "comma_combo",
    "rationale": "Optimizer (research-v1): _base_comma_combo (Base key: Comma and LessThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftControl",
    "modifiers": [],
    "label": "leftcontrol",
    "rationale": "Optimizer (research-v1): _base_leftcontrol (Base key: LeftControl)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [],
    "label": "a",
    "rationale": "Optimizer (research-v1): _base_a (Base key: A)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F17",
    "modifiers": [],
    "label": "f17",
    "rationale": "Optimizer (research-v1): _base_f17 (Base key: F17)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Home",
    "modifiers": [],
    "label": "home_combo",
    "rationale": "Optimizer (research-v1): _base_home_combo (Base key: Home)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "Delete",
    "rationale": "Optimizer (research-v1): Delete (Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [],
    "label": "r",
    "rationale": "Optimizer (research-v1): _base_r (Base key: R)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [],
    "label": "m",
    "rationale": "Optimizer (research-v1): _base_m (Base key: M)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [],
    "label": "o",
    "rationale": "Optimizer (research-v1): _base_o (Base key: O)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+D",
    "rationale": "Optimizer (research-v1): Ctrl+D (Select next occurrence)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard F9",
    "modifiers": [],
    "label": "F9",
    "rationale": "Optimizer (research-v1): F9 (Toggle breakpoint)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F",
    "modifiers": [],
    "label": "f",
    "rationale": "Optimizer (research-v1): _base_f (Base key: F)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Q",
    "modifiers": [],
    "label": "q",
    "rationale": "Optimizer (research-v1): _base_q (Base key: Q)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [],
    "label": "l",
    "rationale": "Optimizer (research-v1): _base_l (Base key: L)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Escape",
    "modifiers": [],
    "label": "escape",
    "rationale": "Optimizer (research-v1): _base_escape (Base key: Escape)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Right",
    "rationale": "Optimizer (research-v1): Ctrl+Shift+Right (Select to right edge)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Left",
    "rationale": "Optimizer (research-v1): Ctrl+Left (Jump to left edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [],
    "label": "tab",
    "rationale": "Optimizer (research-v1): _base_tab (Base key: Tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [],
    "label": "z",
    "rationale": "Optimizer (research-v1): _base_z (Base key: Z)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 0 and Right Bracket",
    "modifiers": [],
    "label": "0",
    "rationale": "Optimizer (research-v1): _base_0 (Base key: 0 and Right Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+R",
    "rationale": "Optimizer (research-v1): Ctrl+R (Reply)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [],
    "label": "period_combo",
    "rationale": "Optimizer (research-v1): _base_period_combo (Base key: Period and GreaterThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [],
    "label": "p",
    "rationale": "Optimizer (research-v1): _base_p (Base key: P)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 9,
    "y": 3,
    "behavior": "Bluetooth",
    "parameter": "BT_SEL 3",
    "modifiers": [],
    "label": "Bluetooth",
    "rationale": "Optimizer (research-v1): _base_bt_sel 3 (Base key: BT_SEL 3)",
    "optimizer_changed": true,
    "apply_batch": true
  }
];
  const layers = [1, 2, 3, 4, 5, 6, 8, 9, 10];

  // --- Layer selection (same selectors as evolved_apply.js) ---

  function findLayerButton(layer) {
    const layerList = document.querySelector('[aria-label="Keymap Layer"]');
    return layerList?.querySelector('[role="option"][data-key="' + layer + '"]')
      || [...(layerList || document).querySelectorAll('[role="option"]')].find(el => clean(el.textContent) === String(layer));
  }

  function selectedLayer() {
    const selected = document.querySelector('[aria-label="Keymap Layer"] [role="option"][aria-selected="true"]');
    return clean(selected?.textContent || "");
  }

  async function selectLayer(layer) {
    if (selectedLayer() === String(layer)) return true;
    const el = findLayerButton(layer);
    if (!el) {
      console.error("Layer " + layer + " not found in ZMK Studio layer list");
      return false;
    }
    el.click();
    await sleep(650);
    if (selectedLayer() !== String(layer)) {
      console.error("Failed to switch to layer " + layer + " (stuck on " + selectedLayer() + ")");
      return false;
    }
    return true;
  }

  // --- Key selection (same as evolved_apply.js) ---

  function findKeyElement(x, y) {
    const holder = document.querySelector('[x="' + x + '"][y="' + y + '"]');
    return holder?.querySelector("button") || holder;
  }

  async function selectKey(x, y) {
    const el = findKeyElement(x, y);
    if (!el) return false;
    (el.closest("button") || el).click();
    await sleep(220);
    return true;
  }

  // --- Read current key state ---

  function visibleSelects() {
    return qa("select").filter(s => s.offsetParent !== null);
  }

  function isBehaviorSelect(s) {
    return [...s.options].some(o => clean(o.textContent) === "Key Press")
      && [...s.options].some(o => clean(o.textContent) === "Transparent");
  }

  function isZoomSelect(s) {
    return [...s.options].some(o => clean(o.textContent) === "Auto")
      && [...s.options].some(o => clean(o.textContent) === "100%");
  }

  function isDefaultTransformSelect(s) {
    return [...s.options].some(o => clean(o.textContent) === "default_transform")
      && s.options.length <= 3;
  }

  function readCurrent() {
    const allSelects = visibleSelects();
    const bSel = allSelects.find(isBehaviorSelect);
    const behavior = bSel ? clean(bSel.options[bSel.selectedIndex]?.textContent) : "";

    // Key Press uses combobox
    const combobox = qa("input").find(i => i.offsetParent !== null && i.getAttribute("role") === "combobox");
    let parameter = combobox ? clean(combobox.value) : "";

    // Non-Key-Press behaviors use a parameter select
    if (!parameter) {
      const paramSelect = allSelects.find(s =>
        s !== bSel && !isBehaviorSelect(s) && !isZoomSelect(s) && !isDefaultTransformSelect(s)
      );
      if (paramSelect) {
        parameter = clean(paramSelect.options[paramSelect.selectedIndex]?.textContent) || "";
      }
    }

    // For Bluetooth "Select Profile" / "Disconnect Profile", also read the profile number input
    if (behavior === "Bluetooth" && (parameter === "Select Profile" || parameter === "Disconnect Profile")) {
      const numInput = qa("input[type=number]").find(i => i.offsetParent !== null);
      if (numInput) {
        parameter = "BT_SEL " + clean(numInput.value);
      }
    }

    const checkboxes = qa("input[type=checkbox]").filter(c => c.offsetParent !== null && c.checked);
    const modifiers = checkboxes.map(c => {
      const label = c.closest("label")?.textContent || c.parentElement?.textContent || "";
      return clean(label);
    }).filter(Boolean);
    return { behavior, parameter, modifiers };
  }

  // --- Main verify loop ---

  console.log("Verifying " + expected.length + " evolved keys across layers " + JSON.stringify(layers) + "...");
  let passed = 0, failed = 0;
  const failures = [];
  let currentLayer = null;

  let skipped = 0;
  for (const key of expected) {
    if (!layers.includes(key.layer)) continue;
    if (key.studio_skip) { skipped++; continue; }

    if (currentLayer !== key.layer) {
      const switched = await selectLayer(key.layer);
      if (!switched) {
        failures.push({ layer: key.layer, x: key.x, y: key.y, label: key.label, issues: ["could not switch to layer " + key.layer], expected: key, actual: {} });
        failed++;
        continue;
      }
      currentLayer = key.layer;
      console.log("Verifying layer " + key.layer + "...");
    }

    const found = await selectKey(key.x, key.y);
    if (!found) {
      failures.push({ layer: key.layer, x: key.x, y: key.y, label: key.label, issues: ["key not found in Studio UI"], expected: key, actual: {} });
      failed++;
      continue;
    }

    const actual = readCurrent();
    const issues = [];

    if (actual.behavior !== key.behavior) {
      issues.push("behavior: expected " + key.behavior + ", got " + actual.behavior);
    }

    if (key.parameter && actual.parameter) {
      const expNorm = clean(key.parameter).replace("Keyboard ", "").toUpperCase();
      const actNorm = clean(actual.parameter).replace("Keyboard ", "").toUpperCase();
      if (expNorm !== actNorm) {
        issues.push("parameter: expected \"" + key.parameter + "\", got \"" + actual.parameter + "\"");
      }
    } else if (key.parameter && !actual.parameter) {
      issues.push("parameter: expected \"" + key.parameter + "\", got empty");
    }

    const expMods = (key.modifiers || []).sort().join("+");
    const actMods = actual.modifiers.sort().join("+");
    if (expMods !== actMods) {
      issues.push("modifiers: expected \"" + expMods + "\", got \"" + actMods + "\"");
    }

    if (issues.length > 0) {
      failures.push({ layer: key.layer, x: key.x, y: key.y, label: key.label, issues, expected: key, actual });
      failed++;
      console.warn("FAIL L" + key.layer + " (" + key.x + "," + key.y + ") " + (key.label || "") + ": " + issues.join("; "));
    } else {
      passed++;
    }
  }

  console.log("\n" + "=".repeat(50));
  if (failed === 0) {
    console.log("PASSED: All " + passed + " keys verified correctly." + (skipped ? " (" + skipped + " firmware-only keys skipped)" : ""));
  } else {
    console.error("FAILED: " + failed + " of " + (passed + failed) + " keys mismatch." + (skipped ? " (" + skipped + " firmware-only skipped)" : ""));
    console.table(failures.map(f => ({
      position: "L" + f.layer + " (" + f.x + "," + f.y + ")",
      label: f.label || "",
      issues: f.issues?.join("; ") || f.issue || ""
    })));
  }
  console.log("=".repeat(50));
})();

