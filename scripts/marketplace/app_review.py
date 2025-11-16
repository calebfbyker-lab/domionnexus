#!/usr/bin/env python3
"""
Marketplace App Review Gate for Codex Immortal v26.0
Automated and manual review workflow for marketplace submissions.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_policy():
    """Load marketplace policy configuration."""
    policy_path = Path(__file__).parent.parent.parent / "config" / "marketplace_policy.json"
    if not policy_path.exists():
        print(f"❌ Policy not found at {policy_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(policy_path, 'r') as f:
        return json.load(f)


def check_metadata(app_data, required_fields):
    """Verify required metadata is present."""
    errors = []
    for field in required_fields:
        if field not in app_data or not app_data[field]:
            errors.append(f"Missing required field: {field}")
    return errors


def check_security_scan(app_data):
    """Stub for security vulnerability scanning."""
    # In production, integrate with:
    # - Snyk, Dependabot, or similar for dependency scanning
    # - SonarQube for static code analysis
    # - Custom security scanners
    
    print("🔍 Running security scan (stub)...")
    
    vulnerabilities = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    # Stub: In production, actually scan the app
    print("   ✅ No vulnerabilities found (stub)")
    
    return vulnerabilities


def check_license(app_data):
    """Verify license compliance."""
    print("📜 Checking license compliance...")
    
    allowed_licenses = [
        "ECCL-1.0",
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "GPL-3.0"
    ]
    
    license_name = app_data.get("license", "")
    
    if not license_name:
        return False, "No license specified"
    
    if license_name not in allowed_licenses:
        return False, f"License '{license_name}' not in allowed list"
    
    print(f"   ✅ License '{license_name}' is allowed")
    return True, None


def review_app(app_data):
    """
    Execute app review workflow.
    
    Returns:
        dict: Review result with status and details
    """
    policy = load_policy()
    
    result = {
        "status": "pending",
        "checks": {},
        "errors": [],
        "warnings": [],
        "reviewed_at": datetime.utcnow().isoformat() + "Z"
    }
    
    print("\n" + "=" * 60)
    print(f"Reviewing App: {app_data.get('name', 'Unknown')}")
    print("=" * 60)
    
    # Check 1: Metadata validation
    print("\n📋 Checking metadata...")
    required_fields = policy["intake_policy"]["rejection_criteria"]["required_metadata"]
    metadata_errors = check_metadata(app_data, required_fields)
    
    if metadata_errors:
        result["errors"].extend(metadata_errors)
        result["checks"]["metadata"] = "failed"
    else:
        print("   ✅ All required metadata present")
        result["checks"]["metadata"] = "passed"
    
    # Check 2: Security scan
    vulnerabilities = check_security_scan(app_data)
    result["checks"]["security_scan"] = vulnerabilities
    
    max_vulns = policy["intake_policy"]["rejection_criteria"]["max_vulnerabilities"]
    
    if vulnerabilities["critical"] > max_vulns["critical"]:
        result["errors"].append(f"Too many critical vulnerabilities: {vulnerabilities['critical']}")
        result["status"] = "rejected"
    elif vulnerabilities["high"] > max_vulns["high"]:
        result["errors"].append(f"Too many high vulnerabilities: {vulnerabilities['high']}")
        result["status"] = "rejected"
    elif vulnerabilities["medium"] > max_vulns["medium"]:
        result["warnings"].append(f"High number of medium vulnerabilities: {vulnerabilities['medium']}")
    
    # Check 3: License verification
    license_valid, license_error = check_license(app_data)
    if license_valid:
        result["checks"]["license"] = "passed"
    else:
        result["errors"].append(license_error)
        result["checks"]["license"] = "failed"
    
    # Determine final status
    if not result["errors"] and result["status"] != "rejected":
        if policy["intake_policy"]["review_required"]:
            result["status"] = "pending_manual_review"
            print("\n⏳ App passed automated checks. Manual review required.")
        else:
            result["status"] = "approved"
            print("\n✅ App approved automatically!")
    elif result["status"] != "rejected":
        result["status"] = "rejected"
        print("\n❌ App rejected due to failures in automated checks.")
    
    return result


def main():
    """Main entry point for app review."""
    print("=" * 60)
    print("Marketplace App Review Gate")
    print("=" * 60)
    
    # Example app submission
    app_data = {
        "name": "Example Marketplace App",
        "version": "1.0.0",
        "description": "A sample marketplace application",
        "license": "ECCL-1.0",
        "author": "Domion Nexus",
        "homepage": "https://example.com"
    }
    
    # Run review
    result = review_app(app_data)
    
    print("\n" + "=" * 60)
    print("Review Summary")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    if result["status"] == "approved" or result["status"] == "pending_manual_review":
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
