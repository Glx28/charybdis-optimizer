const PARAM_ALIASES = {
  "Delete": ["Keyboard Delete", "Backspace"],
  "Delete Forward": ["Keyboard Delete Forward"],
  "Escape": ["Keyboard Escape"],
  "Return Enter": ["Keyboard Return Enter", "Return", "Enter"],
  "Spacebar": ["Keyboard Spacebar", "Keyboard Space", "Space"],
  "Tab": ["Keyboard Tab"],
  "LeftShift": ["Keyboard LeftShift", "Left Shift"],
  "LeftControl": ["Keyboard LeftControl", "Left Control"],
  "LeftAlt": ["Keyboard LeftAlt", "Left Alt"],
  "Left GUI": ["Keyboard Left GUI", "LeftGUI"],
  "LeftArrow": ["Keyboard LeftArrow"],
  "RightArrow": ["Keyboard RightArrow"],
  "UpArrow": ["Keyboard UpArrow"],
  "DownArrow": ["Keyboard DownArrow"],
  "Home": ["Keyboard Home"],
  "End": ["Keyboard End"],
  "SemiColon and Colon": ["Keyboard SemiColon and Colon", "SemiColon"],
  "Left Apos and Double": ["Keyboard Left Apos and Double", "Apostrophe"],
  "Left Brace": ["Keyboard Left Brace", "Left Bracket"],
  "Right Brace": ["Keyboard Right Brace", "Right Bracket"],
  "Backslash and Pipe": ["Keyboard Backslash and Pipe", "Backslash"],
  "ForwardSlash and QuestionMark": ["Keyboard ForwardSlash and QuestionMark", "ForwardSlash"],
  "Comma and LessThan": ["Keyboard Comma and LessThan", "Comma"],
  "Period and GreaterThan": ["Keyboard Period and GreaterThan", "Period"],
  "Dash and Underscore": ["Keyboard Dash and Underscore", "Minus"],
  "Grave Accent and Tilde": ["Keyboard Grave Accent and Tilde", "Grave"],
};

const ALIAS_LOOKUP = new Map();
for (const [canonical, aliases] of Object.entries(PARAM_ALIASES)) {
  ALIAS_LOOKUP.set(canonical.toUpperCase(), canonical);
  for (const alias of aliases) {
    ALIAS_LOOKUP.set(alias.toUpperCase(), canonical);
  }
}

function normalizeParam(param) {
  if (!param) return "";
  const cleaned = param.trim()
    .replace(/^select:/, "")
    .replace(/^Layer::/, "")
    .replace(/^default_transform:default_transform$/, "");
  const upper = cleaned.replace(/^Keyboard\s+/i, "").toUpperCase();
  if (ALIAS_LOOKUP.has(cleaned.toUpperCase())) return ALIAS_LOOKUP.get(cleaned.toUpperCase());
  if (ALIAS_LOOKUP.has(upper)) return ALIAS_LOOKUP.get(upper);
  return cleaned.replace(/^Keyboard\s+/i, "");
}

function normalizeModifiers(mods) {
  if (!mods) return [];
  const arr = Array.isArray(mods) ? mods : mods.split(/[,+]/);
  return arr.map((m) => m.trim()).filter(Boolean).sort();
}

function normalizeBehavior(b) {
  return (b || "").trim();
}

function paramsMatch(a, b) {
  return normalizeParam(a).toUpperCase() === normalizeParam(b).toUpperCase();
}

function modifiersMatch(a, b) {
  const na = normalizeModifiers(a);
  const nb = normalizeModifiers(b);
  return na.join("|") === nb.join("|");
}

module.exports = { normalizeParam, normalizeModifiers, normalizeBehavior, paramsMatch, modifiersMatch, PARAM_ALIASES };
