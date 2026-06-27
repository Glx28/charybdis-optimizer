"""Genome encoding for keyboard layout evolution.

A genome is an integer array of length M where M = number of mutable positions.
Each gene value is a shortcut ID (index into shortcut_pool) or -1 for transparent/empty.
"""
import json
import re
from dataclasses import dataclass, field

# Position value model — see docs/position_value_model.md
# y=2 home row = best, y=1/y=3 adjacent = good, y=0 top = reach, y=4-5 thumb = context-dependent
# Inner columns (x=1-4 left, x=8-11 right) = no extra, outer (x=0,5,7,12) = stretch penalty
ROW_COMFORT = {0: 3.5, 1: 1.0, 2: 0.0, 3: 1.0, 4: 1.5, 5: 2.5}
COL_EFFORT = {0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 7: 2, 8: 0, 9: 0, 10: 0, 11: 0, 12: 2}
LEFT_COLS = {0, 1, 2, 3, 4, 5}
RIGHT_COLS = {7, 8, 9, 10, 11, 12}

FINGER_MAP = {
    0: "far_pinky", 1: "pinky", 2: "ring", 3: "middle", 4: "index", 5: "index_stretch",
    7: "index_stretch", 8: "index", 9: "middle", 10: "ring", 11: "pinky", 12: "far_pinky",
}

LAYER_NAMES_DEFAULT = {
    0: "Base", 1: "L1", 2: "L2", 3: "L3", 4: "L4",
    5: "L5", 6: "L6", 7: "Game", 8: "L8", 9: "L9", 10: "L10",
}
LAYER_NAMES = LAYER_NAMES_DEFAULT

LAYER_ACCESS = {
    1: {"thumb": "left", "key_x": 3, "key_y": 4, "method": "momentary"},
    2: {"thumb": "left", "key_x": 5, "key_y": 5, "method": "momentary_or_locked"},
    3: {"thumb": "right", "key_x": 8, "key_y": 4, "method": "momentary"},
    4: {"thumb": "right", "key_x": 7, "key_y": 4, "method": "momentary"},
    5: {"thumb": None, "method": "toggled"},
    6: {"thumb": None, "method": "toggled"},
    7: {"thumb": None, "method": "locked"},
    8: {"thumb": None, "method": "toggled"},
    9: {"thumb": None, "method": "toggled"},
    10: {"thumb": None, "method": "toggled"},
}

UNIVERSAL_SHORTCUTS = {"Enter", "Tab", "Escape", "Delete", "Backspace"}

def is_universal_shortcut(shortcut):
    """Shortcuts like Enter/Tab/Escape are app-agnostic and valid on any layer."""
    base = shortcut.base_key.strip()
    if base in UNIVERSAL_SHORTCUTS:
        return True
    if not shortcut.modifiers and base.upper() in {
        "RETURN", "ENTER", "TAB", "ESCAPE", "ESC", "DELETE", "BACKSPACE",
        "RETURN ENTER",
    }:
        return True
    return False

THUMB_HAND = {3: "left", 4: "left", 5: "left", 7: "right", 8: "right"}

COACH_BEHAVIORS = {
    "coach_l1_hold", "coach_l2_hold", "coach_l3_hold", "coach_l4_hold",
    "coach_mouse_lock", "coach_game_lock", "coach_base",
    "coach_travel_toggle", "coach_travel_off", "coach_recover_base",
}

STRUCTURAL_BEHAVIORS = COACH_BEHAVIORS | {
    "Momentary Layer", "Toggle Layer", "To Layer",
}

KEY_GROUPS = [
    {"name": "arrows", "params": ["LeftArrow", "RightArrow", "UpArrow", "DownArrow"], "protected": True},
    {"name": "win_directions", "params": ["LeftArrow", "RightArrow", "UpArrow", "DownArrow"], "mods_required": "win", "protected": True},
    {"name": "clipboard", "params": ["C", "V", "X", "Z", "Y"], "mods_required": "ctrl"},
    {"name": "mouse_buttons", "behaviors": ["Mouse Key Press"]},
    {"name": "bt_profiles", "behaviors": ["Bluetooth"]},
    {"name": "f_keys_low", "params": ["F1", "F2", "F3", "F4", "F5", "F6"]},
    {"name": "f_keys_high", "params": ["F7", "F8", "F9", "F10", "F11", "F12"]},
]

