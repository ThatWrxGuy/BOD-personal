#!/usr/bin/env python3
"""
ORM Boundary Guard - Detects SQLAlchemy ORM definitions outside app/models/

Usage:
    python check_orm_boundary.py [--fix]
"""
import os
import re
import sys
from pathlib import Path

# Files that are allowed to have ORM definitions
ALLOWED_ORM_PATHS = [
    "app/models/",
    "app/db/base.py",
    "app/db/__init__.py",
    "app/core/audit.py",  # Core infrastructure
]

# Files that should NOT have ORM definitions
FORBIDDEN_TYPES_PATTERNS = [
    "app/*/*_types.py",
    "app/*/types.py",
]

def find_orm_classes(file_path: Path) -> list[str]:
    """Find SQLAlchemy ORM class definitions in a file."""
    orm_classes = []
    try:
        content = file_path.read_text()
    except Exception:
        return orm_classes
    
    # Check for SQLAlchemy declarative patterns
    # Must have Base (SQLAlchemy) not BaseModel (Pydantic)
    for match in re.finditer(r"class\s+(\w+)\s*\(\s*Base\s*,", content):
        # Make sure it's not BaseModel
        before = content[max(0, match.start()-100):match.start()]
        if "BaseModel" not in before:
            orm_classes.append(match.group(1))
    
    # Also check for __tablename__ (strong indicator of ORM)
    if "__tablename__" in content and "BaseModel" not in content:
        # Find class with __tablename__
        for match in re.finditer(r"class\s+(\w+)\s*\([^)]*\):", content):
            class_def = content[match.start():match.start()+200]
            if "__tablename__" in class_def and "BaseModel" not in class_def:
                orm_classes.append(match.group(1))
    
    return orm_classes

def is_allowed_path(path: str) -> bool:
    """Check if path is allowed to have ORM definitions."""
    for allowed in ALLOWED_ORM_PATHS:
        if allowed in path:
            return True
    return False

def check_orm_boundaries(base_path: Path, fix: bool = False) -> dict:
    """Check for ORM boundary violations."""
    violations = []
    
    # Find all Python files
    py_files = list(base_path.rglob("*.py"))
    
    for py_file in py_files:
        rel_path = str(py_file.relative_to(base_path))
        
        # Skip allowed paths
        if is_allowed_path(rel_path):
            continue
        
        # Skip __pycache__ and test files
        if "__pycache__" in rel_path or "test" in rel_path.lower():
            continue
        
        # Check for ORM classes
        orm_classes = find_orm_classes(py_file)
        
        if orm_classes:
            violations.append({
                "file": rel_path,
                "classes": orm_classes,
                "should_import_from": f"app.models.{py_file.parent.name}" if "app/" in rel_path else None
            })
    
    return {
        "violations": violations,
        "total": len(violations),
        "status": "PASS" if len(violations) == 0 else "FAIL"
    }

if __name__ == "__main__":
    base_path = Path("/workspace/project/BOD-personal/personal_strategic_intelligence_engine")
    fix_mode = "--fix" in sys.argv
    
    result = check_orm_boundaries(base_path, fix_mode)
    
    print("=" * 60)
    print("ORM Boundary Guard Check")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Total violations: {result['total']}")
    print()
    
    if result['violations']:
        print("Violations found:")
        for v in result['violations']:
            print(f"  - {v['file']}: {', '.join(v['classes'])}")
            if v['should_import_from']:
                print(f"    Should import from: {v['should_import_from']}")
        sys.exit(1)
    else:
        print("No violations found. ORM boundaries are clean.")
        sys.exit(0)
