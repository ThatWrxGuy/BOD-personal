# DEPRECATION NOTICE

**Date**: 2026-03-12

## Legacy Simulation Module

The `app/simulation/` directory is **DEPRECATED** as of V5-002.

### Reason for Deprecation

The original simulation functionality has been superseded by the enhanced Strategic Scenario Simulation Engine in `app/strategy_simulation/`.

The new system provides:
- Multi-scenario evaluation
- Strategy scoring with resilience metrics  
- Recommendation generation
- Integration with Forecasting and Monte Carlo engines

### Migration

All functionality has been migrated to:

- `app/strategy_simulation/` - Strategic scenario simulation (V5-002)
- `app/forecasting/` - Forecasting engine (V5-001)
- `app/monte_carlo/` - Monte Carlo stress testing (V5-003)

### Files Affected

The following legacy files are deprecated:
- `app/simulation/simulation_engine.py` → Use `strategy_simulation/enhanced_simulation_engine.py`
- `app/simulation/simulation_types.py` → Use `strategy_simulation/simulation_types.py`
- `app/simulation/scenario_generator.py` → Use `strategy_simulation/scenario_generator.py` (if needed)
- `app/simulation/outcome_modeler.py` → Use `strategy_simulation/outcome_simulator.py`

### Timeline

- **Deprecated**: 2026-03-12
- **Removal**: TBD (after V5-004)

### Action Required

Update any imports from `app.simulation` to use the new modules under `app.strategy_simulation`.

### Example Migration

```python
# OLD (deprecated)
from app.simulation.simulation_engine import SimulationEngine

# NEW (recommended)
from app.strategy_simulation import EnhancedSimulationEngine
```

---

*For questions, please refer to the architecture documentation in `docs/architecture/`*
