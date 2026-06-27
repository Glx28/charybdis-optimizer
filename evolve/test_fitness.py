import json
import copy
import os
import sys
import unittest
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from representation import build_shortcut_pool, build_position_index, encode_current_layout, build_scratch_genome
from fitness import FitnessEvaluator, HARD_INVALID_FITNESS
from run_evolution import (
    ensure_structural_exits, pool_hash,
    diversity_injection_milestone, scratch_phase_for_generation,
)

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
        genome = [-1] * len(self.current)
        pen_base = self.evaluator._cross_layer_duplicate_penalty(np.array(genome, dtype=np.int32))
        # Place a low-importance shortcut on 5 layers
        low_sid = None
        cap_sids = self.evaluator._capability_sid_set()
        for s in self.pool:
            if s.importance < 3.0 and s.category != "base_key" and s.sid not in cap_sids:
                low_sid = s.sid
                break
        if low_sid is None:
            self.skipTest("No low-importance shortcut found")
        placed = 0
        seen_layers = set()
        for i in range(len(genome)):
            layer = self.positions[i].layer
            if layer > 0 and layer not in seen_layers and placed < 5:
                genome[i] = low_sid
                placed += 1
                seen_layers.add(layer)
        if placed < 3:
            self.skipTest("Need placements on at least 3 layers")
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

    def test_frozen_l0_duplicate_penalizes_duplicate_placement(self):
        if not self.evaluator.frozen_l0_sids:
            self.skipTest("No frozen L0 SIDs discovered")
        sid = next(iter(self.evaluator.frozen_l0_sids))
        source_positions = {
            i for i, g in enumerate(self.current)
            if g == sid and self.evaluator.frozen_l0_source_pos_arr[i] > 0
        }
        target = next(
            (i for i, p in enumerate(self.positions)
             if i not in source_positions and (p.layer != 0 or self.current[i] < 0)),
            None,
        )
        if target is None:
            self.skipTest("No candidate duplicate target")

        genome = list(self.current)
        baseline = self.evaluator._frozen_l0_duplicate_violation(np.array(genome, dtype=np.int32))
        genome[target] = sid
        duplicate = self.evaluator._frozen_l0_duplicate_violation(np.array(genome, dtype=np.int32))
        self.assertGreater(duplicate, baseline)

    def test_capability_sids_do_not_trigger_frozen_l0_duplicate_penalty(self):
        cap_sids = self.evaluator._capability_sid_set()
        if not cap_sids:
            self.skipTest("No capability SIDs discovered")
        target = next((i for i in range(len(self.current))
                       if self.evaluator.frozen_l0_source_pos_arr[i] <= 0), None)
        if target is None:
            self.skipTest("No candidate target")

        genome = [-1] * len(self.current)
        genome[target] = next(iter(cap_sids))
        penalty = self.evaluator._frozen_l0_duplicate_violation(np.array(genome, dtype=np.int32))
        self.assertEqual(penalty, 0.0)

    def test_base_return_on_pure_momentary_layer_is_redundant(self):
        if not self.evaluator.coach_base_sids:
            self.skipTest("No base-return SIDs discovered")
        target = next(
            (i for i, p in enumerate(self.positions)
             if p.layer in self.evaluator.pure_momentary_layers),
            None,
        )
        if target is None:
            self.skipTest("No pure momentary position")

        genome = [-1] * len(self.current)
        baseline = self.evaluator._momentary_redundancy_penalty(np.array(genome, dtype=np.int32))
        genome[target] = next(iter(self.evaluator.coach_base_sids))
        redundant = self.evaluator._momentary_redundancy_penalty(np.array(genome, dtype=np.int32))
        self.assertGreater(redundant, baseline)

    def test_position_waste_penalizes_low_importance_on_prime_position(self):
        low_sid = next((s.sid for s in self.pool if 0 <= s.importance < 4.0), None)
        if low_sid is None:
            self.skipTest("No low-importance shortcut")
        prime = next((i for i, p in enumerate(self.positions) if p.effort < 2.0), None)
        high_effort = next((i for i, p in enumerate(self.positions) if p.effort >= 2.0), None)
        if prime is None or high_effort is None:
            self.skipTest("Need prime and high-effort positions")

        genome_prime = [-1] * len(self.current)
        genome_high = [-1] * len(self.current)
        genome_prime[prime] = low_sid
        genome_high[high_effort] = low_sid
        self.assertGreater(
            self.evaluator._position_waste_penalty(np.array(genome_prime, dtype=np.int32)),
            self.evaluator._position_waste_penalty(np.array(genome_high, dtype=np.int32)),
        )

    def test_stale_sid_hard_invalidates_cpu(self):
        genome = list(self.current)
        genome[0] = len(self.pool)
        effort, _adj, violations = self.evaluator.evaluate(genome)
        self.assertEqual(effort, HARD_INVALID_FITNESS)
        self.assertEqual(violations, HARD_INVALID_FITNESS)

    def test_structural_duplicate_penalizes_access_key_flooding(self):
        from layer_access import shortcut_capability
        genome = [-1] * len(self.current)
        cap_sid = None
        cap_layer = None
        for layer in sorted({p.layer for p in self.positions}):
            layer_positions = [i for i, p in enumerate(self.positions) if p.layer == layer]
            if len(layer_positions) < 4:
                continue
            probe = self.positions[layer_positions[0]]
            for s in self.pool:
                if shortcut_capability(s, probe):
                    cap_sid = s.sid
                    cap_layer = layer
                    break
            if cap_sid is not None:
                break
        if cap_sid is None:
            self.skipTest("No repeatable capability SID in pool")
        layer_slots = [i for i, p in enumerate(self.positions) if p.layer == cap_layer]
        base_penalty = self.evaluator._structural_duplicate_penalty(np.array(genome, dtype=np.int32))
        for i in layer_slots[:4]:
            genome[i] = cap_sid
        flood_penalty = self.evaluator._structural_duplicate_penalty(np.array(genome, dtype=np.int32))
        self.assertGreater(flood_penalty, base_penalty)

    def test_structural_duplicate_penalizes_global_target_flooding(self):
        from layer_access import shortcut_capability
        cap_sid = None
        target = mode = None
        for p in self.positions:
            for s in self.pool:
                cap = shortcut_capability(s, p)
                if cap and cap.target > 0:
                    cap_sid = s.sid
                    target = cap.target
                    mode = cap.mode
                    break
            if cap_sid is not None:
                break
        if cap_sid is None:
            self.skipTest("No layer capability SID in pool")
        slots = []
        for i, p in enumerate(self.positions):
            cap = shortcut_capability(self.pool[cap_sid], p)
            if cap and cap.target == target and cap.mode == mode:
                slots.append(i)
            if len(slots) >= 5:
                break
        if len(slots) < 5:
            self.skipTest("Need five slots for global capability duplicate test")
        genome = [-1] * len(self.current)
        for i in slots[:3]:
            genome[i] = cap_sid
        base_penalty = self.evaluator._structural_duplicate_penalty(np.array(genome, dtype=np.int32))
        genome[slots[3]] = cap_sid
        genome[slots[4]] = cap_sid
        flood_penalty = self.evaluator._structural_duplicate_penalty(np.array(genome, dtype=np.int32))
        self.assertGreater(flood_penalty, base_penalty)

    def test_compact_capability_cache_key_ignores_non_capability_changes(self):
        cap_sid = next(iter(self.evaluator._capability_sid_set()), None)
        if cap_sid is None:
            self.skipTest("No capability SID")
        non_cap_sids = [s.sid for s in self.pool if s.sid not in self.evaluator._capability_sid_set()]
        if len(non_cap_sids) < 2:
            self.skipTest("Need non-capability SIDs")
        cap_slot = next((i for i in range(len(self.current))), None)
        non_cap_slot = next((i for i in range(len(self.current)) if i != cap_slot), None)
        g1 = [-1] * len(self.current)
        g2 = [-1] * len(self.current)
        g1[cap_slot] = cap_sid
        g2[cap_slot] = cap_sid
        g1[non_cap_slot] = non_cap_sids[0]
        g2[non_cap_slot] = non_cap_sids[1]
        self.assertEqual(
            self.evaluator._capability_cache_key_for_genome(g1),
            self.evaluator._capability_cache_key_for_genome(g2),
        )

    def test_validation_cache_lru_respects_max_entries(self):
        cfg = copy.deepcopy(self.config)
        cfg["validation_cache_max_entries"] = 3
        evaluator = FitnessEvaluator(
            self.positions, self.pool, cfg,
            usage_stats={}, conjunction_pairs={},
            device="cpu", current_genome=self.current, canonical=self.canonical,
        )
        evaluator._init_capability_cache()
        for i in range(5):
            evaluator._validation_cache[f"k{i}".encode("ascii")] = i
        evaluator._trim_validation_cache()
        self.assertLessEqual(len(evaluator._validation_cache), 3)
        self.assertNotIn(b"k0", evaluator._validation_cache)
        self.assertIn(b"k4", evaluator._validation_cache)

    def test_diversity_injection_milestones_fire_once(self):
        cfg = {"diversity_injection_plateaus": [150, 300, 450]}
        fired = set()
        self.assertIsNone(diversity_injection_milestone(149, fired, cfg))
        self.assertEqual(diversity_injection_milestone(150, fired, cfg), 150)
        fired.add(150)
        self.assertIsNone(diversity_injection_milestone(151, fired, cfg))
        self.assertEqual(diversity_injection_milestone(300, fired, cfg), 300)

    def test_adaptive_scratch_phase_selection(self):
        cfg = {
            "phase_window": 3,
            "exploit_max_improvement": 0.001,
            "scratch_exploit_force_gen": 1200,
        }
        self.assertEqual(scratch_phase_for_generation(10, [], cfg, True), "explore")
        self.assertEqual(scratch_phase_for_generation(200, [100, 95, 90, 80], cfg, True), "balanced")
        self.assertEqual(scratch_phase_for_generation(200, [100, 100, 100, 100], cfg, True), "exploit")
        self.assertEqual(scratch_phase_for_generation(1200, [100, 99, 98, 97], cfg, True), "exploit")

    def test_scratch_repair_seeds_exit_required_layers(self):
        scratch = build_scratch_genome(self.canonical, self.positions, self.pool)
        layer_positions = {}
        for p in self.positions:
            layer_positions.setdefault(p.layer, []).append(p)
        repaired, changed = ensure_structural_exits(
            scratch, self.positions, self.pool, layer_positions, self.evaluator.access_analyzer
        )
        self.assertTrue(changed)
        result = self.evaluator.access_analyzer.validate(repaired)
        exit_errors = [e for e in result.errors if "has no return-to-base exit" in e]
        self.assertFalse(exit_errors, exit_errors)

    def test_mouse_buttons_missing_get_direct_penalty(self):
        if not self.evaluator.mouse_button_required_sids:
            self.skipTest("No mouse button SIDs")
        genome_missing = [-1] * len(self.current)
        genome_present = [-1] * len(self.current)
        slots = iter(range(len(genome_present)))
        for sid in sorted(self.evaluator.mouse_button_required_sids):
            genome_present[next(slots)] = sid
        missing_penalty = self.evaluator._missing_important_penalty(np.array(genome_missing, dtype=np.int32))
        present_penalty = self.evaluator._missing_important_penalty(np.array(genome_present, dtype=np.int32))
        self.assertGreater(missing_penalty, present_penalty)

    def test_missing_required_exits_hard_invalidates_when_analyzer_fails(self):
        from layer_access import shortcut_capability
        scratch = build_scratch_genome(self.canonical, self.positions, self.pool)
        layer_positions = {}
        for p in self.positions:
            layer_positions.setdefault(p.layer, []).append(p)
        repaired, _ = ensure_structural_exits(
            scratch, self.positions, self.pool, layer_positions, self.evaluator.access_analyzer
        )
        checked = 0
        for layer in sorted(self.evaluator.access_analyzer.exit_required_layers):
            genome = list(repaired)
            removed = 0
            for p in layer_positions.get(layer, []):
                sid = genome[p.gene_idx]
                if sid < 0:
                    continue
                cap = shortcut_capability(self.pool[int(sid)], p)
                if cap and cap.source == layer and cap.target == 0:
                    genome[p.gene_idx] = -1
                    removed += 1
            if removed == 0:
                continue
            validation = self.evaluator.access_analyzer.validate(genome)
            if validation.valid:
                continue
            checked += 1
            effort, _adj, violations = self.evaluator.evaluate(genome)
            self.assertEqual(effort, HARD_INVALID_FITNESS)
            self.assertEqual(violations, HARD_INVALID_FITNESS)
        self.assertGreater(checked, 0)

    def test_pool_hash_changes_when_pool_changes(self):
        pool_copy = copy.deepcopy(self.pool)
        self.assertEqual(pool_hash(self.pool), pool_hash(pool_copy))
        pool_copy[0].importance += 0.123
        self.assertNotEqual(pool_hash(self.pool), pool_hash(pool_copy))

    def test_export_emits_unchanged_assigned_keys(self):
        from export_zmk import export_genome_to_zmk
        exported = export_genome_to_zmk(self.current, self.positions, self.pool, self.canonical, "test")
        unchanged = [k for k in exported if not k.get("optimizer_changed")]
        assigned_count = sum(1 for sid in self.current if sid >= 0)
        self.assertTrue(unchanged)
        self.assertGreater(len(exported), 0)
        self.assertGreaterEqual(len(exported), assigned_count)

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

    def test_gpu_stale_sid_hard_invalidates_with_cpu(self):
        if not self.has_gpu:
            self.skipTest("No GPU available")
        genome = list(self.current)
        genome[0] = len(self.pool) + 5
        cpu_result = self.gpu_evaluator.evaluate(genome)
        gpu_result = self.gpu_evaluator.evaluate_batch_gpu([genome])[0]
        self.assertEqual(cpu_result[0], HARD_INVALID_FITNESS)
        self.assertEqual(cpu_result[2], HARD_INVALID_FITNESS)
        self.assertEqual(gpu_result[0], HARD_INVALID_FITNESS)
        self.assertEqual(gpu_result[2], HARD_INVALID_FITNESS)

    def test_gpu_effort_includes_layer_demand_weight_delta(self):
        if not self.has_gpu:
            self.skipTest("No GPU available")
        cfg_low = copy.deepcopy(self.config)
        cfg_high = copy.deepcopy(self.config)
        cfg_low.setdefault("weights", {})["layer_demand"] = 0.0
        cfg_high.setdefault("weights", {})["layer_demand"] = 10.0
        low = FitnessEvaluator(
            self.positions, self.pool, cfg_low,
            usage_stats={}, conjunction_pairs={},
            device="cuda", current_genome=self.current, canonical=self.canonical,
        )
        high = FitnessEvaluator(
            self.positions, self.pool, cfg_high,
            usage_stats={}, conjunction_pairs={},
            device="cuda", current_genome=self.current, canonical=self.canonical,
        )
        cpu_delta = high.evaluate(self.current)[0] - low.evaluate(self.current)[0]
        gpu_delta = high.evaluate_batch_gpu([self.current])[0][0] - low.evaluate_batch_gpu([self.current])[0][0]
        self.assertGreater(gpu_delta, 0.0)
        self.assertAlmostEqual(gpu_delta, cpu_delta, delta=max(abs(cpu_delta) * 0.01, 1.0))

    def test_gpu_same_finger_requires_same_layer(self):
        if not self.has_gpu:
            self.skipTest("No GPU available")
        sid_a, sid_b = 0, 1
        pair_key = "|".join(sorted([self.pool[sid_a].keys, self.pool[sid_b].keys]))
        cfg = copy.deepcopy(self.config)
        cfg["weights"] = {
            "effort": 0.0,
            "finger_balance": 0.0,
            "same_finger_penalty": 2.0,
            "learning_curve": 0.0,
            "thumb_utilization": 0.0,
            "cross_layer_consistency": 0.0,
            "trackball_proximity": 0.0,
            "group_placement": 0.0,
            "app_coherence": 0.0,
            "mouse_accessibility": 0.0,
            "adjacency": 0.0,
            "layer_switch_penalty": 0.0,
            "zmk_compatibility": 0.0,
            "duplicate": 0.0,
            "unassignment": 0.0,
            "missing_important": 0.0,
            "group_split": 0.0,
            "momentary_redundancy": 0.0,
            "cross_layer_duplicate": 0.0,
            "layer_redundancy": 0.0,
            "violations": 0.0,
        }
        evaluator = FitnessEvaluator(
            self.positions, self.pool, cfg,
            usage_stats={}, conjunction_pairs={pair_key: 10.0},
            device="cuda", current_genome=None, canonical=None,
        )

        by_finger = {}
        for i, pos in enumerate(self.positions):
            by_finger.setdefault(pos.finger, []).append(i)
        same_layer = diff_layer = None
        for idxs in by_finger.values():
            for a in idxs:
                for b in idxs:
                    if a == b:
                        continue
                    if self.positions[a].layer == self.positions[b].layer:
                        same_layer = same_layer or (a, b)
                    else:
                        diff_layer = diff_layer or (a, b)
                if same_layer and diff_layer:
                    break
            if same_layer and diff_layer:
                break
        if not same_layer or not diff_layer:
            self.skipTest("Need same-finger positions on same and different layers")

        genome_same = [-1] * len(self.positions)
        genome_same[same_layer[0]] = sid_a
        genome_same[same_layer[1]] = sid_b
        genome_diff = [-1] * len(self.positions)
        genome_diff[diff_layer[0]] = sid_a
        genome_diff[diff_layer[1]] = sid_b

        cpu_same = evaluator.evaluate(genome_same)[0]
        cpu_diff = evaluator.evaluate(genome_diff)[0]
        gpu_same, gpu_diff = [r[0] for r in evaluator.evaluate_batch_gpu([genome_same, genome_diff])]
        self.assertGreater(cpu_same, cpu_diff)
        self.assertGreater(gpu_same, gpu_diff)
        self.assertAlmostEqual(gpu_same - gpu_diff, cpu_same - cpu_diff, delta=0.1)


class OperatorSafetyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical, cls.positions, cls.pool, cls.current, cls.evaluator, cls.config = load_fixture()

    def test_mutate_preserves_valid_sids(self):
        from operators import custom_mutate, OperatorContext
        from representation import build_layer_to_positions
        import random
        random.seed(123)
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        genome = list(self.current)
        for _ in range(20):
            result = custom_mutate(genome, ctx, generation=100)
            mutated = result[0]
            for sid in mutated:
                self.assertTrue(sid == -1 or (0 <= sid < len(self.pool)),
                                f"Invalid SID {sid} in mutated genome")
            genome = mutated

    def test_exit_sids_are_operator_protected(self):
        from operators import OperatorContext
        from representation import build_layer_to_positions
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        exit_sid = next(iter(ctx.exit_sid_set), None)
        if exit_sid is None:
            self.skipTest("No exit SIDs")
        genome = [-1] * len(self.current)
        target = next((i for i, p in enumerate(self.positions) if p.layer > 0), None)
        genome[target] = exit_sid
        protected = ctx.protected_indices(genome)
        self.assertIn(target, protected)


if __name__ == "__main__":
    unittest.main()
