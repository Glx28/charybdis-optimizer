# Kimi Coding Agent — Handoff Document

> **Purpose:** This document packages everything the next Kimi coding agent session needs to immediately take over from Codex and work effectively with the Claude Manager. Read this entire document before touching any code.
>
> **Project cleaned: 2026-06-28.** Old session prompts, superseded handoffs, smoke test artifacts, and Python caches were removed. Only current/relevant files remain. See Section 0 for the clean file layout.

---

## 0. Project File Layout (After Cleanup)

### Root directory (clean — no old session prompt clutter)
| File | Purpose |
|------|---------|
| `AGENTS.md` | Project overview, quick start, architecture |
| `README.md` | Standard README |
| `SESSION8_MANAGER_PROMPT.md` | Current Claude Manager session prompt (active) |
| `sync_repos.ps1` | Repo sync script |
| `.gitignore` | Excludes checkpoints, logs, archives, caches, old prompts |

### `docs/` (only current/relevant docs)
| File | Purpose |
|------|---------|
| `HANDOFF_KIMI_CODING_AGENT.md` | **This document** — your primary reference |
| `run_audit_session7_run11.md` | Most recent pre-Run 12 audit (violation floor analysis) |
| `FIXES_AND_METRICS_HANDOFF.md` | Technical details on scoring fixes, metrics, pool validation |
| `BROKEN_LAYOUT_DIAGNOSIS.md` | Diagnostic reference for layout failures |
| `position_value_model.md` | Position value scoring reference |
| `archive/` | **Old handoffs moved here** — only reference if Manager asks |

### `build/` (active + permanent data only)
| File/Dir | Purpose | Do NOT Touch |
|----------|---------|-------------|
| `canonical.json` | Current layout snapshot | |
| `app_shortcut_scores.json` | Scored shortcut corpus | |
| `evolution_scratch_checkpoint.json` | **Active Run 12 checkpoint** | ✅ |
| `evolution_scratch_checkpoint.npz` | **Active Run 12 checkpoint data** | ✅ |
| `evolution_scratch_results_interim.json` | **Active Run 12 interim results** | ✅ |
| `run_logs/` | **Active Run 12 logs** | ✅ |
| `candidate_snapshots/` | Run 11/12 candidate exports (keep for now) | |
| `archive/` | Compressed old `best_runs/` from Jun 26 | |
| `*.js`, `*.csv`, `*.json` | Pipeline outputs, evolved layouts, etc. | |

### `evolve/` (all core code — no caches)
| File | Purpose |
|------|---------|
| `fitness.py` | Fitness function (CPU + GPU paths) |
| `representation.py` | Genome encoding, pool, positions, groups |
| `operators.py` | Mutation, crossover, diversity injection |
| `run_evolution.py` | Main entry point, health logger |
| `config_scratch.json` | Current production config |
| `config.json` | Normal mode config |
| `layer_access.py` | Layer access validation |
| `analyze_results.py` | Post-run analysis |
| `evaluate_cpu_gpu_parity.py` | CPU/GPU parity verification |
| `test_fitness.py`, `test_layer_access.py` | Unit tests |
| `export_*.py`, `generate_verify.py`, `decode_results.py` | Export/utility scripts |
| `bench.py`, `profile_evolution.py`, `validate_fitness.py` | Benchmark/validation tools |

> **What was removed:** Old `SESSION6/7_*.md` prompts, duplicate `CLAUDE.md`, `best_runs/` (157MB compressed to archive), 10+ smoke test directories (~7MB), stale `best_evolved_genome.json`, `evolved_diff.txt`, `fitness_validation_template.json`, Python `__pycache__` and `.pytest_cache` directories.

---

## 1. Team Structure & Roles

| Agent | Role | What They Do | What They DON'T Do |
|-------|------|-------------|-------------------|
| **Claude** | Manager | Monitors runs, audits results, writes fix handoffs, decides when to launch/relaunch | NEVER modifies code |
| **Kimi (you)** | Coding Agent | Reads handoffs, diagnoses root causes, fixes code, runs tests, validates fixes | NEVER launches long runs without Manager approval |
| **User** | Product Owner | Decides strategy, approves changes, gives context | — |