# Importance scores for base/structural keys — these protect keys through math, not freezes.
# Mouse buttons are critical: no physical mouse, trackball only. MB1-3 are essential.
# Norwegian layout: semicolon=ø, left_apos=æ, left_brace=å — these are on L0 locked area.
BASE_KEY_IMPORTANCE = {
    "spacebar": 100.0,
    "return enter": 40.0,
    "backspace": 35.0,
    "tab": 25.0,
    "escape": 20.0,
    "delete": 15.0,
    "leftshift": 35.0,
    "rightshift": 30.0,
    "leftcontrol": 35.0,
    "rightcontrol": 30.0,
    "leftalt": 25.0,
    "rightalt": 20.0,
    "left gui": 20.0,
    # Mouse buttons — no physical mouse, trackball keyboard. High value.
    "select:mb1": 45.0,     # left click — most used input after typing
    "select:mb2": 35.0,     # right click — context menus, essential
    "select:mb3": 20.0,     # middle click — open in new tab, close tab, scroll click
    "select:mb4": 12.0,     # back — browser/explorer navigation
    "select:mb5": 12.0,     # forward — browser/explorer navigation
    "coach_l1_hold": 18.0,
    "coach_l2_hold": 20.0,
    "coach_l3_hold": 15.0,
    "coach_l4_hold": 15.0,
    "coach_base": 12.0,
    "coach_mouse_lock": 10.0,
    # Scroll: Momentary Layer 6 — only way to scroll on trackball keyboard
    "momentary_layer_layer::6": 40.0,
    "coach_game_lock": 8.0,
    "coach_travel_toggle": 8.0,
    "coach_travel_off": 6.0,
    "coach_recover_base": 6.0,
    "momentary layer": 15.0,
    "toggle layer": 15.0,
    "to layer": 12.0,
    "bt_sel 0": 8.0,
    "bt_sel 1": 8.0,
    "bt_sel 2": 7.0,
    "bt_sel 3": 6.0,
    "bt_sel 4": 5.0,
    "select:clear selected profile": 5.0,
    "select:ble output": 6.0,
    "select:usb output": 6.0,
    "select:toggle outputs": 5.0,
    "reset": 3.0,
    "bootloader": 3.0,
    # F-keys
    "f1": 8.0, "f2": 10.0, "f3": 8.0, "f4": 8.0, "f5": 10.0, "f6": 6.0,
    "f7": 6.0, "f8": 8.0, "f9": 8.0, "f10": 8.0, "f11": 10.0, "f12": 12.0,
    "f13": 10.0, "f14": 10.0, "f15": 10.0, "f16": 10.0, "f17": 10.0, "f18": 10.0,
    "f19": 10.0, "f20": 10.0, "f21": 10.0, "f22": 10.0, "f23": 10.0, "f24": 10.0,
}

PUNCTUATION_IMPORTANCE = {
    "period": 40.0,
    "comma": 35.0,
    "semicolon": 30.0,          # ø on Norwegian layout
    "left apos": 25.0,          # æ on Norwegian layout
    "left brace": 25.0,         # å on Norwegian layout
    "forwardslash": 20.0,
    "backslash": 15.0,
    "dash": 20.0,
    "minus": 20.0,
    "equals": 15.0,
    "equal": 15.0,
    "right brace": 15.0,
    "right bracket": 15.0,
    "left bracket": 15.0,
    "grave accent": 10.0,
    # Combo keys (shifted/modified chars — Norwegian layout produces special chars)
    "semicolon_combo": 18.0,    # Ø (shifted ø)
    "left brace_combo": 15.0,   # Å (shifted å)
    "period_combo": 24.0,       # : (colon — very common in code/URLs)
    "comma_combo": 21.0,        # ; (semicolon — common in code)
    "minus_combo": 12.0,        # _ (underscore — very common in code)
    "equal_combo": 9.0,
    "forwardslash_combo": 12.0,
    "backslash_combo": 9.0,
    "left bracket_combo": 9.0,
    "right bracket_combo": 9.0,
    "right brace_combo": 9.0,
    # Navigation keys — individual importance + group bonus from KEY_GROUPS
    "leftarrow": 30.0,
    "rightarrow": 30.0,
    "uparrow": 30.0,
    "downarrow": 30.0,
    "home": 15.0,
    "end": 15.0,
    "pageup": 12.0,
    "pagedown": 12.0,
    "page up": 12.0,
    "page down": 12.0,
    "keypad 9": 12.0,
    "keypad 3": 12.0,
    "insert": 8.0,
    "print screen": 10.0,
    "printscreen": 10.0,
    # Combo navigation (Shift+arrows = selection, common in editors)
    "leftarrow_combo": 18.0,
    "rightarrow_combo": 18.0,
    "uparrow_combo": 18.0,
    "downarrow_combo": 18.0,
    "home_combo": 9.0,
    "end_combo": 9.0,
    "pageup_combo": 7.2,
    "pagedown_combo": 7.2,
}
# Letters get uniform high importance
for _letter in "abcdefghijklmnopqrstuvwxyz":
    BASE_KEY_IMPORTANCE[_letter] = 50.0
