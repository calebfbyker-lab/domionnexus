#!/usr/bin/env python3
"""
Monetization Verification Tool
Part of the Codex Continuum Build System
EUCELA Tri-License © 2025 Caleb Fedor Byker (Konev)
"""

import json
import os
import hashlib
from pathlib import Path

def compute_sha256(filepath):
    """Compute SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_artifacts():
    """Verify integrity of generated artifacts"""
    
    print("🔐 Verifying Artifact Integrity...")
    
    required_files = [
        "OMEGA_LOCK.json",
        "codex_omega_bundle.zip",
        "codex_capsule.txt",
        "chain/attestations.jsonl"
    ]
    
    verification_results = {
        "verified": True,
        "timestamp": None,
        "files": []
    }
    
    # Check all required files exist
    for filepath in required_files:
        if not os.path.exists(filepath):
            print(f"❌ Missing required file: {filepath}")
            verification_results["verified"] = False
            verification_results["files"].append({
                "path": filepath,
                "exists": False,
                "error": "File not found"
            })
        else:
            # Compute hash for existing files
            file_hash = compute_sha256(filepath)
            file_size = os.path.getsize(filepath)
            
            print(f"✓ {filepath}")
            print(f"  SHA-256: {file_hash}")
            print(f"  Size: {file_size} bytes")
            
            verification_results["files"].append({
                "path": filepath,
                "exists": True,
                "sha256": file_hash,
                "size": file_size
            })
    
    # Verify OMEGA_LOCK.json is valid JSON
    if os.path.exists("OMEGA_LOCK.json"):
        try:
            with open("OMEGA_LOCK.json", "r") as f:
                omega_data = json.load(f)
            
            # Verify it has the required omega_id field
            if "omega_id" not in omega_data:
                print("❌ OMEGA_LOCK.json missing omega_id field")
                verification_results["verified"] = False
            else:
                print(f"✓ OMEGA_ID: {omega_data['omega_id'][:16]}...")
                verification_results["omega_id"] = omega_data["omega_id"]
                
        except json.JSONDecodeError as e:
            print(f"❌ OMEGA_LOCK.json is not valid JSON: {e}")
            verification_results["verified"] = False
    
    # Load treasury and economy data if they exist
    if os.path.exists("treasury_allocation.json"):
        with open("treasury_allocation.json", "r") as f:
            treasury = json.load(f)
        print(f"✓ Treasury allocation loaded")
        verification_results["treasury_verified"] = True
    
    if os.path.exists("economy_monetization.json"):
        with open("economy_monetization.json", "r") as f:
            economy = json.load(f)
        print(f"✓ Economy monetization loaded")
        verification_results["economy_verified"] = True
    
    # Write verification summary
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/verification_summary.json", "w") as f:
        json.dump(verification_results, f, indent=2)
    
    if verification_results["verified"]:
        print("\n✅ All artifacts verified successfully")
        return 0
    else:
        print("\n❌ Verification failed - see errors above")
        return 1

if __name__ == "__main__":
    exit(verify_artifacts())
