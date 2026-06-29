# CHARYBDIS V2 — CODEX HANDOFF: CHECK & IMPROVE

**Status**: A run is currently executing (or about to start) with the manager agent. The code has been fixed for critical bugs but several issues remain for you to verify and improve.

---

## What Was Just Fixed (Check These Worked)

### 1. Objective Normalization
**File**: `fitness/evaluator.py`, `run_evolution.py`  
**What**: `FitnessEvaluator` now divides each objective by its standard deviation from 5000 random training layouts. This makes effort, adjacency, and violations all have similar scale (~0.5-2.0) so NSGA2 gives equal selection pressure.  
**What to verify**: The scale factors printed at startup should be: effort≈2000, adj≈100000, viol≈10000000. If they're wildly different, the normalization is wrong.  
**What to verify**: The surrogate is now trained on normalized scores (not raw). After retraining, R² should still be > 0.90.

### 2. Frozen Position Preservation
**File**: `evolution/__init__.py`  
**What**: `PermutationSampling`, `CycleCrossover`, and `LayoutRepair` now all preserve frozen positions from the seed genome.  
**What to verify**: After any generation, check that `layout.genome[layout.frozen_mask]` matches the seed values. Run:
```python
from core.loader import build_layout
layout = build_layout('../build')
# Check frozen positions are unchanged from seed
```

### 3. Unbuffered Output
**File**: `run_evolution.py`  
**What**: `sys.stdout.reconfigure(line_buffering=True)` and all `print()` calls now use `flush=True`.  
**What to verify**: The manager should see output in real-time, not empty files.

### 4. Periodic Checkpointing
**File**: `run_evolution.py`  
**What**: `SurrogateCallback` saves `build/v2_checkpoint_gen100.json`, `gen200.json`, etc. every 100 generations.  
**What to verify**: Checkpoints exist and contain valid `best_exact.genome` arrays.

### 5. Bad Config Deleted
**File**: `build/config_v2.yaml` was deleted.  
**What to verify**: The run uses built-in defaults: pop=1000, gens=10000, n_initial=5000.

---

## Critical Issues to Fix or Verify

### 🚨 CRITICAL: Seed Genome Not Injected into Initial Population
**File**: `run_evolution.py` line 231-236  
**Problem**: The seed genome injection is just a `pass` comment. The operators preserve frozen positions, but the initial population is entirely random. The seed (which has 303 good assignments) is not included in generation 0.  
**Fix**: After `algorithm` is created and `minimize` starts, pymoo samples the initial population. You need to inject the seed genome as one individual in the initial population. One way:
```python
# After algorithm setup, before minimize:
if layout.n_assigned > 0:
    # Replace first individual with seed genome
    algorithm.pop = None  # force re-sampling
    # Or use algorithm.setup() then modify algorithm.pop
```
Alternatively, use pymoo's `sampling` parameter to pass the seed as part of the initial population. Or modify the `PermutationSampling._do` to always include the seed genome as the first sample.

**Impact**: Without this, generation 0 starts with random layouts (violations ~50M) instead of the seed (violations ~11M). Evolution wastes 100+ generations just getting back to the seed quality.

### 🚨 CRITICAL: TrackballProximityFactor Does Nothing
**File**: `fitness/factors/trackball_proximity.py`  
**Problem**: The factor searches for `mouse` or `click` in `shortcut.action.lower()`. But there are **0 shortcuts** in the corpus with these words in their action names.  
**Verify**:
```python
from core.loader import load_shortcuts
shortcuts = load_shortcuts('../build/app_shortcut_scores.json')
mouse = [s for s in shortcuts if 'mouse' in s.action.lower() or 'click' in s.action.lower()]
print(len(mouse))  # Currently 0
```
**Fix**: The shortcut corpus needs mouse-related shortcuts (MB1, MB2, MB3, etc.) OR the factor should use a different detection method. Check `shortcut.category` or `shortcut.keys` for mouse button names ("MB1", "MB2", etc.). Or check if the action name contains "wheel", "scroll", "trackball".

