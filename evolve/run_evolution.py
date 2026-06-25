"""Main entry point for DEAP + pyribs evolutionary keyboard layout optimization.

GPU-accelerated batch fitness evaluation + multiprocessing for operators.
Usage: python run_evolution.py <build_dir>
"""
import sys
import os
import json
import random
import time
import copy
from pathlib import Path
from multiprocessing import cpu_count

import numpy as np

from deap import base, creator, tools, algorithms


def _safe_replace(src, dst, retries=3):
    for i in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i < retries - 1:
                time.sleep(0.5)
    os.replace(src, dst)

from representation import (
    build_position_index, build_shortcut_pool, build_layer_to_positions,
    encode_current_layout, decode_genome,
)
from fitness import FitnessEvaluator
from operators import custom_mutate, pmx_crossover

HAS_TORCH = False
try:
    import torch
    HAS_TORCH = True
except ImportError:
    pass

QD_AVAILABLE = False
try:
    from ribs.archives import GridArchive
    from ribs.emitters import EvolutionStrategyEmitter
    from ribs.schedulers import Scheduler
    QD_AVAILABLE = True
except ImportError:
    pass


def load_config():
    config_path = Path(__file__).parent / "config.json"
    with open(config_path) as f:
        return json.load(f)


def load_build_data(build_dir):
    def load(name):
        with open(os.path.join(build_dir, name), encoding="utf-8") as f:
            return json.load(f)

    canonical = load("canonical.json")
    scores = load("app_shortcut_scores.json")

    usage_stats = {}
    try:
        usage_stats = load("usage_stats.json")
    except FileNotFoundError:
        pass

    conjunction_pairs = {}
    try:
        reorg = load("reorganize_proposals.json")
        if "conjunction_pairs_count" in reorg:
            pass
    except FileNotFoundError:
        pass

    return canonical, scores, usage_stats, conjunction_pairs


def build_conjunction_pairs_from_scores(scores):
    pairs = {}
    for app in scores["apps"]:
        by_cat = {}
        for s in app["shortcuts"]:
            if not s.get("mapped"):
                continue
            cat = s.get("category", "general")
            by_cat.setdefault(cat, []).append(s)
        for cat, shortcuts in by_cat.items():
            for i in range(len(shortcuts)):
                for j in range(i + 1, len(shortcuts)):
                    w = min(shortcuts[i]["importance"], shortcuts[j]["importance"]) * 0.3
                    key = "|".join(sorted([shortcuts[i]["keys"], shortcuts[j]["keys"]]))
                    pairs[key] = pairs.get(key, 0) + w
    return pairs


def load_previous_elites(build_dir, n_positions):
    """Load genomes from previous evolution run if available.
    Checks both final results and interim results (from interrupted runs)."""
    elites = []
    for filename in ["evolution_results.json", "evolution_results_interim.json"]:
        results_path = os.path.join(build_dir, filename)
        if not os.path.exists(results_path):
            continue
        try:
            with open(results_path, "r", encoding="utf-8") as f:
                prev = json.load(f)
            for sol in prev.get("pareto_front", []):
                g = sol.get("genome")
                if g and len(g) == n_positions:
                    elites.append(list(g))
            for sol in prev.get("qd_solutions", []):
                g = sol.get("genome")
                if g and len(g) == n_positions:
                    elites.append(list(g))
        except (json.JSONDecodeError, KeyError):
            continue
    # Deduplicate
    seen = set()
    unique = []
    for e in elites:
        key = tuple(e)
        if key not in seen:
            seen.add(key)
            unique.append(e)
    if unique:
        print(f"Loaded {len(unique)} elites from previous run(s)")
    return unique


