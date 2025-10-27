#!/usr/bin/env python3
"""
sbom_stub.py - Generate Software Bill of Materials (SBOM)
Part of Codex v93.x Constellation bundle
"""
import json
import sys
from datetime import datetime


def generate_sbom():
    """Generate a basic SBOM in SPDX-lite format"""
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "Codex-v93x-Constellation-SBOM",
        "documentNamespace": f"https://github.com/calebfbyker-lab/domionnexus/sbom-{datetime.utcnow().isoformat()}",
        "creationInfo": {
            "created": datetime.utcnow().isoformat() + "Z",
            "creators": ["Tool: sbom_stub.py"],
            "licenseListVersion": "3.21"
        },
        "packages": [
            {
                "SPDXID": "SPDXRef-Package-Codex-v93x",
                "name": "Codex v93.x Constellation",
                "versionInfo": "93.x",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "MIT",
                "licenseDeclared": "MIT",
                "copyrightText": "NOASSERTION"
            }
        ],
        "relationships": [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": "SPDXRef-Package-Codex-v93x"
            }
        ]
    }
    
    output_path = "codex/sbom.spdx.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=2)
    
    print(f"SBOM generated: {output_path}")
    return sbom


if __name__ == "__main__":
    generate_sbom()