# Numbers get moderate importance
for _digit in "0123456789":
    BASE_KEY_IMPORTANCE[_digit] = 20.0


def discover_dynamic_groups(conjunction_pairs, usage_stats, shortcut_pool, threshold=0.5):
    """Discover groups from usage sequences and conjunction pairs.

    Returns list of dynamic groups: {"name": str, "sids": [int], "weight": float, "protected": True}
    """
    sid_lookup = {s.keys: s.sid for s in shortcut_pool}
    pair_weights = {}

    sequences = usage_stats.get("sequences", {})
    for seq_key, data in sequences.items():
        count = data if isinstance(data, (int, float)) else data.get("count", 0)
        if count < 2:
            continue
        parts = seq_key.split("|")
        if len(parts) != 2:
            continue
        sid_a = sid_lookup.get(parts[0])
        sid_b = sid_lookup.get(parts[1])
        if sid_a is not None and sid_b is not None:
            key = tuple(sorted([sid_a, sid_b]))
            pair_weights[key] = pair_weights.get(key, 0) + count

    for pair_key, weight in conjunction_pairs.items():
        parts = pair_key.split("|")
        if len(parts) != 2:
            continue
        sid_a = sid_lookup.get(parts[0])
        sid_b = sid_lookup.get(parts[1])
        if sid_a is not None and sid_b is not None:
            key = tuple(sorted([sid_a, sid_b]))
            pair_weights[key] = pair_weights.get(key, 0) + weight

    if not pair_weights:
        return []

    max_w = max(pair_weights.values())
    if max_w <= 0:
        return []

    groups = []
    used_sids = set()

    # Chain-derived groups: chains with 3+ members become multi-SID groups
    chains = usage_stats.get("chains", {})
    for chain_key, chain_data in chains.items():
        parts = chain_key.split(" -> ")
        count = chain_data if isinstance(chain_data, (int, float)) else chain_data.get("count", 0)
        if count < 3 or len(parts) < 3:
            continue
        chain_sids = []
        for p in parts:
            sid = sid_lookup.get(p)
            if sid is not None and sid not in chain_sids:
                chain_sids.append(sid)
        if len(chain_sids) < 3:
            continue
        name = f"chain_{'_'.join(shortcut_pool[s].keys for s in chain_sids[:3])}"
        groups.append({
            "name": name,
            "sids": chain_sids,
            "weight": 1.0,
            "protected": True,
            "dynamic": True,
        })
        for s in chain_sids:
            used_sids.add(s)

    # Pair-derived groups from conjunction weights
    sorted_pairs = sorted(pair_weights.items(), key=lambda x: -x[1])
    for (sid_a, sid_b), w in sorted_pairs:
        norm_w = w / max_w
        if norm_w < threshold:
            break
        if sid_a in used_sids or sid_b in used_sids:
            continue
        sa = shortcut_pool[sid_a]
        sb = shortcut_pool[sid_b]
        groups.append({
            "name": f"dynamic_{sa.keys}_{sb.keys}",
            "sids": [sid_a, sid_b],
            "weight": norm_w,
            "protected": True,
            "dynamic": True,
        })
        used_sids.add(sid_a)
        used_sids.add(sid_b)

    return groups


