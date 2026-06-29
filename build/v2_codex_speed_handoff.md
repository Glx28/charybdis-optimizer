# CODEX HANDOFF: GPU & SPEED OPTIMIZATION

## Current Status

A run is executing. The surrogate is on GPU (GTX 1070, CUDA 12.1). Each generation takes ~3-5s with pop=1000. The goal is to get this to **under 1 second per generation** by any means necessary: more GPU, more CPU cores, more RAM, more VRAM, batching, parallelization, JIT compilation, tensorization, etc.

## Current Bottlenecks (Inferred)

Based on the architecture, the time per generation is spent in:

1. **Exact eval batch** (every 50 gens): 20 individuals × 8 factors × ~70ms = ~11s every 50 gens = ~0.22s amortized per gen
2. **Surrogate predict**: 1000 individuals × 0.023ms = ~23ms per gen (GPU)
3. **pymoo overhead**: selection, crossover, mutation, repair = ~1-2s per gen
4. **Callback overhead**: exact eval check, retrain check, checkpoint = negligible
5. **FitnessEvaluator.evaluate()**: When called for exact eval, it's 8 factors on CPU, each doing loops over 616 positions

The **biggest remaining bottleneck** is the **exact fitness evaluation** and **pymoo's CPU-side operations**. The surrogate is already fast (23ms). The problem is that exact eval still evaluates one layout at a time, and pymoo's genetic operators are all in Python/numpy on CPU.

## Optimization Targets

### 1. GPU Batch Exact Fitness Evaluation (HIGHEST IMPACT)

**Current**: `evaluate_exact_batch()` evaluates layouts one-by-one in a Python loop. Each layout calls `FitnessEvaluator.evaluate()` which computes 8 factors, each factor looping over 616 positions. This is pure Python/NumPy on CPU.

**Target**: Evaluate **all 20 (or all 1000) layouts simultaneously on GPU** using batched tensor operations.

**How**:

Create a `GPUBatchEvaluator` class that:
- Takes a batch of genomes (shape: [batch, 616]) as a torch tensor on GPU
- Computes all 8 factors in parallel using PyTorch operations
- Returns [batch, 3] objective scores on GPU

**Key insight**: Most fitness factors can be expressed as tensor operations:

- **Effort**: For each position, `effort = position.effort * shortcut.importance`. Sum across positions. This is just `torch.sum(effort_map[genome] * importance_map[genome])` with masking for unassigned positions.
- **Adjacency**: Pre-compute pairwise distance matrix `D[pos_a, pos_b] = dist`. For each layout, `score = sum over assigned pairs of D[genome == sid_a, genome == sid_b]`. This can be batched by creating a mask tensor `M[batch, n_positions]` where M[b, i] = 1 if assigned.
- **Finger balance**: Count assigned shortcuts per hand/finger. Batched histogram.
- **Same finger**: Same as finger balance but penalize.
- **Violations**: Duplicate detection can be done via `torch.unique(genome, dim=1, return_counts=True)` across the batch.
- **Group split**: Check which positions each group member is on, count unique layers.
- **Thumb occupancy**: Layer lookup per position.
- **Workflow coherence**: Chain lookup from pre-built adjacency matrix.
- **Learning curve**: `torch.sum(genome != reference_genome)`.
- **App coherence**: Per-layout histogram of apps per layer.

**Implementation plan**:

```python
# In a new file: fitness/gpu_evaluator.py
import torch
import torch.nn.functional as F

class GPUBatchEvaluator:
    def __init__(self, layout, weights, device='cuda'):
        self.device = device
        self.n_positions = layout.n_positions
        self.n_shortcuts = layout.n_shortcuts
        
        # Pre-compute constant tensors on GPU
        # position_effort: [n_positions] -> effort per position
        # position_layer: [n_positions] -> layer per position  
        # position_hand: [n_positions] -> hand per position (0=left, 1=right)
        # position_finger: [n_positions] -> finger per position
        # position_coords: [n_positions, 2] -> (x, y)
        # shortcut_importance: [n_shortcuts]
        # shortcut_app: [n_shortcuts] -> app index
        # shortcut_keys: [n_shortcuts] -> string keys
        # frozen_mask: [n_positions] -> bool
        # reference_genome: [n_positions]
        # ... etc
        
        # Pre-compute distance matrix: [n_positions, n_positions]
        coords = torch.tensor([(p.x, p.y) for p in layout.positions], device=device)
        self.dist_matrix = torch.cdist(coords, coords)
        
        # Pre-compute adjacency for sequences: {seq_key -> (sid_a, sid_b, count, weight)}
        # Build a sparse tensor or lookup table
        
    def evaluate(self, genomes: torch.Tensor) -> torch.Tensor:
        """
        genomes: [batch, n_positions], values in [-1, n_shortcuts-1]
        Returns: [batch, 3] objectives
        """
        batch = genomes.shape[0]
        assigned_mask = genomes >= 0  # [batch, n_positions]
        
        # --- Effort ---
        effort = torch.zeros(batch, device=self.device)
        for b in range(batch):
            sids = genomes[b][assigned_mask[b]]
            if len(sids) > 0:
                pos_idx = torch.where(assigned_mask[b])[0]
                effort[b] = torch.sum(self.position_effort[pos_idx] * self.shortcut_importance[sids])
        
        # ... etc for all factors
        
        objectives = torch.stack([effort, adjacency, violations], dim=1)
        return objectives
```

