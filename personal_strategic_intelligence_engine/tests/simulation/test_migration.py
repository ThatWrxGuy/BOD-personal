"""Migration tests - Verify canonical simulation imports work."""
import pytest


class TestCanonicalImports:
    """Test that canonical import paths work."""
    
    def test_import_simulation_core(self):
        """Test importing SimulationCore from canonical path."""
        from app.simulation_engine import SimulationCore
        assert SimulationCore is not None
    
    def test_import_strategy_simulator(self):
        """Test importing StrategySimulator from canonical path."""
        from app.simulation_engine import StrategySimulator
        assert StrategySimulator is not None
    
    def test_import_monte_carlo(self):
        """Test importing MonteCarloEngine from canonical path."""
        from app.simulation_engine import MonteCarloEngine
        assert MonteCarloEngine is not None
    
    def test_import_models(self):
        """Test importing models from canonical path."""
        from app.simulation_engine import SimulationConfig, SimulationResult, DomainState
        assert SimulationConfig is not None
        assert SimulationResult is not None
        assert DomainState is not None


class TestLegacyWrapperImports:
    """Test that legacy wrapper imports still work."""
    
    def test_legacy_simulation_import(self):
        """Test importing from legacy app.simulation."""
        from app.simulation import SimulationCore
        assert SimulationCore is not None
    
    def test_legacy_strategy_simulation_import(self):
        """Test importing from legacy app.strategy_simulation."""
        from app.strategy_simulation import StrategySimulator
        assert StrategySimulator is not None
    
    def test_legacy_monte_carlo_import(self):
        """Test importing from legacy app.monte_carlo."""
        from app.monte_carlo import MonteCarloEngine
        assert MonteCarloEngine is not None


class TestOutputEquivalence:
    """Test that legacy and canonical produce equivalent outputs."""
    
    def test_simulation_results_equivalence(self):
        """Test that canonical and legacy produce same results."""
        from app.simulation_engine import SimulationCore, SimulationConfig, SimulationType, DomainState
        from app.simulation import SimulationCore as LegacyCore
        
        # Create test domain
        domain = DomainState(domain="test", current_score=5.0, target_score=7.0)
        domains = {"test": domain}
        
        # Run with canonical
        core = SimulationCore()
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, num_iterations=10)
        canonical_result = core.run_simulation(config, domains)
        
        # Run with legacy wrapper
        legacy_core = LegacyCore()
        legacy_result = legacy_core.run_simulation(config, domains)
        
        # Should produce same type
        assert type(canonical_result) == type(legacy_result)
        assert canonical_result.simulation_type == legacy_result.simulation_type


class TestCanonicalOnlyExecution:
    """Test that canonical is the only execution source."""
    
    def test_canonical_runs(self):
        """Test canonical simulation can execute."""
        from app.simulation_engine import SimulationCore, SimulationConfig, SimulationType, DomainState
        
        core = SimulationCore()
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, num_iterations=5)
        domain = DomainState(domain="health", current_score=6.0)
        
        result = core.run_simulation(config, {"health": domain})
        
        assert result is not None
        assert result.status.value == "completed"


class TestArchitectureGuardCompliance:
    """Test architecture guard compliance."""
    
    def test_architecture_guard_exists(self):
        """Test that architecture guard script exists."""
        import os
        assert os.path.exists("scripts/architecture_guard.py")
    
    def test_canonical_path_in_guard(self):
        """Test that canonical simulation path is recognized."""
        import os
        with open("scripts/architecture_guard.py") as f:
            content = f.read()
        assert "app.simulation_engine" in content