def find_group_members(sid, genome, positions, pool, dynamic_groups=None):
    """Given a shortcut sid, find if it belongs to a protected group.
    Returns (group, member_gene_indices) or (None, [])."""
    if sid < 0:
        return None, []
    s = pool[sid]

    for group in KEY_GROUPS:
        if not group.get("protected"):
            continue
        if "behaviors" in group:
            continue
        params = [p.upper() for p in group.get("params", [])]
        mods_req = group.get("mods_required", "")
        if s.base_key.upper() not in params:
            continue
        if mods_req and not any(mods_req.lower() in m.lower() for m in s.modifiers):
            continue
        try:
            idx = list(genome).index(sid)
        except ValueError:
            continue
        pos = positions[idx]
        member_indices = []
        for i, other_sid in enumerate(genome):
            if other_sid < 0:
                continue
            other = pool[other_sid]
            if other.base_key.upper() not in params:
                continue
            if mods_req and not any(mods_req.lower() in m.lower() for m in other.modifiers):
                continue
            if positions[i].layer == pos.layer:
                member_indices.append(i)
        return group, member_indices

    for dg in (dynamic_groups or []):
        if sid not in dg["sids"]:
            continue
        try:
            idx = list(genome).index(sid)
        except ValueError:
            continue
        pos = positions[idx]
        member_indices = []
        for i, other_sid in enumerate(genome):
            if other_sid < 0:
                continue
            if other_sid in dg["sids"] and positions[i].layer == pos.layer:
                member_indices.append(i)
        if len(member_indices) >= 2:
            return dg, member_indices

    return None, []


def is_in_protected_group(gene_idx, genome, positions, pool, dynamic_groups=None):
    """Check if the shortcut at gene_idx is part of a protected group."""
    sid = genome[gene_idx]
    if sid < 0:
        return False
    group, _ = find_group_members(sid, genome, positions, pool, dynamic_groups)
    return group is not None

KNOWN_KEY_NAMES = {
    "Keyboard 0 and Right Bracket", "Keyboard 1 and Bang", "Keyboard 2 and At",
    "Keyboard 3 and Hash", "Keyboard 4 and Dollar", "Keyboard 5 and Percent",
    "Keyboard 6 and Caret", "Keyboard 7 and Ampersand", "Keyboard 8 and Star",
    "Keyboard 9 and Left Bracket", "Keyboard A", "Keyboard B",
    "Keyboard Backslash and Pipe", "Keyboard C", "Keyboard Comma and LessThan",
    "Keyboard D", "Keyboard Dash and Underscore", "Keyboard Delete",
    "Keyboard Delete Forward", "Keyboard DownArrow", "Keyboard E", "Keyboard End",
    "Keyboard Equals and Plus", "Keyboard Escape", "Keyboard F",
    "Keyboard F1", "Keyboard F2", "Keyboard F3", "Keyboard F4", "Keyboard F5",
    "Keyboard F6", "Keyboard F7", "Keyboard F8", "Keyboard F9", "Keyboard F10",
    "Keyboard F11", "Keyboard F12", "Keyboard F13", "Keyboard F14", "Keyboard F15",
    "Keyboard F16", "Keyboard F17", "Keyboard F18", "Keyboard F19", "Keyboard F20",
    "Keyboard F21", "Keyboard F22", "Keyboard F23", "Keyboard F24",
    "Keyboard ForwardSlash and QuestionMark", "Keyboard G",
    "Keyboard Grave Accent and Tilde", "Keyboard H", "Keyboard Home", "Keyboard I",
    "Keyboard J", "Keyboard K", "Keyboard L", "Keyboard Left Apos and Double",
    "Keyboard Left Brace", "Keyboard Left GUI", "Keyboard LeftAlt",
    "Keyboard LeftArrow", "Keyboard LeftControl", "Keyboard LeftShift", "Keyboard M",
    "Keyboard N", "Keyboard O", "Keyboard P", "Keyboard PageDown", "Keyboard PageUp",
    "Keyboard Period and GreaterThan",
    "Keyboard PrintScreen and SysReq", "Keyboard Q", "Keyboard R",
    "Keyboard Return Enter", "Keyboard Right Brace", "Keyboard RightArrow",
    "Keyboard S", "Keyboard SemiColon and Colon", "Keyboard Spacebar", "Keyboard T",
    "Keyboard Tab", "Keyboard U", "Keyboard UpArrow", "Keyboard V", "Keyboard W",
    "Keyboard X", "Keyboard Y", "Keyboard Z",
    "Keypad 3 and PageDn", "Keypad 9 and PageUp",
}


@dataclass
class Position:
    gene_idx: int
    layer: int
    x: int
    y: int
    coord: str
    effort: float
    hand: str
    finger: str
    is_thumb: bool


