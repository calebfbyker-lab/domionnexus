#!/usr/bin/env python3
"""
Codex Capsule Generator
Generates a human-readable capsule from the codex state.
"""
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def generate_capsule():
    """Generate a human-readable codex capsule."""
    print("📦 Generating codex capsule...")
    
    # Collect information from various sources
    capsule_lines = []
    capsule_lines.append("=" * 80)
    capsule_lines.append("🪬 CODEX IMMORTAL CAPSULE")
    capsule_lines.append("=" * 80)
    capsule_lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    capsule_lines.append("")
    
    # Add license information
    capsule_lines.append("LICENSE:")
    capsule_lines.append("  © 2025 Caleb Fedor Byker (Konev) — EUCELA Tri-License")
    capsule_lines.append("  Subject Hash: 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a")
    capsule_lines.append("")
    
    # Add OMEGA_LOCK if it exists
    omega_file = Path("OMEGA_LOCK.json")
    if omega_file.exists():
        try:
            with open(omega_file, 'r') as f:
                omega = json.load(f)
            capsule_lines.append("OMEGA LOCK:")
            capsule_lines.append(f"  ID: {omega.get('omega_id', 'N/A')}")
            capsule_lines.append(f"  Timestamp: {omega.get('timestamp', 'N/A')}")
        except Exception as e:
            capsule_lines.append(f"OMEGA LOCK: Error reading - {e}")
    else:
        capsule_lines.append("OMEGA LOCK: Not yet sealed")
    
    capsule_lines.append("")
    
    # Add attestation count
    attestation_file = Path("chain/attestations.jsonl")
    if attestation_file.exists():
        try:
            with open(attestation_file, 'r') as f:
                count = sum(1 for line in f if line.strip())
            capsule_lines.append(f"ATTESTATIONS: {count} records in chain")
        except Exception as e:
            capsule_lines.append(f"ATTESTATIONS: Error reading - {e}")
    else:
        capsule_lines.append("ATTESTATIONS: No chain yet")
    
    capsule_lines.append("")
    
    # Add treasury info
    treasury_file = Path("treasury_allocation.json")
    if treasury_file.exists():
        try:
            with open(treasury_file, 'r') as f:
                treasury = json.load(f)
            capsule_lines.append("TREASURY:")
            capsule_lines.append(f"  Owner: {treasury.get('owner', 'N/A')}%")
            capsule_lines.append(f"  Reserve: {treasury.get('reserve', 'N/A')}%")
            capsule_lines.append(f"  Community: {treasury.get('community', 'N/A')}%")
        except Exception as e:
            capsule_lines.append(f"TREASURY: Error reading - {e}")
    else:
        capsule_lines.append("TREASURY: Not configured")
    
    capsule_lines.append("")
    capsule_lines.append("=" * 80)
    capsule_lines.append("END CAPSULE")
    capsule_lines.append("=" * 80)
    
    # Write capsule to file
    capsule_content = "\n".join(capsule_lines)
    output_file = Path("codex_capsule.txt")
    
    with open(output_file, 'w') as f:
        f.write(capsule_content)
    
    print(f"✅ Capsule generated: {output_file}")
    print(capsule_content)
    
    return True


if __name__ == "__main__":
    import sys
    success = generate_capsule()
    sys.exit(0 if success else 1)
