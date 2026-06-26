import json
import copy
import os
import sys
import unittest
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from representation import build_shortcut_pool, build_position_index, encode_current_layout
from fitness import FitnessEvaluator, HARD_INVALID_FITNESS

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def load_fixture():
    canonical = json.loads((BUILD / "canonical.json").read_text(encoding="utf-8"))
    scores = json.loads((BUILD / "app_shortcut_scores.json").read_text(encoding="utf-8"))
    positions = build_position_index(canonical, {7})
    pool = build_shortcut_pool(scores, canonical)
    current = encode_current_layout(canonical, positions, pool)
    usage = {}
    usage_path = BUILD / "usage_stats.json"
    if usage_path.exists():
        usage = json.loads(usage_path.read_text(encoding="utf-8"))
    conj = {}
    conj_path = BUILD / "conjunction_pairs.json"
    if conj_path.exists():
        conj = json.loads(conj_path.read_text(encoding="utf-8"))
    config = json.loads((Path(__file__).parent / "config.json").read_text(encoding="utf-8"))
    evaluator = FitnessEvaluator(
        positions, pool, config,
        usage_stats=usage, conjunction_pairs=conj,
        device="cpu", current_genome=current, canonical=canonical,
    )
    return canonical, positions, pool, current, evaluator, config


class PenaltyFunctionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical, cls.positions, cls.pool, cls.current, cls.evaluator, cls.config = load_fixture()

    def test_current_layout_has_finite_scores(self):
        result = self.evaluator.evaluate(self.current)
        self.assertLess(result[0], HARD_INVALID_FITNESS)
        self.assertLess(result[2], HARD_INVALID_FITNESS)

    def test_empty_genome_has_high_violations(self):
        empty = [-1] * len(self.current)
        result = self.evaluator.evaluate(empty)
        self.assertEqual(result[0], HARD_INVALID_FITNESS)

    def test_toggled_base_penalty_scales(self):
        genome = list(self.current)
        base_penalty = self.evaluator._toggled_base_violation(np.array(genome, dtype=np.int32))
        # Remove all coach_base keys to increase penalty
        for i in range(len(genome)):
            if genome[i] >= 0 and self.pool[genome[i]].keys in (
                '_base_coach_base', '_base_coach_recover_base', '_base_coach_travel_off'):
                genome[i] = -1
        worse_penalty = self.evaluator._toggled_base_violation(np.array(genome, dtype=np.int32))
        self.assertGreater(worse_penalty, base_penalty)
        self.assertGreaterEqual(worse_penalty, 5000.0)

    def test_unassignment_penalty_scales_with_importance(self):
        genome_low = list(self.current)
        genome_high = list(self.current)
        # Find a low-importance and high-importance assigned position
        low_idx = high_idx = None
        for i in range(len(self.current)):
            if self.current[i] >= 0:
                imp = self.pool[self.current[i]].importance
                if imp < 3.0 and low_idx is None:
                    low_idx = i
                if imp > 15.0 and high_idx is None:
                    high_idx = i
        if low_idx is None or high_idx is None:
            self.skipTest("Need both low and high importance positions")
        genome_low[low_idx] = -1
        genome_high[high_idx] = -1
        pen_low = self.evaluator._unassignment_penalty(np.array(genome_low, dtype=np.int32))
        pen_high = self.evaluator._unassignment_penalty(np.array(genome_high, dtype=np.int32))
        self.assertGreater(pen_high, pen_low)

    def test_cross_layer_duplicate_escalating(self):
        genome = list(self.current)
        pen_base = self.evaluator._cross_layer_duplicate_penalty(np.array(genome, dtype=np.int32))
        # Place a low-importance shortcut on 5 layers
        low_sid = None
        for s in self.pool:
            if s.importance < 3.0 and s.category != "base_key":
                low_sid = s.sid
                break
        if low_sid is None:
            self.skipTest("No low-importance shortcut found")
        placed = 0
        for i in range(len(genome)):
            if genome[i] < 0 and self.positions[i].layer > 0 and placed < 5:
                genome[i] = low_sid
                placed += 1
        pen_worse = self.evaluator._cross_layer_duplicate_penalty(np.array(genome, dtype=np.int32))
        self.assertGreater(pen_worse, pen_base)

    def test_layer_redundancy_penalizes_same_dominant_app_only(self):
        app_sids = {}
        for s in self.pool:
            if s.category != "base_key":
                app_sids.setdefault(s.app, []).append(s.sid)
        usable_apps = [app for app, sids in app_sids.items() if len(sids) >= 4]
        if len(usable_apps) < 2:
            self.skipTest("Need two apps with enough shortcuts")

        layer_ids = [
            layer for layer in sorted({p.layer for p in self.positions})
            if layer not in (0, 7) and sum(1 for p in self.positions if p.layer == layer) >= 8
        ]
        if len(layer_ids) < 2:
            self.skipTest("Need two non-base layers with enough positions")

        layer_a, layer_b = layer_ids[:2]
        pos_a = [i for i, p in enumerate(self.positions) if p.layer == layer_a][:8]
        pos_b = [i for i, p in enumerate(self.positions) if p.layer == layer_b][:8]
        app_a, app_b = usable_apps[:2]

        redundant = [-1] * len(self.current)
        for offset, idx in enumerate(pos_a):
            redundant[idx] = app_sids[app_a][offset % len(app_sids[app_a])]
        for offset, idx in enumerate(pos_b):
            redundant[idx] = app_sids[app_a][offset % len(app_sids[app_a])]

        mixed = [-1] * len(self.current)
        mixed_sids = app_sids[app_a][:4] + app_sids[app_b][:4]
        for offset, idx in enumerate(pos_a):
            mixed[idx] = mixed_sids[offset]
        for offset, idx in enumerate(pos_b):
            mixed[idx] = mixed_sids[offset]

        redundant_pen = self.evaluator._layer_redundancy_penalty(np.array(redundant, dtype=np.int32))
        mixed_pen = self.evaluator._layer_redundancy_penalty(np.array(mixed, dtype=np.int32))
        self.assertGreater(redundant_pen, 0.0)
        self.assertEqual(mixed_pen, 0.0)

    def test_missing_important_penalty_nonzero(self):
        pen = self.evaluator._missing_important_penalty(np.array(self.current, dtype=np.int32))
        self.assertIsInstance(pen, float)

    def test_evaluate_full_returns_all_keys(self):
        result = self.evaluator.evaluate_full(self.current)
        expected = {"effort", "violations", "adjacency", "layer_access_valid",
                    "layer_demand_penalty", "finger_balance", "thumb_utilization",
                    "unassignment_penalty"}
        for key in expected:
            self.assertIn(key, result, f"Missing key: {key}")