@dataclass
class Shortcut:
    sid: int
    keys: str
    action: str
    app: str
    category: str
    importance: float
    base_key: str
    modifiers: list = field(default_factory=list)
    zmk_parameter: str = ""
    apps: list = field(default_factory=list)  # all apps this shortcut belongs to


def effort(x, y):
    return ROW_COMFORT.get(y, 5) + COL_EFFORT.get(x, 5)


def hand(x):
    return "left" if x in LEFT_COLS else "right"


def finger(x):
    return FINGER_MAP.get(x, "unknown")


def is_structural(binding, layer_num=None):
    """Only truly non-assignable bindings: layer control mechanics, studio unlock.
    Transparent/none on non-L0 layers are EMPTY SLOTS (genome=-1), not structural.
    On L0, transparent/none are structural (nothing below to pass through to).
    Coach behaviors are assignable and movable."""
    b = binding.get("behavior", "")
    if b.lower() in ("transparent", "none", ""):
        if layer_num is not None and layer_num > 0:
            return False  # empty slot on non-L0 layer, optimizer can fill it
        return True  # L0 or unknown layer: treat as structural
    if b in ("Momentary Layer", "Toggle Layer", "To Layer"):
        return False  # movable base keys — optimizer places them via importance scoring
    if any(kw in b.lower() for kw in ["studio unlock"]):
        return True
    return False


def get_base_key_id(binding):
    """Extract a base key identifier from a binding for importance lookup.
    Returns (key_id, importance) or (None, 0) if not a base key."""
    b = binding.get("behavior", "")
    p = binding.get("parameter", "").lower()
    mods = binding.get("modifiers", [])

    if b.lower() in COACH_BEHAVIORS:
        return b.lower(), BASE_KEY_IMPORTANCE.get(b.lower(), 5.0)

    if b in ("Momentary Layer", "Toggle Layer", "To Layer"):
        key_id = f"{b.lower().replace(' ', '_')}_{p}"
        imp = BASE_KEY_IMPORTANCE.get(key_id, BASE_KEY_IMPORTANCE.get(b.lower(), 15.0))
        return key_id, imp

    if "mouse key press" in b.lower():
        search_text = " ".join(str(binding.get(k, "")) for k in ("parameter", "label", "purpose", "usage_notes"))
        mb_match = re.search(r"(?:select:\s*)?mb\s*([1-5])", search_text, re.IGNORECASE)
        if mb_match:
            key_id = f"select:mb{mb_match.group(1)}"
            return key_id, BASE_KEY_IMPORTANCE.get(key_id, 5.0)
        return p, BASE_KEY_IMPORTANCE.get(p, 5.0)

    if any(kw in b.lower() for kw in ["bluetooth", "output selection"]):
        return p, BASE_KEY_IMPORTANCE.get(p, 5.0)

    if any(kw in b.lower() for kw in ["reset", "bootloader"]):
        return b.lower(), BASE_KEY_IMPORTANCE.get(b.lower(), 3.0)

    # Modifier keys themselves (LeftAlt etc.) come with their own modifier flag — ignore it
    for kw in ["spacebar", "return enter", "tab", "escape", "delete",
                "leftshift", "rightshift", "leftcontrol", "rightcontrol",
                "leftalt", "rightalt", "left gui"]:
        if kw in p:
            return kw, BASE_KEY_IMPORTANCE.get(kw, 10.0)

    if not mods:
        # Single letter/number keys
        clean = p.replace("keyboard ", "").split(" and ")[0].split(" ")[0].strip()
        if len(clean) == 1 and clean.isalpha():
            return clean, BASE_KEY_IMPORTANCE.get(clean, 50.0)
        if clean.isdigit() or (len(clean) >= 2 and clean[0].isdigit()):
            return clean[0] if clean[0].isdigit() else clean, BASE_KEY_IMPORTANCE.get(clean[0] if clean[0].isdigit() else clean, 20.0)

    # Punctuation, navigation, and symbol keys (with or without modifiers)
    # These are physical keys that need protection regardless of modifier state
    for punct_key, punct_imp in PUNCTUATION_IMPORTANCE.items():
        if punct_key in p:
            if mods:
                # With modifiers: it's a combo like Ctrl+LeftArrow — moderate importance
                return f"{punct_key}_combo", punct_imp * 0.6
            return punct_key, punct_imp

    # F13-F24 (host trigger keys) — important functional keys
    f_match = re.search(r'\bf(\d+)\b', p)
    if f_match:
        f_num = int(f_match.group(1))
        if 1 <= f_num <= 12:
            return f"f{f_num}", BASE_KEY_IMPORTANCE.get(f"f{f_num}", 8.0) if not mods else 6.0
        elif 13 <= f_num <= 24:
            return f"f{f_num}", 10.0 if not mods else 6.0

    return None, 0




