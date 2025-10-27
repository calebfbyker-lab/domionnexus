#!/usr/bin/env python3
"""
verify_manifest.py - Verify integrity of files against manifest
Part of Codex v93.x Constellation bundle
"""
import sys
import json
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
        return None


def main():
    manifest_path = "codex/manifest.v93x.json"
    
    if "--manifest" in sys.argv:
        i = sys.argv.index("--manifest")
        if i + 1 < len(sys.argv):
            manifest_path = sys.argv[i + 1]
    
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error: Could not load manifest: {e}", file=sys.stderr)
        sys.exit(1)
    
    files = manifest.get("files", {})
    errors = []
    verified = 0
    skipped = []
    
    for rel_path, file_info in files.items():
        # Skip the manifest file itself to avoid self-reference issues
        if rel_path.endswith("manifest.v93x.json") or rel_path.endswith("manifest.json"):
            skipped.append(rel_path)
            continue
            
        expected_hash = file_info.get("sha256")
        filepath = Path(rel_path)
        
        if not filepath.exists():
            errors.append(f"Missing: {rel_path}")
            continue
        
        actual_hash = sha256_file(filepath)
        if actual_hash is None:
            errors.append(f"Error reading: {rel_path}")
            continue
        
        if actual_hash != expected_hash:
            errors.append(f"Hash mismatch: {rel_path}")
            continue
        
        verified += 1
    
    print(json.dumps({
        "manifest": manifest_path,
        "total": len(files),
        "verified": verified,
        "skipped": len(skipped),
        "errors": len(errors),
        "error_details": errors[:10]  # Limit to first 10 errors
    }, indent=2))
    
    if errors:
        sys.exit(1)
    else:
        print(f"✓ All {verified} files verified successfully (skipped {len(skipped)} meta files)")


if __name__ == "__main__":
    main()