**This is a major rewrite.** The point is: batch the entire fitness computation on GPU so exact eval of 20 layouts takes <100ms instead of 11s.

**Alternative approach** (easier): Write a Numba JIT-compiled version that evaluates multiple layouts in parallel using `prange`. This keeps the code structure but compiles it to machine code with OpenMP parallel loops.

```python
from numba import njit, prange
import numpy as np

@njit(parallel=True, fastmath=True)
def batch_evaluate_effort(genomes, position_effort, shortcut_importance, n_positions, n_shortcuts):
    batch = genomes.shape[0]
    scores = np.zeros(batch, dtype=np.float32)
    for b in prange(batch):
        for i in range(n_positions):
            sid = genomes[b, i]
            if sid >= 0:
                scores[b] += position_effort[i] * shortcut_importance[sid]
    return scores
```

Numba with `parallel=True` and `prange` will use all CPU cores. This alone might cut exact eval time by 4-8x.

**Recommendation**: Try Numba first (low effort, high impact). If that's not enough, do the full PyTorch GPU batch evaluator.

### 2. Reduce Surrogate Model Size (Medium Impact)

**Current**: hidden_dim=256, 10.2M parameters, embedding 64-dim.

**Target**: hidden_dim=128, 32-dim embedding. Cut parameters by ~4x. Less VRAM usage, faster training, faster inference.

**File**: `evolution/surrogate.py` line 12
```python
def __init__(self, n_positions: int, n_shortcuts: int, n_factors: int = 3, hidden_dim: int = 128):
    self.embedding = nn.Embedding(n_shortcuts + 1, 32)
```

**Also**: Use `torch.compile(surrogate)` after initialization. PyTorch 2.5.1 supports `torch.compile` which can give 2-5x speedup for MLPs.

```python
surrogate = LayoutSurrogate(...)
if torch.cuda.is_available():
    surrogate = torch.compile(surrogate)
```

### 3. Optimize DataLoader (Small Impact)

**Current**: `DataLoader(dataset, batch_size=min(batch_size, len(X)), shuffle=True)` with no `num_workers` or `pin_memory`.

**Target**: Add `num_workers=4`, `pin_memory=True`, `persistent_workers=True`.

```python
loader = DataLoader(
    dataset, 
    batch_size=256, 
    shuffle=True, 
    num_workers=4, 
    pin_memory=True,
    persistent_workers=True,
)
```

This keeps the data loading pipeline fed while GPU is training. With small batches (256) and 1000 samples, this might not matter much, but for larger runs it will.

### 4. Pre-allocate GPU Buffers (Small Impact)

**Current**: `predict()` creates a new torch tensor every call.

**Target**: Pre-allocate a reusable GPU buffer and copy data into it.

```python
class SurrogateTrainer:
    def __init__(self, ...):
        ...
        self._predict_buffer = None
    
    def predict(self, layouts: np.ndarray) -> np.ndarray:
        self.surrogate.eval()
        n = layouts.shape[0]
        if self._predict_buffer is None or self._predict_buffer.shape[0] < n:
            self._predict_buffer = torch.empty((n, self.surrogate.n_positions), dtype=torch.long, device=self.device)
        with torch.no_grad():
            self._predict_buffer[:n].copy_(torch.from_numpy(layouts + 1))
            pred = self.surrogate(self._predict_buffer[:n]).cpu().numpy()
        return pred * self.std + self.mean
```