def build_position_index(canonical, frozen_layers=None):
    """Build mutable position index. Only L7 (RPG) is frozen by default.
    All other layers including L0 are mutable — protected by importance scores."""
    if frozen_layers is None:
        frozen_layers = {7}
    positions = []
    idx = 0
    def _layer_sort(item):
        try:
            return int(item[0])
        except (TypeError, ValueError):
            return 10**9

    for layer_id, layer_data in sorted(canonical["layers"].items(), key=_layer_sort):
        try:
            layer_num = int(layer_id)
        except (TypeError, ValueError):
            continue
        if layer_num in frozen_layers:
            continue
        for coord, binding in sorted(layer_data["keys"].items()):
            try:
                x, y = map(int, coord.split(":"))
            except (AttributeError, TypeError, ValueError):
                continue
            if is_structural(binding, layer_num):
                continue
            pos = Position(
                gene_idx=idx, layer=layer_num, x=x, y=y, coord=coord,
                effort=effort(x, y), hand=hand(x), finger=finger(x), is_thumb=(y >= 4),
            )
            positions.append(pos)
            idx += 1
    return positions


_BARE_LETTER_KEYS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
_BARE_SYMBOL_KEYS = set('/?=')
_MULTI_CHAR_BARE = {'gg', 'gi', 'yy', 'gs', 'ge', 'gE', 'yt', 'yf'}

# Keys that don't exist in ZMK Studio combobox
_UNAVAILABLE_KEYS = {'Pause', 'Break', 'ScrollLock', 'NumLock', 'CapsLock', 'Menu',
                     'Sleep', 'Wake', 'Power'}

# Shortcuts that can't be represented as a single ZMK Studio key press
_UNSUPPORTED_SHORTCUTS = {
    'Ctrl+K S', 'Ctrl+K Ctrl+F', 'Ctrl+K Ctrl+W', 'Ctrl+K Ctrl+S',
    'Ctrl+K Ctrl+C', 'Ctrl+K Ctrl+U', 'Ctrl+K Ctrl+X', 'Ctrl+K Ctrl+O',
    'Ctrl+K Ctrl+I', 'Ctrl+K Ctrl+T', 'Ctrl+K Ctrl+K',
    'Win+Pause', 'Alt+Shift',
    'Click', 'Alt+Click', 'Ctrl+Click', 'Shift+Click',
}


def split_shortcut_keys(key):
    """Return (modifiers, base) for shortcut strings, including Ctrl++."""
    if key.endswith("++"):
        raw_parts = key[:-1].split("+")
        base = "+"
    else:
        raw_parts = key.split("+")
        base = raw_parts[-1] if raw_parts else ""

    mods = [p for p in raw_parts[:-1] if p.lower() in ("ctrl", "shift", "alt", "win")]
    return mods, base


def _is_redundant_bare_key(key, mods):
    """Filter shortcuts that are just bare keystrokes already on L0.
    Vimium single letters, symbols like / and =, and multi-char sequences
    like gg/yy that can't be a single key position."""
    if mods:
        return False
    if key in _BARE_LETTER_KEYS or key in _BARE_SYMBOL_KEYS:
        return True
    if key in _MULTI_CHAR_BARE:
        return True
    return False


def _is_unsupported_shortcut(key):
    """Filter shortcuts that can't be represented as a single ZMK Studio binding."""
    if key in _UNSUPPORTED_SHORTCUTS:
        return True
    # VS Code chords: Ctrl+K followed by another key combo
    if key.startswith('Ctrl+K '):
        return True
    # Modifier-only combos (no base key)
    mods, base = split_shortcut_keys(key)
    if not base:
        return True
    # Base key contains a space and isn't a known multi-word key
    _KNOWN_MULTIWORD = {'Page Up', 'Page Down', 'Print Screen', 'Left GUI',
                        'Right GUI', 'Delete Forward', 'Return Enter'}
    if ' ' in base and base not in _KNOWN_MULTIWORD:
        return True
    # Base key is an unavailable key
    if base in _UNAVAILABLE_KEYS:
        return True
    return False


