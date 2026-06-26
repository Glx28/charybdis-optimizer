/*
Charybdis optimizer layout — research-v1
385 key changes across layers [1, 2, 3, 4, 5, 6, 8, 9, 10].
Self-contained: paste this one file in ZMK Studio console to apply all changes.
*/


// Post-apply summary — runs after apply_every_key.js finishes
window._CHARYBDIS_APPLY_ERRORS = window._CHARYBDIS_APPLY_ERRORS || [];
window._CHARYBDIS_APPLY_SKIPPED = window._CHARYBDIS_APPLY_SKIPPED || [];
const _origError = console.error.bind(console);
const _origWarn = console.warn.bind(console);
console.error = function(...args) {
  const msg = args.map(String).join(" ");
  if (msg.includes("UNKNOWN KEY") || msg.includes("NO MATCHING") || msg.includes("Failed L")) {
    window._CHARYBDIS_APPLY_ERRORS.push(msg);
  }
  _origError(...args);
};
console.warn = function(...args) {
  const msg = args.map(String).join(" ");
  if (msg.includes("No exact visible") || msg.includes("Verify manually")) {
    window._CHARYBDIS_APPLY_ERRORS.push(msg);
  }
  _origWarn(...args);
};


window.CHARYBDIS_FINAL_LAYOUT = {
  "project": "Charybdis Optimizer Layout",
  "version": "research-v1",
  "keyCount": 385,
  "keys": [
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
]
};

window.CHARYBDIS_MODE = "applyLayer";
window.CHARYBDIS_APPLY_LAYER_INDEX = "all";
window.CHARYBDIS_ENABLE_LAYER_APPLY = true;

console.log("Applying " + window.CHARYBDIS_FINAL_LAYOUT.keyCount + " keys across layers [1, 2, 3, 4, 5, 6, 8, 9, 10]...");

