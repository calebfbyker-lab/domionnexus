#!/usr/bin/env python3
"""
Verify v100 - Manifest verification for v100 bundle
Codex Continuum v100 - Continuum Σ (Sigma)

Verifies integrity of v100 bundle against manifest
"""
import hashlib
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

def load_manifest(manifest_file: str) -> Dict:
    """Load manifest from file"""
    try:
        with open(manifest_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⛔ Manifest not found: {manifest_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"⛔ Invalid manifest JSON: {e}", file=sys.stderr)
        sys.exit(1)

def hash_file(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def verify_files(manifest: Dict, root_dir: str) -> Tuple[bool, List[str], List[str], List[str]]:
    """
    Verify files against manifest
    
    Returns:
        (all_valid, mismatches, missing, extra)
    """
    root_path = Path(root_dir)
    files = manifest.get("files", [])
    
    mismatches = []
    missing = []
    verified = []
    
    print(f"🔍 Verifying {len(files)} files...")
    
    for file_entry in files:
        file_path = root_path / file_entry["path"]
        expected_hash = file_entry["hash"]
        
        if not file_path.exists():
            missing.append(file_entry["path"])
            print(f"❌ Missing: {file_entry['path']}")
            continue
        
        actual_hash = hash_file(file_path)
        
        if actual_hash != expected_hash:
            mismatches.append({
                "path": file_entry["path"],
                "expected": expected_hash,
                "actual": actual_hash
            })
            print(f"❌ Hash mismatch: {file_entry['path']}")
        else:
            verified.append(file_entry["path"])
    
    # Check for extra files not in manifest
    manifest_paths = {f["path"] for f in files}
    extra = []
    
    exclude_patterns = [".git", "__pycache__", ".venv", "venv", "*.pyc", "*.log"]
    
    for filepath in root_path.rglob("*"):
        should_exclude = any(pattern in str(filepath) for pattern in exclude_patterns)
        if should_exclude or not filepath.is_file():
            continue
        
        rel_path = str(filepath.relative_to(root_path))
        if rel_path not in manifest_paths:
            extra.append(rel_path)
    
    all_valid = len(mismatches) == 0 and len(missing) == 0
    
    return all_valid, mismatches, missing, extra

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_v100.py <manifest.json> [root_dir]")
        sys.exit(1)
    
    manifest_file = sys.argv[1]
    root_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    print("📋 Loading manifest...")
    manifest = load_manifest(manifest_file)
    
    print(f"   Version: {manifest.get('version', 'unknown')}")
    print(f"   Release: {manifest.get('release', 'unknown')}")
    print(f"   Manifest hash: {manifest.get('manifest_hash', 'N/A')[:16]}...")
    
    # Verify
    all_valid, mismatches, missing, extra = verify_files(manifest, root_dir)
    
    # Report
    print("\n" + "=" * 60)
    print("📊 Verification Report")
    print("=" * 60)
    
    if all_valid and len(extra) == 0:
        print("✅ ALL FILES VERIFIED")
        print(f"   {manifest.get('total_files', 0)} files match manifest")
        sys.exit(0)
    else:
        if mismatches:
            print(f"\n❌ Hash Mismatches: {len(mismatches)}")
            for mismatch in mismatches[:5]:  # Show first 5
                print(f"   - {mismatch['path']}")
                print(f"     Expected: {mismatch['expected'][:16]}...")
                print(f"     Actual:   {mismatch['actual'][:16]}...")
        
        if missing:
            print(f"\n❌ Missing Files: {len(missing)}")
            for miss in missing[:5]:  # Show first 5
                print(f"   - {miss}")
        
        if extra:
            print(f"\n⚠️  Extra Files (not in manifest): {len(extra)}")
            for ext in extra[:5]:  # Show first 5
                print(f"   - {ext}")
        
        print("\n❌ VERIFICATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