def seed_population(current_genome, n_pop, positions, shortcut_pool, layer_positions,
                    build_dir=None):
    from operators import swap_within_layer, swap_to_empty, migrate_shortcut, custom_mutate

    population = [copy.copy(current_genome)]

    prev_elites = load_previous_elites(build_dir, len(current_genome)) if build_dir else []

    # ~30% from previous elites (direct injection)
    elite_budget = int(n_pop * 0.3)
    for elite in prev_elites[:elite_budget]:
        population.append(copy.copy(elite))

    # ~20% wild mutations of previous elites (explore around known good solutions)
    wild_budget = int(n_pop * 0.2)
    if prev_elites:
        for _ in range(wild_budget):
            base = copy.copy(random.choice(prev_elites))
            n_swaps = random.randint(10, 40)
            for _ in range(n_swaps):
                r = random.random()
                if r < 0.5:
                    base = swap_within_layer(base, positions, layer_positions, shortcut_pool)
                elif r < 0.75:
                    base = swap_to_empty(base, positions, layer_positions, shortcut_pool)
                else:
                    base = migrate_shortcut(base, positions, shortcut_pool, layer_positions)
            population.append(base)

    # Conservative mutations of current layout
    for _ in range(min(n_pop // 10, 50)):
        ind = copy.copy(current_genome)
        n_swaps = random.randint(1, 5)
        for _ in range(n_swaps):
            ind = swap_within_layer(ind, positions, layer_positions, shortcut_pool)
        population.append(ind)

    # Fill rest with fresh exploration from current layout
    while len(population) < n_pop:
        ind = copy.copy(current_genome)
        n_swaps = random.randint(5, 20)
        for _ in range(n_swaps):
            r = random.random()
            if r < 0.5:
                ind = swap_within_layer(ind, positions, layer_positions, shortcut_pool)
            elif r < 0.75:
                ind = swap_to_empty(ind, positions, layer_positions, shortcut_pool)
            else:
                ind = migrate_shortcut(ind, positions, shortcut_pool, layer_positions)
        population.append(ind)

    return population[:n_pop]


def run_nsga2(evaluator, current_genome, positions, shortcut_pool, config,
              usage_stats=None, conjunction_pairs=None, build_dir=None):
    layer_positions = build_layer_to_positions(positions)
    n_pos = len(positions)

    if hasattr(creator, "FitnessMulti"):
        del creator.FitnessMulti
    if hasattr(creator, "Individual"):
        del creator.Individual

    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    def fast_selNSGA2(individuals, k):
        """GPU-accelerated NSGA-II selection using PyTorch for dominance checks."""
        n = len(individuals)
        fits_np = np.array([ind.fitness.values for ind in individuals], dtype=np.float32)

        if HAS_TORCH and torch.cuda.is_available():
            d = "cuda"
            fits_t = torch.tensor(fits_np, device=d)
        else:
            d = None
            fits_t = None

        ranks = np.full(n, -1, dtype=np.int32)
        remaining = np.ones(n, dtype=bool)
        front_rank = 0
        selected_count = 0

        while selected_count < k and remaining.any():
            idxs = np.where(remaining)[0]
            m = len(idxs)

            if d and m > 50:
                # GPU dominance check: f[j] dominates f[i] iff all(f[j]<=f[i]) and any(f[j]<f[i])
                f = fits_t[torch.tensor(idxs, device=d, dtype=torch.long)]
                # Process in chunks to fit VRAM: each chunk checks (chunk, m, 3)
                dominated = torch.zeros(m, device=d, dtype=torch.bool)
                GPU_CHUNK = min(m, 2000)
                for ci in range(0, m, GPU_CHUNK):
                    ce = min(ci + GPU_CHUNK, m)
                    chunk = f[ci:ce]  # (cs, 3)
                    # j dominates i: all(f[j] <= chunk[i]) and any(f[j] < chunk[i])
                    le = (f.unsqueeze(0) <= chunk.unsqueeze(1))  # (cs, m, 3)
                    lt = (f.unsqueeze(0) < chunk.unsqueeze(1))   # (cs, m, 3)
                    dom = le.all(dim=2) & lt.any(dim=2)  # (cs, m)
                    # Zero out self-domination
                    arange = torch.arange(ci, ce, device=d)
                    dom[torch.arange(ce - ci, device=d), arange] = False
                    dominated[ci:ce] = dom.any(dim=1)
                dominated_np = dominated.cpu().numpy()
            else:
                f = fits_np[idxs]
                dominated_np = np.zeros(m, dtype=bool)
                for i in range(m):
                    if dominated_np[i]:
                        continue
                    le = (f[i] <= f).all(axis=1)
                    lt = (f[i] < f).any(axis=1)
                    i_dominates = le & lt
                    i_dominates[i] = False
                    dominated_np |= i_dominates

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

        selected = [individuals[i] for i in range(n) if ranks[i] >= 0]
        return selected

    toolbox = base.Toolbox()
    toolbox.register("evaluate", evaluator.evaluate)
    toolbox.register("select", fast_selNSGA2)

    dynamic_groups = evaluator.dynamic_groups

    def mate(ind1, ind2):
        c1, c2 = pmx_crossover(list(ind1), list(ind2), positions, layer_positions, shortcut_pool, dynamic_groups)
        return creator.Individual(c1), creator.Individual(c2)

    def mutate(ind):
        result = custom_mutate(list(ind), positions, shortcut_pool, layer_positions, dynamic_groups)
        return (creator.Individual(result[0]),)

    toolbox.register("mate", mate)
    toolbox.register("mutate", mutate)

    pop_size = config.get("pop_size", 2000)
    n_gen = config.get("generations", 500)
    cxpb = config.get("crossover_rate", 0.7)
    mutpb = config.get("mutation_rate", 0.15)

    use_gpu_batch = evaluator.device != "cpu" and HAS_TORCH
    print(f"Seeding population: {pop_size} individuals, {n_pos} mutable positions")
    print(f"Device: {evaluator.device} | GPU batch eval: {use_gpu_batch}")
    sys.stdout.flush()
    raw_pop = seed_population(current_genome, pop_size, positions, shortcut_pool, layer_positions, build_dir)
    population = [creator.Individual(ind) for ind in raw_pop]

    def batch_evaluate(pop_list):
        if use_gpu_batch:
            return evaluator.evaluate_batch_gpu([list(ind) for ind in pop_list])
        return [toolbox.evaluate(ind) for ind in pop_list]

    fitnesses = batch_evaluate(population)
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", lambda fits: tuple(min(f[i] for f in fits) for i in range(3)))
    stats.register("avg", lambda fits: tuple(np.mean([f[i] for f in fits]) for i in range(3)))

    logbook = tools.Logbook()
    logbook.header = ["gen", "nevals", "min", "avg"]

    checkpoint_interval = config.get("checkpoint_interval", 25)
    checkpoint_path = os.path.join(build_dir, "evolution_checkpoint.json") if build_dir else None

    # Try to resume from checkpoint
    start_gen = 0
    convergence = []
    best_effort_ever = float('inf')
    plateau_count = 0

    if checkpoint_path and os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                ckpt = json.load(f)
            if (ckpt.get("n_positions") == n_pos and
                ckpt.get("pop_size") == pop_size and
                ckpt.get("config_hash") == _config_hash(config)):
                saved_pop = ckpt["population"]
                population = [creator.Individual(g) for g in saved_pop]
                fitnesses = batch_evaluate(population)
                for ind, fit in zip(population, fitnesses):
                    ind.fitness.values = fit
                start_gen = ckpt.get("generation", 0) + 1
                convergence = ckpt.get("convergence", [])
                best_effort_ever = ckpt.get("best_effort_ever", float('inf'))
                plateau_count = ckpt.get("plateau_count", 0)
                print(f"  RESUMED from checkpoint at gen {start_gen - 1} "
                      f"(best effort {best_effort_ever:.1f})")
                sys.stdout.flush()
            else:
                print("  Checkpoint found but config changed -- starting fresh")
                sys.stdout.flush()
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"  Checkpoint load failed ({e}) -- starting fresh")
            sys.stdout.flush()

    if start_gen == 0:
        fitnesses = batch_evaluate(population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", lambda fits: tuple(min(f[i] for f in fits) for i in range(3)))
    stats.register("avg", lambda fits: tuple(np.mean([f[i] for f in fits]) for i in range(3)))

    logbook = tools.Logbook()
    logbook.header = ["gen", "nevals", "min", "avg"]

    t0 = time.time()

    def save_checkpoint(gen):
        if not checkpoint_path:
            return
        ckpt = {
            "generation": gen,
            "n_positions": n_pos,
            "pop_size": pop_size,
            "config_hash": _config_hash(config),
            "best_effort_ever": best_effort_ever,
            "plateau_count": plateau_count,
            "convergence": convergence,
            "population": [list(ind) for ind in population],
        }
        tmp = checkpoint_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(ckpt, f)
        _safe_replace(tmp, checkpoint_path)

    def save_interim_results(gen):
        """Save current Pareto front as results so progress is never lost."""
        if not build_dir:
            return
        try:
            cur_front = tools.sortNondominated(population, len(population), first_front_only=True)[0]
            cur_front.sort(key=lambda ind: ind.fitness.values[0])
            interim = []
            for i, ind in enumerate(cur_front[:config.get("pareto_front_size", 20)]):
                genome = list(ind)
                interim.append({
                    "id": f"evo_{i}",
                    "fitness": {
                        "effort": round(ind.fitness.values[0], 2),
                        "adjacency": round(-ind.fitness.values[1], 2),
                        "violations": round(ind.fitness.values[2], 2),
                    },
                    "genome": genome,
                    "total_assignments": sum(1 for g in genome if g >= 0),
                })
            interim_path = os.path.join(build_dir, "evolution_results_interim.json")
            tmp = interim_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "generation": gen,
                    "status": "in_progress",
                    "pareto_front": interim,
                    "convergence": convergence,
                }, f, indent=2)
            _safe_replace(tmp, interim_path)
        except Exception as e:
            print(f"  WARNING: interim save failed: {e}")

    try:
        for gen in range(start_gen, n_gen):
            offspring = algorithms.varAnd(population, toolbox, cxpb, mutpb)

            invalid = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = batch_evaluate(invalid)
            for ind, fit in zip(invalid, fitnesses):
                ind.fitness.values = fit

            population = toolbox.select(population + offspring, pop_size)

            record = stats.compile(population)
            logbook.record(gen=gen, nevals=len(invalid), **record)

            # Multi-objective plateau: track best violations (primary target)
            best_eff = min(population, key=lambda ind: ind.fitness.values[0])
            best_viol = min(population, key=lambda ind: ind.fitness.values[2])
            current_best_viol = best_viol.fitness.values[2]

            if current_best_viol < best_effort_ever - 1.0:
                best_effort_ever = current_best_viol
                plateau_count = 0
            else:
                plateau_count += 1

            if gen % checkpoint_interval == 0 or gen == n_gen - 1:
                elapsed = time.time() - t0
                print(f"  Gen {gen:4d}: eff={best_eff.fitness.values[0]:.0f} "
                      f"adj={-best_eff.fitness.values[1]:.0f} "
                      f"viol={best_viol.fitness.values[2]:.0f} "
                      f"({elapsed:.1f}s) plateau={plateau_count}")
                sys.stdout.flush()
                convergence.append({
                    "gen": gen, "elapsed_s": round(elapsed, 1),
                    "best_effort": round(best_eff.fitness.values[0], 2),
                    "best_adjacency": round(-best_eff.fitness.values[1], 2),
                    "best_violations": round(best_viol.fitness.values[2], 2),
                })
                save_checkpoint(gen)
                save_interim_results(gen)

            if plateau_count >= 200:
                print(f"  EARLY STOP: violations plateaued for {plateau_count} gens at gen {gen}")
                sys.stdout.flush()
                break

    except KeyboardInterrupt:
        print(f"\n  INTERRUPTED at gen {gen} -- saving progress...")
        sys.stdout.flush()
        save_checkpoint(gen)
        save_interim_results(gen)
    except Exception as e:
        print(f"\n  ERROR at gen {gen}: {e!r} -- saving progress...")
        sys.stdout.flush()
        save_checkpoint(gen)
        save_interim_results(gen)
        raise

    front = tools.sortNondominated(population, len(population), first_front_only=True)[0]
    front.sort(key=lambda ind: ind.fitness.values[0])
    return front, convergence