(async function CharybdisStudioAssistant() {
  const MODE = window.CHARYBDIS_MODE || "applyLayer";
  const APPLY_LAYER_INDEX = window.CHARYBDIS_APPLY_LAYER_INDEX === undefined
    ? "all"
    : (window.CHARYBDIS_APPLY_LAYER_INDEX === "all"
      ? "all"
      : (Number.isInteger(Number(window.CHARYBDIS_APPLY_LAYER_INDEX)) ? Number(window.CHARYBDIS_APPLY_LAYER_INDEX) : 2));
  const ENABLE_LAYER_APPLY = window.CHARYBDIS_ENABLE_LAYER_APPLY !== false;
  const APPLY_ONLY_BATCH = window.CHARYBDIS_APPLY_ONLY_BATCH !== false;
  const APPLY_LAYERS = Array.isArray(window.CHARYBDIS_APPLY_LAYERS)
    ? window.CHARYBDIS_APPLY_LAYERS.map((layer) => Number(layer)).filter(Number.isInteger)
    : null;
  const ONE_KEY_TEST = window.CHARYBDIS_ONE_KEY_TEST || { layer: 9, x: 4, y: 5, behavior: "Key Press", parameter: "F24", label: "TEST F24" };
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const FALLBACK_LAYOUT = {
    project: "Charybdis Ultimate Keyboard Experience",
    version: "fallback-one-key-test-only",
    keys: [
      { layer: 9, x: 4, y: 5, behavior: "Key Press", parameter: "F24", label: "TEST F24", rationale: "Fallback one-key test only. Paste final_v1_layout.json into CHARYBDIS_FINAL_LAYOUT for real work.", apply_batch: false }
    ]
  };

  function clean(text) {
    return (text || "").replace(/\s+/g, " ").trim();
  }

  function visible(el) {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && cs.display !== "none" && cs.visibility !== "hidden" && cs.opacity !== "0";
  }

  function qa(selector, root = document) {
    return [...root.querySelectorAll(selector)];
  }

  function nativeSetValue(el, value) {
    const proto = el instanceof HTMLSelectElement ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
    const desc = Object.getOwnPropertyDescriptor(proto, "value");
    desc.set.call(el, value);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function nativeSetChecked(el, checked) {
    const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "checked");
    desc.set.call(el, checked);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  async function click(el, delay = 180) {
    el.scrollIntoView({ block: "center", inline: "center" });
    el.click();
    await sleep(delay);
  }

  function getLayout() {
    const data = window.CHARYBDIS_FINAL_LAYOUT || FALLBACK_LAYOUT;
    if (!data || !Array.isArray(data.keys)) {
      throw new Error("Layout data must be an object with a keys array.");
    }
    return data;
  }

  function plannedKeys() {
    return getLayout().keys
      .filter((item) => item && Number.isInteger(Number(item.layer)))
      .filter((item) => !APPLY_ONLY_BATCH || item.apply_batch === true || MODE === "oneKeyTest");
  }

  function visibleSelects() {
    return qa("select").filter(visible);
  }

  function visibleInputs() {
    return qa("input").filter(visible);
  }

  function cleanLabel(el) {
    const id = el.getAttribute("id");
    const aria = el.getAttribute("aria-labelledby");
    const ariaLabel = el.getAttribute("aria-label");
    if (ariaLabel) return clean(ariaLabel);
    if (aria) {
      return aria.split(/\s+/).map((part) => clean(document.getElementById(part)?.textContent)).filter(Boolean).join(" ");
    }
    if (id) {
      const label = document.querySelector(`label[for="${CSS.escape(id)}"]`);
      if (label) return clean(label.textContent);
    }
    const nearbyLabel = el.closest("div")?.querySelector("label");
    return clean(nearbyLabel?.textContent);
  }

  function findLayerButton(layer) {
    const layerList = document.querySelector('[aria-label="Keymap Layer"]');
    return layerList?.querySelector(`[role="option"][data-key="${layer}"]`)
      || qa('[role="option"]', layerList || document).find((el) => clean(el.textContent) === String(layer));
  }

  function selectedLayer() {
    const selected = document.querySelector('[aria-label="Keymap Layer"] [role="option"][aria-selected="true"]');
    return clean(selected?.textContent || "");
  }

  function findKeyElement(x, y) {
    const holder = document.querySelector(`[x="${x}"][y="${y}"]`);
    return holder?.querySelector("button") || holder;
  }

  function keyExistsInDom(x, y) {
    return Boolean(document.querySelector(`[x="${x}"][y="${y}"]`));
  }

  function validatePlanCoordinates(items) {
    const missing = items.filter((item) => !keyExistsInDom(item.x, item.y));
    if (!missing.length) {
      console.info(`Coordinate validation passed for ${items.length} planned key(s).`);
      return true;
    }

    console.group("Coordinate validation failed");
    console.error("The following planned keys do not exist in the visible ZMK Studio keymap. Nothing was applied.");
    for (const item of missing) {
      console.error(`Layer ${item.layer} x${item.x} y${item.y}: ${item.behavior} ${item.parameter || ""} [${item.label || ""}]`);
    }
    console.groupEnd();
    return false;
  }

  function validateSupportedBehaviors(items) {
    const supported = new Set(["Key Press", "Mouse Key Press", "Momentary Layer", "To Layer", "Toggle Layer", "Bluetooth", "Output Selection", "Studio Unlock", "Reset", "Bootloader", "Transparent", "None", "coach_l1_hold", "coach_l2_hold", "coach_l3_hold", "coach_l4_hold", "coach_mouse_lock", "coach_game_lock", "coach_base", "coach_travel_toggle", "coach_travel_off", "coach_recover_base"]);
    const unsupported = items.filter((item) => !supported.has(item.behavior));
    if (!unsupported.length) return true;

    console.group("Unsupported behavior validation failed");
    console.error("These behaviors are not automated because their Studio controls are firmware/source-dependent or unverified.");
    for (const item of unsupported) {
      console.error(`Layer ${item.layer} x${item.x} y${item.y}: ${item.behavior} ${item.parameter || ""} [${item.label || ""}]`);
    }
    console.groupEnd();
    return false;
  }

  async function selectLayer(layer) {
    if (selectedLayer() === String(layer)) return;
    const el = findLayerButton(layer);
    if (!el) throw new Error(`Layer ${layer} was not found in the ZMK Studio layer list.`);
    await click(el, 650);
    if (selectedLayer() !== String(layer)) {
      throw new Error(`Tried to select layer ${layer}, but selected layer is ${selectedLayer() || "unknown"}.`);
    }
  }

  async function selectKey(x, y) {
    const el = findKeyElement(x, y);
    if (!el) throw new Error(`Key x${x} y${y} was not found in the visible keymap.`);
    await click(el.closest("button") || el, 220);
  }

  async function setBehavior(behaviorName) {
    const select = visibleSelects().find((s) => [...s.options].some((o) => clean(o.textContent) === behaviorName));
    if (!select) throw new Error(`Could not find visible Behavior select with option "${behaviorName}".`);
    const option = [...select.options].find((o) => clean(o.textContent) === behaviorName);
    nativeSetValue(select, option.value);
    await sleep(behaviorName === "Key Press" ? 900 : 350);
  }

  function behaviorSelect() {
    return visibleSelects().find(isBehaviorSelect);
  }

  function currentBehaviorName() {
    const select = behaviorSelect();
    if (!select) return "";
    return clean(select.options[select.selectedIndex]?.textContent);
  }

  function currentTextParameters() {
    return visibleInputs()
      .filter((input) => input.type === "text")
      .map((input) => clean(input.value || input.getAttribute("value") || ""))
      .filter(Boolean);
  }

  function currentSelectParameters() {
    return visibleSelects()
      .filter((select) => !isBehaviorSelect(select) && !isZoomSelect(select))
      .map((select) => clean(select.options[select.selectedIndex]?.textContent || select.value))
      .filter(Boolean);
  }

  function currentImplicitModifiers() {
    const group = qa('[role="group"]').find((el) => /Implicit Modifiers/i.test(clean(el.getAttribute("aria-label") || el.textContent)));
    if (!group) return [];

    return qa("label", group)
      .map((label) => {
        const input = label.querySelector('input[type="checkbox"]');
        return input?.checked ? normalizeModifierName(label.textContent) : "";
      })
      .filter(Boolean)
      .sort();
  }

  function normalizeKeyName(value) {
    const raw = clean(String(value || ""))
      .replace(/^Keyboard\s+/i, "")
      .replace(/\s+/g, " ")
      .toUpperCase();
    const aliases = {
      LEFT: "LEFTARROW",
      RIGHT: "RIGHTARROW",
      UP: "UPARROW",
      DOWN: "DOWNARROW",
      "PAGE UP": "PAGEUP",
      "PAGE DOWN": "PAGEDOWN",
      "PG UP": "PAGEUP",
      PGUP: "PAGEUP",
      "PG DOWN": "PAGEDOWN",
      PGDN: "PAGEDOWN",
      "KEYPAD 9 AND PAGEUP": "PAGEUP",
      "KEYPAD 3 AND PAGEDN": "PAGEDOWN",
      DELETE: "DELETE",
      DEL: "DELETE",
      INSERT: "INSERT",
      INS: "INSERT",
      ESC: "ESCAPE",
      SPACE: "SPACEBAR",
      LEFTSHIFT: "LEFTSHIFT",
      "LEFT SHIFT": "LEFTSHIFT",
      LSHIFT: "LEFTSHIFT",
      LEFTCTRL: "LEFTCTRL",
      "LEFT CTRL": "LEFTCTRL",
      LCTRL: "LEFTCTRL",
      LEFTALT: "LEFTALT",
      "LEFT ALT": "LEFTALT",
      LALT: "LEFTALT",
      "1 AND BANG": "1",
      "2 AND AT": "2",
      "3 AND HASH": "3",
      "4 AND DOLLAR": "4",
      "5 AND PERCENT": "5",
      "6 AND CARET": "6",
      "7 AND AMPERSAND": "7",
      "8 AND ASTERISK": "8",
      "9 AND LEFT PARENTHESIS": "9",
      "0 AND RIGHT PARENTHESIS": "0",
      "GRAVE ACCENT AND TILDE": "GRAVE",
      LEFTARROW: "LEFTARROW",
      RIGHTARROW: "RIGHTARROW",
      UPARROW: "UPARROW",
      DOWNARROW: "DOWNARROW"
    };
    return aliases[raw] || raw.replace(/\s+/g, "");
  }

  function currentLooksLike(item) {
    if (currentBehaviorName() !== item.behavior) return false;

    if (["Transparent", "None", "Studio Unlock", "Reset", "Bootloader"].includes(item.behavior)) {
      return true;
    }

    const wantedModifiers = (item.modifiers || []).map(normalizeModifierName).sort();
    const currentModifiers = currentImplicitModifiers();
    if (wantedModifiers.join("|") !== currentModifiers.join("|")) {
      return false;
    }

    if (!item.parameter) return true;

    const wanted = normalizeKeyName(item.parameter);
    const visibleValues = [...currentTextParameters(), ...currentSelectParameters()].map(normalizeKeyName);

    if (visibleValues.includes(wanted)) return true;
    if (item.behavior === "Bluetooth" && /^BTSEL\d+$/i.test(wanted)) {
      return visibleValues.includes("SELECTPROFILE") && currentTextParameters().some((value) => clean(value) === wanted.replace(/^BTSEL/i, ""));
    }
    return false;
  }

  async function setTextParameter(parameter) {
    const inputs = visibleInputs().filter((i) => i.type === "text");
    const candidate = inputs.find((i) => /^Key:?$/i.test(cleanLabel(i)))
      || inputs.find((i) => /Key:/i.test(cleanLabel(i)))
      || inputs[1]
      || inputs[0];
    if (!candidate) throw new Error(`Could not find a visible text input for parameter "${parameter}".`);
    candidate.focus();
    candidate.select?.();
    nativeSetValue(candidate, parameter);
    candidate.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", bubbles: true }));
    candidate.dispatchEvent(new KeyboardEvent("keyup", { key: "Enter", code: "Enter", bubbles: true }));
    candidate.blur();
    await sleep(180);
  }

  function findKeyInput() {
    const inputs = visibleInputs().filter((i) => i.type === "text");
    return inputs.find((i) => i.getAttribute("role") === "combobox" && /^Key:?$/i.test(cleanLabel(i)))
      || inputs.find((i) => /^Key:?$/i.test(cleanLabel(i)))
      || inputs.find((i) => i.getAttribute("role") === "combobox")
      || inputs.find((i) => /Key:/i.test(cleanLabel(i)))
      || inputs[1]
      || inputs[0];
  }

  function keySearchTerms(parameter) {
    const text = clean(String(parameter || ""));
    const upper = text.toUpperCase();
    const terms = new Set([text]);
    const known = {
      "1": ["Keyboard 1 and Bang", "1"],
      "2": ["Keyboard 2 and At", "2"],
      "3": ["Keyboard 3 and Hash", "3"],
      "4": ["Keyboard 4 and Dollar", "4"],
      "5": ["Keyboard 5 and Percent", "5"],
      "6": ["Keyboard 6 and Caret", "6"],
      "7": ["Keyboard 7 and Ampersand", "7"],
      "8": ["Keyboard 8 and Star", "8"],
      "9": ["Keyboard 9 and Left Bracket", "9"],
      "0": ["Keyboard 0 and Right Bracket", "0"],
      GRAVE: ["Keyboard Grave Accent and Tilde", "Keyboard Grave", "Grave"],
      LEFT: ["Keyboard LeftArrow", "Left"],
      RIGHT: ["Keyboard RightArrow", "Right"],
      UP: ["Keyboard UpArrow", "Up"],
      DOWN: ["Keyboard DownArrow", "Down"],
      "PAGE UP": ["Keypad 9 and PageUp", "Keyboard Page Up", "Keyboard PageUp", "Page Up", "PageUp", "Keyboard Prior", "Prior"],
      PAGEUP: ["Keypad 9 and PageUp", "Keyboard Page Up", "Keyboard PageUp", "Page Up", "PageUp", "Keyboard Prior", "Prior"],
      PGUP: ["Keypad 9 and PageUp", "Keyboard Page Up", "Keyboard PageUp", "Page Up", "PageUp", "Keyboard Prior", "Prior"],
      "PAGE DOWN": ["Keypad 3 and PageDn", "Keyboard Page Down", "Keyboard PageDown", "Page Down", "PageDown", "Keyboard Next", "Next"],
      PAGEDOWN: ["Keypad 3 and PageDn", "Keyboard Page Down", "Keyboard PageDown", "Page Down", "PageDown", "Keyboard Next", "Next"],
      PGDN: ["Keypad 3 and PageDn", "Keyboard Page Down", "Keyboard PageDown", "Page Down", "PageDown", "Keyboard Next", "Next"],
      SPACE: ["Keyboard Space", "Space"],
      LEFTSHIFT: ["Keyboard LeftShift", "LeftShift", "Left Shift"],
      "LEFT SHIFT": ["Keyboard LeftShift", "LeftShift", "Left Shift"],
      LSHIFT: ["Keyboard LeftShift", "LeftShift", "Left Shift"],
      LEFTCTRL: ["Keyboard LeftControl", "LeftControl", "Left Control"],
      LEFTALT: ["Keyboard LeftAlt", "LeftAlt", "Left Alt"],
      LEFTGUI: ["Keyboard Left GUI", "Left GUI", "LeftGUI"],
      APOSTROPHE: ["Keyboard Left Apos and Double", "Keyboard Apostrophe and Quotation Mark", "Keyboard Apostrophe", "Apostrophe", "'"],
      KEYBOARDAPOSTROPHE: ["Keyboard Left Apos and Double", "Keyboard Apostrophe and Quotation Mark", "Keyboard Apostrophe", "Apostrophe", "'"],
      APOS: ["Keyboard Left Apos and Double", "Keyboard Apostrophe and Quotation Mark", "Keyboard Apostrophe", "Apostrophe", "'"],
      "'": ["Keyboard Left Apos and Double", "Keyboard Apostrophe and Quotation Mark", "Keyboard Apostrophe", "Apostrophe", "'"]
    };
    if (known[upper]) {
      known[upper].forEach((term) => terms.add(term));
    }
    return [...terms].filter(Boolean);
  }

  function optionScore(text, terms) {
    const actual = clean(text).toUpperCase();
    const normalizedTerms = terms.map((term) => clean(term).toUpperCase());
    const exactIndex = normalizedTerms.findIndex((term) => actual === term);
    if (exactIndex >= 0) return 1000 - exactIndex;
    const keyboardExactIndex = normalizedTerms.findIndex((term) => actual === `KEYBOARD ${term}`);
    if (keyboardExactIndex >= 0) return 900 - keyboardExactIndex;
    const containsIndex = normalizedTerms.findIndex((term) => actual.includes(term));
    if (containsIndex >= 0) return 100 - containsIndex;
    return 0;
  }

  function listboxForKeyCombobox(input) {
    const controls = input?.getAttribute("aria-controls");
    if (controls) {
      const controlled = document.getElementById(controls);
      if (controlled && controlled.getAttribute("aria-label") !== "Keymap Layer") return controlled;
    }
    return qa('[role="listbox"]')
      .filter(visible)
      .filter((listbox) => listbox.getAttribute("aria-label") !== "Keymap Layer")
      .find((listbox) => qa('[role="option"]', listbox).some(visible));
  }

  function visibleSuggestionNodes(parameter, input) {
    const terms = keySearchTerms(parameter);
    const scopedList = listboxForKeyCombobox(input);
    const roots = scopedList
      ? [scopedList]
      : qa('[role="listbox"]').filter((listbox) => listbox.getAttribute("aria-label") !== "Keymap Layer");
    return roots
      .flatMap((root) => qa('[role="option"]', root))
      .filter(visible)
      .map((el) => ({ el, text: clean(el.textContent || el.getAttribute("aria-label") || "") }))
      .filter((item) => item.text.length > 0 && item.text.length < 120)
      .map((item) => ({ ...item, score: optionScore(item.text, terms) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score);
  }

  const KNOWN_KEY_NAMES = new Set([
    "Keyboard 0 and Right Bracket","Keyboard 1 and Bang","Keyboard 2 and At","Keyboard 3 and Hash",
    "Keyboard 4 and Dollar","Keyboard 5 and Percent","Keyboard 6 and Caret","Keyboard 7 and Ampersand",
    "Keyboard 8 and Star","Keyboard 9 and Left Bracket","Keyboard A","Keyboard B","Keyboard Backslash and Pipe",
    "Keyboard C","Keyboard Comma and LessThan","Keyboard D","Keyboard Dash and Underscore","Keyboard Delete",
    "Keyboard Delete Forward","Keyboard DownArrow","Keyboard E","Keyboard End","Keyboard Equals and Plus",
    "Keyboard Escape","Keyboard F","Keyboard F1","Keyboard F2","Keyboard F3","Keyboard F4","Keyboard F5",
    "Keyboard F6","Keyboard F7","Keyboard F8","Keyboard F9","Keyboard F10","Keyboard F11","Keyboard F12",
    "Keyboard F13","Keyboard F14","Keyboard F15","Keyboard F16","Keyboard F17","Keyboard F18","Keyboard F19",
    "Keyboard F20","Keyboard F21","Keyboard F22","Keyboard F23","Keyboard F24",
    "Keyboard ForwardSlash and QuestionMark","Keyboard G","Keyboard Grave Accent and Tilde","Keyboard H",
    "Keyboard Home","Keyboard I","Keyboard J","Keyboard K","Keyboard L","Keyboard Left Apos and Double",
    "Keyboard Left Brace","Keyboard Left GUI","Keyboard LeftAlt","Keyboard LeftArrow","Keyboard LeftControl",
    "Keyboard LeftShift","Keyboard M","Keyboard N","Keyboard O","Keyboard P","Keyboard PageDown",
    "Keyboard PageUp","Keyboard Period and GreaterThan","Keyboard PrintScreen",
    "Keyboard Q","Keyboard R","Keyboard Return Enter","Keyboard Right Brace","Keyboard RightArrow",
    "Keyboard RightAlt","Keyboard RightControl","Keyboard RightShift","Keyboard Right GUI",
    "Keyboard S","Keyboard SemiColon and Colon","Keyboard Spacebar","Keyboard T","Keyboard Tab",
    "Keyboard U","Keyboard UpArrow","Keyboard V","Keyboard W","Keyboard X","Keyboard Y","Keyboard Z",
    "Keypad 0 and Insert","Keypad 1 and End","Keypad 2 and DownArrow","Keypad 3 and PageDn",
    "Keypad 4 and LeftArrow","Keypad 5","Keypad 6 and RightArrow","Keypad 7 and Home",
    "Keypad 8 and UpArrow","Keypad 9 and PageUp","Keypad Asterisk","Keypad Enter","Keypad Equals",
    "Keypad ForwardSlash","Keypad Minus","Keypad Period and Delete","Keypad Plus"
  ]);

  async function setComboboxKeyParameter(parameter) {
    if (parameter && parameter.startsWith("Keyboard ") && !KNOWN_KEY_NAMES.has(parameter)) {
      const candidates = [...KNOWN_KEY_NAMES].filter(k => {
        const pWords = parameter.toLowerCase().split(/\s+/);
        return pWords.some(w => w.length > 2 && k.toLowerCase().includes(w));
      });
      console.error(`UNKNOWN KEY: "${parameter}"`);
      if (candidates.length) console.log("  Candidates:", candidates.join(", "));
      window._CHARYBDIS_APPLY_ERRORS.push({parameter, candidates, layer: arguments[0]?.layer, x: arguments[0]?.x, y: arguments[0]?.y});
      return;
    }

    const input = findKeyInput();
    if (!input) throw new Error(`Could not find Key combobox for parameter "${parameter}".`);

    input.scrollIntoView({ block: "center", inline: "center" });
    input.focus();
    input.select?.();
    nativeSetValue(input, "");
    await sleep(80);
    const searchTerm = keySearchTerms(parameter)[0] || parameter;
    nativeSetValue(input, searchTerm);
    input.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: searchTerm }));
    await sleep(450);

    const comboButton = input.closest(".react-aria-ComboBox")?.querySelector("button")
      || input.parentElement?.querySelector("button");
    if (comboButton && comboButton.getAttribute("aria-expanded") !== "true") {
      comboButton.click();
      await sleep(450);
    }

    let suggestions = visibleSuggestionNodes(parameter, input);
    if (!suggestions.length) {
      input.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", code: "ArrowDown", bubbles: true }));
      input.dispatchEvent(new KeyboardEvent("keyup", { key: "ArrowDown", code: "ArrowDown", bubbles: true }));
      await sleep(250);
      suggestions = visibleSuggestionNodes(parameter, input);
    }

    if (suggestions.length) {
      const chosen = suggestions[0];
      chosen.el.scrollIntoView({ block: "center", inline: "center" });
      chosen.el.click();
      await sleep(350);
    } else {
      const allOptions = [...document.querySelectorAll("[role=option], li")]
        .filter(el => el.offsetParent !== null)
        .map(el => el.textContent.trim())
        .filter(Boolean);
      console.error(`NO MATCH: "${parameter}"`);
      if (allOptions.length) console.log("  Visible options:", allOptions.slice(0, 10).join(", "));
      window._CHARYBDIS_APPLY_ERRORS.push({parameter, visibleOptions: allOptions.slice(0, 10)});
      return;
    }

    document.activeElement?.blur?.();
    input.blur();
    await sleep(250);
  }

  async function setKeyPressParameter(parameter) {
    await setComboboxKeyParameter(parameter);
    await sleep(350);
    const selected = document.querySelector('[x][y] button[aria-selected="true"]');
    const visibleText = clean(selected?.innerText);
    if (!visibleText.includes(parameter)) {
      console.info(`Key Press parameter "${parameter}" was entered. ZMK Studio may update the visible key label asynchronously; verify this key manually before saving.`);
    }
  }

  function normalizeModifierName(name) {
    const compact = clean(name).toUpperCase().replace(/[_-]+/g, " ");
    const aliases = {
      "LC": "L CTRL",
      "LCTRL": "L CTRL",
      "LEFT CTRL": "L CTRL",
      "LEFT CONTROL": "L CTRL",
      "LS": "L SHIFT",
      "LSHIFT": "L SHIFT",
      "LEFT SHIFT": "L SHIFT",
      "LA": "L ALT",
      "LALT": "L ALT",
      "LEFT ALT": "L ALT",
      "LG": "L GUI",
      "LGUI": "L GUI",
      "LEFT GUI": "L GUI",
      "WIN": "L GUI",
      "WINDOWS": "L GUI",
      "GUI": "L GUI",
      "RC": "R CTRL",
      "RCTRL": "R CTRL",
      "RIGHT CTRL": "R CTRL",
      "RIGHT CONTROL": "R CTRL",
      "RS": "R SHIFT",
      "RSHIFT": "R SHIFT",
      "RIGHT SHIFT": "R SHIFT",
      "RA": "R ALT",
      "RALT": "R ALT",
      "RIGHT ALT": "R ALT",
      "RG": "R GUI",
      "RGUI": "R GUI",
      "RIGHT GUI": "R GUI"
    };
    return aliases[compact.replace(/\s+/g, "")] || aliases[compact] || compact;
  }

  async function setCheckboxChecked(input, checked) {
    if (input.checked === checked) return;
    const label = input.closest("label");
    if (label) {
      label.click();
      await sleep(120);
    }
    if (input.checked !== checked) {
      input.click();
      await sleep(120);
    }
    if (input.checked !== checked) {
      nativeSetChecked(input, checked);
      await sleep(120);
    }
  }

  async function setImplicitModifiers(modifiers) {
    const wanted = new Set((modifiers || []).map(normalizeModifierName));
    const group = qa('[role="group"]')
      .filter((el) => /Implicit Modifiers/i.test(clean(el.getAttribute("aria-label") || el.textContent)))
      .find((el) => visible(el) && el.getAttribute("aria-hidden") !== "true")
      || qa('[role="group"]').find((el) => /Implicit Modifiers/i.test(clean(el.getAttribute("aria-label") || el.textContent)));
    if (!group) {
      if (wanted.size) console.warn("Could not find Implicit Modifiers group. Verify modifiers manually:", [...wanted]);
      return;
    }

    const byValue = {
      "1": "L CTRL",
      "2": "L SHIFT",
      "4": "L ALT",
      "8": "L GUI",
      "16": "R CTRL",
      "32": "R SHIFT",
      "64": "R ALT",
      "128": "R GUI"
    };
    const rows = qa('input[type="checkbox"]', group).map((input) => ({
      input,
      name: byValue[input.value || ""] || normalizeModifierName(input.closest("label")?.textContent || "")
    }));
    for (const row of rows) {
      await setCheckboxChecked(row.input, wanted.has(row.name));
      await sleep(60);
    }

    const missing = [...wanted].filter((modifier) => !rows.some((row) => row.name === modifier));
    if (missing.length) {
      console.warn("Some requested modifiers were not found in Studio:", missing);
    }
  }

  function parameterAliases(parameter) {
    const text = clean(String(parameter));
    const upper = text.toUpperCase();
    const aliases = new Set([text, upper]);

    const stripped = upper.replace(/^SELECT:/, "");
    const mouseAliases = { MB1: "MB1", MB2: "MB2", MB3: "MB3", MB4: "MB4", MB5: "MB5" };
    if (mouseAliases[stripped]) { aliases.add(mouseAliases[stripped]); aliases.add(stripped); }

    const outputAliases = {
      OUT_TOG: "Toggle Outputs",
      OUT_TOGGLE: "Toggle Outputs",
      OUT_USB: "USB Output",
      USB: "USB Output",
      "USB OUTPUT": "USB Output",
      "SELECT:USB OUTPUT": "USB Output",
      OUT_BLE: "BLE Output",
      BLE: "BLE Output",
      "BLE OUTPUT": "BLE Output",
      "SELECT:BLE OUTPUT": "BLE Output",
      "SELECT:CLEAR SELECTED PROFILE": "Clear Selected Profile",
      "CLEAR SELECTED PROFILE": "Clear Selected Profile",
    };
    if (outputAliases[upper]) aliases.add(outputAliases[upper]);
    if (outputAliases[stripped]) aliases.add(outputAliases[stripped]);

    const bluetoothAliases = {
      BT_NXT: "Next Profile",
      BT_NEXT: "Next Profile",
      BT_PRV: "Previous Profile",
      BT_PREV: "Previous Profile",
      BT_CLR: "Clear Selected Profile",
      BT_CLEAR: "Clear Selected Profile",
      BT_CLR_ALL: "Clear All Profiles",
      BT_DISC: "Disconnect Profile"
    };
    if (bluetoothAliases[upper]) aliases.add(bluetoothAliases[upper]);
    if (bluetoothAliases[stripped]) aliases.add(bluetoothAliases[stripped]);

    if (/^BT_SEL\s+\d+$/i.test(text) || /^BT_SEL_\d+$/i.test(text)) aliases.add("Select Profile");
    return [...aliases].filter(Boolean);
  }

  function profileFromParameter(parameter) {
    const match = clean(String(parameter)).match(/^BT_SEL(?:\s+|_)(\d+)$/i);
    return match ? match[1] : null;
  }

  function isBehaviorSelect(select) {
    return [...select.options].some((o) => clean(o.textContent) === "Key Press")
      && [...select.options].some((o) => clean(o.textContent) === "Transparent");
  }

  function isZoomSelect(select) {
    return [...select.options].some((o) => clean(o.textContent) === "Auto")
      && [...select.options].some((o) => clean(o.textContent) === "100%");
  }

  async function setSelectParameter(parameter) {
    const normalized = clean(parameter);
    const aliases = parameterAliases(normalized);
    const select = visibleSelects().find((s) => !isBehaviorSelect(s) && !isZoomSelect(s) && [...s.options].some((o) => aliases.includes(clean(o.textContent)) || aliases.includes(clean(o.value))));
    if (!select) return false;
    const option = [...select.options].find((o) => aliases.includes(clean(o.textContent)) || aliases.includes(clean(o.value)));
    nativeSetValue(select, option.value);
    await sleep(180);

    const profile = profileFromParameter(normalized);
    if (profile !== null) {
      await sleep(500);
      const profileInput = visibleInputs().find((input) => input.type === "number" && Number(input.min) <= Number(profile) && Number(input.max) >= Number(profile));
      if (profileInput) {
        profileInput.focus();
        nativeSetValue(profileInput, profile);
        profileInput.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: profile }));
        profileInput.dispatchEvent(new Event("change", { bubbles: true }));
        profileInput.blur();
        await sleep(180);
        return true;
      }

      const profileSelect = visibleSelects().find((s) => !isBehaviorSelect(s) && !isZoomSelect(s) && s !== select && [...s.options].some((o) => clean(o.textContent) === profile || clean(o.value) === profile));
      if (!profileSelect) {
        console.warn(`Selected Bluetooth "Select Profile", but could not find a number/select Profile field for profile ${profile}. Verify manually before saving.`);
        return true;
      }
      const profileOption = [...profileSelect.options].find((o) => clean(o.textContent) === profile || clean(o.value) === profile);
      nativeSetValue(profileSelect, profileOption.value);
      await sleep(180);
    }
    return true;
  }

  async function applyItem(item) {
    if (item.studio_skip || item.behavior === "Output Selection") {
      console.log("Skipping (firmware-only, not in Studio UI):", item);
      return;
    }

    await selectLayer(item.layer);
    await selectKey(item.x, item.y);

    if (currentLooksLike(item)) {
      console.log("Already correct, skipping", item);
      return;
    }

    await setBehavior(item.behavior);

    if (["Transparent", "None", "Studio Unlock", "Reset", "Bootloader", "External Power",
         "launcher_powertoys", "launcher_win_search", "mouse_move", "mouse_scroll",
         "scroll_horizontal_encoder", "scroll_vertical_encoder",
         "To0_macro", "To1_macro", "To1_macro_A", "To2_macro", "To2_macro_A"
        ].includes(item.behavior) || /^coach_/.test(item.behavior)) {
      return;
    }

    const supported = ["Key Press", "Mouse Key Press", "Momentary Layer", "To Layer", "Toggle Layer", "Bluetooth", "Underglow"];
    if (!supported.includes(item.behavior)) {
      throw new Error(`Behavior "${item.behavior}" has behavior-specific controls that this applier does not safely automate yet. Use manualSteps or inspect_selected_behavior_controls.js.`);
    }

    if (!item.parameter) {
      console.warn("No parameter supplied for", item);
      return;
    }

    if (item.behavior === "Key Press") {
      await setKeyPressParameter(item.parameter);
      await setImplicitModifiers(item.modifiers || []);
      return;
    }

    const selectWorked = await setSelectParameter(item.parameter);
    if (!selectWorked) {
      console.warn(`No exact visible select option matched parameter "${item.parameter}". Trying visible text input/combobox. Verify manually before saving.`);
      await setTextParameter(item.parameter);
    }
  }

  function printPlan(items) {
    console.group("Charybdis ZMK Studio planned changes");
    console.warn("Safety: this script never clicks Save. Export backup first. Verify every key in Studio before saving.");
    for (const item of items) {
      const modifiers = item.modifiers?.length ? ` modifiers=${item.modifiers.join("+")}` : "";
      console.log(`Layer ${item.layer} x${item.x} y${item.y}: ${item.behavior} ${item.parameter || ""}${modifiers} [${item.label || ""}] - ${item.rationale || ""}`);
    }
    console.groupEnd();
  }

  function printManualSteps(items) {
    console.group("Manual ZMK Studio steps");
    for (const item of items) {
      console.log([
        `Layer ${item.layer}`,
        `click key x${item.x} y${item.y}`,
        `set Behavior = ${item.behavior}`,
        item.parameter ? `set parameter/key = ${item.parameter}` : "no parameter",
        item.modifiers?.length ? `set implicit modifiers = ${item.modifiers.join(", ")}` : "",
        item.label ? `label/check = ${item.label}` : "",
        item.rationale ? `why: ${item.rationale}` : ""
      ].filter(Boolean).join(" | "));
    }
    console.groupEnd();
  }

  const allItems = plannedKeys();
  const layerFilteredItems = APPLY_LAYERS
    ? allItems.filter((item) => APPLY_LAYERS.includes(Number(item.layer)))
    : allItems;
  const modeItems = MODE === "applyLayer" && APPLY_LAYER_INDEX !== "all"
    ? layerFilteredItems.filter((item) => Number(item.layer) === Number(APPLY_LAYER_INDEX))
    : layerFilteredItems;

  if (MODE === "dryRun") {
    validatePlanCoordinates(modeItems);
    validateSupportedBehaviors(modeItems);
    printPlan(modeItems);
    return;
  }

  if (MODE === "manualSteps") {
    validatePlanCoordinates(modeItems);
    validateSupportedBehaviors(modeItems);
    printManualSteps(modeItems);
    return;
  }

  if (MODE === "oneKeyTest") {
    console.warn("ONE KEY TEST: applying exactly one test key. Do not save until manually verified.");
    console.log(ONE_KEY_TEST);
    if (!validatePlanCoordinates([ONE_KEY_TEST]) || !validateSupportedBehaviors([ONE_KEY_TEST])) return;
    await applyItem(ONE_KEY_TEST);
    console.warn("One-key test complete. Verify the key in ZMK Studio. Save manually only if correct.");
    return;
  }

  if (MODE === "applyLayer") {
    if (!ENABLE_LAYER_APPLY) {
      console.error("Layer application is disabled. Set ENABLE_LAYER_APPLY = true only after dryRun and oneKeyTest succeed.");
      printPlan(modeItems);
      return;
    }
    if (!validatePlanCoordinates(modeItems) || !validateSupportedBehaviors(modeItems)) return;
    const confirmed = window.confirm(`Apply ${modeItems.length} planned changes ${APPLY_LAYER_INDEX === "all" ? "across multiple layers" : `to layer ${APPLY_LAYER_INDEX}`}? This will NOT save.`);
    if (!confirmed) {
      console.warn("Cancelled by user.");
      return;
    }
    for (const item of modeItems) {
      console.log("Applying", item);
      await applyItem(item);
    }
    console.warn("Layer apply complete. This script did NOT save. Verify in the UI before saving manually.");
    return;
  }

  throw new Error(`Unknown MODE "${MODE}". Use dryRun, manualSteps, oneKeyTest, or applyLayer.`);
})();