class GPUCPUParityTest(unittest.TestCase):
    """Verify GPU batch evaluation matches CPU single-genome evaluation."""

    @classmethod
    def setUpClass(cls):
        cls.canonical, cls.positions, cls.pool, cls.current, cls.evaluator, cls.config = load_fixture()
        try:
            import torch
            if not torch.cuda.is_available():
                raise ImportError("No CUDA")
            cls.gpu_evaluator = FitnessEvaluator(
                cls.positions, cls.pool, cls.config,
                usage_stats={}, conjunction_pairs={},
                device="cuda", current_genome=cls.current, canonical=cls.canonical,
            )
            cls.has_gpu = True
        except (ImportError, RuntimeError):
            cls.has_gpu = False

    def test_gpu_cpu_parity(self):
        if not self.has_gpu:
            self.skipTest("No GPU available")
        import random
        random.seed(42)
        genomes = []
        for _ in range(5):
            g = list(self.current)
            for _ in range(20):
                i = random.randint(0, len(g) - 1)
                if random.random() < 0.5:
                    g[i] = -1
                else:
                    g[i] = random.randint(0, len(self.pool) - 1)
            genomes.append(g)

        gpu_results = self.gpu_evaluator.evaluate_batch_gpu(genomes)
        for i, genome in enumerate(genomes):
            cpu_result = self.gpu_evaluator.evaluate(genome)
            gpu_eff, gpu_adj, gpu_viol = gpu_results[i]
            cpu_eff, cpu_adj, cpu_viol = cpu_result
            # Allow 1% tolerance for floating point differences
            if cpu_viol < HARD_INVALID_FITNESS and gpu_viol < HARD_INVALID_FITNESS:
                self.assertAlmostEqual(gpu_viol, cpu_viol, delta=max(abs(cpu_viol) * 0.05, 100),
                                       msg=f"Genome {i}: violations diverge GPU={gpu_viol:.0f} CPU={cpu_viol:.0f}")


class OperatorSafetyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical, cls.positions, cls.pool, cls.current, cls.evaluator, cls.config = load_fixture()

    def test_mutate_preserves_valid_sids(self):
        from operators import custom_mutate
        import random
        random.seed(123)
        genome = list(self.current)
        for _ in range(20):
            result = custom_mutate(genome, self.positions, self.pool, generation=100)
            mutated = result[0]
            for sid in mutated:
                self.assertTrue(sid == -1 or (0 <= sid < len(self.pool)),
                                f"Invalid SID {sid} in mutated genome")
            genome = mutated


if __name__ == "__main__":
    unittest.main()