**Communication flow:**
1. Manager writes audit/handoff → `docs/run_audit_sessionN_runM.md`
2. You read handoff, diagnose, fix, test → report back with specific findings
3. Manager decides if fixes are sufficient → either approves long run or writes follow-up handoff
4. You do NOT declare "ready for long run" — that's the Manager's call

---

## 2. What This Project Is

The **Charybdis Optimizer** is a keyboard layout optimizer for a split keyboard with a trackball. It uses:
- **Node.js pipeline** (13 modules): analyzes shortcuts, usage stats, generates candidates
- **Python DEAP/pyribs evolutionary optimizer** (`evolve/`): evolves keyboard layouts using NSGA-II with 3 objectives (effort, adjacency, violations)
- **316 shortcuts** in the pool, **559 mutable positions** across 11 layers (L7 is frozen)
- **Scratch mode**: evolves from random initialization (this is what we're currently running)
- **Normal mode**: evolves from current `canonical.json` layout

Key files:
- `evolve/run_evolution.py` — main entry point
- `evolve/fitness.py` — 12-factor fitness function (CPU + GPU batch paths)
- `evolve/representation.py` — layout genome encoding, position index, pool building
- `evolve/operators.py` — crossover, mutation, diversity injection
- `evolve/config_scratch.json` — current production config (5000 pop, 10000 gen)
- `build/canonical.json` — current layout snapshot (from ZMK Studio export)
- `build/app_shortcut_scores.json` — scored shortcut corpus

---

## 3. Current State (Run 12)

**Run 12** is currently alive at gen ~200/10,000 (launched 2026-06-28 12:35).
- PID: 18160
- Log: `build/run_logs/scratch_20260628_123511.out.log`
- Config: pop_size=5000, generations=10000, checkpoint_interval=100
- Gen 0 was healthy: effort=-13341, viol=-289, adj=4710, all groups 100%, structural 100%

**⚠️ DO NOT touch these active files:**
- `build/evolution_scratch_checkpoint.json`
- `build/evolution_scratch_checkpoint.npz`
- `build/evolution_scratch_results_interim.json`
- `build/run_logs/scratch_20260628_123511.*.log`

**What was fixed before Run 12:**
1. L0 thumb freeze — mutable thumbs now filled with structural keys (coach holds, MB1, leftalt)
2. f_keys_high — added synthetic F1-F12 base keys, pool now 316 (was 315)
3. Ctrl+Z parity boost — importance=10 (matches Ctrl+C/V), now lands at eff=3.5 (was 5.5)
4. Exit_to_base duplicates — exempt from structural duplicate penalty (was causing permanent ~5,400 floor)
5. Operator protection — only protects if placement is legal at position (was locking DownArrow on L0 thumb)
6. Mouse seeding — MB1/2/3 + clipboard seeded together on L2 left home row in scratch mode
7. Prime empty repair — fills empty prime positions when unassigned shortcuts exist
8. Health logger — toggleable diagnostic (`health_logging` in config, default false for long runs)

**Manager monitor**: triggers every 1000 gens + on errors. Do NOT poll the Manager.

---

## 4. The Critical Problem: Violation Floor

The #1 unsolved issue from previous runs is **violations frozen at ~5,400** across 2,600 generations. This is a **fixed violation floor**, not a convergence problem. The floor dropped by exactly 4 every ~500 gens — one penalty component resolved, then nothing.

### Why This Matters
If the floor is still present in Run 12, the optimizer will waste thousands of generations making no progress on violations. The Manager will detect this and write a handoff. Your job is to **diagnose and fix**.

### The Math You Must Check

**Pool size: 316 shortcuts. Positions: 559 mutable.**
Even with perfect placement: 559 - 316 = **243 positions MUST be empty.**

The empty_prime penalty (30 × position_waste = 150 effort per empty eff≤1.5 position) may be creating a **permanent violation floor** that evolution can never resolve because it's physically impossible to fill all positions.

**You MUST calculate this:**
- How many eff≤1.5 positions exist across all layers?
- How many of those positions are on L0 (frozen, not counted)?
- How many are on other layers?
- If the number of empty prime positions > 0 even after all 316 SIDs are placed, the penalty is a tax on physics.

### The Decomposition Task

Before proposing ANY fix, you must decompose the violation score into sub-components. The aggregate `violations: 7,554.9` (or similar) is useless for diagnosis.

**The fitness function has these violation components:**
- `zmk_compatibility` violations (weight: 20.0)
- `unassignment_penalty` (weight: 50.0)
- `duplicate` — same-layer duplicates (weight: 50.0)
- `cross_layer_duplicate` (weight: 25.0)
- `structural_duplicate` — now exempt for exit_to_base (weight: 25.0)
- `group_split` (weight: 50.0)
- `missing_important` (weight: 80.0)
- `momentary_redundancy` (weight: 8.0)
- `layer_redundancy` (weight: 15.0)
- `l0_thumb_structural` — 80.0 per content key on mutable L0 thumb
- `empty_prime_position` — 30 × position_waste per empty eff≤1.5 non-L0
- `toggled_base_violation` — missing coach_base on toggled/locked layers (weight: 30.0, but was made hard constraint in some fixes)

**What you must do:**
1. Add a `violation_breakdown()` function (or similar) that returns each sub-component as a named dict
2. Run it on a freshly generated best_violations genome (or interim result from a run)
3. Report the exact breakdown: which components contribute how much
4. Determine which are **structural/inevitable** (can't be fixed by evolution) vs **fixable**

**Do NOT:**
- Guess which component is causing the floor
- Propose a fix without numbers backing it up
- Run a 20-gen smoke and declare victory

---

## 5. What Codex Did Badly (Learn From Their Mistakes)

### Failure 1: Never Actually Diagnosed the Root Cause
The Manager asked Codex to decompose the violation score. Codex added a `violation_breakdown()` function but **never ran it on actual data**. They hypothesized about empty positions and structural duplicates but provided zero numbers. They never answered: "Is the floor 3,000 from empty positions + 2,000 from structural duplicates, or is it something else?"

**Your rule:** Always provide numbers. A diagnosis without numbers is speculation.

### Failure 2: 20-Gen Smoke Tests Are Meaningless for Convergence
The original problem was violations frozen for **2,600 generations**. Codex ran a 20-gen smoke and declared victory. Twenty generations cannot possibly validate a convergence floor.

**Your rule:** If the issue is "frozen for N generations," you must run at least N/2 generations to validate the fix, OR provide a mathematical proof that the floor is removed.

### Failure 3: Band-Aid Fixes Instead of Root Cause
f_keys_high went from 99% to 0%. Codex's response was "add more synthetic keys to the pool." But the keys already existed (99% before). Something in the code **broke** between runs — likely group matching, protected flag handling, or pool dedup. Codex didn't investigate why; they just added more keys.

**Your rule:** If something worked before and broke now, find the code change that caused it. Don't mask symptoms.

### Failure 4: Didn't Do the Math
With 316 pool entries and 559 positions, 243 positions MUST be empty. Codex didn't calculate whether the empty_prime penalty is mathematically unavoidable. Their "prime empty repair" only helps when unassigned shortcuts exist — once all 316 are placed, the penalty is a permanent tax.

**Your rule:** Do the math. Count positions, count pool entries, calculate theoretical minimums. If a penalty is physically unavoidable, it must be removed or capped.

### Failure 5: Seeding ≠ Evolution
Codex seeded MB1-3 together on L2 and called it "fixed." But the original problem was that the **optimizer scattered them during evolution**. Seeding them together doesn't guarantee they stay together after thousands of generations of mutation and crossover.

**Your rule:** A fix must be validated through actual evolution, not just seeding. If you strengthen a scoring term, verify through a multi-hundred-gen run that the behavior persists.

### Failure 6: Premature "Ready" Declaration
The user said: *"keep testing and improving until all problems mentioned are gone."* Codex stopped at unit tests + 20-gen smoke and declared ready for a 10,000-gen run. The Manager had to correct them.

**Your rule:** You do NOT declare runs ready. You report findings and test results. The Manager decides if fixes are sufficient.

### Failure 7: Building Tools Without Using Them
Codex built a health logger (good) but never used it to answer the actual diagnostic questions. The Manager still had no data on whether the 5,400 floor was structural, mathematical, or fixable.

**Your rule:** Tools are means, not ends. If you build a diagnostic tool, USE it to produce actionable data immediately.

---

## 6. How to Work With the Manager (Claude)

### When You Receive a Handoff
1. Read the handoff file completely
2. Read any referenced files (fitness.py, representation.py, etc.)
3. Formulate a hypothesis
4. **Write a test or diagnostic that produces numbers** — not a guess
5. Run the diagnostic on actual data (exported genome, checkpoint, interim result)
6. Report back with: exact numbers, what you found, what fix you propose
7. Implement the fix, run tests, verify

### What to Report Back
| Always Include | Never Include |
|--------------|---------------|
| Exact numbers from diagnostics | "I think..." or "probably..." |
| Which file changed, which lines | Long explanations without data |
| Test results (pass/fail, specific values) | Declarations that a fix is "complete" |
| Whether CPU/GPU parity still holds | Vague confidence statements |
| Violation breakdown if relevant | Recommendations about launching runs |

### The Manager Will Check
- `build/run_logs/` for latest log
- `docs/` for your handoff response
- Unit test pass/fail
- Whether the fix actually addresses the root cause (not symptoms)

---

## 7. Key Files & What to Know About Each

### `evolve/fitness.py`
- **CPU path**: `evaluate()` — single genome, full validation, slow but authoritative
- **GPU path**: `evaluate_batch_gpu()` — batch evaluation, fast, must match CPU exactly
- **Critical**: CPU/GPU parity must be maintained. After ANY scoring change, run `evaluate_cpu_gpu_parity.py`
- `HARD_INVALID_FITNESS` = (-1e9, -1e9, -1e9) — genomes with invalid layer access, stale SIDs, etc.
- `toggled_base_violation` — missing coach_base on toggled/locked layers. Was made a hard constraint in some fixes. Verify which version is active.

### `evolve/representation.py`
- `build_shortcut_pool()` — builds the 316-entry pool. If this changes, pool size changes, checkpoints become invalid.
- `build_position_index()` — effort values for each position. Home row inner = 0.0, top edges = 5.5.
- `is_frozen_l0_position()` — L0 main grid (letters, numbers, punctuation) is frozen; ~6-8 thumb positions are mutable.
- `KEY_GROUPS` — defines group membership (arrows, clipboard, f_keys_high, f_keys_low, win_directions, mouse_buttons). Check protected flags.
- `seed_population_scratch()` — creates initial population. Currently seeds MB1-3 + clipboard on L2 left, repairs groups.

### `evolve/operators.py`
- `mutate()` — must respect frozen positions, protected SIDs, L0 thumb structural policy
- `crossover()` — must preserve structural keys (coach_base on toggled layers)
- `diversity_injection()` — reintroduces random genomes at plateaus to escape local optima
- Protection logic: `only protect if legal at position` — this was the fix for DownArrow on L0 thumb

### `evolve/run_evolution.py`
- Main loop: initialize → evaluate → select → crossover → mutate → inject diversity
- Checkpointing every 100 gens (configurable)
- Saves: `best_weighted`, `best_effort`, `best_violations`, `pareto_front`
- Health logger: toggleable via `health_logging` config flag
- **Do NOT modify config values directly** — ask the Manager if config changes are needed

### `evolve/config_scratch.json`
Current production config (do not change without Manager approval):
```json
{
  "pop_size": 5000,
  "generations": 10000,
  "checkpoint_interval": 100,
  "health_logging": false,
  "violations": 50.0,
  "importance_effort_alignment": 4.0,
  "mouse_accessibility": 25.0,
  "position_waste": 5.0,
  "high_importance_misplacement": 1.5
}
```

> **Note on `.gitignore`:** Checkpoints, interim results, run logs, and archives are excluded from git. If you create new test artifacts, they should go in `build/` (which is mostly gitignored) or a temporary subdirectory. Do NOT commit checkpoint files or large JSON artifacts.

---

## 8. Testing Requirements

### Always Run After Code Changes
1. **Unit tests**: `python -m unittest test_fitness test_layer_access -v`
   - Target: all pass, 0 failures (1 skip is normal)
2. **CPU/GPU parity**: `python evaluate_cpu_gpu_parity.py ../build`
   - Target: max_abs_diff effort≤0.25, adjacency≤0.01, violations=0.00
   - If this fails, the GPU batch path is wrong — fix before anything else
3. **Compile check**: `python -m py_compile evolve/*.py` — must pass with no syntax errors

### Validation Tests You Should Know
- `test_fitness.py` — tests individual fitness components
- `test_layer_access.py` — tests layer access validation (coach_base on toggled layers, etc.)
- `validate_fitness.py` — comprehensive fitness validation
- `bench.py` — performance benchmark

### How to Validate a Fix (The Right Way)
If the issue is "violations frozen at X":
1. Write a diagnostic that decomposes violations into sub-components
2. Run it on the current best_violations genome from a checkpoint or interim result
3. Identify the largest sub-components
4. Propose a fix targeted at those specific components
5. Run a **medium-length test** (at least 200-500 gens, preferably 1000) to verify the trajectory changes
6. Compare before/after violation curves

If the issue is "mouse buttons scattered":
1. Run a 500+ gen test
2. Check the best layout at the end: are MB1/2/3 still together?
3. Check intermediate checkpoints: when did they separate?
4. If they stay together for 500+ gens, the fix is likely real; if they scatter by gen 200, the fix is insufficient

---

## 9. The Empty Position Math (Do This Calculation)

This is the most likely source of the violation floor. You must verify this.

**Given:**
- Pool size: 316 shortcuts
- Mutable positions: 559 (L7 frozen, excluded)
- Structural keys (coach_base, exits, layer switches): ~20-30 additional placements
- Theoretical max assignments: ~330-340
- Empty positions: 559 - 340 = ~219 minimum

**Questions to answer:**
1. How many positions have effort ≤ 1.5 across all mutable layers (excluding L0 frozen)?
2. How many of those can be filled with the 316 pool entries + structural keys?
3. If the count from (1) > count from (2), the empty_prime penalty is **permanent**.
4. If permanent, the penalty should be removed from violations (or capped at unassigned pool entries).

**How to calculate:**
```python
# In a Python shell or test script:
from representation import build_position_index, build_shortcut_pool
import json

canonical = json.load(open('build/canonical.json'))
scores = json.load(open('build/app_shortcut_scores.json'))
positions = build_position_index(canonical, {7})
pool = build_shortcut_pool(scores, canonical)

# Count prime positions (eff ≤ 1.5, non-L0, non-frozen)
prime_positions = [p for p in positions if p.effort <= 1.5 and p.layer != 0]
print(f"Prime positions: {len(prime_positions)}")
print(f"Pool size: {len(pool)}")
print(f"Structural keys: {count_structural_keys()}")  # you need to implement this
print(f"Minimum empty primes: {len(prime_positions) - len(pool) - structural_count}")
```

If minimum empty primes > 0, the empty_prime penalty creates a floor. Propose removing it from violations or making it conditional.

---

## 10. Known Bugs & Their Current Status

| Bug | Status | Notes |
|-----|--------|-------|
| Pareto front ≠ population best | Fixed | best_weighted/effort/violations now saved separately |
| L0 freeze broke in scratch | Fixed | position-based freeze, not genome-based |
| DownArrow on L0 thumb | Fixed | operator only protects if legal at position |
| Exit_to_base duplicates | Fixed | exempt from structural_duplicate penalty |
| Silent CUDA OOM | Partially fixed | flushed logging markers added, but still watch for silent death |
| Duplicate initial GPU eval | Fixed | removed double startup eval |
| win_directions group 0 matches | Fixed | params were LeftArrow/RightArrow, pool has Left/Right |
| f_keys_high regression | Fixed | added synthetic F1-F12 base keys, pool 316 |
| L2 missing from toggled_layer_indices | Claimed fixed | Verify in fitness.py: `toggled_layer_indices` should include L2 |
| GPU/CPU divergence for stale SIDs | Claimed fixed | Verify SID clamping in GPU batch path |
| Toggled_base as hard constraint | Claimed fixed | Verify in fitness.py: does it set HARD_INVALID_FITNESS? |

**Your job when you receive a handoff:** Verify the "claimed fixed" items are actually fixed. Codex often said things were fixed without proper verification.

---

## 11. Quick Reference Commands

```powershell
# Check if Run 12 is alive
Get-Process -Id 18160 -ErrorAction SilentlyContinue

# Check latest gen
tail -f "C:\Users\nos\charybdis-optimizer\build\run_logs\scratch_20260628_123511.out.log" | grep -E "Gen  [0-9]+:"

# Run unit tests
cd C:\Users\nos\charybdis-optimizer\evolve
python -m unittest test_fitness test_layer_access -v

# CPU/GPU parity
cd C:\Users\nos\charybdis-optimizer\evolve
python evaluate_cpu_gpu_parity.py ../build

# Analyze completed run results
python analyze_results.py ../build --scratch

# Run a short test (ask Manager before running medium/long)
python run_evolution.py build --scratch --gens 100 --pop 500

# Compile check
python -m py_compile evolve/*.py
```

---

## 12. What to Do When You Receive a Handoff

1. **Read the handoff completely** — don't skim
2. **Read the referenced files** — the Manager will cite specific files/lines
3. **Formulate a hypothesis** about root cause
4. **Write a diagnostic** that produces numbers (not guesses)
5. **Run the diagnostic** on actual data from the run
6. **Report findings** with exact numbers
7. **Propose a fix** with expected impact (e.g., "removing empty_prime from violations should reduce floor by ~X")
8. **Implement the fix**
9. **Run tests** (unit tests, parity check, compile check)
10. **Run a validation test** (200-1000 gens if the issue is convergence-related)
11. **Report back** with: what changed, test results, what remains uncertain

---

## 13. Violation Breakdown Template

When the Manager asks you to decompose violations, use this exact format:

```python
def violation_breakdown(genome, positions, pool, config):
    """Returns a dict of {component_name: raw_value} for each violation sub-component."""
    # ... implementation ...
    return {
        'zmk_compatibility': 0.0,
        'unassignment': 0.0,
        'duplicate': 0.0,
        'cross_layer_duplicate': 0.0,
        'structural_duplicate': 0.0,
        'group_split': 0.0,
        'missing_important': 0.0,
        'momentary_redundancy': 0.0,
        'layer_redundancy': 0.0,
        'l0_thumb_structural': 0.0,
        'empty_prime_position': 0.0,
        'toggled_base_violation': 0.0,
    }
```

**Report format:**
```
Violation Breakdown (raw units, before weighting):
  zmk_compatibility:          0.0
  unassignment:               0.0
  duplicate:                  12.5  ← 12.5 × 50 = 625 contribution
  cross_layer_duplicate:        8.2  ← 8.2 × 25 = 205 contribution
  structural_duplicate:         0.0  (exit_to_base exempted)
  group_split:                 3.1  ← 3.1 × 50 = 155 contribution
  missing_important:            0.0
  momentary_redundancy:         0.0
  layer_redundancy:             0.0
  l0_thumb_structural:          0.0
  empty_prime_position:       45.2  ← 45.2 × 150 = 6,780 contribution ← FLOOR SOURCE
  toggled_base_violation:       0.0
  
  TOTAL RAW: 68.9
  TOTAL WEIGHTED: 7,765
  
  Floor analysis: empty_prime_position = 45.2 raw units.
  Prime positions available: 87. Pool entries: 316. Structural keys: 25.
  Minimum empty primes: 87 - (316 - 25) = 87 - 291 = 0 → wait, all prime positions CAN be filled?
  Recheck: 87 prime positions, 291 non-structural pool entries...
```

---

## 14. Remember: The Goal Is Not "Tests Pass"

The goal is **real layouts that work**. A 20-gen smoke where all tests pass means nothing if the issue is a convergence floor that takes 2,000+ generations to appear.

- **Short tests** (20-100 gens): validate that code doesn't crash, basic functionality works
- **Medium tests** (200-1000 gens): validate that fixes actually change convergence trajectories
- **Long tests** (5000-10000 gens): Manager decides when to launch these. You do not.

Your job is rigorous diagnosis, targeted fixes, and honest reporting. The Manager's job is deciding when to run the long experiments.

---

*Document version: 2026-06-28 (cleaned). Next Kimi session should read this entire document before touching any code.*

---

## A. What NOT to Commit to Git

The `.gitignore` already excludes these, but be aware:
- `build/*checkpoint*` — active run checkpoints (the running process needs these)
- `build/*results_interim*` — interim results
- `build/run_logs/` — run logs
- `build/archive/` — compressed old runs
- `docs/archive/` — old handoffs
- `__pycache__/` and `*.pyc` — Python caches
- `SESSION*_PROMPT.md` — old agent prompts

**Rule:** Only commit code changes, config changes, and documentation. Never commit checkpoint data, logs, or test artifacts.
