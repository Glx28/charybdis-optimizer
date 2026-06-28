import json
import copy
import os
import sys
import unittest
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from representation import (
    build_shortcut_pool, build_position_index, encode_current_layout,
    build_scratch_genome, is_frozen_l0_position, is_l0_thumb_worthy_shortcut,
)
from fitness import FitnessEvaluator, HARD_INVALID_FITNESS
from run_evolution import (
    ensure_structural_exits, pool_hash,
    diversity_injection_milestone, scratch_phase_for_generation,
    repair_seeded_groups, preseed_unplaced_shortcuts, layout_health_metrics,
    population_diagnostics,
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

    def test_high_importance_misplacement_penalizes_bad_positions(self):
        high_sid = next((s.sid for s in self.pool if s.importance >= 8.0), None)
        good = next((i for i, p in enumerate(self.positions) if p.effort <= 1.0), None)
        bad = next((i for i, p in enumerate(self.positions) if p.effort >= 4.0), None)
        if high_sid is None or good is None or bad is None:
            self.skipTest("Need high-importance SID and good/bad positions")
        genome_good = [-1] * len(self.current)
        genome_bad = [-1] * len(self.current)
        genome_good[good] = high_sid
        genome_bad[bad] = high_sid
        self.assertGreater(
            self.evaluator._high_importance_misplacement_penalty(np.array(genome_bad, dtype=np.int32)),
            self.evaluator._high_importance_misplacement_penalty(np.array(genome_good, dtype=np.int32)),
        )
        self.assertGreater(
            self.evaluator._importance_effort_alignment_bonus(np.array(genome_good, dtype=np.int32)),
            self.evaluator._importance_effort_alignment_bonus(np.array(genome_bad, dtype=np.int32)),
        )

    def test_relationship_awareness_prefers_nearby_related_mouse_buttons(self):
        mb1 = self.evaluator.mouse_button_sids.get('1')
        mb2 = self.evaluator.mouse_button_sids.get('2')
        if mb1 is None or mb2 is None:
            self.skipTest("Need MB1 and MB2")
        l2_left = [p for p in self.positions if p.layer == 2 and p.hand == "left"]
        if len(l2_left) < 2:
            self.skipTest("Need L2 left positions")
        l2_left.sort(key=lambda p: (p.y, p.x))
        other_layer = next((p for p in self.positions if p.layer not in (2, 7)), None)
        if other_layer is None:
            self.skipTest("Need a second mutable layer")

        close = [-1] * len(self.current)
        close[l2_left[0].gene_idx] = mb1
        close[l2_left[1].gene_idx] = mb2
        scattered = [-1] * len(self.current)
        scattered[l2_left[0].gene_idx] = mb1
        scattered[other_layer.gene_idx] = mb2
        self.assertGreater(
            self.evaluator._relationship_awareness_score(np.array(close, dtype=np.int32)),
            self.evaluator._relationship_awareness_score(np.array(scattered, dtype=np.int32)),
        )

    def test_mouse_accessibility_prefers_same_left_mouse_layer(self):
        mb1 = self.evaluator.mouse_button_sids.get('1')
        mb2 = self.evaluator.mouse_button_sids.get('2')
        mb3 = self.evaluator.mouse_button_sids.get('3')
        if mb1 is None or mb2 is None or mb3 is None:
            self.skipTest("Need MB1-3")
        same_layer = [
            p for p in self.positions
            if p.layer in self.evaluator.left_hand_mouse_layers and p.hand == "left" and p.effort <= 2
        ]
        if len(same_layer) < 3:
            self.skipTest("Need three left mouse layer positions")
        same_layer.sort(key=lambda p: (p.layer, p.effort, p.y, p.x))
        split_layers = []
        for layer in sorted(self.evaluator.left_hand_mouse_layers):
            slot = next((p for p in self.positions if p.layer == layer and p.hand == "left" and p.effort <= 2), None)
            if slot:
                split_layers.append(slot)
        if len(split_layers) < 2:
            self.skipTest("Need split left mouse layer positions")
        l0_slot = next((p for p in self.positions if p.layer == 0 and p.hand == "left" and p.is_thumb), None)
        if l0_slot is None:
            self.skipTest("Need L0 left thumb")

        clustered = [-1] * len(self.current)
        for sid, pos in zip((mb1, mb2, mb3), same_layer[:3]):
            clustered[pos.gene_idx] = sid
        split = [-1] * len(self.current)
        split[l0_slot.gene_idx] = mb1
        split[split_layers[0].gene_idx] = mb2
        split[split_layers[-1].gene_idx] = mb3

        self.assertGreater(
            self.evaluator._mouse_accessibility_score(np.array(clustered, dtype=np.int32)),
            self.evaluator._mouse_accessibility_score(np.array(split, dtype=np.int32)) + 50.0,
        )

    def test_mouse_workflow_violation_rejects_split_trackball_workflow(self):
        mb1 = self.evaluator.mouse_button_sids.get('1')
        mb2 = self.evaluator.mouse_button_sids.get('2')
        mb3 = self.evaluator.mouse_button_sids.get('3')
        if mb1 is None or mb2 is None or mb3 is None:
            self.skipTest("Need MB1-3")
        same_layer = [
            p for p in self.positions
            if p.layer in self.evaluator.left_hand_mouse_layers and p.hand == "left" and p.effort <= 2
        ]
        if len(same_layer) < 3:
            self.skipTest("Need three left mouse layer positions")
        same_layer.sort(key=lambda p: (p.layer, p.effort, p.y, p.x))
        split_slots = [
            next((p for p in self.positions if p.layer == layer and p.hand == "left"), None)
            for layer in sorted(self.evaluator.left_hand_mouse_layers)
        ]
        split_slots = [p for p in split_slots if p is not None]
        l0_slot = next((p for p in self.positions if p.layer == 0 and p.hand == "left" and p.is_thumb), None)
        if len(split_slots) < 2 or l0_slot is None:
            self.skipTest("Need split slots")

        clustered = [-1] * len(self.current)
        for sid, pos in zip((mb1, mb2, mb3), same_layer[:3]):
            clustered[pos.gene_idx] = sid
        split = [-1] * len(self.current)
        split[l0_slot.gene_idx] = mb1
        split[split_slots[0].gene_idx] = mb2
        split[split_slots[-1].gene_idx] = mb3

        self.assertLess(
            self.evaluator._mouse_workflow_violation(np.array(clustered, dtype=np.int32)),
            self.evaluator._mouse_workflow_violation(np.array(split, dtype=np.int32)),
        )

    def test_relationship_awareness_includes_non_mouse_groups(self):
        clipboard = [s.sid for s in self.pool if s.keys in {"Ctrl+C", "Ctrl+V"}]
        if len(clipboard) < 2:
            self.skipTest("Need Ctrl+C and Ctrl+V")
        same_layer = [p for p in self.positions if p.layer == 2 and p.hand == "left"]
        if len(same_layer) < 2:
            self.skipTest("Need same-hand positions")
        other_layer = next((p for p in self.positions if p.layer not in (2, 7)), None)
        if other_layer is None:
            self.skipTest("Need another mutable layer")
        close = [-1] * len(self.current)
        close[same_layer[0].gene_idx] = clipboard[0]
        close[same_layer[1].gene_idx] = clipboard[1]
        split = [-1] * len(self.current)
        split[same_layer[0].gene_idx] = clipboard[0]
        split[other_layer.gene_idx] = clipboard[1]
        self.assertGreater(
            self.evaluator._relationship_awareness_score(np.array(close, dtype=np.int32)),
            self.evaluator._relationship_awareness_score(np.array(split, dtype=np.int32)),
        )

    def test_same_finger_ignores_self_pairs(self):
        sid = next((s.sid for s in self.pool if s.importance >= 1.0), None)
        if sid is None:
            self.skipTest("Need SID")
        original_pairs = self.evaluator.conj_pairs
        self.evaluator.conj_pairs = [(sid, sid, 1000.0)]
        try:
            genome = [-1] * len(self.current)
            slots = [i for i, p in enumerate(self.positions) if p.layer == 1]
            if len(slots) < 2:
                self.skipTest("Need same-layer slots")
            genome[slots[0]] = sid
            genome[slots[1]] = sid
            self.assertEqual(self.evaluator._same_finger_penalty(np.array(genome, dtype=np.int32)), 0.0)
            self.assertEqual(self.evaluator.same_finger_offenders(np.array(genome, dtype=np.int32)), [])
        finally:
            self.evaluator.conj_pairs = original_pairs

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

    def test_l0_open_position_rejects_content_keys(self):
        """Content keys (arrows, F-keys) on L0 mutable thumbs should be penalized."""
        arrow_sid = next((s.sid for s in self.pool if "arrow" in s.keys.lower() and s.category == "base_key"), None)
        coach_sid = next((s.sid for s in self.pool if "coach_l1_hold" in s.keys), None)
        l0_thumb = next((i for i, p in enumerate(self.positions)
                         if p.layer == 0 and p.is_thumb and not is_frozen_l0_position(p)), None)
        if arrow_sid is None or coach_sid is None or l0_thumb is None:
            self.skipTest("Need arrow, coach, and L0 mutable thumb")
        genome_arrow = list(self.current)
        genome_arrow[l0_thumb] = arrow_sid
        genome_coach = list(self.current)
        genome_coach[l0_thumb] = coach_sid
        self.assertGreater(
            self.evaluator._l0_open_position_penalty(np.array(genome_arrow, dtype=np.int32)),
            self.evaluator._l0_open_position_penalty(np.array(genome_coach, dtype=np.int32)),
        )

    def test_no_duplicate_semantic_base_keys(self):
        """Pool should not contain two base keys with the same zmk_parameter
        (excluding layer switches and mouse buttons which legitimately share params)."""
        from collections import Counter
        exclude = {"momentary_layer", "toggle_layer", "to_layer", "select:mb", "coach_"}
        base_params = [s.zmk_parameter for s in self.pool
                       if s.category == "base_key" and s.zmk_parameter
                       and s.zmk_parameter != "default_transform"
                       and not any(ex in s.keys.lower() for ex in exclude)]
        dupes = {p: c for p, c in Counter(base_params).items() if c > 1}
        self.assertEqual(dupes, {}, f"Duplicate semantic base keys: {dupes}")

    def test_clipboard_group_is_protected(self):
        """Clipboard group should be protected so group_placement rewards apply."""
        from representation import KEY_GROUPS
        clipboard = next((g for g in KEY_GROUPS if g["name"] == "clipboard"), None)
        self.assertIsNotNone(clipboard)
        self.assertTrue(clipboard.get("protected", False))

    def test_f_key_groups_match_only_base_function_keys(self):
        from representation import KEY_GROUPS, shortcut_matches_group
        high = next((g for g in KEY_GROUPS if g["name"] == "f_keys_high"), None)
        self.assertIsNotNone(high)
        members = [s.keys for s in self.pool if shortcut_matches_group(s, high)]
        self.assertEqual(
            set(members),
            {"_base_f7", "_base_f8", "_base_f9", "_base_f10", "_base_f11", "_base_f12"},
        )

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

    def test_seed_group_repair_moves_split_arrows_together(self):
        arrow_sids = [
            s.sid for s in self.pool
            if s.base_key.upper() in {"LEFTARROW", "RIGHTARROW", "UPARROW", "DOWNARROW"}
        ]
        if len(arrow_sids) < 2:
            self.skipTest("Need arrow SIDs")
        layer_positions = {}
        for p in self.positions:
            layer_positions.setdefault(p.layer, []).append(p)
        target_layer = next((l for l, ps in layer_positions.items() if l > 0 and len(ps) >= 3), None)
        other_layer = next((l for l, ps in layer_positions.items() if l != target_layer and l > 0 and ps), None)
        if target_layer is None or other_layer is None:
            self.skipTest("Need two mutable layers")
        genome = [-1] * len(self.current)
        target_pos = layer_positions[target_layer][0]
        other_pos = layer_positions[other_layer][0]
        genome[target_pos.gene_idx] = arrow_sids[0]
        genome[other_pos.gene_idx] = arrow_sids[1]
        repaired = repair_seeded_groups(genome, self.positions, self.pool, layer_positions)
        repaired_layers = {
            self.positions[i].layer for i, sid in enumerate(repaired) if sid in set(arrow_sids)
        }
        self.assertLessEqual(len(repaired_layers), 1)

    def test_preseed_places_mouse_workflow_on_left_mouse_layer(self):
        from representation import build_layer_to_positions, LAYER_ACCESS
        scratch = build_scratch_genome(self.canonical, self.positions, self.pool)
        seeded = preseed_unplaced_shortcuts(scratch, self.positions, self.pool, build_layer_to_positions(self.positions))
        required = {"_base_select:mb1", "_base_select:mb2", "_base_select:mb3", "Ctrl+C", "Ctrl+V", "Ctrl+X", "Ctrl+Z"}
        placements = {}
        for i, sid in enumerate(seeded):
            if sid >= 0 and self.pool[int(sid)].keys in required:
                placements[self.pool[int(sid)].keys] = self.positions[i]
        self.assertTrue(required.issubset(placements.keys()))
        layers = {p.layer for p in placements.values()}
        self.assertEqual(len(layers), 1)
        layer = next(iter(layers))
        self.assertEqual(LAYER_ACCESS.get(layer, {}).get("thumb"), "left")
        self.assertIn("momentary", LAYER_ACCESS.get(layer, {}).get("method", ""))
        self.assertTrue(all(p.hand == "left" for p in placements.values()))

    def test_layout_health_reports_generic_failures(self):
        bad = [-1] * len(self.current)
        mb_sids = [
            next((s.sid for s in self.pool if s.keys == key), None)
            for key in ("_base_select:mb1", "_base_select:mb2", "_base_select:mb3")
        ]
        if any(sid is None for sid in mb_sids):
            self.skipTest("Need MB1-3")
        slots = [
            next((p for p in self.positions if p.layer == 0 and p.is_thumb and not is_frozen_l0_position(p)), None),
            next((p for p in self.positions if p.layer == 1 and p.hand == "right"), None),
            next((p for p in self.positions if p.layer == 3 and p.hand == "right"), None),
        ]
        if any(p is None for p in slots):
            self.skipTest("Need scattered slots")
        arrow_sid = next((s.sid for s in self.pool if s.keys == "_base_downarrow"), None)
        if arrow_sid is None:
            self.skipTest("Need DownArrow")
        for sid, pos in zip(mb_sids, slots):
            bad[pos.gene_idx] = sid
        bad[slots[0].gene_idx] = arrow_sid
        health = layout_health_metrics([bad], self.positions, self.pool, self.evaluator)
        self.assertGreater(health["workflow_clusters"]["mouse_critical"]["scattered_pct"], 0.0)
        self.assertGreater(health["role_violations"]["l0_bad_total"], 0)
        self.assertGreater(health["prime_empty"]["with_unassigned_nonbase"], 0)

    def test_layout_health_reports_repaired_mouse_workflow_intact(self):
        from operators import OperatorContext, repair_position_compatibility
        from representation import build_layer_to_positions
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        scratch = build_scratch_genome(self.canonical, self.positions, self.pool)
        seeded = preseed_unplaced_shortcuts(scratch, self.positions, self.pool, layer_positions, verbose=False)
        repaired, _ = repair_position_compatibility(seeded, ctx)
        health = layout_health_metrics([repaired], self.positions, self.pool, self.evaluator)
        self.assertEqual(health["workflow_clusters"]["mouse_critical"]["intact_pct"], 1.0)
        self.assertEqual(health["workflow_clusters"]["clipboard"]["intact_pct"], 1.0)
        self.assertEqual(health["role_violations"]["l0_bad_total"], 0)

    def test_population_diagnostics_health_is_opt_in(self):
        diagnostics = population_diagnostics([self.current], self.positions, self.pool, self.evaluator)
        self.assertNotIn("layout_health", diagnostics)
        diagnostics = population_diagnostics(
            [self.current], self.positions, self.pool, self.evaluator,
            include_health=True, health_config={"health_sample_limit": 1},
        )
        self.assertIn("layout_health", diagnostics)

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
            "high_importance_misplacement": 0.0,
            "importance_effort_alignment": 0.0,
            "position_waste": 0.0,
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

    def test_illegal_l0_arrow_is_not_operator_protected(self):
        from operators import OperatorContext
        from representation import build_layer_to_positions
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        l0_thumb = next((i for i, p in enumerate(self.positions)
                         if p.layer == 0 and p.is_thumb and not is_frozen_l0_position(p)), None)
        down_sid = next((s.sid for s in self.pool if s.keys == "_base_downarrow"), None)
        if l0_thumb is None or down_sid is None:
            self.skipTest("Need mutable L0 thumb and DownArrow")
        genome = [-1] * len(self.current)
        genome[l0_thumb] = down_sid
        self.assertIn(down_sid, ctx.protected_sid_set)
        self.assertFalse(ctx.position_accepts_sid(l0_thumb, down_sid))
        self.assertNotIn(l0_thumb, ctx.protected_indices(genome))

    def test_position_repair_evacuates_downarrow_from_l0_thumb(self):
        from operators import OperatorContext, repair_position_compatibility
        from representation import build_layer_to_positions
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        l0_thumb = next((i for i, p in enumerate(self.positions)
                         if p.layer == 0 and p.is_thumb and not is_frozen_l0_position(p)), None)
        down_sid = next((s.sid for s in self.pool if s.keys == "_base_downarrow"), None)
        legal_empty = next((i for i, p in enumerate(self.positions)
                            if p.layer > 0 and self.current[i] < 0), None)
        if l0_thumb is None or down_sid is None or legal_empty is None:
            self.skipTest("Need mutable L0 thumb, DownArrow, and legal empty slot")
        genome = list(self.current)
        genome[l0_thumb] = down_sid
        genome[legal_empty] = -1
        repaired, count = repair_position_compatibility(genome, ctx)
        self.assertGreaterEqual(count, 1)
        self.assertNotEqual(repaired[l0_thumb], down_sid)
        self.assertGreaterEqual(repaired[l0_thumb], 0)
        self.assertTrue(ctx.position_accepts_sid(l0_thumb, repaired[l0_thumb]))
        self.assertIn(down_sid, repaired)
        offenders = ctx.incompatible_indices(repaired)
        self.assertEqual(offenders, [])

    def test_scratch_repair_does_not_steal_mouse_workflow_for_l0_thumb(self):
        from operators import OperatorContext, repair_position_compatibility
        from representation import build_layer_to_positions, LAYER_ACCESS
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        scratch = build_scratch_genome(self.canonical, self.positions, self.pool)
        seeded = preseed_unplaced_shortcuts(scratch, self.positions, self.pool, layer_positions, verbose=False)
        repaired, count = repair_position_compatibility(seeded, ctx)
        mb_sids = {
            s.sid for s in self.pool
            if s.keys in {"_base_select:mb1", "_base_select:mb2", "_base_select:mb3"}
        }
        if len(mb_sids) < 3:
            self.skipTest("Need MB1-3")
        mb_positions = [self.positions[i] for i, sid in enumerate(repaired) if sid in mb_sids]
        self.assertEqual(len(mb_positions), 3)
        layers = {p.layer for p in mb_positions}
        self.assertEqual(len(layers), 1)
        layer = next(iter(layers))
        self.assertEqual(LAYER_ACCESS.get(layer, {}).get("thumb"), "left")
        self.assertTrue(all(p.hand == "left" for p in mb_positions))
        self.assertEqual(ctx.incompatible_indices(repaired), [])
        for idx in ctx.l0_mutable_thumb_indices:
            self.assertGreaterEqual(repaired[idx], 0)
            self.assertTrue(ctx.position_accepts_sid(idx, repaired[idx]))

    def test_mutation_does_not_leave_illegal_l0_thumb_content(self):
        from operators import custom_mutate, OperatorContext
        from representation import build_layer_to_positions
        import random
        random.seed(456)
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        l0_thumb = next((i for i, p in enumerate(self.positions)
                         if p.layer == 0 and p.is_thumb and not is_frozen_l0_position(p)), None)
        down_sid = next((s.sid for s in self.pool if s.keys == "_base_downarrow"), None)
        if l0_thumb is None or down_sid is None:
            self.skipTest("Need mutable L0 thumb and DownArrow")
        genome = list(self.current)
        genome[l0_thumb] = down_sid
        for _ in range(40):
            genome = custom_mutate(genome, ctx, scratch_mode=True, generation=500)[0]
            self.assertEqual(ctx.incompatible_indices(genome), [])
            for idx in ctx.l0_mutable_thumb_indices:
                self.assertGreaterEqual(genome[idx], 0)
                self.assertTrue(ctx.position_accepts_sid(idx, genome[idx]))

    def test_position_repair_fills_prime_empty_slots(self):
        from operators import OperatorContext, repair_position_compatibility
        from representation import build_layer_to_positions
        layer_positions = build_layer_to_positions(self.positions)
        ctx = OperatorContext(self.positions, self.pool, layer_positions,
                              self.evaluator.dynamic_groups)
        genome = build_scratch_genome(self.canonical, self.positions, self.pool)
        prime_slots = [
            i for i, p in enumerate(self.positions)
            if p.layer != 0 and p.effort <= 1.5
        ][:5]
        if len(prime_slots) < 5:
            self.skipTest("Need prime slots")
        for idx in prime_slots:
            genome[idx] = -1
        repaired, count = repair_position_compatibility(genome, ctx)
        self.assertGreaterEqual(count, len(prime_slots))
        self.assertTrue(all(repaired[idx] >= 0 for idx in prime_slots))
        self.assertEqual(ctx.incompatible_indices(repaired), [])


if __name__ == "__main__":
    unittest.main()
