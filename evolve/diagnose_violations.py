import json
import sys
import os
import numpy as np

from representation import build_position_index, build_shortcut_pool, is_frozen_l0_position, Position, encode_current_layout, build_scratch_genome
from fitness import FitnessEvaluator

BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build')

def main():
    from run_evolution import load_build_data, build_conjunction_pairs_from_scores, repair_seeded_groups, preseed_unplaced_shortcuts
    canonical, scores, usage_stats, _ = load_build_data(BUILD_DIR)
    pool = build_shortcut_pool(scores, canonical)
    conjunction_pairs = build_conjunction_pairs_from_scores(scores)
    
    positions = build_position_index(canonical, {7})
    config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_scratch.json'), encoding='utf-8'))
    
    # 1. Count prime positions (effort <= 1.5, non-L0, not frozen)
    prime_positions = [p for p in positions if p.effort <= 1.5 and p.layer != 0]
    prime_by_layer = {}
    for p in prime_positions:
        prime_by_layer.setdefault(p.layer, []).append(p)
    
    # 2. Count all positions by layer
    all_by_layer = {}
    for p in positions:
        all_by_layer.setdefault(p.layer, []).append(p)
    
    # 3. Count mutable L0 positions (thumb area)
    l0_mutable = [p for p in positions if p.layer == 0 and p.is_thumb and not is_frozen_l0_position(p)]
    l0_frozen = [p for p in positions if p.layer == 0 and is_frozen_l0_position(p)]
    
    # 4. Count structural keys in pool (these "must" be placed)
    structural_keys = [s for s in pool if s.keys.startswith('_base_coach') or s.keys.startswith('_base_momentary') or s.keys.startswith('_base_toggle') or s.keys.startswith('_base_to_layer')]
    
    # 5. Count base keys (letters, numbers, etc.) vs app shortcuts
    base_keys = [s for s in pool if s.category == 'base_key']
    app_shortcuts = [s for s in pool if s.category != 'base_key']
    
    # 6. Count high-importance keys
    high_imp = [s for s in pool if s.importance >= 9.0]
    
    print("=" * 60)
    print("EMPTY POSITION MATH DIAGNOSTIC")
    print("=" * 60)
    print(f"Total mutable positions: {len(positions)}")
    print(f"  L0 mutable thumbs: {len(l0_mutable)}")
    print(f"  L0 frozen (structural): {len(l0_frozen)}")
    print(f"  Non-L0 positions: {len(positions) - len(l0_mutable) - len(l0_frozen)}")
    print()
    print(f"Prime positions (effort <= 1.5, non-L0): {len(prime_positions)}")
    for layer, pos_list in sorted(prime_by_layer.items()):
        print(f"  Layer {layer}: {len(pos_list)} prime positions")
    print()
    print(f"Pool size: {len(pool)}")
    print(f"  Base keys: {len(base_keys)}")
    print(f"  App shortcuts: {len(app_shortcuts)}")
    print(f"  Structural/layer keys: {len(structural_keys)}")
    print(f"  High importance (>=9.0): {len(high_imp)}")
    print()
    
    # The empty_prime penalty in _position_waste_penalty:
    # 30 * pw_weight for each empty position with effort <= 1.5 on non-L0
    pw_weight = config.get('weights', {}).get('position_waste', 5.0)
    empty_prime_penalty_per_slot = 30.0 * pw_weight
    print(f"Empty prime penalty per slot: {empty_prime_penalty_per_slot} (30 * position_waste={pw_weight})")
    
    shortcuts_that_belong_on_prime = [s for s in pool if s.importance >= 3.0]
    print(f"Shortcuts with importance >= 3.0: {len(shortcuts_that_belong_on_prime)} (candidates for prime positions)")
    
    print()
    print(f"If ALL {len(pool)} pool entries placed exactly once:")
    print(f"  Empty positions: {len(positions) - len(pool)}")
    print(f"  Prime positions: {len(prime_positions)}")
    print(f"  If all empty positions were prime: penalty = {len(prime_positions) * empty_prime_penalty_per_slot}")
    
    # Count positions by effort tier (non-L0 only)
    effort_tiers = {}
    for p in positions:
        if p.layer == 0:
            continue
        tier = f"eff_{p.effort}"
        effort_tiers.setdefault(tier, 0)
        effort_tiers[tier] += 1
    
    print(f"\nNon-L0 position effort distribution:")
    for tier in sorted(effort_tiers.keys(), key=lambda x: float(x.split('_')[1])):
        print(f"  {tier}: {effort_tiers[tier]} positions")
    
    print(f"\n--- KEY MATH ---")
    print(f"Prime positions (non-L0, eff<=1.5): {len(prime_positions)}")
    print(f"Pool size: {len(pool)}")
    print(f"Structural keys in pool: {len(structural_keys)}")
    non_structural_pool = len(pool) - len(structural_keys)
    print(f"Non-structural pool entries: {non_structural_pool}")
    print(f"If structural keys MUST be placed, they occupy ~{len(structural_keys)} positions")
    print(f"Remaining positions for non-structural: ~{len(positions) - len(structural_keys)}")
    print(f"Prime positions available for non-structural: ~{len(prime_positions)} (if structural avoid prime)")
    
    print(f"\nPool size ({len(pool)}) >= Prime positions ({len(prime_positions)})? {len(pool) >= len(prime_positions)}")
    if len(pool) >= len(prime_positions):
        print("  -> In theory, ALL prime positions CAN be filled with pool entries.")
        print("  -> The empty_prime penalty should NOT be a permanent floor if evolution is optimal.")
    else:
        min_empty_prime = len(prime_positions) - len(pool)
        print(f"  -> MINIMUM empty prime positions: {min_empty_prime}")
        print(f"  -> Permanent floor from empty_prime: {min_empty_prime * empty_prime_penalty_per_slot}")
    
    print("\n" + "=" * 60)
    print("CHECKING FOR CHECKPOINT DATA")
    print("=" * 60)
    
    interim_path = os.path.join(BUILD_DIR, 'evolution_scratch_results_interim.json')
    checkpoint_path = os.path.join(BUILD_DIR, 'evolution_scratch_checkpoint.json')
    
    genome = None
    if os.path.exists(interim_path):
        print(f"Found interim results: {interim_path}")
        try:
            interim = json.load(open(interim_path, encoding='utf-8'))
            if 'best_violations' in interim and 'genome' in interim['best_violations']:
                genome = np.array(interim['best_violations']['genome'], dtype=np.int32)
                print(f"Loaded best_violations genome from interim, length={len(genome)}")
            elif 'best_weighted' in interim and 'genome' in interim['best_weighted']:
                genome = np.array(interim['best_weighted']['genome'], dtype=np.int32)
                print(f"Loaded best_weighted genome from interim, length={len(genome)}")
        except Exception as e:
            print(f"Error loading interim: {e}")
    
    if genome is None and os.path.exists(checkpoint_path):
        print(f"Found checkpoint: {checkpoint_path}")
        try:
            ckpt = json.load(open(checkpoint_path, encoding='utf-8'))
            if 'best_violations' in ckpt and 'genome' in ckpt['best_violations']:
                genome = np.array(ckpt['best_violations']['genome'], dtype=np.int32)
                print(f"Loaded best_violations genome from checkpoint, length={len(genome)}")
            elif 'best_weighted' in ckpt and 'genome' in ckpt['best_weighted']:
                genome = np.array(ckpt['best_weighted']['genome'], dtype=np.int32)
                print(f"Loaded best_weighted genome from checkpoint, length={len(genome)}")
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
    
    if genome is not None and len(genome) == len(positions):
        # Check checkpoint generation and fitness
        ckpt_gen = None
        if os.path.exists(checkpoint_path):
            try:
                ckpt = json.load(open(checkpoint_path, encoding='utf-8'))
                ckpt_gen = ckpt.get('generation', 'unknown')
                print(f"Checkpoint generation: {ckpt_gen}")
                if 'best_violations' in ckpt:
                    print(f"Checkpoint best_violations fitness: {ckpt['best_violations'].get('fitness', {})}")
                    print(f"Checkpoint best_violations assignments: {ckpt['best_violations'].get('total_assignments', 'unknown')}")
                if 'best_weighted' in ckpt:
                    print(f"Checkpoint best_weighted fitness: {ckpt['best_weighted'].get('fitness', {})}")
                if 'best_effort' in ckpt:
                    print(f"Checkpoint best_effort fitness: {ckpt['best_effort'].get('fitness', {})}")
            except Exception as e:
                print(f"Error reading checkpoint gen: {e}")
        
        # In scratch mode, current_genome is build_scratch_genome, not canonical
        # We need to reconstruct it the same way the run does
        from run_evolution import repair_seeded_groups, preseed_unplaced_shortcuts
        from operators import OperatorContext
        scratch_genome = build_scratch_genome(canonical, positions, pool)
        layer_positions = {}
        for pos in positions:
            layer_positions.setdefault(pos.layer, []).append(pos)
        scratch_genome = repair_seeded_groups(scratch_genome, positions, pool, layer_positions)
        scratch_genome = preseed_unplaced_shortcuts(scratch_genome, positions, pool, layer_positions)
        current_genome = scratch_genome
        
        print(f"\nScratch genome has {sum(1 for g in current_genome if g >= 0)} assigned positions")
        print(f"Canonical genome has {sum(1 for g in encode_current_layout(canonical, positions, pool) if g >= 0)} assigned positions")
        
        print("\nRunning violation_breakdown WITH scratch current_genome...")
        evaluator_cpu = FitnessEvaluator(positions, pool, config, device='cpu', current_genome=current_genome, canonical=canonical, usage_stats=usage_stats, conjunction_pairs=conjunction_pairs)
        breakdown_cpu = evaluator_cpu.violation_breakdown(genome)
        
        print("\n" + "=" * 60)
        print("VIOLATION BREAKDOWN (CPU with scratch current_genome)")
        print("=" * 60)
        for name, value in sorted(breakdown_cpu.items(), key=lambda x: -x[1]):
            print(f"  {name:30s}: {value:10.2f}")
        
        # Also run GPU evaluation
        try:
            evaluator_gpu = FitnessEvaluator(positions, pool, config, device='cuda', current_genome=current_genome, canonical=canonical, usage_stats=usage_stats, conjunction_pairs=conjunction_pairs)
            result_gpu = evaluator_gpu.evaluate_batch_gpu([genome.tolist()])
            print(f"\nGPU evaluate_batch_gpu result: effort={result_gpu[0][0]:.2f}, adj={result_gpu[0][1]:.2f}, viol={result_gpu[0][2]:.2f}")
            
            # Also run single GPU eval if possible
            single_gpu = evaluator_gpu.evaluate(genome)
            print(f"GPU evaluate() result: effort={single_gpu[0]:.2f}, adj={single_gpu[1]:.2f}, viol={single_gpu[2]:.2f}")
        except Exception as e:
            print(f"GPU evaluation failed: {e}")
        
        cpu_result = evaluator_cpu.evaluate(genome)
        print(f"CPU evaluate() result: effort={cpu_result[0]:.2f}, adj={cpu_result[1]:.2f}, viol={cpu_result[2]:.2f}")
        
        empty_primes = 0
        for i, sid in enumerate(genome):
            if sid < 0 and positions[i].effort <= 1.5 and positions[i].layer > 0:
                empty_primes += 1
        print(f"\n  Actual empty prime positions in genome: {empty_primes}")
        print(f"  Contribution to position_waste from empty primes: {empty_primes * empty_prime_penalty_per_slot}")
        
        filled = sum(1 for g in genome if g >= 0)
        print(f"  Total filled positions: {filled}")
        print(f"  Total empty positions: {len(positions) - filled}")
        
        assigned_sids = set(int(g) for g in genome if g >= 0)
        print(f"  Unique SIDs assigned: {len(assigned_sids)}")
        print(f"  Pool entries not assigned: {len(pool) - len(assigned_sids)}")
    else:
        print("No usable checkpoint/interim data found or genome length mismatch.")
        if genome is not None:
            print(f"  Genome length: {len(genome)}, positions: {len(positions)}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
