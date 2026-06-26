/*
Charybdis optimizer layout — evolved-evo_best_gen150
296 key changes across layers [1, 2, 3, 4, 5, 6, 8, 9, 10].
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
  "version": "evolved-evo_best_gen150",
  "keyCount": 296,
  "keys": [
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
    "Keyboard PageUp","Keyboard Period","Keyboard Period and GreaterThan","Keyboard PrintScreen and SysReq",
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

    const mouseAliases = { MB1: "MB1", MB2: "MB2", MB3: "MB3", MB4: "MB4", MB5: "MB5" };
    if (mouseAliases[upper]) aliases.add(mouseAliases[upper]);

    const outputAliases = {
      OUT_TOG: "Toggle Outputs",
      OUT_TOGGLE: "Toggle Outputs",
      OUT_USB: "USB Output",
      USB: "USB Output",
      OUT_BLE: "BLE Output",
      BLE: "BLE Output"
    };
    if (outputAliases[upper]) aliases.add(outputAliases[upper]);

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
      await sleep(250);
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

    if (["Transparent", "None", "Studio Unlock", "Reset", "Bootloader"].includes(item.behavior) || /^coach_/.test(item.behavior)) {
      return;
    }

    const supported = ["Key Press", "Mouse Key Press", "Momentary Layer", "To Layer", "Toggle Layer", "Bluetooth", "Output Selection"];
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