**Alternative**: Remove this factor entirely if the corpus doesn't have mouse shortcuts. It's dead weight.

### 🚨 CRITICAL: AppCoherenceFactor Uses Wrong App Names
**File**: `fitness/factors/app_coherence.py`  
**Problem**: `sc.app` is the app name from the corpus (e.g., "Browser (Chrome/Edge)"). But the usage log uses exe names (e.g., "msedge.exe"). The `AppCoherenceFactor` groups by `sc.app`, which is correct for the corpus, but some shortcuts might not have the right app assignment.  
**Verify**: Check if shortcuts used together in the usage log are actually assigned to the same app in the corpus.

More importantly: The `AppCoherenceFactor` rewards same-app shortcuts being on the same layer. But it doesn't account for **multi-app shortcuts** — shortcuts that appear in multiple apps. The v1 had special handling for shortcuts used by 3+ apps. The v2 doesn't.

**Fix**: Consider weighting app coherence by `app_demand` (how much the shortcut is used across apps). Or add a multi-app shortcut bonus.

### 🚨 CRITICAL: 104 Blind Spots Detected
**File**: `fitness/factors/workflow_coherence.py` (blind_spots penalty)  
**Problem**: There are 104 high-importance shortcuts the user never uses despite spending time in those apps. This suggests either:
1. The shortcuts are genuinely not useful (over-importance in corpus)
2. The user uses them but they're not captured by the logger
3. The shortcuts are ZMK-specific or require specific layer states not captured