def build_shortcut_pool(scores, canonical=None):
    """Build the shortcut pool from app scores, optionally adding base keys from canonical."""
    pool = []
    key_to_idx = {}
    sid = 0
    filtered_count = 0
    unsupported_count = 0
    for app in scores["apps"]:
        app_id = app["id"]
        for s in app["shortcuts"]:
            key = s["keys"]
            imp = s.get("importance", 1.0)
            mods, base = split_shortcut_keys(key)
            if _is_redundant_bare_key(key, mods):
                filtered_count += 1
                continue
            if _is_unsupported_shortcut(key):
                unsupported_count += 1
                continue
            if key in key_to_idx:
                existing = pool[key_to_idx[key]]
                if app_id not in existing.apps:
                    existing.apps.append(app_id)
                if imp > existing.importance:
                    existing.importance = imp
                    existing.app = app_id
                    existing.action = s.get("action", existing.action)
                continue
            pool.append(Shortcut(
                sid=sid, keys=key, action=s.get("action", ""),
                app=app_id, category=s.get("category", ""),
                importance=imp,
                base_key=base, modifiers=mods,
                zmk_parameter=(s.get("best_match") or {}).get("parameter", ""),
                apps=[app_id],
            ))
            key_to_idx[key] = sid
            sid += 1

    if filtered_count:
        print(f"  Filtered {filtered_count} redundant bare-key shortcuts (Vimium letters, symbols, multi-char)")
    if unsupported_count:
        print(f"  Filtered {unsupported_count} unsupported shortcuts (chords, modifier-only, unavailable keys)")

    if canonical:
        _add_base_keys_to_pool(pool, key_to_idx, canonical)

    return pool


def _add_base_keys_to_pool(pool, key_to_idx, canonical):
    """Add base keys (spacebar, modifiers, MB1, BT, letters, etc.) to the pool
    so the optimizer can reason about displacing them via importance scores."""
    sid = len(pool)
    seen_base_keys = set()

    def _layer_sort(item):
        try:
            return int(item[0])
        except (TypeError, ValueError):
            return 10**9

    for layer_id, layer_data in sorted(canonical["layers"].items(), key=_layer_sort):
        try:
            layer_num = int(layer_id)
        except (TypeError, ValueError):
            continue
        if layer_num == 7:  # RPG frozen
            continue
        for coord, binding in sorted(layer_data.get("keys", {}).items()):
            b = binding.get("behavior", "")
            p = binding.get("parameter", "")

            key_id, importance = get_base_key_id(binding)
            if key_id is None or importance <= 0:
                continue

            label = f"_base_{key_id}"
            if label in key_to_idx or label in seen_base_keys:
                continue
            seen_base_keys.add(label)

            action_desc = p or b
            pool.append(Shortcut(
                sid=sid, keys=label, action=f"Base key: {action_desc}",
                app="base", category="base_key",
                importance=importance,
                base_key=key_id, modifiers=[],
                zmk_parameter=p,
                apps=["base"],
            ))
            key_to_idx[label] = sid
            sid += 1

    # Mouse buttons are structural base bindings, but ZMK Studio exports may
    # hide the actual button behind "default_transform" or a frozen game layer.
    # Seed the canonical MB set so scratch runs can build a complete mouse mode.
    for mb_num in range(1, 6):
        key_id = f"select:mb{mb_num}"
        label = f"_base_{key_id}"
        if label in key_to_idx or label in seen_base_keys:
            continue
        seen_base_keys.add(label)
        pool.append(Shortcut(
            sid=sid, keys=label, action=f"Base key: MB{mb_num}",
            app="base", category="base_key",
            importance=BASE_KEY_IMPORTANCE.get(key_id, 5.0),
            base_key=key_id, modifiers=[],
            zmk_parameter=f"MB{mb_num}",
            apps=["base"],
        ))
        key_to_idx[label] = sid
        sid += 1


def build_layer_to_positions(positions):
    layer_map = {}
    for pos in positions:
        layer_map.setdefault(pos.layer, []).append(pos)
    return layer_map


