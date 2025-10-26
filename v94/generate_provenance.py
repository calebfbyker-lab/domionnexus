#!/usr/bin/env python3
"""
Generate SLSA Provenance v4 for v94 bundle
"""
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def compute_sha256(file_path: str) -> str:
    """Compute SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_provenance_v4(
    artifact_path: str,
    materials: List[Dict[str, Any]],
    builder_id: str = "https://github.com/calebfbyker-lab/domionnexus",
    build_type: str = "https://github.com/calebfbyker-lab/domionnexus/v94@v1"
) -> Dict[str, Any]:
    """
    Generate SLSA Provenance v4
    
    Args:
        artifact_path: Path to the built artifact
        materials: List of input materials (dependencies, source files)
        builder_id: Builder identifier
        build_type: Build type URI
    
    Returns:
        dict: SLSA Provenance v4 document
    """
    
    # Compute artifact digest
    artifact_digest = compute_sha256(artifact_path)
    
    # Generate provenance
    provenance = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [
            {
                "name": Path(artifact_path).name,
                "digest": {
                    "sha256": artifact_digest
                }
            }
        ],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": build_type,
                "externalParameters": {
                    "repository": "https://github.com/calebfbyker-lab/domionnexus",
                    "ref": "refs/heads/main"
                },
                "internalParameters": {
                    "buildConfig": {
                        "version": "94.0.0",
                        "features": [
                            "jwks-verification",
                            "glyph-guard-v14",
                            "sbom-generation",
                            "vulnerability-scanning",
                            "cosign-verification"
                        ]
                    }
                },
                "resolvedDependencies": materials
            },
            "runDetails": {
                "builder": {
                    "id": builder_id
                },
                "metadata": {
                    "invocationId": f"build-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    "startedOn": datetime.utcnow().isoformat() + "Z",
                    "finishedOn": datetime.utcnow().isoformat() + "Z"
                }
            }
        }
    }
    
    return provenance

def collect_materials_from_requirements(requirements_file: str = "requirements.txt") -> List[Dict[str, Any]]:
    """Collect materials from requirements.txt"""
    materials = []
    
    try:
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' in line:
                        name, version = line.split('==', 1)
                        materials.append({
                            "uri": f"pkg:pypi/{name.strip()}@{version.strip()}",
                            "digest": {
                                "sha256": ""  # Would need to fetch from PyPI
                            }
                        })
    except FileNotFoundError:
        print(f"Warning: {requirements_file} not found")
    
    return materials

def main():
    """Generate provenance for v94 bundle"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SLSA Provenance v4")
    parser.add_argument("artifact", help="Path to artifact to generate provenance for")
    parser.add_argument("--output", default="provenance.json", 
                       help="Output file path")
    parser.add_argument("--requirements", default="requirements.txt",
                       help="Requirements file for materials")
    
    args = parser.parse_args()
    
    print(f"Generating SLSA Provenance v4 for: {args.artifact}")
    
    # Collect materials
    materials = collect_materials_from_requirements(args.requirements)
    print(f"Found {len(materials)} materials")
    
    # Generate provenance
    provenance = generate_provenance_v4(args.artifact, materials)
    
    # Write to file
    with open(args.output, 'w') as f:
        json.dump(provenance, f, indent=2)
    
    print(f"✓ Provenance written to: {args.output}")
    print(f"  Subject: {provenance['subject'][0]['name']}")
    print(f"  SHA256: {provenance['subject'][0]['digest']['sha256'][:16]}...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