def _config_hash(config):
    """Hash the config keys that affect population compatibility."""
    import hashlib
    relevant = {
        "frozen_layers": config.get("frozen_layers"),
        "weights": config.get("weights"),
    }
    return hashlib.md5(json.dumps(relevant, sort_keys=True).encode()).hexdigest()[:12]


def run_qd(evaluator, current_genome, positions, shortcut_pool, config):
    if not QD_AVAILABLE:
        print("pyribs not available, skipping QD. Install with: pip install ribs")
        return None, []

    layer_positions = build_layer_to_positions(positions)
    n_pos = len(positions)

    grid_dims = config.get("qd_grid_dims", [10, 10])
    archive = GridArchive(
        solution_dim=n_pos,
        dims=grid_dims,
        ranges=[(0.0, 1.0), (0.0, 1.0)],
    )

    seed = np.array(current_genome, dtype=np.float64)
    archive.add(seed.reshape(1, -1),
                np.array([-evaluator.evaluate(current_genome)[0]]),
                np.array([evaluator.behavior_descriptors(current_genome)]))

    n_gen = min(config.get("generations", 500), 200)
    print(f"Running QD MAP-Elites: {n_gen} iterations, grid {grid_dims}")

    for gen in range(n_gen):
        if archive.stats.num_elites > 0:
            elite_idx = random.randint(0, archive.stats.num_elites - 1)
            elites = list(archive)
            if elite_idx < len(elites):
                parent = list(elites[elite_idx]["solution"].astype(int))
            else:
                parent = copy.copy(current_genome)
        else:
            parent = copy.copy(current_genome)

        child = custom_mutate(parent, positions, shortcut_pool, layer_positions, evaluator.dynamic_groups)[0]
        child_arr = np.array(child, dtype=np.float64)
        fitness_tuple = evaluator.evaluate(child)
        obj = -fitness_tuple[0]
        bds = evaluator.behavior_descriptors(child)

        archive.add(child_arr.reshape(1, -1), np.array([obj]), np.array([bds]))

        if gen % 50 == 0:
            print(f"  QD gen {gen}: {archive.stats.num_elites} elites, "
                  f"coverage={archive.stats.coverage:.1%}")
            sys.stdout.flush()

    results = []
    for elite in archive:
        genome = list(elite["solution"].astype(int))
        bd = elite["measures"]
        results.append({
            "genome": genome,
            "objective": float(elite["objective"]),
            "behavior": {"app_balance": float(bd[0]), "thumb_utilization": float(bd[1])},
        })

    results.sort(key=lambda r: -r["objective"])
    return results, archive


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_evolution.py <build_dir>")
        sys.exit(1)

    build_dir = sys.argv[1]
    config = load_config()

    if config.get("seed") is not None:
        random.seed(config["seed"])
        np.random.seed(config["seed"])

    print("=" * 60)
    print("CHARYBDIS EVOLUTIONARY LAYOUT OPTIMIZER")
    print("=" * 60)

    canonical, scores, usage_stats, _ = load_build_data(build_dir)
    conjunction_pairs = build_conjunction_pairs_from_scores(scores)

    frozen = set(config.get("frozen_layers", [0, 6, 7, 8]))
    positions = build_position_index(canonical, frozen)
    shortcut_pool = build_shortcut_pool(scores)

    print(f"\nPositions: {len(positions)} mutable ({sum(1 for p in positions if p.is_thumb)} thumb)")
    print(f"Shortcuts: {len(shortcut_pool)} in corpus")
    print(f"Conjunction pairs: {len(conjunction_pairs)}")
    from representation import discover_dynamic_groups
    preview_dg = discover_dynamic_groups(conjunction_pairs, usage_stats, shortcut_pool, threshold=0.3)
    print(f"Dynamic groups discovered: {len(preview_dg)}")

    # Auto-detect GPU
    import torch
    if config.get("use_gpu", True) and torch.cuda.is_available():
        device = "cuda"
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        device = "cpu"
        print("GPU: not available, using CPU")

    print(f"CPU cores: {cpu_count()}")
    sys.stdout.flush()

    current_genome = encode_current_layout(canonical, positions, shortcut_pool, frozen)

    evaluator = FitnessEvaluator(
        positions, shortcut_pool, config,
        usage_stats=usage_stats,
        conjunction_pairs=conjunction_pairs,
        device=device,
        current_genome=current_genome,
    )
    assigned_count = sum(1 for g in current_genome if g >= 0)
    print(f"Current layout: {assigned_count}/{len(current_genome)} positions assigned")

    seed_fitness = evaluator.evaluate(current_genome)
    seed_breakdown = evaluator.evaluate_full(current_genome)
    print(f"Seed fitness: effort={seed_fitness[0]:.1f}, adj={-seed_fitness[1]:.1f}, viol={seed_fitness[2]:.1f}")
    print(f"Breakdown: {json.dumps({k: round(float(v), 2) for k, v in seed_breakdown.items()})}")
    sys.stdout.flush()

    # Run NSGA-II
    print(f"\n--- NSGA-II ({config.get('pop_size', 2000)} pop, {config.get('generations', 500)} gen) ---")
    sys.stdout.flush()
    front, convergence = run_nsga2(evaluator, current_genome, positions, shortcut_pool, config,
                                    usage_stats=usage_stats, conjunction_pairs=conjunction_pairs,
                                    build_dir=build_dir)

    pareto_solutions = []
    for i, ind in enumerate(front[:config.get("pareto_front_size", 20)]):
        genome = list(ind)
        breakdown = evaluator.evaluate_full(genome)
        bd = evaluator.behavior_descriptors(genome)
        changes = decode_genome(genome, positions, shortcut_pool)

        pareto_solutions.append({
            "id": f"evo_{i}",
            "fitness": {
                "effort": round(ind.fitness.values[0], 2),
                "adjacency": round(-ind.fitness.values[1], 2),
                "violations": round(ind.fitness.values[2], 2),
            },
            "behavior": {"app_balance": round(bd[0], 3), "thumb_utilization": round(bd[1], 3)},
            "scoring_breakdown": {k: round(float(v), 2) for k, v in breakdown.items()},
            "total_assignments": sum(1 for g in genome if g >= 0),
            "changes_from_current": sum(1 for i in range(len(genome)) if genome[i] != current_genome[i]),
            "genome": genome,
            "changes": changes[:50],
        })

    # Run QD (optional)
    qd_results = None
    qd_archive_stats = {}
    if QD_AVAILABLE:
        print(f"\n--- Quality-Diversity MAP-Elites ---")
        sys.stdout.flush()
        qd_elites, qd_archive = run_qd(evaluator, current_genome, positions, shortcut_pool, config)
        if qd_elites:
            qd_results = []
            for i, elite in enumerate(qd_elites[:20]):
                genome = elite["genome"]
                changes = decode_genome(genome, positions, shortcut_pool)
                breakdown = evaluator.evaluate_full(genome)
                qd_results.append({
                    "id": f"qd_{i}",
                    "objective": elite["objective"],
                    "behavior": elite["behavior"],
                    "scoring_breakdown": {k: round(float(v), 2) for k, v in breakdown.items()},
                    "total_assignments": sum(1 for g in genome if g >= 0),
                    "genome": genome,
                    "changes": changes[:50],
                })
            if qd_archive:
                qd_archive_stats = {
                    "num_elites": int(qd_archive.stats.num_elites),
                    "coverage": round(float(qd_archive.stats.coverage), 4),
                    "qd_score": round(float(qd_archive.stats.qd_score), 2),
                }

    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": config,
        "device": device,
        "positions_count": len(positions),
        "shortcuts_count": len(shortcut_pool),
        "conjunction_pairs_count": len(conjunction_pairs),
        "seed_fitness": {
            "effort": round(seed_fitness[0], 2),
            "adjacency": round(-seed_fitness[1], 2),
            "violations": round(seed_fitness[2], 2),
        },
        "seed_breakdown": {k: round(float(v), 2) for k, v in seed_breakdown.items()},
        "pareto_front": pareto_solutions,
        "convergence": convergence,
    }

    if qd_results:
        output["qd_archive"] = qd_archive_stats
        output["qd_solutions"] = qd_results

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    out_path = os.path.join(build_dir, "evolution_results.json")
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    _safe_replace(tmp_path, out_path)

    # Clean up checkpoint and interim on successful completion
    for cleanup in ["evolution_checkpoint.json", "evolution_results_interim.json"]:
        p = os.path.join(build_dir, cleanup)
        if os.path.exists(p):
            os.remove(p)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {len(pareto_solutions)} Pareto front solutions")
    if qd_results:
        print(f"QD: {qd_archive_stats.get('num_elites', 0)} elites, "
              f"{qd_archive_stats.get('coverage', 0):.1%} coverage")
    print(f"Written to: {out_path}")
    print("=" * 60)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
