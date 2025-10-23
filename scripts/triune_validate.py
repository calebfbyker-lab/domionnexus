#!/usr/bin/env python3
"""
Triune Validator for Codex Immortal v26.0
Three-fold validation: Structure, Security, and Semantics.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def validate_structure() -> Dict:
    """Validate structural integrity."""
    print("🔍 Validating structure (Triune 1/3)...")
    
    errors = []
    
    # Check directory structure
    required_dirs = [
        "api",
        "config",
        "schemas",
        "scripts",
        "i18n",
        "trust"
    ]
    
    for dir_name in required_dirs:
        if not Path(dir_name).is_dir():
            errors.append(f"Missing required directory: {dir_name}")
    
    # Check critical files
    critical_files = [
        "api/openapi.json",
        "config/marketplace_policy.json",
        "config/feature_flags.json",
        "schemas/model_entry.schema.json"
    ]
    
    for file_path in critical_files:
        if not Path(file_path).exists():
            errors.append(f"Missing critical file: {file_path}")
    
    return {
        "aspect": "Structure",
        "passed": len(errors) == 0,
        "errors": errors
    }


def validate_security() -> Dict:
    """Validate security aspects."""
    print("🔍 Validating security (Triune 2/3)...")
    
    errors = []
    warnings = []
    
    # Check webhook signing
    sign_stub = Path("scripts/webhooks/sign_stub.py")
    verify_stub = Path("scripts/webhooks/verify_stub.py")
    
    if not sign_stub.exists():
        errors.append("Webhook signing stub missing")
    elif "STUB" not in sign_stub.read_text():
        warnings.append("Webhook signing stub may contain production code")
    
    if not verify_stub.exists():
        errors.append("Webhook verification stub missing")
    
    # Check for hardcoded secrets
    python_files = list(Path(".").rglob("*.py"))
    for py_file in python_files:
        try:
            content = py_file.read_text()
            # Simple checks for common secret patterns
            if any(pattern in content.lower() for pattern in ["sk-", "api_key = \"", "secret = \"", "password = \""]):
                # Ignore if it's a stub or example
                if "STUB" not in content and "example" not in str(py_file).lower():
                    warnings.append(f"Possible hardcoded secret in {py_file}")
        except Exception:
            pass
    
    return {
        "aspect": "Security",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_semantics() -> Dict:
    """Validate semantic correctness."""
    print("🔍 Validating semantics (Triune 3/3)...")
    
    errors = []
    warnings = []
    
    # Validate JSON files
    json_files = [
        "api/openapi.json",
        "config/marketplace_policy.json",
        "config/feature_flags.json",
        "config/greenops.json",
        "schemas/model_entry.schema.json",
        "i18n/en.json",
        "i18n/es.json"
    ]
    
    for json_file in json_files:
        json_path = Path(json_file)
        if json_path.exists():
            try:
                with open(json_path) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in {json_file}: {str(e)}")
    
    # Check version consistency
    version_files = {
        "api/openapi.json": ["info", "version"],
        "config/marketplace_policy.json": ["version"],
        "config/feature_flags.json": ["version"],
        "config/greenops.json": ["version"]
    }
    
    expected_version = "26.0.0"
    
    for file_path, keys in version_files.items():
        if Path(file_path).exists():
            with open(file_path) as f:
                data = json.load(f)
                version = data
                for key in keys:
                    version = version.get(key, {})
                
                if isinstance(version, str) and version != expected_version:
                    warnings.append(f"Version mismatch in {file_path}: {version} != {expected_version}")
    
    return {
        "aspect": "Semantics",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def main():
    """Main entry point for Triune validation."""
    print("=" * 60)
    print("Triune Validator")
    print("Three-fold validation: Structure, Security, Semantics")
    print("=" * 60)
    
    # Run all three validations
    validations = [
        validate_structure(),
        validate_security(),
        validate_semantics()
    ]
    
    # Summary
    print("\n" + "=" * 60)
    print("Triune Validation Summary")
    print("=" * 60)
    
    passed_count = sum(1 for v in validations if v["passed"])
    total_count = len(validations)
    
    print(f"\n📊 Results: {passed_count}/{total_count} aspects validated\n")
    
    for validation in validations:
        status = "✅" if validation["passed"] else "❌"
        print(f"{status} {validation['aspect']}")
        
        if validation.get("errors"):
            for error in validation["errors"]:
                print(f"      ❌ {error}")
        
        if validation.get("warnings"):
            for warning in validation["warnings"]:
                print(f"      ⚠️  {warning}")
    
    if passed_count == total_count:
        print("\n✅ Triune validation passed!")
        return 0
    else:
        print(f"\n❌ Triune validation failed: {total_count - passed_count} aspect(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
