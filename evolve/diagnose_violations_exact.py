import json
import sys
import os
import numpy as np

# Replicate the run's setup exactly
from representation import (
    build_position_index, build_shortcut_pool, is_frozen_l0_position, 
    Position, encode_current_layout, build_scratch_genome, discover_dynamic_groups
)
from fitness import FitnessEvaluator
from run_evolution import (
    load_build_data, build_conjunction_pairs_from_scores, 
    repair_seeded_groups, preseed_unplaced_shortcuts, pool_hash
)

BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build')

def main():
    # 1. Load data exactly as the run does
    canonical, scores, usage_stats, _ = load_build_data(BUILD_DIR)
    
    # 2. Build conjunction_pairs with all augmentations
    conjunction_pairs = build_conjunction_pairs_from_scores(scores)
    
    usage_sequences = usage_stats.get("sequences", {})
    usage_conj_count = 0
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
        usage_conj_count += 1
    if usage_conj_count:
        print(f"Added {usage_conj_count} usage-derived conjunction pairs")

    usage_chains = usage_stats.get("chains", {})
    chain_count = 0
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
        chain_count += 1
    if chain_count:
        print(f"Added {chain_count} chain-derived conjunction boosts")

    chain_list = []
    for chain_key, chain_data in usage_chains.items():
        parts = chain_key.split(" -> ")
        count = chain_data.get("count", 0)
        if count >= 2 and len(parts) >= 2:
            chain_list.append((parts, count))
    sim_boost_count = 0
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
                    sim_boost_count += 1
    if sim_boost_count:
        print(f"Added {sim_boost_count} chain-similarity conjunction boosts")

    usage_workflows = usage_stats.get("workflows", {})
    wf_count = 0
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
        wf_count += 1
    if wf_count:
        print(f"Added {wf_count} workflow-derived conjunction boosts")

    layer_sessions = usage_stats.get("layer_sessions", {})
    ls_count = 0
    for layer_str, session_data in layer_sessions.items():
        common_keys = session_data.get("common_keys", [])
        count = session_data.get("count", 1)
        if len(common_keys) < 2:
            continue
        for i in range(min(len(common_keys), 5)):
            for j in range(i+1, min(len(common_keys), 5)):
                pair_key = "|".join(sorted([common_keys[i], common_keys[j]]))
                conjunction_pairs[pair_key] = conjunction_pairs.get(pair_key, 0) + count * 0.2
                ls_count += 1
    if ls_count:
        print(f"Added {ls_count} layer-session conjunction pairs")
    
    print(f"Total conjunction pairs: {len(conjunction_pairs)}")
    
    # 3. Build pool and positions
    config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_scratch.json'), encoding='utf-8'))
    frozen = set(config.get("frozen_layers", [7]))
    positions = build_position_index(canonical, frozen)
    pool = build_shortcut_pool(scores, canonical)
    
    ph = pool_hash(pool)
    print(f"Pool size: {len(pool)}, hash: {ph}")
    
    # 4. Build current_genome (scratch mode)
    scratch_genome = build_scratch_genome(canonical, positions, pool)
    layer_positions = {}
    for pos in positions:
        layer_positions.setdefault(pos.layer, []).append(pos)
    scratch_genome = repair_seeded_groups(scratch_genome, positions, pool, layer_positions)
    scratch_genome = preseed_unplaced_shortcuts(scratch_genome, positions, pool, layer_positions)
    current_genome = scratch_genome
    
    print(f"Scratch genome: {sum(1 for g in current_genome if g >= 0)} assigned positions")
    
    # 5. Load interim genome
    interim_path = os.path.join(BUILD_DIR, 'evolution_scratch_results_interim.json')
    interim = json.load(open(interim_path, encoding='utf-8'))
    genome = np.array(interim['best_violations']['genome'], dtype=np.int32)
    stored_fitness = interim['best_violations']['fitness']
    print(f"Loaded best_violations genome, length={len(genome)}")
    print(f"Stored fitness: effort={stored_fitness['effort']}, adj={stored_fitness['adjacency']}, viol={stored_fitness['violations']}")
    
    # 6. Create evaluator
    evaluator_cpu = FitnessEvaluator(
        positions, pool, config, device='cpu',
        current_genome=current_genome, canonical=canonical,
        usage_stats=usage_stats, conjunction_pairs=conjunction_pairs
    )
    
    # 7. CPU evaluation
    cpu_result = evaluator_cpu.evaluate(genome)
    cpu_breakdown = evaluator_cpu.violation_breakdown(genome)
    print(f"\nCPU evaluate: effort={cpu_result[0]:.2f}, adj={cpu_result[1]:.2f}, viol={cpu_result[2]:.2f}")
    print(f"CPU violation breakdown:")
    for name, value in sorted(cpu_breakdown.items(), key=lambda x: -x[1]):
        print(f"  {name:30s}: {value:10.2f}")
    
    # 8. GPU evaluation
    evaluator_gpu = FitnessEvaluator(
        positions, pool, config, device='cuda',
        current_genome=current_genome, canonical=canonical,
        usage_stats=usage_stats, conjunction_pairs=conjunction_pairs
    )
    gpu_result = evaluator_gpu.evaluate_batch_gpu([genome.tolist()])
    print(f"\nGPU evaluate_batch_gpu: effort={gpu_result[0][0]:.2f}, adj={gpu_result[0][1]:.2f}, viol={gpu_result[0][2]:.2f}")
    
    # 9. Compare
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    print(f"Stored (run): effort={stored_fitness['effort']:.2f}, adj={stored_fitness['adjacency']:.2f}, viol={stored_fitness['violations']:.2f}")
    print(f"CPU:         effort={cpu_result[0]:.2f}, adj={cpu_result[1]:.2f}, viol={cpu_result[2]:.2f}")
    print(f"GPU batch:   effort={gpu_result[0][0]:.2f}, adj={gpu_result[0][1]:.2f}, viol={gpu_result[0][2]:.2f}")
    
    print(f"\nDiff CPU vs Stored: effort={cpu_result[0]-stored_fitness['effort']:.2f}, adj={cpu_result[1]-(-stored_fitness['adjacency']):.2f}, viol={cpu_result[2]-stored_fitness['violations']:.2f}")
    print(f"Diff GPU vs Stored: effort={gpu_result[0][0]-stored_fitness['effort']:.2f}, adj={gpu_result[0][1]-(-stored_fitness['adjacency']):.2f}, viol={gpu_result[0][2]-stored_fitness['violations']:.2f}")
    
    # 10. Count dynamic groups
    dynamic_groups = discover_dynamic_groups(conjunction_pairs, usage_stats, pool, threshold=0.3)
    print(f"\nDynamic groups: {len(dynamic_groups)}")
    for dg in dynamic_groups[:5]:
        print(f"  {dg['name']}: sids={dg['sids']}, weight={dg.get('weight', 1.0):.2f}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
