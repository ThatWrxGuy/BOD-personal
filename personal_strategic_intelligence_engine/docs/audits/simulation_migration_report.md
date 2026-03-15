# Simulation Migration Report

**Date:** 2026-03-12  
**Directive:** V6-003

---

## Summary

This report documents the simulation architecture migration completed under Directive V6-003.

---

## Canonical Package Definition

The canonical simulation package is:

```
app.simulation_engine/
├── __init__.py
├── simulation_models.py      # Unified data models
├── strategy_simulator.py    # Strategy simulation
├── monte_carlo_engine.py    # Monte Carlo simulation  
└── simulation_core.py       # Unified interface
```

**Preferred Import Path:**
```python
from app.simulation_engine import (
    SimulationCore,
    StrategySimulator,
    MonteCarloEngine,
    SimulationConfig,
    SimulationResult,
    DomainState,
)
```

---

## Legacy Wrappers Retained

The following legacy directories have been converted to thin wrappers:

| Directory | Status | Files |
|-----------|--------|-------|
| `app/simulation/` | DEPRECATED | Wrapper only (19 legacy files remain) |
| `app/strategy_simulation/` | DEPRECATED | Wrapper only (7 legacy files remain) |
| `app/monte_carlo/` | DEPRECATED | Wrapper only |

Each wrapper module re-exports from `app.simulation_engine` for backward compatibility.

---

## Migration Status

### Files Migrated to Canonical

1. Created `app/simulation_engine/` - new canonical simulation package
2. Converted legacy `__init__.py` files to import-forwarding wrappers

### Known Blockers

The following active modules still import from legacy paths:

1. `app/api/simulation_api.py` - Uses legacy simulation
2. `app/api/simulation.py` - Uses legacy simulation  
3. `app/chat/command_interpreter.py` - Uses legacy simulation
4. `app/planning/plan_simulation_validator.py` - Uses legacy simulation

**Action Required:** These files should be migrated in a follow-up directive to use `app.simulation_engine` imports.

---

## Architecture Guard

The architecture guard (`scripts/architecture_guard.py`) has been enhanced with:

- Detection of legacy simulation imports in active code
- Detection of excessive files in legacy directories (>5 files = warning)
- Exclusion of legacy wrapper directories from internal import checks

---

## Test Coverage

Migration tests added at `tests/simulation/test_migration.py`:

- Canonical import verification
- Legacy wrapper import verification  
- Output equivalence tests
- Architecture guard compliance

---

## Recommendations

1. **Phase 1:** Migrate `app/api/simulation*.py` to canonical imports
2. **Phase 2:** Migrate remaining active modules 
3. **Phase 3:** Remove legacy files when all imports are updated
4. **Phase 4:** Delete deprecated wrapper `__init__.py` files

---

## Conclusion

The canonical simulation architecture is established. Legacy directories are now thin wrappers. Active migration of API and other modules remains as a follow-up task.

**Status:** Canonical implementation complete, backward compatibility preserved, migration in progress.
