"""
Boot-time self-check module for Codex v98 Orthos
Verifies file integrity against manifest before allowing service to run
"""
import json
import hashlib
import sys
from pathlib import Path

MANIFEST_FILE = "manifest.json"
CRITICAL_FILES = ["app.py", "selfcheck.py"]


def calculate_sha256(filepath):
    """Calculate SHA256 hash of a file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def verify_integrity(manifest_path=MANIFEST_FILE, strict=True):
    """
    Verify file integrity against manifest
    
    Args:
        manifest_path: Path to manifest.json
        strict: If True, fail on any mismatch. If False, only fail on critical files.
    
    Returns:
        tuple: (success: bool, errors: list)
    """
    errors = []
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        return False, [f"Manifest not found: {manifest_path}"]
    except json.JSONDecodeError as e:
        return False, [f"Invalid manifest JSON: {e}"]
    
    files = manifest.get('files', [])
    if not files:
        return False, ["Manifest contains no files"]
    
    # Check critical files first
    critical_errors = []
    for entry in files:
        path = entry.get('path')
        expected_hash = entry.get('sha256')
        
        if not path or not expected_hash:
            continue
            
        actual_hash = calculate_sha256(path)
        
        if actual_hash is None:
            error = f"MISSING: {path}"
            if any(cf in path for cf in CRITICAL_FILES):
                critical_errors.append(error)
            errors.append(error)
        elif actual_hash != expected_hash:
            error = f"MISMATCH: {path} (expected: {expected_hash[:8]}..., got: {actual_hash[:8]}...)"
            if any(cf in path for cf in CRITICAL_FILES):
                critical_errors.append(error)
            errors.append(error)
    
    # If there are critical errors, always fail
    if critical_errors:
        return False, critical_errors
    
    # If strict mode and any errors, fail
    if strict and errors:
        return False, errors
    
    # Success
    return True, []


def selfcheck(strict=True):
    """
    Run self-check and exit if verification fails
    
    Args:
        strict: If True, fail on any mismatch. If False, only fail on critical files.
    """
    print("[Orthos Self-Check] Verifying integrity...")
    success, errors = verify_integrity(strict=strict)
    
    if not success:
        print("[Orthos Self-Check] ❌ INTEGRITY CHECK FAILED")
        print("[Orthos Self-Check] Service will NOT start - code diverged from manifest")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("[Orthos Self-Check] ✓ Integrity verified")
        return True


if __name__ == "__main__":
    selfcheck()
