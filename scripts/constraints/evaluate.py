#!/usr/bin/env python3
"""
Constraints Evaluator for Codex Immortal v26.0
Evaluates system constraints and requirements.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def evaluate_api_constraints() -> Dict:
    """Evaluate API constraints."""
    print("🔍 Evaluating API constraints...")
    
    errors = []
    warnings = []
    
    # Check OpenAPI spec
    openapi_spec = Path("api/openapi.json")
    if not openapi_spec.exists():
        errors.append("OpenAPI specification missing")
    else:
        with open(openapi_spec) as f:
            spec = json.load(f)
            
            # Verify OpenAPI version
            if not spec.get("openapi", "").startswith("3.0"):
                errors.append(f"Unsupported OpenAPI version: {spec.get('openapi')}")
            
            # Check for security schemes
            if not spec.get("components", {}).get("securitySchemes"):
                warnings.append("No security schemes defined in API spec")
            
            # Check for required metadata
            info = spec.get("info", {})
            if not info.get("version"):
                errors.append("API version not specified")
            
            if info.get("version") != "26.0.0":
                warnings.append(f"API version mismatch: expected 26.0.0, got {info.get('version')}")
    
    return {
        "constraint": "API Constraints",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def evaluate_sdk_constraints() -> Dict:
    """Evaluate SDK generation constraints."""
    print("🔍 Evaluating SDK constraints...")
    
    errors = []
    
    # Check SDK generator script
    sdk_generator = Path("scripts/sdk/generate_clients_stub.py")
    if not sdk_generator.exists():
        errors.append("SDK generator script missing")
    
    return {
        "constraint": "SDK Constraints",
        "passed": len(errors) == 0,
        "errors": errors
    }


def evaluate_marketplace_constraints() -> Dict:
    """Evaluate marketplace constraints."""
    print("🔍 Evaluating marketplace constraints...")
    
    errors = []
    warnings = []
    
    # Check marketplace policy
    policy_path = Path("config/marketplace_policy.json")
    if not policy_path.exists():
        errors.append("Marketplace policy missing")
    else:
        with open(policy_path) as f:
            policy = json.load(f)
            
            # Check review workflow
            if not policy.get("review_workflow"):
                errors.append("Review workflow not defined")
            
            # Check rate limits
            if not policy.get("rate_limits"):
                warnings.append("Rate limits not defined")
    
    # Check app review script
    app_review = Path("scripts/marketplace/app_review.py")
    if not app_review.exists():
        errors.append("App review script missing")
    
    return {
        "constraint": "Marketplace Constraints",
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def evaluate_feature_flag_constraints() -> Dict:
    """Evaluate feature flag constraints."""
    print("🔍 Evaluating feature flag constraints...")
    
    errors = []
    
    # Check feature flags config
    flags_config = Path("config/feature_flags.json")
    if not flags_config.exists():
        errors.append("Feature flags configuration missing")
    else:
        with open(flags_config) as f:
            flags = json.load(f)
            
            # Verify version
            if flags.get("version") != "26.0.0":
                errors.append(f"Feature flags version mismatch: {flags.get('version')}")
    
    # Check flag evaluation script
    flag_eval = Path("scripts/feature/flag_eval.py")
    if not flag_eval.exists():
        errors.append("Feature flag evaluation script missing")
    
    # Check canary guard
    canary_guard = Path("scripts/feature/canary_guard.py")
    if not canary_guard.exists():
        errors.append("Canary guard script missing")
    
    return {
        "constraint": "Feature Flag Constraints",
        "passed": len(errors) == 0,
        "errors": errors
    }


def evaluate_model_constraints() -> Dict:
    """Evaluate model registry constraints."""
    print("🔍 Evaluating model constraints...")
    
    errors = []
    
    # Check model schema
    model_schema = Path("schemas/model_entry.schema.json")
    if not model_schema.exists():
        errors.append("Model entry schema missing")
    
    # Check model scripts
    register_script = Path("scripts/models/register_model.py")
    eval_script = Path("scripts/models/run_evals_stub.py")
    
    if not register_script.exists():
        errors.append("Model registration script missing")
    
    if not eval_script.exists():
        errors.append("Model evaluation script missing")
    
    return {
        "constraint": "Model Constraints",
        "passed": len(errors) == 0,
        "errors": errors
    }


def main():
    """Main entry point for constraints evaluation."""
    print("=" * 60)
    print("Constraints Evaluator")
    print("=" * 60)
    
    # Run all constraint evaluations
    evaluations = [
        evaluate_api_constraints(),
        evaluate_sdk_constraints(),
        evaluate_marketplace_constraints(),
        evaluate_feature_flag_constraints(),
        evaluate_model_constraints()
    ]
    
    # Summary
    print("\n" + "=" * 60)
    print("Constraints Summary")
    print("=" * 60)
    
    passed_count = sum(1 for e in evaluations if e["passed"])
    total_count = len(evaluations)
    
    print(f"\n📊 Results: {passed_count}/{total_count} constraints satisfied\n")
    
    for evaluation in evaluations:
        status = "✅" if evaluation["passed"] else "❌"
        print(f"{status} {evaluation['constraint']}")
        
        if evaluation.get("errors"):
            for error in evaluation["errors"]:
                print(f"      ❌ {error}")
        
        if evaluation.get("warnings"):
            for warning in evaluation["warnings"]:
                print(f"      ⚠️  {warning}")
    
    if passed_count == total_count:
        print("\n✅ All constraints satisfied!")
        return 0
    else:
        print(f"\n❌ {total_count - passed_count} constraint(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
