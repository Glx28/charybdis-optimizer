import json, time, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')
from representation import build_position_index, build_shortcut_pool, build_layer_to_positions, encode_current_layout
from fitness import FitnessEvaluator
import numpy as np, random, copy

with open('../build/canonical.json', encoding='utf-8') as f:
    canonical = json.load(f)
with open('../build/app_shortcut_scores.json', encoding='utf-8') as f:
    scores = json.load(f)
config = json.load(open('config.json'))
frozen = {7}
positions = build_position_index(canonical, frozen)
pool = build_shortcut_pool(scores, canonical)

pairs = {}
for app in scores['apps']:
    by_cat = {}
    for s in app['shortcuts']:
        if not s.get('mapped'):
            continue
        cat = s.get('category','general')
        by_cat.setdefault(cat,[]).append(s)
    for cat, shortcuts in by_cat.items():
        for i in range(len(shortcuts)):
            for j in range(i+1,len(shortcuts)):
                w = min(shortcuts[i]['importance'], shortcuts[j]['importance']) * 0.3
                key = '|'.join(sorted([shortcuts[i]['keys'], shortcuts[j]['keys']]))
                pairs[key] = pairs.get(key,0) + w

import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Device: {device}')
print(f'GPU: {torch.cuda.get_device_name(0)}')

eval_gpu = FitnessEvaluator(positions, pool, config, conjunction_pairs=pairs, device=device)
eval_cpu = FitnessEvaluator(positions, pool, config, conjunction_pairs=pairs, device='cpu')

genome = encode_current_layout(canonical, positions, pool)
layer_positions = build_layer_to_positions(positions)
from operators import swap_within_layer

# Generate test population
genomes = []
for _ in range(5000):
    g = copy.copy(genome)
    for _ in range(random.randint(5,20)):
        g = swap_within_layer(g, positions, layer_positions)
    genomes.append(g)

# CPU single-threaded
t0 = time.time()
for g in genomes[:500]:
    eval_cpu.evaluate(g)
cpu_time = time.time() - t0
cpu_rate = 500 / cpu_time
print(f'CPU sequential: 500 evals in {cpu_time:.2f}s = {cpu_rate:.0f} evals/s')

# GPU batch - 3000
t0 = time.time()
results_3k = eval_gpu.evaluate_batch_gpu(genomes[:3000])
gpu_3k_time = time.time() - t0
print(f'GPU batch 3000: {gpu_3k_time:.2f}s = {3000/gpu_3k_time:.0f} evals/s')

# GPU batch - 5000
t0 = time.time()
results_5k = eval_gpu.evaluate_batch_gpu(genomes[:5000])
gpu_5k_time = time.time() - t0
print(f'GPU batch 5000: {gpu_5k_time:.2f}s = {5000/gpu_5k_time:.0f} evals/s')

# Speedup
print(f'\nSpeedup vs CPU: {(500/cpu_time * gpu_3k_time / 3000):.1f}x slower or {(3000/gpu_3k_time) / cpu_rate:.1f}x faster')

# Verify accuracy
cpu_r = eval_cpu.evaluate(genomes[0])
gpu_r = results_5k[0]
print(f'\nCPU[0]: effort={cpu_r[0]:.1f} adj={cpu_r[1]:.1f} viol={cpu_r[2]:.1f}')
print(f'GPU[0]: effort={gpu_r[0]:.1f} adj={gpu_r[1]:.1f} viol={gpu_r[2]:.1f}')

# Estimate run times
print(f'\n--- Estimated run times ---')
for pop, gen in [(3000, 300), (5000, 500), (5000, 2000)]:
    gpu_gen_time = (pop / (5000 / gpu_5k_time))
    total = gpu_gen_time * gen
    print(f'pop={pop} gen={gen}: {gpu_gen_time:.1f}s/gen, total={total/60:.1f} min')
    cpu_gen_time = pop / cpu_rate
    cpu_total = cpu_gen_time * gen
    print(f'  (CPU would be: {cpu_gen_time:.1f}s/gen, total={cpu_total/60:.1f} min)')
