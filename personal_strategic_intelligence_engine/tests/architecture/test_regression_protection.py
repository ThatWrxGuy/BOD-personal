"""Architecture guard validation tests."""
import os
import subprocess
import sys


def test_architecture_guard_runs():
    """Test that architecture guard script executes without error."""
    result = subprocess.run(
        [sys.executable, "scripts/architecture_guard.py"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) or "."
    )
    # Guard should pass (exit code 0)
    assert result.returncode == 0, f"Architecture guard failed: {result.stderr}"


def test_no_legacy_simulation_imports():
    """Test that active modules don't import from legacy simulation paths."""
    result = subprocess.run(
        [sys.executable, "-c", """
import os
import sys

# Check for legacy simulation imports in active code
for root, dirs, files in os.walk('app'):
    if '__pycache__' in root or 'simulation' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path) as fp:
                content = fp.read()
                if 'from app.simulation ' in content or 'from app.strategy_simulation' in content or 'from app.monte_carlo' in content:
                    print(f'Legacy import in {path}')
                    sys.exit(1)
print('OK')
"""],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Legacy simulation imports found: {result.stdout}"


def test_no_deprecated_forecasting_imports():
    """Test that active modules don't import from deprecated forecasting paths."""
    result = subprocess.run(
        [sys.executable, "-c", """
import os
import sys

# Check for deprecated forecasting imports
deprecated = [
    'app.intelligence.forecasting_engine',
    'app.intelligence.trend_analyzer',
    'app.intelligence.risk_projection_engine',
    'app.intelligence.goal_probability_model',
]

for root, dirs, files in os.walk('app'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            # Skip wrapper files
            if 'intelligence/forecasting_engine.py' in path:
                continue
            if 'intelligence/trend_analyzer.py' in path:
                continue
            if 'intelligence/risk_projection_engine.py' in path:
                continue
            if 'intelligence/goal_probability_model.py' in path:
                continue
            with open(path) as fp:
                content = fp.read()
                for dep in deprecated:
                    if f'from {dep} ' in content or f'import {dep}' in content:
                        print(f'Deprecated import in {path}: {dep}')
                        sys.exit(1)
print('OK')
"""],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Deprecated forecasting imports found: {result.stdout}"


def test_canonical_simulation_imports():
    """Test that canonical simulation engine is importable."""
    from app.simulation_engine import SimulationCore, get_simulation_core
    assert SimulationCore is not None
    assert get_simulation_core is not None


def test_canonical_forecasting_imports():
    """Test that canonical forecasting is importable."""
    from app.forecasting import ForecastEngine, TrendAnalyzer, RiskProjector
    assert ForecastEngine is not None
    assert TrendAnalyzer is not None
    assert RiskProjector is not None


def test_no_versioned_filenames():
    """Test that active modules don't use versioned filenames."""
    result = subprocess.run(
        [sys.executable, "-c", """
import os
import re

patterns = [r'_v2\\.py$', r'_v3\\.py$', r'_new\\.py$', r'_temp\\.py$', r'_experimental\\.py$']
pattern = re.compile('|'.join(patterns))

violations = []
for root, dirs, files in os.walk('app'):
    if '__pycache__' in root or '/tests' in root:
        continue
    for f in files:
        if pattern.search(f):
            violations.append(os.path.join(root, f))

if violations:
    print('Versioned files found:', violations)
    exit(1)
print('OK')
"""],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Versioned filenames found: {result.stdout}"
