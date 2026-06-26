"""Profile evolution to find bottlenecks."""
import sys
import os
import time
import copy
import random
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from representation import (
    build_position_index, build_shortcut_pool, build_layer_to_positions,
    encode_current_layout, discover_dynamic_groups,
)
from fitness import FitnessEvaluator
from operators import custom_mutate, pmx_crossover
from run_evolution import load_build_data, load_config, build_conjunction_pairs_from_scores, seed_population, run_nsga2

import torch


def timed(label, fn, *args, **kwargs):
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    elapsed = time.perf_counter() - t0
    print(f"  {label}: {elapsed*1000:.1f}ms")
    return result, elapsed


def main():
    build_dir = sys.argv[1] if len(sys.argv) > 1 else "../build"
    config = load_config()
    random.seed(42)
    np.random.seed(42)

    canonical, scores, usage_stats, _ = load_build_data(build_dir)
    conjunction_pairs = build_conjunction_pairs_from_scores(scores)
    frozen = set(config.get("frozen_layers", [7]))
    positions = build_position_index(canonical, frozen)
    pool = build_shortcut_pool(scores, canonical)
    layer_positions = build_layer_to_positions(positions)
    current = encode_current_layout(canonical, positions, pool)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Pop size: {config.get('pop_size', 2000)}")
    print(f"Positions: {len(positions)}, Shortcuts: {len(pool)}")
    print(f"Conjunction pairs: {len(conjunction_pairs)}")
    print()

    evaluator = FitnessEvaluator(
        positions, pool, config,
        usage_stats=usage_stats,
        conjunction_pairs=conjunction_pairs,
        device=device,
        current_genome=current,
    )
    dynamic_groups = evaluator.dynamic_groups

    # --- Profile seeding ---
    print("=== SEEDING ===")
    pop, t_seed = timed("seed_population", seed_population,
                        current, config.get("pop_size", 2000), positions, pool,
                        layer_positions, build_dir)

    # --- Profile GPU batch eval ---
    print("\n=== GPU BATCH EVAL ===")
    genomes = [list(ind) for ind in pop]

    # Warmup
    evaluator.evaluate_batch_gpu(genomes[:100])
    torch.cuda.synchronize()

    for batch_size in [500, 1000, 2000, 5000]:
        batch = genomes[:batch_size]
        _, t = timed(f"batch eval {batch_size}", evaluator.evaluate_batch_gpu, batch)
        print(f"    => {t/batch_size*1000:.2f}ms per individual, {batch_size/t:.0f} evals/sec")

    # --- Profile single CPU eval ---
    print("\n=== SINGLE CPU EVAL ===")
    sample = genomes[0]
    for _ in range(3):
        evaluator.evaluate(sample)
    _, t_single = timed("single eval (avg of 100)", lambda: [evaluator.evaluate(genomes[i]) for i in range(100)])
    print(f"    =>{t_single/100*1000:.2f}ms per individual")

    # --- Profile CPU eval breakdown ---
    print("\n=== CPU EVAL BREAKDOWN (1 genome) ===")
    g = np.array(sample, dtype=np.int32)
    timed("_effort_score", evaluator._effort_score, g)
    timed("_adjacency_score", evaluator._adjacency_score, g)
    timed("_violation_score", evaluator._violation_score, g)

    # --- Profile operators ---
    print("\n=== OPERATORS ===")
    n_ops = 200
    _, t_mut = timed(f"mutate x{n_ops}", lambda: [custom_mutate(copy.copy(genomes[i % len(genomes)]), positions, pool, layer_positions, dynamic_groups) for i in range(n_ops)])
    print(f"    =>{t_mut/n_ops*1000:.2f}ms per mutation")

    pairs = [(genomes[i], genomes[i+1]) for i in range(0, min(n_ops*2, len(genomes)-1), 2)]
    _, t_cx = timed(f"crossover x{len(pairs)}", lambda: [pmx_crossover(copy.copy(a), copy.copy(b), positions, layer_positions, pool, dynamic_groups) for a, b in pairs])
    print(f"    =>{t_cx/len(pairs)*1000:.2f}ms per crossover")

    # --- Profile NSGA-II selection ---
    print("\n=== NSGA-II SELECTION ===")
    from deap import base, creator, tools
    if hasattr(creator, "FitnessMulti"):
        del creator.FitnessMulti
    if hasattr(creator, "Individual"):
        del creator.Individual
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    deap_pop = [creator.Individual(g) for g in genomes]
    fitnesses = evaluator.evaluate_batch_gpu(genomes)
    for ind, fit in zip(deap_pop, fitnesses):
        ind.fitness.values = fit

    _, t_sel_old = timed(f"DEAP selNSGA2 ({len(deap_pop)} -> {len(deap_pop)//2})",
                     tools.selNSGA2, deap_pop, len(deap_pop)//2)

    # Test GPU-accelerated selection
    # Rebuild fast_selNSGA2 inline since it's defined inside run_nsga2
    def fast_selNSGA2(individuals, k):
        fits_np = np.array([ind.fitness.values for ind in individuals], dtype=np.float32)
        n = len(individuals)
        fits_t = torch.tensor(fits_np, device="cuda") if torch.cuda.is_available() else None
        d = "cuda" if fits_t is not None else None
        ranks = np.full(n, -1, dtype=np.int32)
        remaining = np.ones(n, dtype=bool)
        front_rank = 0
        selected_count = 0
        while selected_count < k and remaining.any():
            idxs = np.where(remaining)[0]
            m = len(idxs)
            if d and m > 50:
                f = fits_t[torch.tensor(idxs, device=d, dtype=torch.long)]
                dominated = torch.zeros(m, device=d, dtype=torch.bool)
                GPU_CHUNK = min(m, 2000)
                for ci in range(0, m, GPU_CHUNK):
                    ce = min(ci + GPU_CHUNK, m)
                    chunk = f[ci:ce]
                    le = (f.unsqueeze(0) <= chunk.unsqueeze(1))
                    lt = (f.unsqueeze(0) < chunk.unsqueeze(1))
                    dom = le.all(dim=2) & lt.any(dim=2)
                    arange = torch.arange(ci, ce, device=d)
                    dom[torch.arange(ce - ci, device=d), arange] = False
                    dominated[ci:ce] = dom.any(dim=1)
                dominated_np = dominated.cpu().numpy()
            else:
                f = fits_np[idxs]
                dominated_np = np.zeros(m, dtype=bool)
                for i in range(m):
                    if dominated_np[i]: continue
                    le = (f[i] <= f).all(axis=1)
                    lt = (f[i] < f).any(axis=1)
                    d2 = le & lt; d2[i] = False
                    dominated_np |= d2
            front_idxs = idxs[~dominated_np]
            if selected_count + len(front_idxs) <= k:
                ranks[front_idxs] = front_rank
                remaining[front_idxs] = False
                selected_count += len(front_idxs)
            else:
                ff = fits_np[front_idxs]
                n_front = len(front_idxs)
                crowding = np.zeros(n_front, dtype=np.float64)
                for obj in range(fits_np.shape[1]):
                    order = np.argsort(ff[:, obj])
                    crowding[order[0]] = np.inf
                    crowding[order[-1]] = np.inf
                    obj_range = float(ff[order[-1], obj] - ff[order[0], obj])
                    if obj_range > 0:
                        crowding[order[1:-1]] += (ff[order[2:], obj] - ff[order[:-2], obj]) / obj_range
                need = k - selected_count
                best = np.argsort(-crowding)[:need]
                ranks[front_idxs[best]] = front_rank
                selected_count += need
                break
            front_rank += 1
        return [individuals[i] for i in range(n) if ranks[i] >= 0]

    _, t_sel = timed(f"GPU selNSGA2 ({len(deap_pop)} -> {len(deap_pop)//2})",
                     fast_selNSGA2, deap_pop, len(deap_pop)//2)

    # --- Summary ---
    print("\n=== ESTIMATED GENERATION TIME ===")
    pop_size = config.get("pop_size", 2000)
    # One gen: mutate/crossover offspring + batch eval + selection
    n_offspring = pop_size  # varAnd produces ~pop_size offspring
    t_operators = (t_mut / n_ops) * n_offspring * 0.5 + (t_cx / len(pairs)) * n_offspring * 0.5
    _, t_eval_full = timed(f"batch eval {pop_size} (full pop)", evaluator.evaluate_batch_gpu, genomes[:pop_size])
    t_gen_est = t_operators + t_eval_full + (t_sel if t_sel else 0)
    print(f"  Operators: {t_operators:.1f}s")
    print(f"  Batch eval: {t_eval_full:.1f}s")
    print(f"  Selection: {t_sel:.1f}s")
    print(f"  TOTAL per gen: {t_gen_est:.1f}s")
    print(f"  100 gens: {t_gen_est*100/60:.0f} min")
    print(f"  300 gens: {t_gen_est*300/3600:.1f} hours")


if __name__ == "__main__":
    main()
