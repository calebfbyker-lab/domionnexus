#!/usr/bin/env python3
"""
Hash v100 - Enhanced hashing for v100 bundle
Codex Continuum v100 - Continuum Σ (Sigma)

Creates a comprehensive manifest with cryptographic hashes
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

def hash_file(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"⚠️  Error hashing {filepath}: {e}", file=sys.stderr)
        return ""

def scan_directory(root_dir: str, exclude_patterns: List[str] = None) -> List[Dict]:
    """Scan directory and hash all files"""
    if exclude_patterns is None:
        exclude_patterns = [
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            "*.pyc",
            "*.log",
            "audit.jsonl",
            "chain.jsonl"
        ]
    
    root_path = Path(root_dir)
    files = []
    
    print(f"🔍 Scanning directory: {root_dir}")
    
    for filepath in root_path.rglob("*"):
        # Check exclusions
        should_exclude = False
        for pattern in exclude_patterns:
            if pattern.startswith("*."):
                # Extension pattern
                if filepath.suffix == pattern[1:]:
                    should_exclude = True
                    break
            else:
                # Directory or filename pattern
                if pattern in str(filepath):
                    should_exclude = True
                    break
        
        if should_exclude:
            continue
        
        if filepath.is_file():
            rel_path = filepath.relative_to(root_path)
            file_hash = hash_file(filepath)
            
            if file_hash:
                files.append({
                    "path": str(rel_path),
                    "hash": file_hash,
                    "size": filepath.stat().st_size,
                    "modified": filepath.stat().st_mtime
                })
    
    print(f"✅ Scanned {len(files)} files")
    return files

def create_manifest(root_dir: str, output_file: str):
    """Create v100 manifest with hashes"""
    print("📦 Creating v100 manifest...")
    
    # Scan files
    files = scan_directory(root_dir)
    
    # Calculate manifest hash
    files_str = json.dumps(files, sort_keys=True, separators=(',', ':'))
    manifest_hash = hashlib.sha256(files_str.encode('utf-8')).hexdigest()
    
    # Create manifest
    manifest = {
        "version": "v100",
        "release": "Continuum Σ (Sigma)",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": root_dir,
        "manifest_hash": manifest_hash,
        "total_files": len(files),
        "files": files,
        "metadata": {
            "generator": "hash_v100.py",
            "subject_id_sha256": "1f6e1f1ca3c4f3e1b1f6e2b317d7c1dff9b5d6d2b0d4e0f7b6a8c9e0f2a4b1c3"
        }
    }
    
    # Write manifest
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Manifest created: {output_file}")
    print(f"   Manifest hash: {manifest_hash[:16]}...")
    print(f"   Total files: {len(files)}")
    
    return manifest

def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else "codex/manifest.v100.json"
    
    manifest = create_manifest(root_dir, output_file)

if __name__ == "__main__":
    main()
