#!/usr/bin/env python3
"""
Build Status Verification Script for Codex Immortal v33.33
Verifies build artifacts and reports build status.
"""

import sys
import os
import json
from pathlib import Path

def check_manifest():
    """Verify manifest.json exists and is valid."""
    manifest_path = Path(__file__).parent.parent.parent / "provenance" / "manifest.json"
    
    if not manifest_path.exists():
        print(f"❌ ERROR: Manifest not found at {manifest_path}")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        version = manifest.get('version', 'unknown')
        print(f"✅ Manifest found: version {version}")
        
        if version != 'v33.33':
            print(f"⚠️  WARNING: Expected version v33.33, got {version}")
            return False
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in manifest: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to read manifest: {e}")
        return False

def check_workflow():
    """Verify GitHub workflow exists."""
    workflow_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "v33_33_release.yml"
    
    if not workflow_path.exists():
        print(f"❌ ERROR: Workflow not found at {workflow_path}")
        return False
    
    print(f"✅ Workflow file exists: {workflow_path.name}")
    return True

def check_scripts():
    """Verify all required scripts exist."""
    scripts_dir = Path(__file__).parent
    required_scripts = ['build_status.py', 'deploy_stub.py', 'verify_integrity.py']
    
    all_exist = True
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"✅ Script found: {script}")
        else:
            print(f"❌ ERROR: Script not found: {script}")
            all_exist = False
    
    return all_exist

def main():
    """Main build status check."""
    print("=" * 60)
    print("Codex Immortal v33.33 - Build Status Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Manifest", check_manifest),
        ("Workflow", check_workflow),
        ("Scripts", check_scripts),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name} Check]")
        result = check_func()
        results.append(result)
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ All build status checks PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ Some build status checks FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