def encode_current_layout(canonical, positions, shortcut_pool):
    keys_lookup = {}
    base_key_lookup = {}
    for s in shortcut_pool:
        if s.keys.startswith("_base_"):
            base_key_lookup[s.keys] = s.sid
        else:
            keys_lookup[s.keys.upper()] = s.sid

    genome = [-1] * len(positions)

    for pos in positions:
        layer_data = canonical["layers"].get(str(pos.layer), {})
        binding = layer_data.get("keys", {}).get(pos.coord, {})
        b = binding.get("behavior", "")
        if b.lower() in ("transparent", "none", ""):
            continue  # empty slot, genome stays -1
        if is_structural(binding, pos.layer):
            continue

        # Try base key lookup first (spacebar, modifiers, MB1, BT, letters)
        key_id, imp = get_base_key_id(binding)
        if key_id is not None:
            label = f"_base_{key_id}"
            sid = base_key_lookup.get(label)
            if sid is not None:
                genome[pos.gene_idx] = sid
                continue

        # Standard shortcut lookup
        param = binding.get("parameter", "")
        mods = binding.get("modifiers", [])
        mod_names = []
        for m in mods:
            ml = m.lower()
            if "gui" in ml:
                mod_names.append("Win")
            elif "ctrl" in ml:
                mod_names.append("Ctrl")
            elif "shift" in ml:
                mod_names.append("Shift")
            elif "alt" in ml:
                mod_names.append("Alt")
        # Sort modifiers in canonical order: Win, Ctrl, Shift, Alt (matches pool convention)
        MOD_ORDER = {"Win": 0, "Ctrl": 1, "Shift": 2, "Alt": 3}
        mod_names.sort(key=lambda m: MOD_ORDER.get(m, 9))

        base = param.upper().replace("KEYBOARD ", "").split(" AND ")[0].split(" ")[0]
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if param.upper() == f"KEYBOARD {letter}":
                base = letter
                break

        shortcut_key = "+".join(mod_names + [base]) if mod_names else base
        sid = keys_lookup.get(shortcut_key.upper())
        if sid is not None:
            genome[pos.gene_idx] = sid

    return genome


def build_scratch_genome(canonical, positions, shortcut_pool):
    """Build a genome seeded with L0 keys + access keys + greedy importance-first fill.
    The greedy fill places unassigned high-importance shortcuts on low-effort empty
    positions, giving the optimizer a valid starting point instead of ~400 empty slots."""
    full_genome = encode_current_layout(canonical, positions, shortcut_pool)
    scratch = [-1] * len(positions)
    access_keys = {
        "_base_coach_l1_hold", "_base_coach_l2_hold",
        "_base_coach_l3_hold", "_base_coach_l4_hold",
        "_base_coach_mouse_lock", "_base_coach_game_lock",
        "_base_coach_travel_toggle", "_base_coach_travel_off",
        "_base_coach_base", "_base_coach_recover_base",
    }
    for i, pos in enumerate(positions):
        if pos.layer == 0 and not pos.is_thumb and full_genome[i] >= 0:
            scratch[i] = full_genome[i]
            continue
        if full_genome[i] >= 0:
            skey = shortcut_pool[full_genome[i]].keys
            if skey in access_keys or skey.startswith(("_base_toggle_layer_", "_base_momentary_layer_", "_base_to_layer_")):
                scratch[i] = full_genome[i]

    assigned_sids = set(g for g in scratch if g >= 0)
    unplaced = [s for s in shortcut_pool if s.sid not in assigned_sids and s.importance >= 1.0
                and s.category != "base_key"]
    unplaced.sort(key=lambda s: -s.importance)

    empty_positions = [(i, positions[i]) for i in range(len(positions))
                       if scratch[i] < 0 and positions[i].layer > 0]
    empty_positions.sort(key=lambda x: x[1].effort)

    placed = set()
    for s in unplaced:
        if s.sid in placed:
            continue
        for j, (idx, pos) in enumerate(empty_positions):
            if scratch[idx] < 0:
                scratch[idx] = s.sid
                placed.add(s.sid)
                break

    return scratch


def decode_genome(genome, positions, shortcut_pool):
    changes = []
    for i, sid in enumerate(genome):
        if sid == -1:
            continue
        pos = positions[i]
        shortcut = shortcut_pool[sid]
        changes.append({
            "layer": pos.layer,
            "coord": pos.coord,
            "x": pos.x, "y": pos.y,
            "effort": pos.effort,
            "hand": pos.hand,
            "is_thumb": pos.is_thumb,
            "shortcut_id": sid,
            "keys": shortcut.keys,
            "action": shortcut.action,
            "app": shortcut.app,
            "importance": shortcut.importance,
        })
    return changes