This avoids GPU memory allocation overhead every predict call. With 1000 gens × 1000 pop = 1M predictions, this could save significant time.

### 5. Reduce pymoo Overhead (Medium Impact)

**Current**: pymoo's NSGA2 does selection, crossover, mutation, repair on CPU with numpy.

**Target**: Use `pymoo`'s `n_threads` or `n_processes` options for parallel evaluation. Or switch to `pymoo.algorithms.moo.nsga3` if NSGA2 is too slow.

**Better**: Write custom `Crossover` and `Mutation` that operate on torch tensors directly on GPU. This avoids CPU-GPU transfer every generation.

Actually, the bigger issue: pymoo passes the entire population (1000 × 616) to the surrogate every generation. The surrogate is already on GPU, so this transfer is fast. But the genetic operators (crossover, mutation, repair) are pure Python.

**Recommendation**: Use `n_threads=mp.cpu_count()` in `minimize()` or configure the problem for parallel evaluation.

```python
res = minimize(
    problem, 
    algorithm, 
    ("n_gen", n_gen), 
    seed=seed, 
    verbose=True, 
    callback=callback,
    # pymoo doesn't have n_threads directly, but:
    # Some algorithms support parallel evaluation
)
```

### 6. Reduce Initial Exact Eval Samples (Already Done)

Reduced from 5000 to 1000. This was the right call. But can we go lower? 500 samples might be enough for a decent surrogate. The trade-off is R² accuracy.

**Test**: Try 500 samples. If R² > 0.90, keep 500. If R² < 0.85, go back to 1000.

### 7. Disable Exact Eval During Evolution (High Impact, Risky)

**Current**: Exact eval every 50 gens (20 individuals). This takes ~11s every 50 gens = 0.22s amortized per gen.

**Target**: Reduce to every 100 gens or 200 gens. Or only do exact eval of the best individual (not 20 random ones).

**File**: `config/__init__.py` or `run_evolution.py`
```python
exact_eval_every=100  # instead of 50
exact_eval_batch=5    # instead of 20
```

**Risk**: Surrogate might drift more. But with GPU training being fast, retrain every 200 gens is still good.

### 8. JIT Compile the Surrogate Model (Medium Impact)

```python
surrogate = LayoutSurrogate(...)
if hasattr(torch, 'compile'):
    surrogate = torch.compile(surrogate, mode='max-autotune')
```

`max-autotune` mode will spend more time at compile but give fastest inference. For a 10M parameter model, this could be 2-5x faster.

### 9. Use Mixed Precision Training (Medium Impact)

**Current**: Training uses float32 everywhere.

**Target**: Use `torch.cuda.amp.autocast()` for training and inference. GTX 1070 has Tensor Cores that support FP16. This can give 2x speedup for training and inference.

```python
from torch.cuda.amp import autocast

def predict(self, layouts):
    self.surrogate.eval()
    with torch.no_grad(), autocast():
        X = torch.tensor(layouts + 1, dtype=torch.long, device=self.device)
        pred = self.surrogate(X).cpu().float().numpy()
    return pred * self.std + self.mean

def train(self, ...):
    ...
    for epoch in range(epochs):
        for batch_x, batch_y in loader:
            with autocast():
                pred = self.surrogate(batch_x)
                loss = F.mse_loss(pred, batch_y)
            loss.backward()
            optimizer.step()
```

### 10. Streamline Callback (Small Impact)

**Current**: Checkpoint every 100 gens with JSON serialization of the full Pareto front (1000 individuals × 616 positions = 616K integers). This is large.

**Target**: Only checkpoint the best individual, not the full Pareto front. Or checkpoint every 500 gens instead of 100.

```python
checkpoint_every=500  # instead of 100
```

### 11. Use Shared Memory for Parallel Exact Eval (Medium Impact)

**Current**: `evaluate_exact_batch()` uses `multiprocessing.Pool` with `imap_unordered`. Each worker unpickles the full layout and evaluator.

**Target**: Use `torch.multiprocessing` with shared memory. The layout data (positions, shortcuts) is read-only and can be shared across workers via `torch.Tensor` shared memory.

```python
import torch.multiprocessing as mp
mp.set_start_method('spawn', force=True)

# Pre-load layout into shared memory
shared_positions = torch.from_numpy(...).share_memory_()
shared_shortcuts = torch.from_numpy(...).share_memory_()
```

This avoids pickling/unpickling overhead per worker.

### 12. Optimize Surrogate Architecture (Medium Impact)

