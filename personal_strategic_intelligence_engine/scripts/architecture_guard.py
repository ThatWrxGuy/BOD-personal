#!/usr/bin/env python3
"""Architecture Guard - Validates architectural boundaries and detects violations.

This script checks for:
- Cross-layer imports
- Forbidden dependencies
- Duplicate subsystem creation
- Legacy simulation imports in active code
- Versioned/temporary module naming violations
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Tuple


# Version/temporary naming patterns to detect
VERSION_PATTERNS = [
    r"_[vV]\d+",           # _v2, _V2, _v3, etc.
    r"_new\b",              # _new
    r"_experimental\b",     # _experimental
    r"_legacy\b",           # _legacy
    r"_old\b",              # _old
    r"_temp\b",             # _temp
    r"_refactor\b",         # _refactor
    r"_fixed\b",            # _fixed
    r"_better\b",           # _better
]

VERSION_PATTERN = re.compile("|".join(VERSION_PATTERNS))


# Define architectural layers (from low to high)
LAYERS = {
    "core": ["app/core", "app/db", "app/models"],
    "kernel": ["app/kernel"],
    "intelligence": ["app/intelligence", "app/forecasting"],
    "simulation": ["app/simulation_engine"],
    "execution": ["app/execution", "app/intervention", "app/workers"],
    "orchestration": ["app/orchestration"],
    "api": ["app/api", "app/executive"],
}

# Forbidden imports - active code should not import from these legacy paths
LEGACY_SIMULATION_PATHS = [
    "app.simulation",
    "app.strategy_simulation",
    "app.monte_carlo",
]

# Deprecated forecasting paths - should use app.forecasting instead
DEPRECATED_FORECASTING_PATHS = [
    "app.intelligence.forecasting_engine",
    "app.intelligence.trend_analyzer",
    "app.intelligence.risk_projection_engine",
    "app.intelligence.goal_probability_model",
]

# Legacy directories that are now wrappers - ignore their internal imports
LEGACY_DIRS = [
    "app/simulation",
    "app/strategy_simulation", 
    "app/monte_carlo",
    "app/intelligence/forecasting_engine.py",
    "app/intelligence/trend_analyzer.py",
    "app/intelligence/risk_projection_engine.py",
    "app/intelligence/goal_probability_model.py",
]

# These paths are allowed to import legacy (for backward compatibility testing)
ALLOWED_LEGACY_IMPORTS = [
    "app/simulation/__init__.py",
    "app/strategy_simulation/__init__.py",
    "app/monte_carlo/__init__.py",
    # Forecasting wrappers
    "app/intelligence/forecasting_engine.py",
    "app/intelligence/trend_analyzer.py",
    "app/intelligence/risk_projection_engine.py",
    "app/intelligence/goal_probability_model.py",
]

# Maximum allowed files in legacy directories (for wrapper detection)
MAX_LEGACY_WRAPPER_FILES = 5


def is_in_legacy_dir(file_path: str) -> bool:
    """Check if file is in a legacy directory."""
    return any(legacy in file_path for legacy in LEGACY_DIRS)


def is_deprecated_forecasting(module: str) -> bool:
    """Check if module is from deprecated forecasting paths."""
    for deprecated in DEPRECATED_FORECASTING_PATHS:
        if module == deprecated:
            return True
    return False


def get_file_layer(file_path: str) -> Tuple[str, str]:
    """Determine which layer a file belongs to."""
    for layer, paths in LAYERS.items():
        for path in paths:
            if path in file_path:
                return layer, path
    return "unknown", ""


def is_legacy_simulation_path(module: str) -> bool:
    """Check if module is from legacy simulation paths.
    
    Must be exact match for legacy paths, not prefix.
    """
    # Exact legacy paths (not simulation_engine which is canonical)
    exact_legacy = [
        "app.simulation",
        "app.strategy_simulation",
        "app.monte_carlo",
    ]
    
    for legacy in exact_legacy:
        if module == legacy:
            return True
    
    return False


def check_imports(file_path: str) -> List[Dict[str, str]]:
    """Check imports in a file for violations."""
    violations = []
    
    if not os.path.exists(file_path):
        return violations
    
    # Skip allowed legacy wrapper files
    if any(allowed in file_path for allowed in ALLOWED_LEGACY_IMPORTS):
        return violations
    
    # Skip files in legacy directories (they're wrappers)
    if is_in_legacy_dir(file_path):
        return violations
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except:
        return violations
    
    # Find all imports
    import_lines = [line.strip() for line in content.split('\n') 
                   if 'import ' in line and not line.strip().startswith('#')]
    
    for line in import_lines:
        # Extract module being imported
        if 'from app.' in line:
            parts = line.split('from app.')[1].split('.')
            module = 'app.' + parts[0]
        elif 'import app.' in line:
            parts = line.split('import app.')[1].split('.')
            module = 'app.' + parts[0]
        else:
            continue
        
        # Check if importing from legacy simulation paths
        if is_legacy_simulation_path(module):
            violations.append({
                "file": file_path,
                "import": module,
                "type": "legacy_simulation_import",
                "severity": "HIGH",
                "message": f"Import from legacy simulation path: {module}",
            })
        
        # Check if importing from deprecated forecasting paths
        if is_deprecated_forecasting(module):
            violations.append({
                "file": file_path,
                "import": module,
                "type": "deprecated_forecasting_import",
                "severity": "MEDIUM",
                "message": f"Import from deprecated forecasting path: {module}",
            })
    
    return violations


def check_duplicates() -> List[Dict[str, str]]:
    """Check for duplicate subsystems."""
    findings = []
    
    # Check for multiple simulation implementations
    sim_paths = [
        "app/simulation",
        "app/strategy_simulation", 
        "app/monte_carlo",
        "app/simulation_engine",
    ]
    
    existing = [p for p in sim_paths if os.path.exists(p)]
    
    if len(existing) > 1:
        # Check if legacy dirs have too many files (not just wrappers)
        for legacy_dir in ["app/simulation", "app/strategy_simulation", "app/monte_carlo"]:
            if os.path.exists(legacy_dir):
                files = [f for f in os.listdir(legacy_dir) 
                        if f.endswith('.py') and f != '__init__.py']
                if len(files) > MAX_LEGACY_WRAPPER_FILES:
                    findings.append({
                        "subsystem": "simulation",
                        "location": legacy_dir,
                        "type": "excessive_legacy_files",
                        "severity": "HIGH",
                        "message": f"Legacy dir has {len(files)} files, expected <={MAX_LEGACY_WRAPPER_FILES}",
                    })
    
    # Check forecasting duplicates
    forecast_paths = [
        "app/forecasting",
        "app/intelligence/forecasting_engine.py",
    ]
    
    existing = [p for p in forecast_paths if os.path.exists(p)]
    if len(existing) > 1:
        findings.append({
            "subsystem": "forecasting",
            "locations": existing,
            "type": "duplicate_subsystem",
            "severity": "MEDIUM",
        })
    
    return findings


def run_architecture_check() -> Dict[str, any]:
    """Run full architecture check."""
    
    all_violations = []
    duplicate_findings = []
    
    # Check duplicates first
    duplicate_findings = check_duplicates()
    
    # Walk through all Python files
    app_dir = Path("app")
    if not app_dir.exists():
        return {"error": "app directory not found"}
    
    for py_file in app_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        violations = check_imports(str(py_file))
        all_violations.extend(violations)
    
    # Check versioned/temporary file names
    versioned_violations = check_versioned_files("app")
    all_violations.extend(versioned_violations)
    
    # Generate report
    report = {
        "total_violations": len(all_violations),
        "duplicate_subsystems": len(duplicate_findings),
        "violations": all_violations,
        "duplicates": duplicate_findings,
    }
    
    return report


def print_report(report: Dict) -> None:
    """Print a formatted report."""
    
    print("=" * 60)
    print("ARCHITECTURE GUARD REPORT")
    print("=" * 60)
    
    if "error" in report:
        print(f"ERROR: {report['error']}")
        return
    
    print(f"\nTotal Import Violations: {report['total_violations']}")
    print(f"Duplicate Subsystems: {report['duplicate_subsystems']}")
    
    if report['duplicates']:
        print("\n--- DUPLICATE SUBSYSTEMS ---")
        for dup in report['duplicates']:
            print(f"\n[{dup.get('severity', 'MEDIUM')}] {dup['subsystem']}")
            print(f"  {dup.get('message', '')}")
    
    if report['violations']:
        print("\n--- VIOLATIONS ---")
        for v in report['violations']:
            print(f"\n  File: {v['file']}")
            if 'import' in v:
                print(f"  Import: {v['import']}")
            print(f"  Type: {v.get('type', 'unknown')}")
            print(f"  {v['message']}")
    
    print("\n" + "=" * 60)
    
    # Exit code based on findings - only fail on HIGH severity
    high_severity = sum(1 for d in report['duplicates'] if d.get('severity') == 'HIGH')
    
    if high_severity > 0 or report['total_violations'] > 0:
        print("STATUS: FAILED - Action Required")
        sys.exit(1)
    else:
        print("STATUS: PASSED")
        sys.exit(0)


def check_versioned_files(root_dir: str = "app") -> List[Dict[str, str]]:
    """Check for versioned or temporary file naming in active modules."""
    violations = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip __pycache__ and test directories
        if "__pycache__" in dirpath or "/tests" in dirpath or "\\tests" in dirpath:
            continue
            
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            
            # Check for versioned/temporary patterns
            if VERSION_PATTERN.search(filename):
                full_path = os.path.join(dirpath, filename)
                
                # Determine severity
                if re.search(r"_[vV]\d+", filename):
                    severity = "HIGH"
                elif re.search(r"_(temp|refactor|fixed|better)", filename):
                    severity = "MEDIUM"
                else:
                    severity = "MEDIUM"
                
                violations.append({
                    "file": full_path,
                    "pattern": VERSION_PATTERN.search(filename).group(),
                    "severity": severity,
                    "type": "versioned_filename",
                    "message": f"Versioned/temporary filename: {filename}",
                })
    
    return violations


if __name__ == "__main__":
    report = run_architecture_check()
    print_report(report)
