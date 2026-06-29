# MANAGER AGENT: RUN CHARYBDIS V2 INFINITE EVOLUTION

## Your Task

Start the v2 evolution run and keep it running. Report back at the milestones below or when a real problem occurs. Do not interrupt for normal evolution behavior like slowing improvement or high n_nds.

## Start Command

```bash
cd charybdis-optimizer-v2
uv run python run_evolution.py ../build
```

The default config (`config/__init__.py`) is already set to `pop_size=1000`, `n_generations=10000`, `n_initial_samples=5000`. The run will auto-save results to `build/v2_evolution_results.json`.

## What to Report

After the run starts, capture the first 30 lines of output (seed fitness, surrogate R²). Then let it run. Only report when:

1. **Initial startup complete** (first 10 minutes): Share seed fitness and surrogate R².
2. **Every 500 generations**: Share the last 5 lines of pymoo output (Gen, n_eval, f1, f2, f3, n_nds, eps).
3. **Every 2000 generations**: Run this diagnostic and share the result:
   ```bash
   cd charybdis-optimizer-v2
   uv run python -c "import json; r=json.load(open('../build/v2_evolution_results.json')); print('Best exact viol:', r['best_exact']['violations']); print('R2 history:', r.get('surrogate_r2_history',[])[-3:]); print('Exact eval history:', r.get('exact_eval_history',[])[-3:])"
   ```

## When to STOP and Ask the User for Code Changes

These are the ONLY reasons to interrupt the run. Everything else is normal evolution behavior.

| Trigger | Why | What to ask |
|---------|-----|-------------|
| **Runtime error / exception** | Bug in code | Share full traceback. |
| **Surrogate R² < 0.80 after initial training** | Surrogate is too inaccurate to be useful | Ask: disable surrogate and run exact-only? |
| **Surrogate R² drops below 0.80 after retrain** | Retraining failed; surrogate is now useless | Ask: increase hidden_dim, increase training data, or disable surrogate? |
| **Exact `viol` gets WORSE for 3 consecutive exact evals (150 gens)** while surrogate says it's improving | Surrogate is lying to the optimizer | Ask: disable surrogate and run exact-only? |
| **n_nds == pop_size (1000/1000) for >20 consecutive generations** | Zero selection pressure; evolution is dead | Ask: reduce to 2 objectives, or switch to single-objective weighted sum? |
| **`group_split` > 10,000 and increasing for 500+ gens** | Static group preservation completely broken | Ask: strengthen group_split weight, or add a group repair operator? |
| **`missing_important` > 0 for 500+ gens** | High-importance shortcuts are unassigned | Ask: increase genome size or pre-seed more aggressively? |

## What is NORMAL — Do NOT Interrupt

- `n_nds` rising over time (even to 900+). This is expected with 3 objectives. Only act if it hits exactly 1000/1000 for 20+ gens.
- `eps` dropping to 0.001 or below. This happens. Only act if it stays at 0 for 200+ gens with no improvement in exact eval.
- Exact `viol` improving slowly. Evolution is hard. Only act if it gets WORSE for 3 consecutive exact evals.
- Any single factor score being large. The objectives are on different scales. This is normal.
- Run taking hours. The config is set to 10000 generations. This is expected.

## Current Seed Numbers (For Reference)

If the user asks "what's the baseline?":
- Seed fitness: effort=1612, adj=27775, viol=-41662
- Violation breakdown: duplicate=44, l0_disp=0, missing=0, cross_layer=71, group_split=3279, thumb_occ=94
- group_split=3279 is the biggest driver. This is expected — the greedy seed scatters static groups. Evolution will cluster them.

## Files

- Code: `charybdis-optimizer-v2/`
- Data: `build/canonical.json`, `build/app_shortcut_scores.json`, `build/usage_stats.json`
- Output: `build/v2_evolution_results.json`
- Config: `charybdis-optimizer-v2/config/__init__.py` (defaults)

## Bottom Line

Start the run. Capture initial output. Let it cook. Report every 500 gens. Only ask for code changes if one of the STOP triggers above fires.
