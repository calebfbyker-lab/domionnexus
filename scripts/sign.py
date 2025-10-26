#!/usr/bin/env python3
"""
Artifact Signing Script
Codex Continuum v100 - Continuum Σ (Sigma)

Signs artifacts with cryptographic signatures
"""
import hashlib
import hmac
import json
import sys
import os
import time
from pathlib import Path

def load_keyring(keyring_file: str = "secrets/keyring.json") -> dict:
    """Load signing keys from keyring"""
    try:
        with open(keyring_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Keyring not found: {keyring_file}", file=sys.stderr)
        # Return default for development
        return {
            "keys": {
                "default": "dev-signing-key-change-in-production"
            },
            "active": "default"
        }

def hash_file(filepath: str) -> str:
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"⛔ Error hashing file: {e}", file=sys.stderr)
        sys.exit(1)

def sign_artifact(artifact_path: str, keyring: dict, output_file: str = None):
    """Sign an artifact and create signature file"""
    print(f"📝 Signing artifact: {artifact_path}")
    
    # Hash the artifact
    artifact_hash = hash_file(artifact_path)
    print(f"   Hash: {artifact_hash}")
    
    # Get signing key
    active_key_id = keyring.get("active", "default")
    signing_key = keyring.get("keys", {}).get(active_key_id)
    
    if not signing_key:
        print(f"⛔ No signing key found for: {active_key_id}", file=sys.stderr)
        sys.exit(1)
    
    # Create signature payload
    payload = {
        "artifact": os.path.basename(artifact_path),
        "hash": artifact_hash,
        "algorithm": "sha256",
        "timestamp": int(time.time()),
        "signer": "codex-continuum-v100"
    }
    
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    
    # Sign with HMAC-SHA256
    signature = hmac.new(
        signing_key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # Create signature document
    sig_doc = {
        "version": "v100",
        "payload": payload,
        "signature": signature,
        "key_id": active_key_id,
        "signature_algorithm": "HMAC-SHA256"
    }
    
    # Determine output file
    if not output_file:
        output_file = artifact_path + ".sig"
    
    # Write signature
    with open(output_file, 'w') as f:
        json.dump(sig_doc, f, indent=2)
    
    print(f"✅ Signature created: {output_file}")
    print(f"   Key ID: {active_key_id}")
    print(f"   Algorithm: HMAC-SHA256")
    
    return sig_doc

def main():
    if len(sys.argv) < 2:
        print("Usage: sign.py <artifact_path> [output_signature_file]")
        sys.exit(1)
    
    artifact_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(artifact_path):
        print(f"⛔ Artifact not found: {artifact_path}", file=sys.stderr)
        sys.exit(1)
    
    keyring = load_keyring()
    sign_artifact(artifact_path, keyring, output_file)

if __name__ == "__main__":
    main()
