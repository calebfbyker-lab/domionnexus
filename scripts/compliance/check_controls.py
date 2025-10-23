#!/usr/bin/env python3
"""
Controls Compliance Checker for Codex Immortal v26.0
Validates compliance controls and security requirements.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def check_eccl_compliance() -> Dict:
    """Check ECCL-1.0 license compliance."""
    print("🔍 Checking ECCL-1.0 compliance...")
    
    # Check for required files
    required_files = [
        "README.md",
        "trust/overview.json"
    ]
    
    errors = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            errors.append(f"Missing required file: {file_path}")
    
    # Check for subject ID in README
    readme_path = Path("README.md")
    if readme_path.exists():
        content = readme_path.read_text()
        if "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a" not in content:
            errors.append("Subject ID not found in README.md")
    
    return {
        "control": "ECCL Compliance",
        "passed": len(errors) == 0,
        "errors": errors
    }


def check_security_controls() -> Dict:
    """Check security controls."""
    print("🔍 Checking security controls...")
    
    errors = []
    warnings = []
    
    # Check for webhook signing
    webhook_sign = Path("scripts/webhooks/sign_stub.py")
    webhook_verify = Path("scripts/webhooks/verify_stub.py")
    
    if not webhook_sign.exists() or not webhook_verify.exists():
        errors.append("Webhook signing scripts missing")
    
    # Check for marketplace policy
    marketplace_policy = Path("config/marketplace_policy.json")
    if marketplace_policy.exists():
        with open(marketplace_policy) as f:
            policy = json.load(f)
            if not policy.get("security", {}).get("webhook_signature_required"):
                warnings.append("Webhook signature not required in policy")
    else:
        errors.append("Marketplace policy missing")
    
    return {
        "control": "Security Controls",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def check_data_residency() -> Dict:
    """Check data residency controls."""
    print("🔍 Checking data residency controls...")
    
    errors = []
    
    residency_script = Path("scripts/residency/enforce_paths_stub.py")
    if not residency_script.exists():
        errors.append("Data residency enforcement script missing")
    
    marketplace_policy = Path("config/marketplace_policy.json")
    if marketplace_policy.exists():
        with open(marketplace_policy) as f:
            policy = json.load(f)
            if not policy.get("compliance", {}).get("data_residency_rules"):
                errors.append("Data residency rules not defined in policy")
    
    return {
        "control": "Data Residency",
        "passed": len(errors) == 0,
        "errors": errors
    }


def check_green_ops() -> Dict:
    """Check green operations controls."""
    print("🔍 Checking green ops controls...")
    
    errors = []
    
    greenops_config = Path("config/greenops.json")
    greenops_script = Path("scripts/green/guard.py")
    
    if not greenops_config.exists():
        errors.append("Green ops configuration missing")
    
    if not greenops_script.exists():
        errors.append("Green ops guard script missing")
    
    return {
        "control": "Green Operations",
        "passed": len(errors) == 0,
        "errors": errors
    }


def check_i18n_compliance() -> Dict:
    """Check internationalization compliance."""
    print("🔍 Checking i18n compliance...")
    
    errors = []
    warnings = []
    
    # Check for required language files
    required_langs = ["en.json", "es.json"]
    i18n_dir = Path("i18n")
    
    if not i18n_dir.exists():
        errors.append("i18n directory missing")
    else:
        for lang_file in required_langs:
            if not (i18n_dir / lang_file).exists():
                errors.append(f"Missing translation file: {lang_file}")
    
    # Check for i18n checker script
    i18n_checker = Path("scripts/i18n/check_keys.py")
    if not i18n_checker.exists():
        warnings.append("i18n key checker script missing")
    
    return {
        "control": "Internationalization",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def main():
    """Main entry point for compliance checking."""
    print("=" * 60)
    print("Compliance Controls Checker")
    print("=" * 60)
    
    # Run all compliance checks
    checks = [
        check_eccl_compliance(),
        check_security_controls(),
        check_data_residency(),
        check_green_ops(),
        check_i18n_compliance()
    ]
    
    # Summary
    print("\n" + "=" * 60)
    print("Compliance Summary")
    print("=" * 60)
    
    passed_count = sum(1 for c in checks if c["passed"])
    total_count = len(checks)
    
    print(f"\n📊 Results: {passed_count}/{total_count} controls passed\n")
    
    for check in checks:
        status = "✅" if check["passed"] else "❌"
        print(f"{status} {check['control']}")
        
        if check.get("errors"):
            for error in check["errors"]:
                print(f"      ❌ {error}")
        
        if check.get("warnings"):
            for warning in check["warnings"]:
                print(f"      ⚠️  {warning}")
    
    if passed_count == total_count:
        print("\n✅ All compliance controls passed!")
        return 0
    else:
        print(f"\n❌ {total_count - passed_count} control(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