**Current**: 3-layer MLP: Linear(616*64, 256) -> ReLU -> Linear(256, 256) -> ReLU -> Linear(256, 128) -> ReLU -> Linear(128, 3)

**Target**: Wider and shallower, or use a single large matrix multiply:
- Linear(616*64, 512) -> ReLU -> Linear(512, 3)

This reduces sequential operations and memory bandwidth.

### 13. Reduce Genome Size (Structural Change)

**Current**: 616 positions, 295 shortcuts. The genome is 616 integers.

**Target**: Only encode mutable positions (512). The frozen positions (104) are constant and don't need to be in the genome. This reduces the state space from 616 to 512.

**File**: `core/__init__.py` — `Layout.genome` could be only mutable positions. But this is a deep change.

**Easier**: The surrogate input is 616 positions, but we could mask the frozen positions to reduce the effective input size:
```python
self.encoder = nn.Linear(len(mutable_positions) * 64, hidden_dim)
```

This only helps if the encoder is the bottleneck. With 616*64=39424 input dim, the first Linear is 39424×256 = 10M parameters. Reducing to 512×64=32768 input dim would be 32768×256 = 8.4M. Not a huge savings.

### 14. Use GPU for All PyTorch Operations (Critical)

**Current**: The surrogate `predict()` is on GPU. But `SurrogateTrainer.train()` might have CPU-GPU transfer overhead. Also, the `FastLayoutProblem._evaluate()` does:
```python
F = self.manager.trainer.predict(x)
```
where `x` is a numpy array. This converts numpy → torch → GPU every time.

**Target**: Keep the population as a torch tensor on GPU throughout the evolution. Modify `FastLayoutProblem._evaluate()` to accept torch tensors directly.

Actually, pymoo passes numpy arrays. We can't easily change that. But we can avoid the numpy allocation in `predict()` by using `torch.from_numpy()` which is a zero-copy view (for contiguous arrays). But the `+ 1` operation forces a copy anyway.

**Alternative**: Use `torch.as_tensor(x + 1, dtype=torch.long, device=device)` which might be faster.

### 15. Reduce Surrogate Epochs (Done)

Already reduced from 100 to 50. But maybe 30 is enough if R² stays high.

```python
surrogate_epochs=30  # test and see if R² >= 0.95
```

### 16. Use ProcessPool with max_workers (Done)

`evaluate_exact_batch` already has multiprocessing. But `n_workers = mp.cpu_count() - 1` might be too many for a GPU machine (GPU tasks + CPU tasks competing). Use `max(4, mp.cpu_count() - 2)` to leave 2 cores for GPU driver and system.

### 17. Pre-compute Shortcut-Position Effort Matrix (Medium Impact)

**Current**: `EffortFactor.compute()` loops over all positions and looks up `position.effort * shortcut.importance`.

**Target**: Pre-compute a matrix `effort_matrix[pos, sid] = positions[pos].effort * shortcuts[sid].importance` on GPU. Then `effort = torch.sum(effort_matrix[assigned_positions, assigned_sids])`.

But with 616 positions × 295 shortcuts = 181K entries, this is tiny. The main cost is the Python loop, not the memory lookup.

**Better**: Pre-compute per-position effort and per-shortcut importance, then the effort is just a dot product of selected entries.

### 18. Use GPU for Adjacency Factor (High Impact)

**Current**: Adjacency loops over all pairs of assigned shortcuts, computes distance, and accumulates. O(n²) per layout.

**Target**: Pre-compute distance matrix on GPU. For a batch of layouts, create adjacency masks and compute using matrix multiplication.

This is complex but possible. See the `GPUBatchEvaluator` idea above.

### 19. Remove Non-Essential Factors During Evolution (High Impact)

**Current**: All 8 factors are computed for every exact evaluation.

**Target**: During evolution (surrogate phase), the surrogate predicts 3 objectives. The exact eval is only for validation. But for the final evaluation of the best layout, all 8 factors are needed. During the exact eval batch (every 50 gens), maybe only compute the 3 objectives, not all 8 factor scores.

Actually, the objectives are already computed from the factors. So we can't skip factors without changing the objectives.

**Alternative**: For the exact eval batch, only compute the 3 objectives in a simplified way. But the objectives ARE the weighted sum of factors. So we need the factors.

**Better idea**: Cache factor computations across exact evals. If a position hasn't changed between two layouts in the batch, don't recompute its contribution. But with 20 random layouts, this is unlikely to help much.

