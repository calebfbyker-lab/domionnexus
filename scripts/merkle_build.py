#!/usr/bin/env python3
"""
Merkle Tree Builder for Codex Immortal v26.0
Builds a Merkle tree of project artifacts for integrity verification.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional


class MerkleNode:
    """Represents a node in the Merkle tree."""
    
    def __init__(self, hash_value: str, left: Optional['MerkleNode'] = None, right: Optional['MerkleNode'] = None):
        self.hash = hash_value
        self.left = left
        self.right = right


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
        print(f"⚠️  Error hashing {file_path}: {e}", file=sys.stderr)
        return ""


def hash_pair(left: str, right: str) -> str:
    """Hash a pair of hashes together."""
    combined = (left + right).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()


def build_merkle_tree(hashes: List[str]) -> MerkleNode:
    """
    Build a Merkle tree from a list of hashes.
    
    Args:
        hashes: List of leaf hashes
    
    Returns:
        MerkleNode: Root of the Merkle tree
    """
    if not hashes:
        raise ValueError("Cannot build Merkle tree from empty list")
    
    # Create leaf nodes
    nodes = [MerkleNode(h) for h in hashes]
    
    # Build tree bottom-up
    while len(nodes) > 1:
        parent_nodes = []
        
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            
            # If odd number of nodes, duplicate the last one
            if i + 1 < len(nodes):
                right = nodes[i + 1]
            else:
                right = nodes[i]
            
            parent_hash = hash_pair(left.hash, right.hash)
            parent = MerkleNode(parent_hash, left, right)
            parent_nodes.append(parent)
        
        nodes = parent_nodes
    
    return nodes[0]


def collect_artifacts() -> List[Dict[str, str]]:
    """Collect all artifacts to include in Merkle tree."""
    artifacts = []
    
    # Critical files and directories
    patterns = [
        "api/**/*.json",
        "config/**/*.json",
        "schemas/**/*.json",
        "scripts/**/*.py",
        "i18n/**/*.json",
        ".github/workflows/*.yml"
    ]
    
    for pattern in patterns:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file():
                file_hash = hash_file(file_path)
                if file_hash:
                    artifacts.append({
                        "path": str(file_path),
                        "hash": file_hash
                    })
    
    # Sort for deterministic tree
    artifacts.sort(key=lambda x: x["path"])
    
    return artifacts


def main():
    """Main entry point for Merkle tree building."""
    print("=" * 60)
    print("Merkle Tree Builder")
    print("=" * 60)
    
    # Collect artifacts
    print("\n🔍 Collecting artifacts...")
    artifacts = collect_artifacts()
    
    print(f"   Found {len(artifacts)} artifacts")
    
    if not artifacts:
        print("❌ No artifacts found")
        return 1
    
    # Build Merkle tree
    print("\n🌳 Building Merkle tree...")
    hashes = [a["hash"] for a in artifacts]
    root = build_merkle_tree(hashes)
    
    print(f"   Merkle root: {root.hash}")
    
    # Save manifest
    manifest = {
        "version": "26.0.0",
        "merkle_root": root.hash,
        "artifact_count": len(artifacts),
        "artifacts": artifacts
    }
    
    manifest_path = Path("trust/merkle_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Merkle manifest saved to {manifest_path}")
    
    # Show sample artifacts
    print("\n📦 Sample artifacts:")
    for artifact in artifacts[:5]:
        print(f"   {artifact['path']}")
        print(f"      {artifact['hash']}")
    
    if len(artifacts) > 5:
        print(f"   ... and {len(artifacts) - 5} more")
    
    print("\n" + "=" * 60)
    print("Merkle Tree Build Complete")
    print("=" * 60)
    print(f"\n✅ Merkle Root: {root.hash}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
