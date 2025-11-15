#!/usr/bin/env python3
"""
Merkle Tree Verifier for Codex Immortal v26.0
Verifies artifact integrity against Merkle tree manifest.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import List, Dict


def hash_file(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return ""


def hash_pair(left: str, right: str) -> str:
    """Hash a pair of hashes together."""
    combined = (left + right).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()


def rebuild_merkle_root(hashes: List[str]) -> str:
    """Rebuild Merkle root from list of hashes."""
    if not hashes:
        return ""
    
    current_level = hashes[:]
    
    while len(current_level) > 1:
        next_level = []
        
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = current_level[i]
            
            parent = hash_pair(left, right)
            next_level.append(parent)
        
        current_level = next_level
    
    return current_level[0]


def verify_merkle_tree() -> Dict:
    """Verify artifacts against Merkle manifest."""
    manifest_path = Path("trust/merkle_manifest.json")
    
    if not manifest_path.exists():
        return {
            "valid": False,
            "error": "Merkle manifest not found. Run merkle_build.py first."
        }
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    expected_root = manifest["merkle_root"]
    artifacts = manifest["artifacts"]
    
    print(f"📋 Manifest version: {manifest['version']}")
    print(f"📦 Artifacts in manifest: {len(artifacts)}")
    print(f"🌳 Expected Merkle root: {expected_root}")
    
    # Verify each artifact
    print("\n🔍 Verifying artifacts...")
    
    modified_files = []
    missing_files = []
    current_hashes = []
    
    for artifact in artifacts:
        file_path = Path(artifact["path"])
        expected_hash = artifact["hash"]
        
        if not file_path.exists():
            missing_files.append(artifact["path"])
            print(f"   ❌ Missing: {artifact['path']}")
        else:
            current_hash = hash_file(file_path)
            current_hashes.append(current_hash)
            
            if current_hash != expected_hash:
                modified_files.append(artifact["path"])
                print(f"   ❌ Modified: {artifact['path']}")
            else:
                print(f"   ✅ {artifact['path']}")
    
    # Rebuild Merkle root from current hashes
    if len(current_hashes) == len(artifacts):
        computed_root = rebuild_merkle_root(current_hashes)
        
        if computed_root == expected_root:
            return {
                "valid": True,
                "merkle_root": computed_root,
                "artifacts_verified": len(artifacts)
            }
        else:
            return {
                "valid": False,
                "error": "Merkle root mismatch",
                "expected_root": expected_root,
                "computed_root": computed_root,
                "modified_files": modified_files,
                "missing_files": missing_files
            }
    else:
        return {
            "valid": False,
            "error": "Artifact count mismatch",
            "modified_files": modified_files,
            "missing_files": missing_files
        }


def main():
    """Main entry point for Merkle verification."""
    print("=" * 60)
    print("Merkle Tree Verifier")
    print("=" * 60)
    
    result = verify_merkle_tree()
    
    print("\n" + "=" * 60)
    print("Verification Result")
    print("=" * 60)
    
    if result["valid"]:
        print("\n✅ Merkle tree verification PASSED")
        print(f"   Root: {result['merkle_root']}")
        print(f"   Verified: {result['artifacts_verified']} artifacts")
        return 0
    else:
        print("\n❌ Merkle tree verification FAILED")
        print(f"   Error: {result['error']}")
        
        if result.get("modified_files"):
            print(f"\n   Modified files ({len(result['modified_files'])}):")
            for file_path in result["modified_files"][:10]:
                print(f"      - {file_path}")
            if len(result["modified_files"]) > 10:
                print(f"      ... and {len(result['modified_files']) - 10} more")
        
        if result.get("missing_files"):
            print(f"\n   Missing files ({len(result['missing_files'])}):")
            for file_path in result["missing_files"][:10]:
                print(f"      - {file_path}")
        
        if result.get("expected_root") and result.get("computed_root"):
            print(f"\n   Expected root: {result['expected_root']}")
            print(f"   Computed root: {result['computed_root']}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