// Restore console and print summary with suggestions
setTimeout(function() {
  if (typeof _origError !== "undefined") {
    console.error = _origError;
    console.warn = _origWarn;
  }
  const errors = window._CHARYBDIS_APPLY_ERRORS || [];
  const total = window.CHARYBDIS_FINAL_LAYOUT?.keyCount || 0;
  console.log("\n" + "=".repeat(60));
  console.log("APPLY SUMMARY");
  console.log("=".repeat(60));
  console.log("Total keys: " + total);
  console.log("Errors: " + errors.length);
  if (errors.length > 0) {
    console.log("\nFAILED KEYS WITH SUGGESTIONS:");
    errors.forEach(function(e) {
      if (typeof e === "object") {
        const pos = e.layer !== undefined ? "L" + e.layer + " (" + e.x + "," + e.y + ")" : "";
        console.log("  " + pos + " " + (e.parameter || ""));
        if (e.candidates && e.candidates.length) {
          console.log("    Candidates: " + e.candidates.join(", "));
        }
        if (e.visibleOptions && e.visibleOptions.length) {
          console.log("    Visible options: " + e.visibleOptions.join(", "));
        }
      } else {
        console.log("  " + e);
      }
    });
    console.log("\nFix these parameter names in export_zmk.py, regenerate, and re-apply.");
  } else {
    console.log("All keys applied or already correct.");
  }
  console.log("=".repeat(60));
}, 2000);

