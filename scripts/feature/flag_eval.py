#!/usr/bin/env python3
"""
Feature Flag Evaluation for Codex Immortal v26.0
Evaluates feature flags for users, organizations, and regions.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional


def load_feature_flags():
    """Load feature flags configuration."""
    flags_path = Path(__file__).parent.parent.parent / "config" / "feature_flags.json"
    if not flags_path.exists():
        print(f"❌ Feature flags not found at {flags_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(flags_path, 'r') as f:
        return json.load(f)


def is_canary_target(flag_config: Dict, context: Dict) -> bool:
    """
    Check if the current context matches canary targets.
    
    Args:
        flag_config: Feature flag configuration
        context: Evaluation context (user_id, org_id, region, etc.)
    
    Returns:
        bool: True if context matches canary targets
    """
    if not flag_config.get("canary_enabled"):
        return False
    
    canary_targets = flag_config.get("canary_targets", [])
    
    for target in canary_targets:
        target_type, target_value = target.split(":", 1)
        
        if target_type == "user" and context.get("user_id") == target_value:
            return True
        elif target_type == "org" and context.get("org_id") == target_value:
            return True
        elif target_type == "region" and context.get("region") == target_value:
            return True
    
    return False


def evaluate_flag(flag_name: str, context: Optional[Dict] = None, environment: str = "production") -> bool:
    """
    Evaluate a feature flag for the given context.
    
    Args:
        flag_name: Name of the feature flag
        context: Evaluation context (optional)
        environment: Environment name (production, staging, development)
    
    Returns:
        bool: True if flag is enabled for this context
    """
    config = load_feature_flags()
    
    if flag_name not in config["flags"]:
        print(f"⚠️  Unknown flag: {flag_name}", file=sys.stderr)
        return False
    
    flag_config = config["flags"][flag_name]
    
    # Check environment overrides
    env_config = config.get("environments", {}).get(environment, {})
    env_overrides = env_config.get("override_flags", {})
    
    if flag_name in env_overrides:
        return env_overrides[flag_name]
    
    # Check if globally enabled
    if not flag_config.get("enabled", False):
        return False
    
    # Check canary targeting if context provided
    if context and flag_config.get("canary_enabled"):
        if is_canary_target(flag_config, context):
            return True
        
        # If not a canary target, flag is disabled (canary rollout)
        # In a real implementation, might use percentage-based rollout here
        return False
    
    return True


def main():
    """Main entry point for feature flag evaluation."""
    print("=" * 60)
    print("Feature Flag Evaluation")
    print("=" * 60)
    
    # Example contexts
    contexts = [
        {
            "name": "Alpha Tester",
            "user_id": "alpha-tester-001",
            "org_id": "test-org",
            "region": "us"
        },
        {
            "name": "Beta Tester",
            "user_id": "beta-tester-001",
            "org_id": "test-org",
            "region": "us"
        },
        {
            "name": "Regular User",
            "user_id": "regular-user-001",
            "org_id": "customer-org",
            "region": "eu"
        },
        {
            "name": "Internal User",
            "user_id": "internal-001",
            "org_id": "domionnexus-internal",
            "region": "us"
        }
    ]
    
    flags_to_test = [
        "marketplace_enabled",
        "webhook_signing_v2",
        "sdk_generation_auto",
        "i18n_runtime_loading"
    ]
    
    for context in contexts:
        print(f"\n📊 Context: {context['name']}")
        print(f"   User: {context['user_id']}")
        print(f"   Org: {context['org_id']}")
        print(f"   Region: {context['region']}")
        print("\n   Flags:")
        
        for flag in flags_to_test:
            enabled = evaluate_flag(flag, context)
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"      {flag}: {status}")
    
    print("\n" + "=" * 60)
    print("✅ Feature flag evaluation complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
