import json
import sys
import os
import numpy as np

from representation import (
    build_position_index, build_shortcut_pool, discover_dynamic_groups
)
from fitness import FitnessEvaluator
from run_evolution import (
    load_build_data, build_conjunction_pairs_from_scores, 
    repair_seeded_groups, preseed_unplaced_shortcuts, pool_hash
)

BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build')

def main():
    # Load data exactly as the run does
    canonical, scores, usage_stats, _ = load_build_data(BUILD_DIR)
    
    # Build conjunction_pairs with all augmentations
    conjunction_pairs = build_conjunction_pairs_from_scores(scores)
    
    usage_sequences = usage_stats.get("sequences", {})
    for seq_key, seq_data in usage_sequences.items():
        parts = seq_key.split(" -> ")
        if len(parts) != 2:
            continue
        count = seq_data.get("count", 0)
        avg_gap = seq_data.get("avg_gap_ms", 9999)
        if count < 1 or avg_gap > 5000:
            continue
        speed_weight = max(0.5, 2.0 - avg_gap / 2000.0)
        weight = count * speed_weight * 0.5
        pair_key = "|".join(sorted(parts))
        conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + weight

    usage_chains = usage_stats.get("chains", {})
    for chain_key, chain_data in usage_chains.items():
        parts = chain_key.split(" -> ")
        count = chain_data.get("count", 0)
        if count < 2 or len(parts) < 2:
            continue
        for i in range(len(parts) - 1):
            pair_key = "|".join(sorted([parts[i], parts[i+1]]))
            conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.3
        for i in range(len(parts)):
            for j in range(i+2, len(parts)):
                pair_key = "|".join(sorted([parts[i], parts[j]]))
                distance_decay = 1.0 / (j - i)
                conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.2 * distance_decay

    chain_list = []
    for chain_key, chain_data in usage_chains.items():
        parts = chain_key.split(" -> ")
        count = chain_data.get("count", 0)
        if count >= 2 and len(parts) >= 2:
            chain_list.append((parts, count))
    for i in range(len(chain_list)):
        for j in range(i + 1, len(chain_list)):
            a_parts, a_count = chain_list[i]
            b_parts, b_count = chain_list[j]
            shorter, longer = (a_parts, b_parts) if len(a_parts) <= len(b_parts) else (b_parts, a_parts)
            s_str = " -> ".join(shorter)
            l_str = " -> ".join(longer)
            if s_str not in l_str:
                continue
            combined_count = min(a_count, b_count)
            for si in range(len(shorter)):
                for sj in range(si + 1, len(shorter)):
                    pair_key = "|".join(sorted([shorter[si], shorter[sj]]))
                    conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + combined_count * 0.4

    usage_workflows = usage_stats.get("workflows", {})
    for wf_key, wf_data in usage_workflows.items():
        parts = wf_key.split(" -> ")
        count = wf_data.get("count", 0)
        if count < 3 or len(parts) < 3:
            continue
        for i in range(len(parts)):
            for j in range(i+1, len(parts)):
                pair_key = "|".join(sorted([parts[i], parts[j]]))
                distance_factor = 1.0 / (j - i)
                conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.4 * distance_factor

    layer_sessions = usage_stats.get("layer_sessions", {})
    for layer_str, session_data in layer_sessions.items():
        common_keys = session_data.get("common_keys", [])
        count = session_data.get("count", 1)
        if len(common_keys) < 2:
            continue
        for i in range(min(len(common_keys), 5)):
            for j in range(i+1, min(len(common_keys), 5)):
                pair_key = "|".join(sorted([common_keys[i], common_keys[j]]))
                conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.2
    
    # Build pool and positions
    config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_scratch.json'), encoding='utf-8'))
    frozen = set(config.get("frozen_layers", [7]))
    positions = build_position_index(canonical, frozen)
    pool = build_shortcut_pool(scores, canonical)
    
    # Build current_genome (scratch mode)
    from representation import build_scratch_genome
    scratch_genome = build_scratch_genome(canonical, positions, pool)
    layer_positions = {}
    for pos in positions:
        layer_positions.setdefault(pos.layer, []).append(pos)
    scratch_genome = repair_seeded_groups(scratch_genome, positions, pool, layer_positions)
    scratch_genome = preseed_unplaced_shortcuts(scratch_genome, positions, pool, layer_positions)
    current_genome = scratch_genome
    
    # Load interim genome
    interim_path = os.path.join(BUILD_DIR, 'evolution_scratch_results_interim.json')
    interim = json.load(open(interim_path, encoding='utf-8'))
    genome = np.array(interim['best_violations']['genome'], dtype=np.int32)
    stored_fitness = interim['best_violations']['fitness']
    
    print("="*60)
    print("CPU/GPU DIVERGENCE TEST")
    print("="*60)
    print(f"Stored fitness: effort={stored_fitness['effort']:.2f}, adj={stored_fitness['adjacency']:.2f}, viol={stored_fitness['violations']:.2f}")
    
    # Test with exact_gpu_scoring=False (current default)
    config_approx = dict(config)
    config_approx["exact_gpu_scoring"] = False
    
    evaluator_cpu_approx = FitnessEvaluator(
        positions, pool, config_approx, device='cpu',
        current_genome=current_genome, canonical=canonical,
        usage_stats=usage_stats, conjunction_pairs=conjunction_pairs
    )
    cpu_approx = evaluator_cpu_approx.evaluate(genome)
    
    evaluator_gpu_approx = FitnessEvaluator(
        positions, pool, config_approx, device='cuda',
        current_genome=current_genome, canonical=canonical,
        usage_stats=usage_stats, conjunction_pairs=conjunction_pairs
    )
    gpu_approx = evaluator_gpu_approx.evaluate_batch_gpu([genome.tolist()])
    
    print(f"\nWith exact_gpu_scoring=False:")
    print(f"  CPU: effort={cpu_approx[0]:.2f}, adj={cpu_approx[1]:.2f}, viol={cpu_approx[2]:.2f}")
    print(f"  GPU: effort={gpu_approx[0][0]:.2f}, adj={gpu_approx[0][1]:.2f}, viol={gpu_approx[0][2]:.2f}")
    print(f"  CPU-GPU diff: effort={abs(cpu_approx[0]-gpu_approx[0][0]):.2f}, adj={abs(cpu_approx[1]-gpu_approx[0][1]):.2f}, viol={abs(cpu_approx[2]-gpu_approx[0][2]):.2f}")
    
    # Test with exact_gpu_scoring=True
    config_exact = dict(config)
    config_exact["exact_gpu_scoring"] = True
    
    evaluator_cpu_exact = FitnessEvaluator(
        positions, pool, config_exact, device='cpu',
        current_genome=current_genome, canonical=canonical,
        usage_stats=usage_stats, conjunction_pairs=conjunction_pairs
    )
    cpu_exact = evaluator_cpu_exact.evaluate(genome)
    
    evaluator_gpu_exact = FitnessEvaluator(
        positions, pool, config_exact, device='cuda',
        current_genome=current_genome, canonical=canonical,
        usage_stats=usage_stats, conjunction_pairs=conjunction_pairs
    )
    gpu_exact = evaluator_gpu_exact.evaluate_batch_gpu([genome.tolist()])
    
    print(f"\nWith exact_gpu_scoring=True:")
    print(f"  CPU: effort={cpu_exact[0]:.2f}, adj={cpu_exact[1]:.2f}, viol={cpu_exact[2]:.2f}")
    print(f"  GPU: effort={gpu_exact[0][0]:.2f}, adj={gpu_exact[0][1]:.2f}, viol={gpu_exact[0][2]:.2f}")
    print(f"  CPU-GPU diff: effort={abs(cpu_exact[0]-gpu_exact[0][0]):.2f}, adj={abs(cpu_exact[1]-gpu_exact[0][1]):.2f}, viol={abs(cpu_exact[2]-gpu_exact[0][2]):.2f}")
    
    print(f"\nConclusion: exact_gpu_scoring={'FIXES' if abs(cpu_exact[2]-gpu_exact[0][2]) < 0.1 else 'DOES NOT FIX'} the violation divergence.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
