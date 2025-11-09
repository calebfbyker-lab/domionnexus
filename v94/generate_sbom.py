#!/usr/bin/env python3
"""
Generate SBOM (Software Bill of Materials) for v94 bundle
Uses cyclonedx-bom or syft format
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def generate_sbom_syft(target_path: str = ".", output_path: str = "sbom.json"):
    """Generate SBOM using Syft"""
    try:
        result = subprocess.run(
            ["syft", target_path, "-o", f"json={output_path}"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ SBOM generated with Syft: {output_path}")
        return True
    except FileNotFoundError:
        print("✗ Syft not installed. Install: https://github.com/anchore/syft")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Syft failed: {e.stderr}")
        return False

def generate_sbom_pip(requirements_file: str = "requirements.txt", output_path: str = "sbom.json"):
    """Generate simple SBOM from requirements.txt"""
    try:
        with open(requirements_file, 'r') as f:
            requirements = f.readlines()
        
        components = []
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                # Parse package==version
                if '==' in req:
                    name, version = req.split('==', 1)
                    components.append({
                        "type": "library",
                        "name": name.strip(),
                        "version": version.strip(),
                        "purl": f"pkg:pypi/{name.strip()}@{version.strip()}"
                    })
        
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "tools": [{"name": "manual-sbom-generator", "version": "1.0"}],
                "component": {
                    "type": "application",
                    "name": "codex-v94",
                    "version": "94.0.0"
                }
            },
            "components": components
        }
        
        with open(output_path, 'w') as f:
            json.dump(sbom, f, indent=2)
        
        print(f"✓ SBOM generated from requirements.txt: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to generate SBOM: {e}")
        return False

def main():
    """Generate SBOM using available tools"""
    print("Generating SBOM for v94 bundle...")
    
    # Try Syft first (more comprehensive)
    if not generate_sbom_syft(".", "sbom-syft.json"):
        # Fallback to requirements.txt parsing
        print("Falling back to requirements.txt parsing...")
        generate_sbom_pip("requirements.txt", "sbom.json")
    
    print("\nSBOM generation complete!")

if __name__ == "__main__":
    main()
