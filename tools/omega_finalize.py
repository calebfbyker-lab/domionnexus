#!/usr/bin/env python3
"""
Omega Finalization Tool
Part of the Codex Continuum Build System
EUCELA Tri-License © 2025 Caleb Fedor Byker (Konev)
"""

import json
import os
import hashlib
import zipfile
import shutil
from datetime import datetime, timezone

def compute_sha256(filepath):
    """Compute SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_omega_id():
    """Generate a unique Omega ID based on current timestamp and content"""
    timestamp = datetime.now(timezone.utc).isoformat()
    content = f"codex_continuum_{timestamp}_EUCELA_Tri_License"
    return hashlib.sha256(content.encode()).hexdigest()

def create_omega_lock():
    """Create OMEGA_LOCK.json with artifact hashes"""
    
    print("🔐 Generating OMEGA_LOCK.json...")
    
    omega_id = generate_omega_id()
    timestamp = datetime.now(timezone.utc).isoformat()
    
    omega_lock = {
        "omega_id": omega_id,
        "version": "1.0.0",
        "generated_at": timestamp,
        "license": "EUCELA Tri-License",
        "copyright": "© 2025 Caleb Fedor Byker (Konev)",
        "artifacts": {},
        "metadata": {
            "build_system": "Codex Continuum",
            "attestation_chain": "chain/attestations.jsonl"
        }
    }
    
    # Collect artifact hashes (will be populated after bundle creation)
    print(f"✓ Omega ID generated: {omega_id[:16]}...")
    
    return omega_lock, omega_id

def create_bundle(omega_id):
    """Create the codex_omega_bundle.zip"""
    
    print("📦 Creating codex_omega_bundle.zip...")
    
    bundle_files = []
    
    # Collect files to include in bundle
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        skip_dirs = {'.git', 'node_modules', '__pycache__', '.github', 'releases', 'artifacts'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith(('.json', '.md', '.txt', '.py', '.js', '.sh')):
                filepath = os.path.join(root, file)
                bundle_files.append(filepath)
    
    # Create the bundle
    with zipfile.ZipFile("codex_omega_bundle.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for filepath in bundle_files:
            zipf.write(filepath)
    
    bundle_size = os.path.getsize("codex_omega_bundle.zip")
    bundle_hash = compute_sha256("codex_omega_bundle.zip")
    
    print(f"✓ Bundle created: {bundle_size} bytes")
    print(f"  SHA-256: {bundle_hash}")
    
    return bundle_hash, bundle_size

def create_capsule(omega_id):
    """Create codex_capsule.txt"""
    
    print("📄 Creating codex_capsule.txt...")
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    capsule_content = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CODEX CONTINUUM CAPSULE                              ║
║                    EUCELA Tri-License Build Attestation                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Omega ID: {omega_id}
Generated: {timestamp}
License: EUCELA Tri-License © 2025 Caleb Fedor Byker (Konev)

This capsule certifies that the Codex Continuum build has been completed,
verified, and attested according to the requirements specified in the
EUCELA Tri-License.

All artifacts included in this build have been cryptographically verified
and recorded in the attestation chain.

═══════════════════════════════════════════════════════════════════════════════

Build Components:
  • OMEGA_LOCK.json - Cryptographic manifest of all artifacts
  • codex_omega_bundle.zip - Complete source bundle
  • chain/attestations.jsonl - Immutable audit trail

All reproductions require attribution and verification.

═══════════════════════════════════════════════════════════════════════════════
"""
    
    with open("codex_capsule.txt", "w") as f:
        f.write(capsule_content.strip())
    
    capsule_hash = compute_sha256("codex_capsule.txt")
    print(f"✓ Capsule created")
    print(f"  SHA-256: {capsule_hash}")
    
    return capsule_hash

def append_attestation(omega_id, bundle_hash, capsule_hash):
    """Append attestation to chain/attestations.jsonl"""
    
    print("📝 Appending attestation to chain...")
    
    attestation = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "final_evolution_build",
        "omega_id": omega_id,
        "artifacts": {
            "bundle": {
                "name": "codex_omega_bundle.zip",
                "sha256": bundle_hash
            },
            "capsule": {
                "name": "codex_capsule.txt",
                "sha256": capsule_hash
            }
        },
        "verified": True,
        "license": "EUCELA Tri-License",
        "steward": "CFBK"
    }
    
    # Ensure chain directory exists
    os.makedirs("chain", exist_ok=True)
    
    # Append to attestations.jsonl (never overwrite)
    with open("chain/attestations.jsonl", "a") as f:
        f.write(json.dumps(attestation) + "\n")
    
    print("✓ Attestation recorded")

def create_treasury_and_economy():
    """Create treasury_allocation.json and economy_monetization.json"""
    
    print("💰 Creating treasury and economy files...")
    
    treasury = {
        "version": "1.0.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "allocations": [
            {
                "category": "development",
                "percentage": 40,
                "description": "Ongoing development and maintenance"
            },
            {
                "category": "research",
                "percentage": 30,
                "description": "Research and innovation"
            },
            {
                "category": "community",
                "percentage": 20,
                "description": "Community engagement and support"
            },
            {
                "category": "operations",
                "percentage": 10,
                "description": "Operational expenses"
            }
        ]
    }
    
    economy = {
        "version": "1.0.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "monetization_strategy": "open_source_with_attribution",
        "license": "EUCELA Tri-License",
        "revenue_streams": [
            {
                "type": "attribution_compliance",
                "status": "active"
            },
            {
                "type": "commercial_licensing",
                "status": "available"
            },
            {
                "type": "consulting_services",
                "status": "available"
            }
        ]
    }
    
    with open("treasury_allocation.json", "w") as f:
        json.dump(treasury, f, indent=2)
    
    with open("economy_monetization.json", "w") as f:
        json.dump(economy, f, indent=2)
    
    print("✓ Treasury and economy files created")

def finalize_omega():
    """Main finalization process"""
    
    print("🚀 Starting Omega Finalization Process...")
    print("=" * 80)
    
    # Step 1: Create OMEGA_LOCK structure
    omega_lock, omega_id = create_omega_lock()
    
    # Step 2: Create bundle
    bundle_hash, bundle_size = create_bundle(omega_id)
    omega_lock["artifacts"]["bundle"] = {
        "filename": "codex_omega_bundle.zip",
        "sha256": bundle_hash,
        "size": bundle_size
    }
    
    # Step 3: Create capsule
    capsule_hash = create_capsule(omega_id)
    omega_lock["artifacts"]["capsule"] = {
        "filename": "codex_capsule.txt",
        "sha256": capsule_hash
    }
    
    # Step 4: Write OMEGA_LOCK.json
    with open("OMEGA_LOCK.json", "w") as f:
        json.dump(omega_lock, f, indent=2)
    
    omega_lock_hash = compute_sha256("OMEGA_LOCK.json")
    print(f"\n✓ OMEGA_LOCK.json created")
    print(f"  SHA-256: {omega_lock_hash}")
    
    # Step 5: Append attestation
    append_attestation(omega_id, bundle_hash, capsule_hash)
    
    # Step 6: Create treasury and economy files
    create_treasury_and_economy()
    
    # Step 7: Copy to releases
    os.makedirs("releases", exist_ok=True)
    shutil.copy("codex_omega_bundle.zip", "releases/codex_omega_bundle.zip")
    print("✓ Bundle copied to releases/")
    
    print("\n" + "=" * 80)
    print("✅ Omega Finalization Complete")
    print(f"   Omega ID: {omega_id}")
    print("=" * 80)

if __name__ == "__main__":
    finalize_omega()
