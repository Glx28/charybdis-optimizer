"""Layer access reachability model for evolved layouts.

This module treats layer access as a semantic capability graph. Access keys may
move or be replaced, but a genome is invalid if it removes reachability to any
required layer or removes a safe exit from locked/toggled layers.
"""
from dataclasses import dataclass
import heapq
import re

from representation import LAYER_ACCESS, effort


HARD_INVALID_FITNESS = 1_000_000_000.0


@dataclass(frozen=True)
class AccessCapability:
    source: int
    target: int
    mode: str
    cost: float
    label: str
    layer: int
    coord: str
    fixed: bool = False


@dataclass
class AccessValidation:
    valid: bool
    reachable_layers: set
    access_costs: dict
    capabilities: list
    errors: list
    required_layers: set
    access_depths: dict = None

    @property
    def layer_access_valid(self):
        return 1.0 if self.valid else 0.0

    @property
    def layer_exit_valid(self):
        return 0.0 if any("no return-to-base" in e for e in self.errors) else 1.0

    @property
    def total_access_cost(self):
        return sum(self.access_costs.get(layer, 0.0) for layer in self.required_layers)


def _parse_layer_parameter(parameter):
    if parameter is None:
        return None
    text = str(parameter)
    match = re.search(r"(\d+)", text)
    if not match:
        return None
    return int(match.group(1))


def _behavior_capability(behavior, parameter, source, cost, layer, coord, fixed=False):
    behavior_l = str(behavior or "").lower()
    target = _parse_layer_parameter(parameter)

    if behavior_l == "coach_l1_hold":
        return AccessCapability(source, 1, "momentary", cost, behavior, layer, coord, fixed)
    if behavior_l == "coach_l2_hold":
        return AccessCapability(source, 2, "momentary_or_locked", cost, behavior, layer, coord, fixed)
    if behavior_l == "coach_l3_hold":
        return AccessCapability(source, 3, "momentary", cost, behavior, layer, coord, fixed)
    if behavior_l == "coach_l4_hold":
        return AccessCapability(source, 4, "momentary", cost, behavior, layer, coord, fixed)
    if behavior_l == "coach_mouse_lock":
        return AccessCapability(source, 2, "lock", cost + 1.0, behavior, layer, coord, fixed)
    if behavior_l == "coach_game_lock":
        return AccessCapability(source, 7, "lock", cost + 1.0, behavior, layer, coord, fixed)
    if behavior_l == "coach_travel_toggle":
        return AccessCapability(source, 8, "toggle", cost + 1.0, behavior, layer, coord, fixed)
    if behavior_l in ("coach_base", "coach_recover_base", "coach_travel_off"):
        return AccessCapability(source, 0, "exit_to_base", cost, behavior, layer, coord, fixed)

    if (behavior == "Momentary Layer" or behavior_l.startswith("momentary_layer_")) and target is not None:
        return AccessCapability(source, target, "momentary", cost, behavior, layer, coord, fixed)
    if (behavior == "Toggle Layer" or behavior_l.startswith("toggle_layer_")) and target is not None:
        return AccessCapability(source, target, "toggle", cost + 1.0, behavior, layer, coord, fixed)
    if (behavior == "To Layer" or behavior_l.startswith("to_layer_")) and target is not None:
        mode = "exit_to_base" if target == 0 else "to_layer"
        return AccessCapability(source, target, mode, cost, behavior, layer, coord, fixed)
    return None


def shortcut_capability(shortcut, pos):
    behavior = shortcut.base_key if shortcut.category == "base_key" else shortcut.keys
    return _behavior_capability(
        behavior=behavior,
        parameter=shortcut.zmk_parameter,
        source=pos.layer,
        cost=float(pos.effort),
        layer=pos.layer,
        coord=pos.coord,
        fixed=False,
    )


def fixed_capabilities_from_canonical(canonical, mutable_positions):
    mutable_coords = {(p.layer, p.coord) for p in mutable_positions}
    caps = []
    for layer_id, layer_data in canonical.get("layers", {}).items():
        try:
            layer = int(layer_id)
        except (TypeError, ValueError):
            continue
        for coord, binding in layer_data.get("keys", {}).items():
            if (layer, coord) in mutable_coords:
                continue
            behavior = binding.get("behavior", "")
            if not (behavior.startswith("coach_") or behavior in ("Momentary Layer", "Toggle Layer", "To Layer")):
                continue
            try:
                x, y = map(int, coord.split(":"))
            except ValueError:
                continue
            cap = _behavior_capability(
                behavior=behavior,
                parameter=binding.get("parameter", ""),
                source=layer,
                cost=float(effort(x, y)),
                layer=layer,
                coord=coord,
                fixed=True,
            )
            if cap:
                caps.append(cap)
    return caps


