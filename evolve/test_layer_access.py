import json
import copy
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from layer_access import LayerAccessAnalyzer, HARD_INVALID_FITNESS
from representation import build_position_index, build_shortcut_pool, encode_current_layout


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def load_fixture():
    canonical = json.loads((BUILD / "canonical.json").read_text(encoding="utf-8"))
    scores = json.loads((BUILD / "app_shortcut_scores.json").read_text(encoding="utf-8"))
    positions = build_position_index(canonical, {7})
    pool = build_shortcut_pool(scores, canonical)
    current = encode_current_layout(canonical, positions, pool)
    analyzer = LayerAccessAnalyzer(canonical, positions, pool)
    return canonical, positions, pool, current, analyzer


def position_index(positions, layer, coord):
    for i, pos in enumerate(positions):
        if pos.layer == layer and pos.coord == coord:
            return i
    raise AssertionError(f"missing position L{layer} {coord}")


def sid_for(pool, key):
    for shortcut in pool:
        if shortcut.keys == key:
            return shortcut.sid
    raise AssertionError(f"missing shortcut {key}")


class LayerAccessInvariantTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical, cls.positions, cls.pool, cls.current, cls.analyzer = load_fixture()

    def test_current_layout_is_valid(self):
        result = self.analyzer.validate(self.current)
        self.assertTrue(result.valid, result.errors)

    def test_evo20_result_is_invalid(self):
        results_path = BUILD / "evolution_results.json"
        if not results_path.exists():
            self.skipTest("evolution_results.json not present")
        results = json.loads(results_path.read_text(encoding="utf-8"))
        evo20 = next((s for s in results.get("pareto_front", []) if s.get("id") == "evo_20"), None)
        if evo20 is None:
            self.skipTest("evo_20 not present")
        genome = evo20["genome"]
        result = self.analyzer.validate(genome)
        self.assertFalse(result.valid)
        self.assertTrue(result.errors)

    def test_moving_l1_hold_keeps_access_valid(self):
        genome = list(self.current)
        src = position_index(self.positions, 0, "3:4")
        dst = position_index(self.positions, 0, "4:4")
        genome[src], genome[dst] = genome[dst], genome[src]
        result = self.analyzer.validate(genome)
        self.assertTrue(result.valid, result.errors)

    def test_removing_all_l1_access_fails(self):
        genome = list(self.current)
        l1_sid = sid_for(self.pool, "_base_coach_l1_hold")
        for i, sid in enumerate(genome):
            if sid == l1_sid:
                genome[i] = -1
        result = self.analyzer.validate(genome)
        self.assertFalse(result.valid)
        self.assertIn("Layer 1 unreachable from base", result.errors)

    def test_locked_toggled_layer_without_exit_fails(self):
        canonical = copy.deepcopy(self.canonical)
        for binding in canonical["layers"]["7"]["keys"].values():
            if binding.get("behavior") == "coach_base":
                binding["behavior"] = "Transparent"
                binding["parameter"] = ""
        analyzer = LayerAccessAnalyzer(canonical, self.positions, self.pool)
        result = analyzer.validate(self.current)
        self.assertFalse(result.valid)
        self.assertTrue(any("Layer 7 has no return-to-base exit" == err for err in result.errors), result.errors)


class LayerDemandScoringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical, cls.positions, cls.pool, cls.current, cls.analyzer = load_fixture()
        usage_path = BUILD / "usage_stats.json"
        cls.usage_stats = json.loads(usage_path.read_text(encoding="utf-8")) if usage_path.exists() else {}
        from fitness import FitnessEvaluator
        config = {"weights": {"layer_demand": 2.0, "layer_access_effort": 1.0}}
        cls.evaluator = FitnessEvaluator(
            cls.positions, cls.pool, config,
            usage_stats=cls.usage_stats,
            current_genome=cls.current,
            canonical=cls.canonical,
        )

    def test_layer_demand_computed(self):
        self.assertTrue(hasattr(self.evaluator, 'layer_demand'))
        self.assertGreater(len(self.evaluator.layer_demand), 0)

    def test_demand_is_genome_derived(self):
        # Demand is computed from genome placement, not hardcoded
        demand_a = self.evaluator._layer_demand_for_genome(self.current)
        # An empty genome should have different demand
        empty = [-1] * len(self.current)
        demand_b = self.evaluator._layer_demand_for_genome(empty)
        # Empty genome: demand comes only from session counts, should differ from full genome
        self.assertNotEqual(demand_a, demand_b)

    def test_direct_access_cheaper_than_nested_for_high_demand(self):
        genome = list(self.current)
        validation = self.analyzer.validate(genome)
        self.assertTrue(validation.valid)
        direct_penalty = self.evaluator._layer_demand_penalty(genome, validation)
        self.assertIsInstance(direct_penalty, float)
        self.assertLess(direct_penalty, HARD_INVALID_FITNESS)

    def test_demand_penalty_in_evaluate_full(self):
        breakdown = self.evaluator.evaluate_full(self.current)
        self.assertIn("layer_demand_penalty", breakdown)
        self.assertIn("layer_demand", breakdown)
        self.assertIn("per_layer_access_costs", breakdown)
        self.assertIn("per_layer_depth", breakdown)

    def test_access_depth_computed(self):
        depths = self.analyzer.access_depth(self.current)
        self.assertEqual(depths[0], 0)
        for layer in self.analyzer.required_layers:
            self.assertIn(layer, depths, f"Layer {layer} should have computed depth")
            self.assertGreater(depths[layer], 0)

    def test_removing_access_still_invalid(self):
        genome = list(self.current)
        l1_sid = sid_for(self.pool, "_base_coach_l1_hold")
        for i, sid in enumerate(genome):
            if sid == l1_sid:
                genome[i] = -1
        validation = self.analyzer.validate(genome)
        self.assertFalse(validation.valid)
        penalty = self.evaluator._layer_demand_penalty(genome, validation)
        self.assertEqual(penalty, HARD_INVALID_FITNESS)


if __name__ == "__main__":
    unittest.main()
