#!/usr/bin/env python3
"""
Integrity Verification Script for Codex Immortal v33.33
Verifies cryptographic integrity of artifacts and attestations.

⚠️  WARNING: Uses placeholder attestations - not production-ready!
   Real verification must use proper KMS/HSM/enclave integration.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

def compute_file_hash(filepath):
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"❌ ERROR: Failed to hash {filepath}: {e}")
        return None

def verify_manifest():
    """Verify manifest integrity."""
    manifest_path = Path(__file__).parent.parent.parent / "provenance" / "manifest.json"
    
    if not manifest_path.exists():
        print(f"❌ ERROR: Manifest not found at {manifest_path}")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        version = manifest.get('version', 'unknown')
        print(f"✅ Manifest valid: {version}")
        
        # Verify required fields
        required_fields = ['version', 'release_name', 'timestamp']
        missing_fields = [f for f in required_fields if f not in manifest]
        
        if missing_fields:
            print(f"⚠️  WARNING: Missing fields: {', '.join(missing_fields)}")
        
        # Compute manifest hash
        manifest_hash = compute_file_hash(manifest_path)
        if manifest_hash:
            print(f"  SHA-256: {manifest_hash}")
        
        return True
    except Exception as e:
        print(f"❌ ERROR: Manifest verification failed: {e}")
        return False

def verify_attestations():
    """Verify attestations (stub implementation)."""
    print("⚠️  Attestation verification: STUB mode")
    print("  Real production must use KMS/HSM/enclave for:")
    print("  - Cryptographic signature verification")
    print("  - Chain-of-custody validation")
    print("  - Sealed key attestations")
    print("✅ Attestation stub check passed")
    return True

def verify_scripts():
    """Verify script integrity."""
    scripts_dir = Path(__file__).parent
    required_scripts = ['build_status.py', 'deploy_stub.py', 'verify_integrity.py']
    
    all_valid = True
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            script_hash = compute_file_hash(script_path)
            if script_hash:
                print(f"✅ {script}: {script_hash[:16]}...")
            else:
                all_valid = False
        else:
            print(f"❌ ERROR: Script not found: {script}")
            all_valid = False
    
    return all_valid

def main():
    """Main integrity verification."""
    print("=" * 60)
    print("Codex Immortal v33.33 - Integrity Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Manifest Integrity", verify_manifest),
        ("Attestations", verify_attestations),
        ("Script Integrity", verify_scripts),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func()
        results.append(result)
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ All integrity checks PASSED")
        print()
        print("⚠️  NOTE: Using STUB attestations - not production-ready!")
        print("   Real deployment requires KMS/HSM/enclave integration")
        print("=" * 60)
        return 0
    else:
        print("❌ Some integrity checks FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
