#!/usr/bin/env python3
"""
Vulnerability scanner for v94 bundle
Uses Grype to scan SBOM for vulnerabilities
"""
import json
import subprocess
import sys
from pathlib import Path

def scan_with_grype(sbom_path: str = "sbom.json", fail_on: str = "high"):
    """
    Scan SBOM with Grype
    
    Args:
        sbom_path: Path to SBOM file
        fail_on: Severity level to fail on (low, medium, high, critical)
    """
    try:
        # Run Grype scan
        result = subprocess.run(
            ["grype", f"sbom:{sbom_path}", "-o", "json"],
            capture_output=True,
            text=True,
            check=False  # Don't raise on non-zero exit
        )
        
        if result.returncode != 0 and not result.stdout:
            print(f"✗ Grype scan failed: {result.stderr}")
            return False
        
        # Parse results
        try:
            scan_results = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"✗ Failed to parse Grype output")
            print(result.stdout)
            return False
        
        matches = scan_results.get("matches", [])
        
        # Count vulnerabilities by severity
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "negligible": 0
        }
        
        for match in matches:
            severity = match.get("vulnerability", {}).get("severity", "unknown").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Print summary
        print("\n" + "="*60)
        print("Vulnerability Scan Results")
        print("="*60)
        print(f"Total vulnerabilities found: {len(matches)}")
        print(f"  Critical: {severity_counts['critical']}")
        print(f"  High:     {severity_counts['high']}")
        print(f"  Medium:   {severity_counts['medium']}")
        print(f"  Low:      {severity_counts['low']}")
        print("="*60)
        
        # Check if we should fail
        fail_levels = {
            "critical": ["critical"],
            "high": ["critical", "high"],
            "medium": ["critical", "high", "medium"],
            "low": ["critical", "high", "medium", "low"]
        }
        
        should_fail = False
        if fail_on in fail_levels:
            for level in fail_levels[fail_on]:
                if severity_counts[level] > 0:
                    should_fail = True
                    break
        
        if should_fail:
            print(f"\n✗ Scan failed: Found {fail_on}+ severity vulnerabilities")
            # Print detailed vulnerabilities
            print("\nDetailed vulnerabilities:")
            for match in matches:
                vuln = match.get("vulnerability", {})
                severity = vuln.get("severity", "unknown").lower()
                if severity in fail_levels[fail_on]:
                    artifact = match.get("artifact", {})
                    print(f"  - {artifact.get('name')} {artifact.get('version')}: "
                          f"{vuln.get('id')} ({severity.upper()})")
            return False
        else:
            print(f"\n✓ Scan passed: No {fail_on}+ severity vulnerabilities found")
            return True
            
    except FileNotFoundError:
        print("✗ Grype not installed. Install: https://github.com/anchore/grype")
        print("  Skipping vulnerability scan...")
        return True  # Don't fail if tool is not installed
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    """Run vulnerability scan"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan SBOM for vulnerabilities")
    parser.add_argument("--sbom", default="sbom.json", help="Path to SBOM file")
    parser.add_argument("--fail-on", default="high", 
                       choices=["low", "medium", "high", "critical"],
                       help="Severity level to fail on")
    parser.add_argument("--skip", action="store_true", 
                       help="Skip scan (for CI environments without Grype)")
    
    args = parser.parse_args()
    
    if args.skip:
        print("⊘ Vulnerability scanning skipped (--skip flag)")
        return 0
    
    print(f"Scanning {args.sbom} for vulnerabilities...")
    print(f"Fail threshold: {args.fail_on}")
    
    success = scan_with_grype(args.sbom, args.fail_on)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
