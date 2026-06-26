"""Genome encoding for keyboard layout evolution.

A genome is an integer array of length M where M = number of mutable positions.
Each gene value is a shortcut ID (index into shortcut_pool) or -1 for transparent/empty.
"""
import json
from dataclasses import dataclass, field

ROW_COMFORT = {0: 3, 1: 2, 2: 1, 3: 2, 4: 4, 5: 5}
COL_EFFORT = {0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 1, 7: 1, 8: 0, 9: 1, 10: 2, 11: 3, 12: 4}
LEFT_COLS = {0, 1, 2, 3, 4, 5}
RIGHT_COLS = {7, 8, 9, 10, 11, 12}

FINGER_MAP = {
    0: "far_pinky", 1: "pinky", 2: "ring", 3: "middle", 4: "index", 5: "index_stretch",
    7: "index_stretch", 8: "index", 9: "middle", 10: "ring", 11: "pinky", 12: "far_pinky",
}

LAYER_NAMES = {
    0: "Base", 1: "Nav", 2: "Mouse", 3: "Window", 4: "System",
    5: "Code", 6: "Scroll", 7: "Game", 8: "Speed", 9: "M-Files", 10: "Excel",
}

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

LAYER_APP_CONTEXT = {
    1: ["windows", "browser", "explorer", "terminal"],
    2: ["windows", "browser"],
    3: ["windows", "explorer"],
    4: ["windows", "teams", "browser", "vscode", "outlook", "terminal"],
    5: ["vscode", "terminal"],
    9: ["mfiles", "mfiles_admin"],
    10: ["excel", "powerpoint", "word"],
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
# If the optimizer proposes displacing spacebar, the importance model is broken.
BASE_KEY_IMPORTANCE = {
    "spacebar": 100.0,
    "return enter": 40.0,
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
    "select:mb1": 45.0,
    "select:mb2": 15.0,
    "select:mb3": 8.0,
    "select:mb4": 5.0,
    "select:mb5": 5.0,
    "coach_l1_hold": 18.0,
    "coach_l2_hold": 20.0,
    "coach_l3_hold": 15.0,
    "coach_l4_hold": 15.0,
    "coach_base": 12.0,
    "coach_mouse_lock": 10.0,
    "coach_game_lock": 8.0,
    "coach_travel_toggle": 8.0,
    "coach_travel_off": 6.0,
    "coach_recover_base": 6.0,
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
    "semicolon": 30.0,          # ø on Norwegian
    "left apos": 25.0,          # æ on Norwegian
    "left brace": 25.0,         # å on Norwegian
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
    # Navigation keys
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
    "keypad 9": 12.0,           # PageUp on keypad
    "keypad 3": 12.0,           # PageDown on keypad
    "insert": 8.0,
    "print screen": 10.0,
    "printscreen": 10.0,
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
        return True
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

    if "mouse key press" in b.lower():
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
    import re
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
    for layer_id, layer_data in sorted(canonical["layers"].items(), key=lambda x: int(x[0])):
        layer_num = int(layer_id)
        if layer_num in frozen_layers:
            continue
        for coord, binding in sorted(layer_data["keys"].items()):
            x, y = map(int, coord.split(":"))
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


def build_shortcut_pool(scores, canonical=None):
    """Build the shortcut pool from app scores, optionally adding base keys from canonical."""
    pool = []
    key_to_idx = {}
    sid = 0
    filtered_count = 0
    for app in scores["apps"]:
        app_id = app["id"]
        for s in app["shortcuts"]:
            key = s["keys"]
            imp = s.get("importance", 1.0)
            mods = [k for k in key.split("+") if k.lower() in ("ctrl", "shift", "alt", "win")]
            if _is_redundant_bare_key(key, mods):
                filtered_count += 1
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
            base = key.split("+")[-1]
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

    if canonical:
        _add_base_keys_to_pool(pool, key_to_idx, canonical)

    return pool


def _add_base_keys_to_pool(pool, key_to_idx, canonical):
    """Add base keys (spacebar, modifiers, MB1, BT, letters, etc.) to the pool
    so the optimizer can reason about displacing them via importance scores."""
    sid = len(pool)
    seen_base_keys = set()

    for layer_id, layer_data in sorted(canonical["layers"].items(), key=lambda x: int(x[0])):
        layer_num = int(layer_id)
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
    """Build a genome with only physically locked L0 keys assigned.
    L0 non-thumb (y<4): letters, numbers, punctuation, modifiers — kept.
    L0 thumb (y>=4) and all non-L0 positions: empty (-1)."""
    full_genome = encode_current_layout(canonical, positions, shortcut_pool)
    scratch = [-1] * len(positions)
    for i, pos in enumerate(positions):
        if pos.layer == 0 and not pos.is_thumb and full_genome[i] >= 0:
            scratch[i] = full_genome[i]
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
