#!/usr/bin/env python3
"""
Build script for v94 bundle
Orchestrates the complete build process
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"✗ {description} failed with exit code {result.returncode}")
        return False
    elif result.returncode == 0:
        print(f"✓ {description} completed successfully")
    
    return result.returncode == 0

def main():
    """Main build orchestration"""
    print("🚀 Building Codex v94 Bundle")
    print("="*60)
    
    steps = [
        {
            "cmd": ["python", "-m", "py_compile", "app.py"],
            "desc": "Syntax check: app.py",
            "required": True
        },
        {
            "cmd": ["python", "-m", "py_compile", "glyph_guard_v14.py"],
            "desc": "Syntax check: glyph_guard_v14.py",
            "required": True
        },
        {
            "cmd": ["python", "glyph_guard_v14.py", "test-glyph"],
            "desc": "Test Glyph Guard",
            "required": True
        },
        {
            "cmd": ["python", "generate_sbom.py"],
            "desc": "Generate SBOM",
            "required": False
        },
        {
            "cmd": ["python", "scan_vulnerabilities.py", "--skip"],
            "desc": "Vulnerability scan (skipped - optional tool)",
            "required": False
        }
    ]
    
    failed_steps = []
    
    for step in steps:
        success = run_command(step["cmd"], step["desc"], check=step["required"])
        if not success and step["required"]:
            failed_steps.append(step["desc"])
    
    print("\n" + "="*60)
    print("📊 Build Summary")
    print("="*60)
    
    if failed_steps:
        print(f"✗ Build failed. {len(failed_steps)} required step(s) failed:")
        for step in failed_steps:
            print(f"  - {step}")
        return 1
    else:
        print("✓ Build completed successfully!")
        print("\nNext steps:")
        print("  1. docker build -t codex-v94:latest .")
        print("  2. docker run -p 8000:8000 codex-v94:latest")
        print("  3. kubectl apply -f k8s/deployment-hardened.yaml")
        return 0

if __name__ == "__main__":
    sys.exit(main())
