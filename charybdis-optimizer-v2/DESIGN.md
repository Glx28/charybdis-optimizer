# Charybdis Optimizer v2 — Architecture Design

## Key Improvements over v1

1. **Modular Fitness** — 3,300-line monolith → 12 clean, testable factors (~50 LOC each)
2. **Neural Surrogate** — 100x speedup via learned fitness model (MKLOGA paper)
3. **pymoo** — replaces DEAP with proper MOEA framework
4. **Cycle Crossover** — proven better than PMX for permutation problems
5. **Hydra Config** — structured, validated configuration
6. **Proper Testing** — 200+ tests target vs 58 in v1

## Structure

```
v2/
  core/           — data structures (Layout, Position, Shortcut)
  fitness/        — modular fitness factors
    factors/      — each factor is a separate module
  evolution/      — pymoo-based algorithm + surrogate
  config/         — Hydra configuration
  tests/          — comprehensive test suite
  pipeline/       — Node.js analysis (ported from v1)
```

## Design Decisions

- **Immutable dataclasses** for type safety
- **Stateless fitness factors** for testability
- **Surrogate model** eliminates GPU/CPU divergence
- **pymoo** for proper NSGA-II/III support

See full design in backup: charybdis-optimizer-backup-run13/
