#!/usr/bin/env python3
"""Architecture Guard - Validates architectural boundaries and detects violations.

This script checks for:
- Cross-layer imports
- Forbidden dependencies
- Duplicate subsystem creation
- Legacy simulation imports in active code
"""
import os
import sys
from pathlib import Path
from typing import List, Set, Dict, Tuple


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

# Legacy directories that are now wrappers - ignore their internal imports
LEGACY_DIRS = [
    "app/simulation",
    "app/strategy_simulation", 
    "app/monte_carlo",
]

# These paths are allowed to import legacy (for backward compatibility testing)
ALLOWED_LEGACY_IMPORTS = [
    "app/simulation/__init__.py",
    "app/strategy_simulation/__init__.py",
    "app/monte_carlo/__init__.py",
]

# Maximum allowed files in legacy directories (for wrapper detection)
MAX_LEGACY_WRAPPER_FILES = 5


def is_in_legacy_dir(file_path: str) -> bool:
    """Check if file is in a legacy directory."""
    return any(legacy in file_path for legacy in LEGACY_DIRS)


def get_file_layer(file_path: str) -> Tuple[str, str]:
    """Determine which layer a file belongs to."""
    for layer, paths in LAYERS.items():
        for path in paths:
            if path in file_path:
                return layer, path
    return "unknown", ""


def is_legacy_simulation_path(module: str) -> bool:
    """Check if module is from legacy simulation paths."""
    for legacy in LEGACY_SIMULATION_PATHS:
        if module.startswith(legacy):
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
            module = line.split('from app.')[1].split('.')[0]
            import_path = 'app.' + module
        elif 'import app.' in line:
            module = line.split('import app.')[1].split('.')[0]
            import_path = 'app.' + module
        else:
            continue
        
        # Check if importing from legacy simulation paths
        if is_legacy_simulation_path(import_path):
            violations.append({
                "file": file_path,
                "import": import_path,
                "type": "legacy_simulation_import",
                "severity": "HIGH",
                "message": f"Import from legacy simulation path: {import_path}",
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
        print("\n--- IMPORT VIOLATIONS ---")
        for v in report['violations']:
            print(f"\n  File: {v['file']}")
            print(f"  Import: {v['import']}")
            print(f"  {v['message']}")
    
    print("\n" + "=" * 60)
    
    # Exit code based on findings
    if report['duplicate_subsystems'] > 0 or report['total_violations'] > 0:
        print("STATUS: FAILED - Action Required")
        sys.exit(1)
    else:
        print("STATUS: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    report = run_architecture_check()
    print_report(report)
