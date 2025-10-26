#!/usr/bin/env python3
"""
Continuum Orchestration Script
Codex Continuum v100 - Continuum Σ (Sigma)

Orchestrates the complete pipeline from verification to deployment
"""
import subprocess
import sys
import os
import json
from pathlib import Path

PIPELINE_STEPS = [
    ("🌀 VERIFY", "scripts/verify_v100.py"),
    ("🧾 AUDIT", None),  # Built into other steps
    ("🛡 SCAN", "scripts/vuln_gate.py"),
    ("🔮 ATTEST", None),  # Future step
    ("🛡‍🔥 SANCTIFY", "scripts/sign.py"),
    ("🚦 ROLLOUT", "scripts/rollout.py"),
    ("⚖️ JUDGE", "scripts/judge.py"),
    ("🌈 DEPLOY", None),  # External deployment
    ("♾ CONTINUUM", None),  # Continuous loop
]

def run_step(step_name: str, script_path: str, args: list = None) -> bool:
    """Run a pipeline step"""
    print(f"\n{step_name}")
    print("=" * 60)
    
    if not script_path:
        print("ℹ️  Step is integrated into other stages")
        return True
    
    if not os.path.exists(script_path):
        print(f"⚠️  Script not found: {script_path}")
        return True  # Don't fail on optional scripts
    
    cmd = ["python", script_path] + (args or [])
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {step_name} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {step_name} failed with exit code {e.returncode}")
        return False

def main():
    print("🌌 Codex Continuum v100 Pipeline")
    print("   Release: Continuum Σ (Sigma)")
    print("=" * 60)
    
    # Default pipeline execution
    manifest_file = sys.argv[1] if len(sys.argv) > 1 else "codex/manifest.v100.json"
    
    # Check if manifest exists
    if not os.path.exists(manifest_file):
        print(f"\n⚠️  Manifest not found: {manifest_file}")
        print("   Creating manifest first...")
        if not run_step("📦 Generate Manifest", "scripts/hash_v100.py", [".", manifest_file]):
            sys.exit(1)
    
    # Run pipeline steps
    success = True
    
    # VERIFY
    if not run_step(PIPELINE_STEPS[0][0], PIPELINE_STEPS[0][1], [manifest_file, "."]):
        success = False
    
    # SCAN (check for SBOM first)
    sbom_file = "sbom.json"
    if not os.path.exists(sbom_file):
        print("\n🔍 Generating SBOM...")
        run_step("Generate SBOM", "scripts/sbom_gen.py", [".", sbom_file])
    
    if os.path.exists(sbom_file):
        if not run_step(PIPELINE_STEPS[2][0], PIPELINE_STEPS[2][1], [sbom_file]):
            print("\n⚠️  Vulnerability gate failed - review and fix issues")
            success = False
    
    # SANCTIFY (sign)
    if success:
        run_step(PIPELINE_STEPS[4][0], PIPELINE_STEPS[4][1], [manifest_file])
    
    # ROLLOUT
    if success and os.path.exists("scripts/rollout.py"):
        run_step(PIPELINE_STEPS[5][0], PIPELINE_STEPS[5][1])
    
    # JUDGE
    if success and os.path.exists("scripts/judge.py"):
        run_step(PIPELINE_STEPS[6][0], PIPELINE_STEPS[6][1])
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ CONTINUUM PIPELINE COMPLETED SUCCESSFULLY")
        print("\nNext steps:")
        print("  1. Review signed artifacts")
        print("  2. Deploy to target environment")
        print("  3. Monitor deployment health")
        sys.exit(0)
    else:
        print("❌ CONTINUUM PIPELINE FAILED")
        print("\nReview errors above and fix issues before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()
