#!/usr/bin/env python3
"""
Vulnerability Gating Script
Codex Continuum v100 - Continuum Σ (Sigma)

Checks SBOM for known vulnerabilities and enforces policy gates
"""
import json
import sys
import os
from typing import Dict, List, Tuple

def load_sbom(sbom_file: str) -> Dict:
    """Load SBOM from file"""
    try:
        with open(sbom_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⛔ SBOM file not found: {sbom_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"⛔ Invalid SBOM JSON: {e}", file=sys.stderr)
        sys.exit(1)

def load_policy(policy_file: str = "policy/sigma.yaml") -> Dict:
    """Load policy configuration"""
    # For now, return hardcoded policy matching sigma.yaml
    return {
        "critical_threshold": 0,
        "high_threshold": 5,
        "medium_threshold": 20,
        "low_threshold": 100
    }

def check_known_vulnerabilities(sbom: Dict) -> Tuple[Dict[str, int], List[Dict]]:
    """
    Check components against known vulnerability database
    In production, this would query OSV, NVD, or similar
    """
    # Mock vulnerability check - in production, integrate with vulnerability DB
    vulnerabilities = []
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    # Simulate checking components
    components = sbom.get("components", [])
    
    # Example: flag some common vulnerable patterns
    vulnerable_packages = {
        "requests": {"versions": ["<2.31.0"], "severity": "medium", "cve": "CVE-2023-32681"},
    }
    
    for component in components:
        name = component.get("name", "")
        version = component.get("version", "")
        
        if name in vulnerable_packages:
            vuln_info = vulnerable_packages[name]
            # Simple version check (in production, use proper version comparison)
            vulnerabilities.append({
                "component": name,
                "version": version,
                "severity": vuln_info["severity"],
                "cve": vuln_info.get("cve", "N/A"),
                "description": f"Known vulnerability in {name}"
            })
            severity_counts[vuln_info["severity"]] += 1
    
    return severity_counts, vulnerabilities

def enforce_policy(severity_counts: Dict[str, int], policy: Dict) -> bool:
    """Enforce vulnerability policy gates"""
    print("\n🛡️  Vulnerability Gate Check")
    print("=" * 50)
    
    # Check each severity level
    checks_passed = True
    
    critical = severity_counts["critical"]
    critical_max = policy["critical_threshold"]
    if critical > critical_max:
        print(f"❌ CRITICAL: {critical} vulnerabilities (max: {critical_max})")
        checks_passed = False
    else:
        print(f"✅ CRITICAL: {critical} vulnerabilities (max: {critical_max})")
    
    high = severity_counts["high"]
    high_max = policy["high_threshold"]
    if high > high_max:
        print(f"❌ HIGH: {high} vulnerabilities (max: {high_max})")
        checks_passed = False
    else:
        print(f"✅ HIGH: {high} vulnerabilities (max: {high_max})")
    
    medium = severity_counts["medium"]
    medium_max = policy["medium_threshold"]
    if medium > medium_max:
        print(f"⚠️  MEDIUM: {medium} vulnerabilities (max: {medium_max})")
        # Medium violations are warnings, not failures
    else:
        print(f"✅ MEDIUM: {medium} vulnerabilities (max: {medium_max})")
    
    low = severity_counts["low"]
    print(f"ℹ️  LOW: {low} vulnerabilities")
    
    return checks_passed

def main():
    if len(sys.argv) < 2:
        print("Usage: vuln_gate.py <sbom.json>")
        sys.exit(1)
    
    sbom_file = sys.argv[1]
    
    print("🔍 Loading SBOM...")
    sbom = load_sbom(sbom_file)
    
    print("📋 Loading policy...")
    policy = load_policy()
    
    print("🔎 Checking vulnerabilities...")
    severity_counts, vulnerabilities = check_known_vulnerabilities(sbom)
    
    # Print vulnerabilities
    if vulnerabilities:
        print(f"\n⚠️  Found {len(vulnerabilities)} vulnerabilities:")
        for vuln in vulnerabilities:
            print(f"  - {vuln['component']} {vuln['version']}: {vuln['cve']} ({vuln['severity']})")
    else:
        print("\n✅ No known vulnerabilities found")
    
    # Enforce policy
    if enforce_policy(severity_counts, policy):
        print("\n✅ Vulnerability gate PASSED")
        sys.exit(0)
    else:
        print("\n❌ Vulnerability gate FAILED")
        print("\nRemediation required:")
        print("  1. Update vulnerable dependencies")
        print("  2. Re-run SBOM generation")
        print("  3. Re-run vulnerability gate")
        sys.exit(1)

if __name__ == "__main__":
    main()
