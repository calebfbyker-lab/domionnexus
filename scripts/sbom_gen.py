#!/usr/bin/env python3
"""
SBOM (Software Bill of Materials) Generator
Codex Continuum v100 - Continuum Σ (Sigma)

Generates a comprehensive SBOM for the project including:
- Python dependencies
- File inventory
- License information
"""
import json
import hashlib
import subprocess
import sys
import os
from pathlib import Path
import time

def get_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def get_pip_packages():
    """Get installed pip packages"""
    try:
        result = subprocess.run(
            ["pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Warning: Could not get pip packages: {e}", file=sys.stderr)
        return []

def scan_project_files(root_dir: str = "."):
    """Scan project files and create inventory"""
    root_path = Path(root_dir)
    files = []
    
    exclude_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}
    exclude_exts = {".pyc", ".pyo", ".log"}
    
    for filepath in root_path.rglob("*"):
        # Skip excluded directories
        if any(excluded in filepath.parts for excluded in exclude_dirs):
            continue
        
        # Skip excluded extensions
        if filepath.suffix in exclude_exts:
            continue
        
        if filepath.is_file():
            rel_path = filepath.relative_to(root_path)
            files.append({
                "path": str(rel_path),
                "size": filepath.stat().st_size,
                "hash": get_file_hash(filepath),
                "extension": filepath.suffix
            })
    
    return files

def generate_sbom(root_dir: str = ".", output_file: str = "sbom.json"):
    """Generate complete SBOM"""
    print("🔍 Generating SBOM...")
    
    # Get dependencies
    pip_packages = get_pip_packages()
    
    # Scan files
    project_files = scan_project_files(root_dir)
    
    # Build SBOM
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tools": [{
                "name": "codex-sbom-generator",
                "version": "v100"
            }],
            "component": {
                "type": "application",
                "name": "domionnexus",
                "version": "v100",
                "description": "Codex Continuum v100 - Continuum Σ (Sigma)"
            }
        },
        "components": [],
        "files": project_files
    }
    
    # Add pip packages as components
    for pkg in pip_packages:
        component = {
            "type": "library",
            "name": pkg["name"],
            "version": pkg["version"],
            "purl": f"pkg:pypi/{pkg['name']}@{pkg['version']}"
        }
        sbom["components"].append(component)
    
    # Write SBOM
    with open(output_file, 'w') as f:
        json.dump(sbom, f, indent=2)
    
    print(f"✅ SBOM generated: {output_file}")
    print(f"   - {len(pip_packages)} dependencies")
    print(f"   - {len(project_files)} project files")
    
    return sbom

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    output = sys.argv[2] if len(sys.argv) > 2 else "sbom.json"
    
    generate_sbom(root, output)
