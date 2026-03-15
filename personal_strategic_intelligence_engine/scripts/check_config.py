#!/usr/bin/env python3
"""Configuration check script.

Run this script to check PSIE configuration readiness without starting the server.
"""
import sys
from app.core.config_check import get_readiness_report
from app.core.config_validation import validate_config


def main():
    """Run configuration checks."""
    print("=" * 60)
    print("PSIE Configuration Readiness Check")
    print("=" * 60)
    
    # Get readiness report
    print("\n📊 Readiness Report:")
    print("-" * 40)
    report = get_readiness_report()
    
    overall = report["overall"]
    print(f"\nOverall Status: {overall['status']}")
    print(f"Message: {overall.get('message', 'N/A')}")
    
    if overall.get("issues"):
        print("\n⚠️  Issues:")
        for issue in overall["issues"]:
            print(f"  - {issue}")
    
    # Component statuses
    print("\n📦 Component Statuses:")
    print("-" * 40)
    
    components = [
        ("Core", report.get("core", {})),
        ("Database", report.get("database", {})),
        ("LLM", report.get("llm", {})),
        ("Workers", report.get("workers", {})),
        ("Connectors", report.get("connectors", {})),
        ("Execution", report.get("execution", {})),
        ("Learning", report.get("learning", {})),
        ("Safety", report.get("safety", {})),
    ]
    
    for name, data in components:
        status = data.get("status", "UNKNOWN")
        emoji = "✅" if status == "READY" else "⚠️" if status in ["PARTIAL", "WARNING"] else "❌" if status in ["MISSING", "UNSAFE"] else "🔶"
        print(f"  {emoji} {name}: {status}")
    
    # Run validation
    print("\n🔍 Configuration Validation:")
    print("-" * 40)
    is_valid, errors, warnings = validate_config()
    
    if is_valid:
        print("✅ Configuration validation passed!")
    else:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Execution status
    exec_data = report.get("execution", {})
    print("\n🔐 Execution Safety:")
    print("-" * 40)
    print(f"  Execution Enabled: {exec_data.get('enabled', False)}")
    print(f"  Safe Mode: {exec_data.get('safe_mode', True)}")
    print(f"  Manual Approval Required: {exec_data.get('manual_approval_required', True)}")
    print(f"  Kill Switch Enabled: {exec_data.get('kill_switch_enabled', True)}")
    
    # Connectors
    conn_data = report.get("connectors", {}).get("connectors", {})
    print("\n🔌 Connector Status:")
    print("-" * 40)
    for name, data in conn_data.items():
        status = "✅ Enabled" if data.get("enabled") else "❌ Disabled"
        configured = " (configured)" if data.get("configured") else ""
        print(f"  {name.capitalize()}: {status}{configured}")
    
    print("\n" + "=" * 60)
    
    # Exit code
    if not is_valid:
        print("❌ Please fix the errors above before running PSIE")
        return 1
    
    if overall["status"] != "READY":
        print("⚠️  System may not function correctly - fix warnings above")
        return 1
    
    print("✅ System is ready to run!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
