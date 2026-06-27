"""Compare CPU single-genome fitness with GPU batch fitness.

This is a diagnostic harness, not a pass/fail test. It samples representative
genomes and reports objective drift so GPU scoring changes are easy to audit.
"""
import copy
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from fitness import FitnessEvaluator, HARD_INVALID_FITNESS
from operators import swap_within_layer, swap_to_empty, migrate_shortcut, OperatorContext
from representation import (
    build_layer_to_positions,
    build_position_index,
    build_shortcut_pool,
    encode_current_layout,
)
from run_evolution import build_conjunction_pairs_from_scores, load_config


ROOT = Path(__file__).resolve().parents[1]


def load_inputs(build_dir):
    build = Path(build_dir)
    canonical = json.loads((build / "canonical.json").read_text(encoding="utf-8"))
    scores = json.loads((build / "app_shortcut_scores.json").read_text(encoding="utf-8"))
    usage_path = build / "usage_stats.json"
    usage = json.loads(usage_path.read_text(encoding="utf-8")) if usage_path.exists() else {}
    config = load_config()
    positions = build_position_index(canonical, set(config.get("frozen_layers", [7])))
    pool = build_shortcut_pool(scores, canonical)
    current = encode_current_layout(canonical, positions, pool)
    pairs = build_conjunction_pairs_from_scores(scores)
    return canonical, scores, usage, config, positions, pool, current, pairs


def representative_genomes(current, positions, pool, evaluator, n=12):
    random.seed(20260626)
    layer_positions = build_layer_to_positions(positions)
    ctx = OperatorContext(positions, pool, layer_positions, evaluator.dynamic_groups)
    genomes = [list(current)]

    for k in range(n):
        g = copy.copy(current)
        for _ in range(4 + k):
            r = random.random()
            if r < 0.50:
                g = swap_within_layer(g, ctx)
            elif r < 0.75:
                g = swap_to_empty(g, ctx)
            else:
                g = migrate_shortcut(g, ctx)
        genomes.append(g)

    sparse = [-1] * len(current)
    for i, sid in enumerate(current):
        if sid >= 0 and positions[i].layer == 0:
            sparse[i] = sid
    genomes.append(sparse)

    dup = copy.copy(current)
    first_sid = next((sid for sid in current if sid >= 0), None)
    if first_sid is not None:
        placed = 0
        for i, sid in enumerate(dup):
            if sid < 0 and positions[i].layer > 0:
                dup[i] = first_sid
                placed += 1
                if placed >= 5:
                    break
        genomes.append(dup)

    return genomes


def main():
    build_dir = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "build")
    try:
        import torch
    except ImportError:
        print("PyTorch unavailable; GPU parity cannot run.")
        return 2
    if not torch.cuda.is_available():
        print("CUDA unavailable; GPU parity cannot run.")
        return 2

    canonical, _scores, usage, config, positions, pool, current, pairs = load_inputs(build_dir)
    config = copy.deepcopy(config)
    config["exact_gpu_scoring"] = True
    cpu = FitnessEvaluator(
        positions, pool, config, usage_stats=usage, conjunction_pairs=pairs,
        device="cpu", current_genome=current, canonical=canonical,
    )
    gpu = FitnessEvaluator(
        positions, pool, config, usage_stats=usage, conjunction_pairs=pairs,
        device="cuda", current_genome=current, canonical=canonical,
    )
    genomes = representative_genomes(current, positions, pool, gpu)
    gpu_results = gpu.evaluate_batch_gpu(genomes)

    max_abs = [0.0, 0.0, 0.0]
    print(f"Compared {len(genomes)} genomes on {torch.cuda.get_device_name(0)}")
    for i, genome in enumerate(genomes):
        c = cpu.evaluate(genome)
        g = gpu_results[i]
        diff = [float(g[j] - c[j]) for j in range(3)]
        for j in range(3):
            if c[j] < HARD_INVALID_FITNESS and g[j] < HARD_INVALID_FITNESS:
                max_abs[j] = max(max_abs[j], abs(diff[j]))
        print(
            f"{i:02d} cpu=({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}) "
            f"gpu=({g[0]:.2f}, {g[1]:.2f}, {g[2]:.2f}) "
            f"diff=({diff[0]:.2f}, {diff[1]:.2f}, {diff[2]:.2f})"
        )

    print(
        "max_abs_diff "
        f"effort={max_abs[0]:.2f} adjacency={max_abs[1]:.2f} violations={max_abs[2]:.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