class LayerAccessAnalyzer:
    def __init__(self, canonical, positions, pool):
        self.canonical = canonical
        self.positions = positions
        self.pool = pool
        self.required_layers = self._required_layers()
        self.exit_required_layers = {
            layer for layer, info in LAYER_ACCESS.items()
            if info.get("method") in ("toggled", "locked", "momentary_or_locked")
            and layer in self.required_layers
        }
        self.fixed_capabilities = fixed_capabilities_from_canonical(canonical, positions)

    def _required_layers(self):
        existing = set()
        for layer in self.canonical.get("layers", {}):
            try:
                existing.add(int(layer))
            except (TypeError, ValueError):
                continue
        return {layer for layer in existing if layer != 0 and layer in LAYER_ACCESS}

    def capabilities_for_genome(self, genome):
        caps = list(self.fixed_capabilities)
        for i, sid in enumerate(genome):
            if sid < 0:
                continue
            if sid >= len(self.pool):
                continue
            cap = shortcut_capability(self.pool[int(sid)], self.positions[i])
            if cap:
                caps.append(cap)
        return caps

    def validate(self, genome):
        caps = self.capabilities_for_genome(genome)
        graph = {}
        for cap in caps:
            graph.setdefault(cap.source, []).append(cap)

        costs = {0: 0.0}
        queue = [(0.0, 0)]
        while queue:
            cur_cost, layer = heapq.heappop(queue)
            if cur_cost > costs.get(layer, float("inf")):
                continue
            for cap in graph.get(layer, []):
                next_cost = cur_cost + cap.cost
                if next_cost < costs.get(cap.target, float("inf")):
                    costs[cap.target] = next_cost
                    heapq.heappush(queue, (next_cost, cap.target))

        reachable = set(costs)
        errors = []
        for layer in sorted(self.required_layers):
            if layer not in reachable:
                errors.append(f"Layer {layer} unreachable from base")

        for layer in sorted(self.exit_required_layers):
            if layer not in reachable:
                continue
            method = LAYER_ACCESS.get(layer, {}).get("method", "")
            has_explicit_exit = any(cap.source == layer and cap.target == 0 for cap in caps)
            has_toggle_return = (
                method == "toggled"
                and any(cap.target == layer and cap.mode == "toggle" and cap.source in reachable for cap in caps)
            )
            has_exit = has_explicit_exit or has_toggle_return
            if not has_exit:
                errors.append(f"Layer {layer} has no return-to-base exit")

        # Compute access depths (BFS) reusing the same graph
        depths = {0: 0}
        bfs_queue = [(0, 0)]
        while bfs_queue:
            cur_depth, cur_layer = bfs_queue.pop(0)
            if cur_depth > depths.get(cur_layer, float("inf")):
                continue
            for cap in graph.get(cur_layer, []):
                next_depth = cur_depth + 1
                if next_depth < depths.get(cap.target, float("inf")):
                    depths[cap.target] = next_depth
                    bfs_queue.append((next_depth, cap.target))

        return AccessValidation(
            valid=not errors,
            reachable_layers=reachable,
            access_costs=costs,
            capabilities=caps,
            errors=errors,
            required_layers=set(self.required_layers),
            access_depths=depths,
        )

    def layer_cost_vector(self, genome):
        validation = self.validate(genome)
        return [validation.access_costs.get(p.layer, HARD_INVALID_FITNESS) for p in self.positions]

    def access_depth(self, genome):
        """Return {layer: depth} where depth = number of layer-switch actions from base.
        Depth 0 = base, 1 = direct momentary/toggle from base, 2 = nested, etc."""
        caps = self.capabilities_for_genome(genome)
        graph = {}
        for cap in caps:
            graph.setdefault(cap.source, []).append(cap)
        depths = {0: 0}
        queue = [(0, 0)]
        while queue:
            cur_depth, layer = queue.pop(0)
            if cur_depth > depths.get(layer, float("inf")):
                continue
            for cap in graph.get(layer, []):
                next_depth = cur_depth + 1
                if next_depth < depths.get(cap.target, float("inf")):
                    depths[cap.target] = next_depth
                    queue.append((next_depth, cap.target))
        return depths