### 20. Profile First, Optimize Second (CRITICAL)

Before doing any of the above, **profile the actual code** to find the real bottleneck.

```bash
cd charybdis-optimizer-v2
uv run python -m cProfile -o profile.stats -c "
from run_evolution import main
import sys
sys.argv = ['run_evolution.py', '../build']
main()
"
```

Or use `py-spy` or `scalene` for line-by-line profiling:
```bash
uv pip install py-spy
py-spy record -o profile.svg -- uv run python run_evolution.py ../build
```

This will show exactly where time is spent. Don't guess — measure.

## Recommended Priority Order

1. **Profile the actual run** (5 min) — Find the real bottleneck before optimizing.
2. **Numba JIT the exact eval** (30 min) — `njit(parallel=True)` for `evaluate_exact_batch`. This alone could cut exact eval time by 4-8x.
3. **torch.compile the surrogate** (5 min) — Add `surrogate = torch.compile(surrogate, mode='max-autotune')`.
4. **Reduce surrogate epochs to 30** (1 min) — Test if R² stays > 0.95.
5. **Mixed precision (FP16)** (10 min) — Add `autocast()` to training and inference.
6. **Pre-allocate GPU buffers** (10 min) — Reuse predict tensor instead of allocating every call.
7. **Reduce checkpoint frequency to 500** (1 min) — Less I/O overhead.
8. **Reduce exact eval batch to 5** (1 min) — Less exact eval overhead.
9. **Full GPU batch evaluator** (2+ hours) — Only if above isn't enough. Major rewrite.
10. **Reduce pop_size to 500** (1 min) — If all else fails, half the population halves the time.

## Quick Wins to Apply Immediately

Apply these before the next run starts:

### A. torch.compile the surrogate
```python
# In run_evolution.py, after creating surrogate:
surrogate = LayoutSurrogate(...)
if hasattr(torch, 'compile'):
    try:
        surrogate = torch.compile(surrogate, mode='max-autotune')
        print("  Surrogate compiled with torch.compile")
    except Exception as e:
        print(f"  torch.compile failed: {e}")
```

### B. Reduce surrogate epochs to 30
```python
# In config/__init__.py
"surrogate_epochs": 30,  # instead of 100
```

### C. Reduce checkpoint frequency to 500
```python
# In run_evolution.py
checkpoint_every=500,  # instead of 100
```

### D. Reduce exact eval batch to 5
```python
# In run_evolution.py
callback = SurrogateCallback(..., exact_eval_batch=5)  # instead of 20
```

### E. Pre-allocate GPU buffer in SurrogateTrainer
```python
# In evolution/surrogate.py predict()
self._predict_buffer = None
# ... in predict():
if self._predict_buffer is None or self._predict_buffer.shape[0] < n:
    self._predict_buffer = torch.empty((n, self.surrogate.n_positions), dtype=torch.long, device=self.device)
self._predict_buffer[:n].copy_(torch.from_numpy(layouts + 1))
pred = self.surrogate(self._predict_buffer[:n]).cpu().numpy()
```

### F. Use autocast for mixed precision
```python
# In predict() and train()
with torch.no_grad(), torch.cuda.amp.autocast():
    ...
```

## Files to Modify

- `charybdis-optimizer-v2/evolution/surrogate.py` — torch.compile, pre-allocated buffers, autocast, GPU device auto-detect
- `charybdis-optimizer-v2/config/__init__.py` — surrogate_epochs=30, n_initial_samples=500
- `charybdis-optimizer-v2/run_evolution.py` — checkpoint_every=500, exact_eval_batch=5, torch.compile
- `charybdis-optimizer-v2/fitness/evaluator.py` — Numba JIT batch evaluation (optional but high impact)

## Success Criteria

- Next run startup: < 60s (surrogate training + initial eval)
- Per generation: < 2s with pop=1000
- 1000 generations: < 35 minutes
- Surrogate R²: > 0.95
- Exact eval batch (5 individuals): < 2s

## Bottom Line

The surrogate is already GPU-fast (23ms per 1000). The bottleneck is either the exact eval batch (every 50 gens) or pymoo's CPU operators. Apply the quick wins first (torch.compile, fewer epochs, less exact eval, pre-allocated buffers). If still too slow, profile and then Numba JIT the exact eval. If STILL too slow, do the full GPU batch evaluator.

**Don't waste time on complex rewrites until the quick wins are applied and measured.**
