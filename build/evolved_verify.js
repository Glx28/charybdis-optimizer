/*
Charybdis optimizer layout VERIFY — research-v1
Verifies 296 evolved changes across layers [1, 2, 3, 4, 5, 6, 8, 9, 10].
Paste in ZMK Studio console AFTER applying. Does not edit or save.
*/

window.CHARYBDIS_LAYER_ACCESS_REPORT = {
  "valid": true,
  "required_layers": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10
  ],
  "reachable_layers": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10
  ],
  "access_cost": 77.0,
  "errors": []
};


(async function VerifyEvolvedLayout() {
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const clean = (s) => String(s || "").trim();
  const qa = (sel, root) => [...(root || document).querySelectorAll(sel)];

  const expected = [
  {
    "layer": 1,
    "x": 0,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+B",
    "rationale": "Optimizer (evo_best_gen150): Win+B (Focus system tray)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+G",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+G (Go to line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 0,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 10,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+C",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+C (Inspect element)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 10,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 11,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Up",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Up (Jump to top edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard End",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+End",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+End (Go to last used cell)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+Down",
    "rationale": "Optimizer (evo_best_gen150): Shift+Alt+Down (Copy line down)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 12,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 12,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 12,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Up",
    "rationale": "Optimizer (evo_best_gen150): Win+Up (Maximize window)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 12,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 1,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F12",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+F12",
    "rationale": "Optimizer (evo_best_gen150): Alt+F12 (Peek definition)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [],
    "label": "leftarrow_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_leftarrow_combo (Base key: LeftArrow)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 1,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Tab",
    "rationale": "Optimizer (evo_best_gen150): Win+Tab (Task View)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard U",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+U",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+U (Mark as unread)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F5",
    "modifiers": [],
    "label": "f5",
    "rationale": "Optimizer (evo_best_gen150): _base_f5 (Base key: F5)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard 1 and Bang",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+1",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+1 (Activity)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard W",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+W",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+W (Change workflow state)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 3,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+N",
    "rationale": "Optimizer (evo_best_gen150): Win+N (Notification center)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard I",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+I",
    "rationale": "Optimizer (evo_best_gen150): Win+I (Settings)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+Right",
    "rationale": "Optimizer (evo_best_gen150): Shift+Alt+Right (Expand selection)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [],
    "label": "Up",
    "rationale": "Optimizer (evo_best_gen150): Up (Edit last sent message)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard 2 and At",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+2",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+2 (Chat)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Down",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Down (Jump to bottom edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 5,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+G",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+G (Source control panel)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F2",
    "modifiers": [],
    "label": "f2",
    "rationale": "Optimizer (evo_best_gen150): _base_f2 (Base key: F2)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+A",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+A (Accept call)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 5,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard PrintScreen and SysReq",
    "modifiers": [],
    "label": "print screen_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_print screen_combo (Base key: Print Screen)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+E",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+E (Check in document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Comma and LessThan",
    "modifiers": [],
    "label": "comma_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_comma_combo (Base key: Comma and LessThan)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Left GUI",
    "modifiers": [],
    "label": "left gui",
    "rationale": "Optimizer (evo_best_gen150): _base_left gui (Base key: Left GUI)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+O",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+O (Open document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+H",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+H (Hang up / end call)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard K",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+K",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+K (Insert link)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+P",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+P (Quick open file)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 9,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+R",
    "rationale": "Optimizer (evo_best_gen150): Win+R (Run dialog)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 1,
    "x": 9,
    "y": 3,
    "behavior": "coach_game_lock",
    "parameter": "",
    "modifiers": [],
    "label": "coach_game_lock",
    "rationale": "Optimizer (evo_best_gen150): _base_coach_game_lock (Base key: coach_game_lock)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+E",
    "rationale": "Optimizer (evo_best_gen150): Win+E (File Explorer)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 0,
    "y": 2,
    "behavior": "Mouse Key Press",
    "parameter": "MB4",
    "modifiers": [],
    "label": "MB4",
    "rationale": "Optimizer (evo_best_gen150): _base_select:mb4 (Base key: select:MB4)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 0,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 10,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+F",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+F (Find)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Dash and Underscore",
    "modifiers": [],
    "label": "minus",
    "rationale": "Optimizer (evo_best_gen150): _base_minus (Base key: Minus)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 10,
    "y": 2,
    "behavior": "coach_base",
    "parameter": "",
    "modifiers": [],
    "label": "coach_base",
    "rationale": "Optimizer (evo_best_gen150): _base_coach_base (Base key: coach_base)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 11,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F6",
    "modifiers": [],
    "label": "f6",
    "rationale": "Optimizer (evo_best_gen150): _base_f6 (Base key: F6)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F5",
    "modifiers": [],
    "label": "f5",
    "rationale": "Optimizer (evo_best_gen150): _base_f5 (Base key: F5)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 12,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Enter",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+Enter (Insert line above)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 1,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F9",
    "modifiers": [],
    "label": "f9",
    "rationale": "Optimizer (evo_best_gen150): _base_f9 (Base key: F9)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard K",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+K",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+K (Delete line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+H",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+H (Find and replace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 1,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard A",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+A",
    "rationale": "Optimizer (evo_best_gen150): Shift+Alt+A (Toggle block comment)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F10",
    "modifiers": [],
    "label": "f10",
    "rationale": "Optimizer (evo_best_gen150): _base_f10 (Base key: F10)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [],
    "label": "Enter",
    "rationale": "Optimizer (evo_best_gen150): Enter (Send message)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+G",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+G (Go to line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard PageUp",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Page Up",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Page Up (Previous sheet)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+G",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+G (Source control panel)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F5",
    "modifiers": [],
    "label": "F5",
    "rationale": "Optimizer (evo_best_gen150): F5 (Refresh page)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard I",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+I",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+I (Italic)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+E",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+E (Check in document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+[",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+[ (Outdent line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard 6 and Caret",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+6",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+6 (Files)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 5,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 5,
    "y": 5,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+C",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+C (Copy)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+Down",
    "rationale": "Optimizer (evo_best_gen150): Shift+Alt+Down (Copy line down)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard ForwardSlash and QuestionMark",
    "modifiers": [],
    "label": "forwardslash_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_forwardslash_combo (Base key: ForwardSlash and QuestionMark)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Right Brace",
    "modifiers": [],
    "label": "right brace_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_right brace_combo (Base key: Right Brace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard 2 and At",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+2",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+2 (Chat)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F4",
    "modifiers": [],
    "label": "f4",
    "rationale": "Optimizer (evo_best_gen150): _base_f4 (Base key: F4)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keypad 9 and PageUp",
    "modifiers": [],
    "label": "pageup",
    "rationale": "Optimizer (evo_best_gen150): _base_pageup (Base key: Keypad 9 and PageUp)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [],
    "label": "left brace_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_left brace_combo (Base key: Left Brace)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+S",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+S (Save)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 2,
    "behavior": "coach_travel_toggle",
    "parameter": "",
    "modifiers": [],
    "label": "coach_travel_toggle",
    "rationale": "Optimizer (evo_best_gen150): _base_coach_travel_toggle (Base key: coach_travel_toggle)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 2,
    "x": 9,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 1,
    "behavior": "Bluetooth",
    "parameter": "BT_SEL 1",
    "modifiers": [],
    "label": "Bluetooth",
    "rationale": "Optimizer (evo_best_gen150): _base_bt_sel 1 (Base key: BT_SEL 1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard U",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+U",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+U (Mark as unread)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 0,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard O",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+O",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+O (Open document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 0,
    "behavior": "Output Selection",
    "parameter": "Ble Output",
    "modifiers": [],
    "label": "select:ble output",
    "rationale": "Optimizer (evo_best_gen150): _base_select:ble output (Base key: select:BLE Output)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F16",
    "modifiers": [],
    "label": "f16",
    "rationale": "Optimizer (evo_best_gen150): _base_f16 (Base key: F16)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 2,
    "behavior": "Output Selection",
    "parameter": "Toggle Outputs",
    "modifiers": [],
    "label": "select:toggle outputs",
    "rationale": "Optimizer (evo_best_gen150): _base_select:toggle outputs (Base key: select:Toggle Outputs)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+R",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+R (Reply)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard 9 and Left Bracket",
    "modifiers": [],
    "label": "left bracket_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_left bracket_combo (Base key: 9 and Left Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard K",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+K",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+K (Delete line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+H",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+H (Hang up / end call)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Tab",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Tab (Next tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 12,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 12,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F8",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+F8",
    "rationale": "Optimizer (evo_best_gen150): Shift+F8 (Go to previous problem)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 12,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+E",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+E (Check in document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 12,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+N",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+N (New folder)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F17",
    "modifiers": [],
    "label": "f17",
    "rationale": "Optimizer (evo_best_gen150): _base_f17 (Base key: F17)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 1,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 2,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Equals and Plus",
    "modifiers": [],
    "label": "equal",
    "rationale": "Optimizer (evo_best_gen150): _base_equal (Base key: Equal and Plus)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 2,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+G",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+G (Go to line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 2,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keypad 3 and PageDn",
    "modifiers": [],
    "label": "keypad 3",
    "rationale": "Optimizer (evo_best_gen150): _base_keypad 3 (Base key: Keypad 3 and PageDn)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard M",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+M",
    "rationale": "Optimizer (evo_best_gen150): Win+M (Minimize all windows)",
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
    "rationale": "Optimizer (evo_best_gen150): Win+Left (Snap window left)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 5,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+V",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+V (Paste without formatting)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Y",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Y",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Y (Redo (alt))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 9,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard P",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+P",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+P (Quick open file)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 9,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard ForwardSlash and QuestionMark",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+/",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+/ (Toggle line comment)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 3,
    "x": 9,
    "y": 3,
    "behavior": "Bluetooth",
    "parameter": "BT_SEL 3",
    "modifiers": [],
    "label": "Bluetooth",
    "rationale": "Optimizer (evo_best_gen150): _base_bt_sel 3 (Base key: BT_SEL 3)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "Backspace",
    "rationale": "Optimizer (evo_best_gen150): Backspace (Go back / up)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F12",
    "modifiers": [],
    "label": "f12",
    "rationale": "Optimizer (evo_best_gen150): _base_f12 (Base key: F12)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F7",
    "modifiers": [],
    "label": "f7",
    "rationale": "Optimizer (evo_best_gen150): _base_f7 (Base key: F7)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 11,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Enter",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Enter (Send (expanded mode))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "delete",
    "rationale": "Optimizer (evo_best_gen150): _base_delete (Base key: Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F5",
    "modifiers": [],
    "label": "f5",
    "rationale": "Optimizer (evo_best_gen150): _base_f5 (Base key: F5)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 1,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+Up",
    "rationale": "Optimizer (evo_best_gen150): Shift+Alt+Up (Copy line up)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 3,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Tab",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Tab (Next tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard I",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+I",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+I (Italic)",
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
    "label": "Tab",
    "rationale": "Optimizer (evo_best_gen150): Tab (Indent / accept suggestion)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+T",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+T (New tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard ForwardSlash and QuestionMark",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+/",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+/ (Toggle line comment)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Return Enter",
    "modifiers": [],
    "label": "return enter",
    "rationale": "Optimizer (evo_best_gen150): _base_return enter (Base key: Return Enter)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Right Brace",
    "modifiers": [],
    "label": "right bracket",
    "rationale": "Optimizer (evo_best_gen150): _base_right bracket (Base key: Right Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard ForwardSlash and QuestionMark",
    "modifiers": [],
    "label": "forwardslash_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_forwardslash_combo (Base key: ForwardSlash and QuestionMark)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard X",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+X",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+X (Expand compose box)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+S",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+S (Save)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard V",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+V",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+V (Paste without formatting)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L GUI",
      "L Ctrl"
    ],
    "label": "Win+Ctrl+D",
    "rationale": "Optimizer (evo_best_gen150): Win+Ctrl+D (New virtual desktop)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard F6",
    "modifiers": [],
    "label": "f6",
    "rationale": "Optimizer (evo_best_gen150): _base_f6 (Base key: F6)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard End",
    "modifiers": [],
    "label": "end",
    "rationale": "Optimizer (evo_best_gen150): _base_end (Base key: End)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftShift",
    "modifiers": [],
    "label": "leftshift",
    "rationale": "Optimizer (evo_best_gen150): _base_leftshift (Base key: LeftShift)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Home",
    "modifiers": [],
    "label": "home",
    "rationale": "Optimizer (evo_best_gen150): _base_home (Base key: Home)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 8,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F9",
    "modifiers": [],
    "label": "f9",
    "rationale": "Optimizer (evo_best_gen150): _base_f9 (Base key: F9)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Left Brace",
    "modifiers": [],
    "label": "left bracket",
    "rationale": "Optimizer (evo_best_gen150): _base_left bracket (Base key: Left Bracket)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 4,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F11",
    "modifiers": [],
    "label": "f11",
    "rationale": "Optimizer (evo_best_gen150): _base_f11 (Base key: F11)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 0,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+N",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+N (New mail)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 0,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F1",
    "modifiers": [],
    "label": "f1",
    "rationale": "Optimizer (evo_best_gen150): _base_f1 (Base key: F1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 10,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keypad 3 and PageDn",
    "modifiers": [],
    "label": "keypad 3",
    "rationale": "Optimizer (evo_best_gen150): _base_keypad 3 (Base key: Keypad 3 and PageDn)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Backslash and Pipe",
    "modifiers": [],
    "label": "backslash",
    "rationale": "Optimizer (evo_best_gen150): _base_backslash (Base key: Backslash and Pipe)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 2,
    "behavior": "coach_travel_toggle",
    "parameter": "",
    "modifiers": [],
    "label": "coach_travel_toggle",
    "rationale": "Optimizer (evo_best_gen150): _base_coach_travel_toggle (Base key: coach_travel_toggle)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 11,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 12,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 12,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 12,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 12,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 1,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 1,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+F",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+F (Format document)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F18",
    "modifiers": [],
    "label": "f18",
    "rationale": "Optimizer (evo_best_gen150): _base_f18 (Base key: F18)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard J",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+J",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+J (Toggle bottom panel)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 2,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 3,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L GUI",
      "L Ctrl"
    ],
    "label": "Win+Ctrl+Right",
    "rationale": "Optimizer (evo_best_gen150): Win+Ctrl+Right (Switch desktop right)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Grave Accent and Tilde",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+`",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+` (New terminal)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+S",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+S (Attach file)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F8",
    "modifiers": [],
    "label": "f8",
    "rationale": "Optimizer (evo_best_gen150): _base_f8 (Base key: F8)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 5,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard H",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+H",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+H (Hang up / end call)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 7,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard G",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+G",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+G (Go to line)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 8,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 9,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L GUI",
      "L Ctrl"
    ],
    "label": "Win+Ctrl+D",
    "rationale": "Optimizer (evo_best_gen150): Win+Ctrl+D (New virtual desktop)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard W",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+W",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+W (Close tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+L",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+L (Focus address bar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 5,
    "x": 9,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 10,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Left",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+Left (Select to left edge)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Ctrl",
      "L Alt"
    ],
    "label": "Ctrl+Alt+Down",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Alt+Down (Add cursor below)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Right",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+Right (Select to right edge)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Up",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+Up (Select to top edge)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 1,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Down",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+Down (Select to bottom edge)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Space",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Space (Select entire column)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F9",
    "modifiers": [],
    "label": "F9",
    "rationale": "Optimizer (evo_best_gen150): F9 (Toggle breakpoint)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 2,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Equals and Plus",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift++",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift++ (Insert cells/rows/columns)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Equals and Plus",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+=",
    "rationale": "Optimizer (evo_best_gen150): Alt+= (AutoSum)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F10",
    "modifiers": [],
    "label": "F10",
    "rationale": "Optimizer (evo_best_gen150): F10 (Step over)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F11",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+F11",
    "rationale": "Optimizer (evo_best_gen150): Shift+F11 (Step out)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Left",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Left (Jump to left edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L GUI",
      "L Shift"
    ],
    "label": "Win+Shift+Left",
    "rationale": "Optimizer (evo_best_gen150): Win+Shift+Left (Move to left monitor)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard 3 and Hash",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+3",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+3 (Teams/channels)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L GUI",
      "L Shift"
    ],
    "label": "Win+Shift+Right",
    "rationale": "Optimizer (evo_best_gen150): Win+Shift+Right (Move to right monitor)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard 0 and Right Bracket",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+0",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+0 (Reset zoom)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Right",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Right (Jump to right edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Space",
    "rationale": "Optimizer (evo_best_gen150): Win+Space (Switch input language)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard F4",
    "modifiers": [],
    "label": "F4",
    "rationale": "Optimizer (evo_best_gen150): F4 (Toggle absolute ref ($))",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard R",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+R",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+R (Reply all)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard I",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+I",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+I (Go to Inbox)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Q",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Q",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Q (Mark as read)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Right",
    "rationale": "Optimizer (evo_best_gen150): Alt+Right (Forward)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard 4 and Dollar",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+4",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+4 (Calendar)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+T",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+T (Reopen closed tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard 5 and Percent",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+5",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+5 (Calls)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F5",
    "modifiers": [],
    "label": "F5",
    "rationale": "Optimizer (evo_best_gen150): F5 (Refresh page)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 6,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard 6 and Caret",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+6",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+6 (Files)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 10,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+.",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+. (Show commands)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 2,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F11",
    "modifiers": [],
    "label": "F11",
    "rationale": "Optimizer (evo_best_gen150): F11 (Step into)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 2,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F6",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+F6",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+F6 (Next section)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 3,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard S",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+S",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+S (Attach file)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 3,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+B",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+B (Toggle background blur)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Escape",
    "modifiers": [],
    "label": "escape",
    "rationale": "Optimizer (evo_best_gen150): _base_escape (Base key: Escape)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Home",
    "modifiers": [],
    "label": "home",
    "rationale": "Optimizer (evo_best_gen150): _base_home (Base key: Home)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Left GUI",
    "modifiers": [],
    "label": "left gui",
    "rationale": "Optimizer (evo_best_gen150): _base_left gui (Base key: Left GUI)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [],
    "label": "tab",
    "rationale": "Optimizer (evo_best_gen150): _base_tab (Base key: Tab)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 4,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard Delete",
    "modifiers": [],
    "label": "Delete",
    "rationale": "Optimizer (evo_best_gen150): Delete (Delete)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [
      "L GUI",
      "L Ctrl"
    ],
    "label": "Win+Ctrl+Right",
    "rationale": "Optimizer (evo_best_gen150): Win+Ctrl+Right (Switch desktop right)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Period and GreaterThan",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+.",
    "rationale": "Optimizer (evo_best_gen150): Win+. (Emoji picker)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 5,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard F10",
    "modifiers": [],
    "label": "F10",
    "rationale": "Optimizer (evo_best_gen150): F10 (Step over)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Escape",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Esc",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+Esc (Task Manager)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Grave Accent and Tilde",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+`",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+` (New terminal)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 7,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard SemiColon and Colon",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+;",
    "rationale": "Optimizer (evo_best_gen150): Win+; (Emoji picker)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard Spacebar",
    "modifiers": [
      "L Shift"
    ],
    "label": "Shift+Space",
    "rationale": "Optimizer (evo_best_gen150): Shift+Space (Select entire row)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Z",
    "modifiers": [
      "L Ctrl",
      "L Shift"
    ],
    "label": "Ctrl+Shift+Z",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Shift+Z (Redo)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard F4",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+F4",
    "rationale": "Optimizer (evo_best_gen150): Alt+F4 (Close window)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Up",
    "rationale": "Optimizer (evo_best_gen150): Alt+Up (Move line up)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 8,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 9,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard Dash and Underscore",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+-",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+- (Delete cells/rows/columns)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 9,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Alt"
    ],
    "label": "Alt+Down",
    "rationale": "Optimizer (evo_best_gen150): Alt+Down (Move line down)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 8,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Home",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Home",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Home (Go to cell A1)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 0,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 0,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard F2",
    "modifiers": [],
    "label": "f2",
    "rationale": "Optimizer (evo_best_gen150): _base_f2 (Base key: F2)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 0,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keypad 9 and PageUp",
    "modifiers": [],
    "label": "pageup",
    "rationale": "Optimizer (evo_best_gen150): _base_pageup (Base key: Keypad 9 and PageUp)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 0,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 3,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 3,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 3,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 4,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard End",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+End",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+End (Go to last used cell)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 4,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard Tab",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Tab",
    "rationale": "Optimizer (evo_best_gen150): Win+Tab (Task View)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 5,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 7,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Up",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Up (Jump to top edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Shift",
      "L Alt"
    ],
    "label": "Shift+Alt+Down",
    "rationale": "Optimizer (evo_best_gen150): Shift+Alt+Down (Copy line down)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftShift",
    "modifiers": [],
    "label": "leftshift",
    "rationale": "Optimizer (evo_best_gen150): _base_leftshift (Base key: LeftShift)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard RightArrow",
    "modifiers": [],
    "label": "rightarrow_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_rightarrow_combo (Base key: RightArrow)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 8,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 9,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 9,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 9,
    "x": 9,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard DownArrow",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Down",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Down (Jump to bottom edge of data)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 10,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard Grave Accent and Tilde",
    "modifiers": [],
    "label": "grave accent_combo",
    "rationale": "Optimizer (evo_best_gen150): _base_grave accent_combo (Base key: Grave Accent and Tilde)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 11,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 11,
    "y": 1,
    "behavior": "Key Press",
    "parameter": "Keyboard B",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+B",
    "rationale": "Optimizer (evo_best_gen150): Win+B (Focus system tray)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 11,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard 2 and At",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+2",
    "rationale": "Optimizer (evo_best_gen150): Win+2 (Open/switch pinned app 2)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 11,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard LeftArrow",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+Left",
    "rationale": "Optimizer (evo_best_gen150): Win+Left (Snap window left)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 12,
    "y": 0,
    "behavior": "Key Press",
    "parameter": "Keyboard C",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+C",
    "rationale": "Optimizer (evo_best_gen150): Win+C (Open Copilot)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 12,
    "y": 1,
    "behavior": "coach_game_lock",
    "parameter": "",
    "modifiers": [],
    "label": "coach_game_lock",
    "rationale": "Optimizer (evo_best_gen150): _base_coach_game_lock (Base key: coach_game_lock)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 12,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard N",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+N",
    "rationale": "Optimizer (evo_best_gen150): Win+N (Notification center)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 12,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 2,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 3,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard UpArrow",
    "modifiers": [
      "L Ctrl",
      "L Alt"
    ],
    "label": "Ctrl+Alt+Up",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Alt+Up (Add cursor above)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 4,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard F13",
    "modifiers": [],
    "label": "f13",
    "rationale": "Optimizer (evo_best_gen150): _base_f13 (Base key: F13)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 2,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard PageDown",
    "modifiers": [
      "L Ctrl"
    ],
    "label": "Ctrl+Page Down",
    "rationale": "Optimizer (evo_best_gen150): Ctrl+Page Down (Next sheet)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 5,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 2,
    "behavior": "Key Press",
    "parameter": "Keyboard L",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+L",
    "rationale": "Optimizer (evo_best_gen150): Win+L (Lock PC)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 4,
    "behavior": "Key Press",
    "parameter": "Keyboard T",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+T",
    "rationale": "Optimizer (evo_best_gen150): Win+T (Cycle taskbar apps)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 7,
    "y": 5,
    "behavior": "Key Press",
    "parameter": "Keyboard D",
    "modifiers": [
      "L GUI",
      "L Ctrl"
    ],
    "label": "Win+Ctrl+D",
    "rationale": "Optimizer (evo_best_gen150): Win+Ctrl+D (New virtual desktop)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 1,
    "behavior": "coach_mouse_lock",
    "parameter": "",
    "modifiers": [],
    "label": "coach_mouse_lock",
    "rationale": "Optimizer (evo_best_gen150): _base_coach_mouse_lock (Base key: coach_mouse_lock)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 3,
    "behavior": "Key Press",
    "parameter": "Keyboard E",
    "modifiers": [
      "L GUI"
    ],
    "label": "Win+E",
    "rationale": "Optimizer (evo_best_gen150): Win+E (File Explorer)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 8,
    "y": 4,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 9,
    "y": 0,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 9,
    "y": 1,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  },
  {
    "layer": 10,
    "x": 9,
    "y": 3,
    "behavior": "Transparent",
    "parameter": "",
    "modifiers": [],
    "label": "",
    "rationale": "Cleared by optimizer (evo_best_gen150)",
    "optimizer_changed": true,
    "apply_batch": true
  }
];
  const layers = [1, 2, 3, 4, 5, 6, 8, 9, 10];
  const accessReport = window.CHARYBDIS_LAYER_ACCESS_REPORT || {};

  // --- Layer selection (mirrors apply script) ---

  function findLayerButton(layer) {
    const layerList = document.querySelector('[aria-label="Keymap Layer"]');
    return layerList?.querySelector('[role="option"][data-key="' + layer + '"]')
      || qa('[role="option"]', layerList || document).find(el => clean(el.textContent) === String(layer));
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

  // --- Key selection (mirrors apply script) ---

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

    const combobox = qa("input").find(i => i.offsetParent !== null && i.getAttribute("role") === "combobox");
    let parameter = combobox ? clean(combobox.value) : "";

    if (!parameter) {
      const paramSelect = allSelects.find(s =>
        s !== bSel && !isBehaviorSelect(s) && !isZoomSelect(s) && !isDefaultTransformSelect(s)
      );
      if (paramSelect) {
        parameter = clean(paramSelect.options[paramSelect.selectedIndex]?.textContent) || "";
      }
    }

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
  let passed = 0, failed = 0, skipped = 0;
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
  console.log("LAYER ACCESS");
  console.log("Valid expected graph: " + (accessReport.valid ? "YES" : "NO"));
  if (accessReport.required_layers) console.log("Required layers: " + accessReport.required_layers.join(", "));
  if (accessReport.reachable_layers) console.log("Reachable layers: " + accessReport.reachable_layers.join(", "));
  if (accessReport.access_cost !== undefined) console.log("Total access cost: " + accessReport.access_cost);
  if (accessReport.errors && accessReport.errors.length) console.error("Access errors: " + accessReport.errors.join("; "));
  console.log("-".repeat(50));
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

