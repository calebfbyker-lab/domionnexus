#!/usr/bin/env python3
"""
hash_all.py - Generate comprehensive SHA-256 manifest of all files
Part of Codex v93.x Constellation bundle
"""
import sys
import json
import os
import hashlib
from pathlib import Path


def sha256_file(filepath):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def walk_and_hash(root_dir, excludes=None):
    """Walk directory tree and hash all files"""
    if excludes is None:
        excludes = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            "*.pyc",
            "audit.jsonl",
        }
    
    manifest = {}
    root_path = Path(root_dir).resolve()
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in excludes]
        
        for filename in filenames:
            # Skip excluded file patterns
            if any(filename.endswith(ext.replace("*", "")) for ext in excludes if "*" in ext):
                continue
            if filename in excludes:
                continue
                
            filepath = Path(dirpath) / filename
            abs_filepath = filepath.resolve()
            
            # Check if file is within root directory
            try:
                rel_path = str(abs_filepath.relative_to(root_path))
            except ValueError:
                # File is outside root directory, skip it
                continue
            
            try:
                file_hash = sha256_file(abs_filepath)
                manifest[rel_path] = {
                    "sha256": file_hash,
                    "size": abs_filepath.stat().st_size if abs_filepath.exists() else 0
                }
            except Exception as e:
                print(f"Warning: Could not hash {rel_path}: {e}", file=sys.stderr)
    
    return manifest


def main():
    out = None
    root_dir = "."
    
    # Parse command line arguments
    if "--out" in sys.argv:
        i = sys.argv.index("--out")
        if i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    
    if "--dir" in sys.argv:
        i = sys.argv.index("--dir")
        if i + 1 < len(sys.argv):
            root_dir = sys.argv[i + 1]
    
    if not out:
        os.makedirs("codex", exist_ok=True)
        out = "codex/manifest.v93x.json"
    
    # Generate manifest
    file_hashes = walk_and_hash(root_dir)
    
    content = {
        "generated_by": "hash_all.py",
        "version": "v93.x",
        "root": os.path.abspath(root_dir),
        "file_count": len(file_hashes),
        "files": file_hashes
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out) if os.path.dirname(out) else ".", exist_ok=True)
    
    # Write manifest
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(content, indent=2))
    
    print(f"hash_all: wrote {out} with {len(file_hashes)} files")


if __name__ == "__main__":
    main()
