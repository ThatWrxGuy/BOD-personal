#!/usr/bin/env python3
"""Architecture Guard - Validates architectural boundaries and detects violations.

This script checks for:
- Cross-layer imports
- Forbidden dependencies
- Duplicate subsystem creation
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
    "simulation": ["app/simulation_engine", "app/simulation", "app/strategy_simulation", "app/monte_carlo"],
    "execution": ["app/execution", "app/intervention", "app/workers"],
    "orchestration": ["app/orchestration"],
    "api": ["app/api", "app/executive"],
}

# Forbidden dependencies (layer -> cannot import these)
FORBIDDEN = {
    "core": ["app/api", "app/executive"],
    "kernel": [],
    "intelligence": ["app/api", "app/executive"],
    "simulation": ["app/api"],
    "execution": [],
    "orchestration": [],
    "api": ["app/core"],  # API shouldn't control core directly
}

# Duplicate subsystems that should be consolidated
DUPLICATES = {
    "simulation": [
        "app/simulation",
        "app/strategy_simulation", 
        "app/monte_carlo",
        "app/simulation_engine",  # Target
    ],
    "forecasting": [
        "app/forecasting",
        "app/intelligence/forecasting_engine.py",
    ],
}


def get_file_layer(file_path: str) -> Tuple[str, str]:
    """Determine which layer a file belongs to."""
    for layer, paths in LAYERS.items():
        for path in paths:
            if path in file_path:
                return layer, path
    return "unknown", ""


def check_imports(file_path: str) -> List[Dict[str, str]]:
    """Check imports in a file for violations."""
    violations = []
    
    if not os.path.exists(file_path):
        return violations
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except:
        return violations
    
    # Get current file's layer
    current_layer, _ = get_file_layer(file_path)
    
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
        
        # Check if import is from a forbidden layer
        if current_layer in FORBIDDEN:
            for forbidden in FORBIDDEN[current_layer]:
                if forbidden in import_path:
                    violations.append({
                        "file": file_path,
                        "layer": current_layer,
                        "import": import_path,
                        "forbidden": forbidden,
                        "type": "cross_layer_import",
                    })
    
    return violations


def check_duplicates() -> List[Dict[str, str]]:
    """Check for duplicate subsystems."""
    findings = []
    
    for subsystem, paths in DUPLICATES.items():
        existing = [p for p in paths if os.path.exists(p)]
        
        if len(existing) > 1:
            findings.append({
                "subsystem": subsystem,
                "locations": existing,
                "type": "duplicate_subsystem",
                "severity": "HIGH",
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
            print(f"\n[{dup['severity']}] {dup['subsystem']}")
            print(f"  Found at: {', '.join(dup['locations'])}")
    
    if report['violations']:
        print("\n--- IMPORT VIOLATIONS ---")
        for v in report['violations'][:10]:  # Show first 10
            print(f"\n  File: {v['file']}")
            print(f"  Layer: {v['layer']} imports {v['import']}")
            print(f"  Forbidden: {v['forbidden']}")
    
    print("\n" + "=" * 60)
    
    # Exit code based on findings
    if report['duplicate_subsystems'] > 0 or report['total_violations'] > 5:
        print("STATUS: FAILED - Action Required")
        sys.exit(1)
    else:
        print("STATUS: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    report = run_architecture_check()
    print_report(report)
