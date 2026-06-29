import copy
import json
import os
import sys
import random
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
    config["exact_gpu_scoring"] = False  # Test with APPROXIMATE scoring

    cpu = FitnessEvaluator(
        positions, pool, config, usage_stats=usage, conjunction_pairs=pairs,
        device="cpu", current_genome=current, canonical=canonical,
    )
    gpu = FitnessEvaluator(
        positions, pool, config, usage_stats=usage, conjunction_pairs=pairs,
        device="cuda", current_genome=current, canonical=canonical,
    )

    random.seed(20260626)
    layer_positions = build_layer_to_positions(positions)
    ctx = OperatorContext(positions, pool, layer_positions, gpu.dynamic_groups)
    genomes = [list(current)]

    for k in range(12):
        g = list(current)
        for _ in range(k + 1):
            op = random.choice([swap_within_layer, swap_to_empty, migrate_shortcut])
            g = op(g, ctx)[0]
        genomes.append(g)

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
    sys.exit(main())