**Verify**: Look at `build/usage_stats.json` → `blind_spots`. Top entries:
- Browser: Ctrl+Tab, Alt+Left, Ctrl+L, Ctrl+Shift+L, Ctrl+Shift+T
- VS Code: Ctrl+Shift+P, Ctrl+Shift+F, Ctrl+`, F12
- Teams: Ctrl+E, Ctrl+Shift+O, Ctrl+Shift+U

These are VERY common shortcuts. If they're truly not used, the optimizer should down-weight their importance. If the logger is missing them, fix the logger.

**Fix**: Add a `usage_informed_importance` that reduces importance of shortcuts not seen in the usage log. Or make the blind_spots penalty scale with actual observed behavior rather than corpus importance.

### 🚨 CRITICAL: LearningCurveFactor May Be Too Strong
**File**: `fitness/factors/learning_curve.py`  
**Problem**: The factor penalizes ANY change from the reference layout. A swap of two high-importance shortcuts costs: `1 + imp*0.5 + imp²*0.01`. For importance=10, that's `1 + 5 + 1 = 7` per swap. With weight=0.5, that's 3.5 per swap. For 100 swaps, that's 350. This is small compared to violations (millions), but after normalization it might be significant.

**Verify**: Check if the learning curve penalty is preventing evolution from making necessary changes. If the best evolved layout has learning_curve > 1000, it's too constrained.

**Fix**: Make the learning curve penalty adaptive — start strong and decay over generations, or weight it inversely by the observed improvement in other objectives.

---

## Medium Issues to Fix or Verify

### ⚠️ Surrogate Accuracy on Evolved Genomes
**File**: `evolution/surrogate.py`  
**Problem**: The surrogate is trained on random layouts. Evolved genomes may be structurally different (more clustered, better organized). The surrogate might have lower R² on evolved genomes than on random ones.  
**Verify**: After each exact eval (every 50 gens), compute the correlation between surrogate predictions and exact scores for those 20 individuals. Log this separately from the overall R². If it drops below 0.70, the surrogate is misleading the optimizer.

**Fix**: If evolved-genome accuracy is low, increase `hidden_dim` or add a validation set of evolved genomes.

### ⚠️ Checkpoint Files Not Cleaned Up
**File**: `run_evolution.py`  
**Problem**: After 10000 generations with checkpoint_every=100, there will be 100 JSON files (~10MB each = 1GB). This wastes disk space.  
**Fix**: Keep only the last 5 checkpoints. After saving a new checkpoint, delete checkpoints older than 500 generations.

### ⚠️ n_initial_samples=5000 is Slow
**File**: `config/__init__.py`  
**Problem**: 5000 exact evaluations at ~100ms each = 8+ minutes of startup time. For quick iterations, this is too slow.  
**Fix**: Reduce to 2000 for faster startup. Or make it configurable per run type (quick vs. production).

### ⚠️ WorkflowCoherenceFactor Uses String Matching
**File**: `fitness/factors/workflow_coherence.py`  
**Problem**: The factor looks up `keys_to_info[sc.keys]` for each chain/workflow step. But the usage data keys (e.g., "Alt+Tab") and the shortcut keys might not match exactly if normalization differs.  
**Verify**: Check that `keys_to_info` actually contains keys matching the chain keys. If many chains have "None" layers, the factor is not working.

**Fix**: Add a normalized-key lookup that handles case differences and modifier ordering.

### ⚠️ SameFingerFactor is a Penalty, Not an Objective
**File**: `fitness/evaluator.py`  
**Problem**: `same_finger` is added to the `violations` objective with weight 2.0. But it's conceptually a comfort/efficiency factor, not a violation. It might be better as a separate objective or part of the `effort` objective.  
**Fix**: Consider adding it to `effort` instead of `violations`, or making it a separate objective (4-objective MOO).

### ⚠️ FingerBalanceFactor is Almost Zero
**File**: `fitness/factors/finger_balance.py`  
**Problem**: The factor computes `abs(left - right) / (left + right + 1e-6)`. With the seed, this is 0.66. After normalization, it becomes `0.66 * 0.8 / 10000 ≈ 0.00005`. This is tiny compared to effort and violations.  
**Verify**: Check if the finger balance actually matters in the Pareto front. If all solutions have similar finger_balance, it's not useful.

**Fix**: Increase the finger_balance weight or make it a standalone constraint rather than part of violations.

### ⚠️ AppCoherenceFactor Doesn't Use Usage Data
**File**: `fitness/factors/app_coherence.py`  
**Problem**: The factor groups shortcuts by `sc.app` (from corpus). It doesn't use `usage_data.by_app` to weight by actual usage. An app with 1000 shortcuts but 0 usage time gets the same coherence reward as an app with 10 shortcuts and 10 hours of usage.  
**Fix**: Weight coherence by `app_time_seconds` from usage data. Apps the user spends more time in should get stronger coherence rewards.

### ⚠️ Group Split Penalty is 3279 at Seed, Should Decrease
**File**: `fitness/factors/violation.py`  
**Problem**: The seed scatters static groups across layers. `group_split=3279` is the dominant sub-violation. After 1000 generations, this should be < 1000. If it's not decreasing, the group preservation is not working.  
**Verify**: Check `group_split` in checkpoint files over time. If it stays > 3000, the penalty is too weak or the operators are not exploring group clustering.

**Fix**: Increase `group_split` weight in `ViolationFactor.sub_weights`, or add a dedicated group repair operator that moves group members to the same layer.

---

## Nice-to-Have Improvements

### 1. Better Surrogate Architecture
The current surrogate is a 3-layer MLP with 64-dim embedding. Consider:
- Adding layer-aware attention (shortcuts on same layer should interact)
- Using transformer instead of MLP for permutation modeling
- Adding positional encoding based on physical (x,y) coordinates

### 2. GPU Support for Exact Eval
Currently exact eval is CPU-only. With 1000 pop and 8 factors, each generation's exact eval would be 1000 * 8ms = 8s, which is fine. But GPU batch eval could be faster for larger populations.

### 3. Hyperparameter Auto-Tuning
The weights (effort=1.0, adjacency=1.5, violations=50.0, etc.) are hand-tuned. Consider using CMA-ES or another optimizer to tune the weights based on Pareto front diversity.

### 4. Visualize Pareto Front
After the run, plot the 3D Pareto front (effort vs adjacency vs violations) to understand trade-offs. This helps identify which objectives are in conflict.

### 5. Add Diversity Metric
Track `n_nds` (already in pymoo output) and add a `crowding_distance` or `hypervolume` metric to the checkpoint files. This helps detect when the Pareto front is collapsing.

### 6. Layer-Specific Effort Maps
Currently effort is computed per-position based on (x,y) distance from home row. But different layers have different "home positions" (e.g., L2 mouse layer has home on thumb cluster). Consider layer-specific effort maps.

---

## Quick Diagnostic Commands for You

**Check scale factors are reasonable:**
```bash
cd charybdis-optimizer-v2
uv run python -c "from core.loader import build_layout; from fitness.evaluator import FitnessEvaluator; import numpy as np; l=build_layout('../build'); eval=FitnessEvaluator(reference_layout=l); eval2=FitnessEvaluator(reference_layout=l, scale_factors=np.array([2000,100000,10000000],dtype=np.float32)); r1=eval.evaluate(l); r2=eval2.evaluate(l); print('Raw:', r1.objectives); print('Normalized:', r2.objectives)"
```

**Check mouse shortcuts exist:**
```bash
cd charybdis-optimizer-v2
uv run python -c "from core.loader import load_shortcuts; s=load_shortcuts('../build/app_shortcut_scores.json'); m=[x for x in s if 'mouse' in x.action.lower() or 'click' in x.action.lower()]; print(f'Mouse shortcuts: {len(m)}'); [print(x.action) for x in m[:10]]"
```

**Check blind spots:**
```bash
cd charybdis-optimizer-v2
uv run python -c "import json; u=json.load(open('../build/usage_stats.json')); b=u.get('blind_spots',[]); print(f'Total: {len(b)}'); [print(f\"{x['app']}: {x['keys']} ({x['action']}) score={x['blind_spot_score']}\") for x in b[:10]]"
```

**Check group_split at seed:**
```bash
cd charybdis-optimizer-v2
uv run python -c "from core.loader import build_layout; from fitness.factors.violation import ViolationFactor; l=build_layout('../build'); vf=ViolationFactor(); print('group_split:', vf._group_split(l)); print('thumb_occ:', vf._thumb_occupancy(l))"
```

**Check frozen preservation in evolved genome:**
```bash
cd charybdis-optimizer-v2
uv run python -c "import json; r=json.load(open('../build/v2_checkpoint_gen100.json')); g=r['best_exact']['genome']; l=build_layout('../build'); diff=sum(1 for i in range(len(g)) if l.frozen_mask[i] and g[i] != l.genome[i]); print(f'Frozen positions changed: {diff} / {sum(l.frozen_mask)}')"
```

---

## Bottom Line Priority Order

1. **Inject seed genome into initial population** (CRITICAL — 10x speedup to useful evolution)
2. **Fix or remove TrackballProximityFactor** (CRITICAL — dead weight)
3. **Verify surrogate trained on normalized scores** (CRITICAL — already fixed, verify in run)
4. **Address blind spots** (HIGH — 104 unused important shortcuts suggest corpus/usage mismatch)
5. **Add evolved-genome surrogate accuracy tracking** (HIGH — detect surrogate drift)
6. **Weight AppCoherence by usage time** (MEDIUM — reward apps the user actually uses)
7. **Verify group_split decreases over time** (MEDIUM — static group preservation is key)
8. **Clean up old checkpoints** (LOW — disk space)
9. **Add Pareto diversity metrics** (LOW — nice for analysis)
10. **Hyperparameter tuning** (LOW — only after run completes)
