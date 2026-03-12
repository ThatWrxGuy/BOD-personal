#!/usr/bin/env python3
"""Check for circular dependencies in the PSIE codebase.

This script analyzes Python imports to detect potential circular dependencies.
"""
import ast
import os
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict, List


def get_imports(file_path: Path) -> Set[str]:
    """Extract imports from a Python file."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
    except:
        return set()
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    return imports


def build_dependency_graph(app_dir: Path) -> Dict[str, Set[str]]:
    """Build dependency graph for app modules."""
    graph = {}
    
    for py_file in app_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        rel_path = py_file.relative_to(app_dir)
        module_parts = rel_path.parts[:-1]  # Remove filename
        
        if not module_parts:
            continue
        
        module_name = ".".join(module_parts)
        
        imports = get_imports(py_file)
        
        # Filter to app imports
        app_imports = {imp for imp in imports if imp == "app"}
        
        graph[module_name] = app_imports
    
    return graph


def find_circular_dependencies(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Detect circular dependencies using DFS."""
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node: str, path: List[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                if dfs(neighbor, path.copy()):
                    return True
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                if cycle not in cycles:
                    cycles.append(cycle)
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    return cycles


def main():
    """Main function."""
    # Find app directory
    current_dir = Path(__file__).parent
    app_dir = current_dir / "personal_strategic_intelligence_engine" / "app"
    
    if not app_dir.exists():
        print("App directory not found, checking current directory...")
        app_dir = current_dir / "app"
    
    if not app_dir.exists():
        print("Error: Could not find app directory")
        return 1
    
    print(f"Analyzing dependencies in: {app_dir}")
    print("-" * 50)
    
    graph = build_dependency_graph(app_dir)
    
    print(f"Found {len(graph)} modules")
    print()
    
    cycles = find_circular_dependencies(graph)
    
    if cycles:
        print("WARNING: Potential circular dependencies found!")
        print()
        for i, cycle in enumerate(cycles, 1):
            print(f"Cycle {i}: {' -> '.join(cycle)}")
    else:
        print("✓ No circular dependencies detected")
    
    print()
    print("Top modules by import count:")
    sorted_modules = sorted(graph.items(), key=lambda x: len(x[1]), reverse=True)
    for module, imports in sorted_modules[:10]:
        print(f"  {module}: {len(imports)} imports")
    
    return 0


if __name__ == "__main__":
    exit(main())
