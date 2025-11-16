#!/usr/bin/env python3
"""
Canary Guard for Codex Immortal v26.0
Monitors canary deployments and provides safety gates.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


def load_feature_flags():
    """Load feature flags configuration."""
    flags_path = Path(__file__).parent.parent.parent / "config" / "feature_flags.json"
    if not flags_path.exists():
        print(f"❌ Feature flags not found at {flags_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(flags_path, 'r') as f:
        return json.load(f)


def check_canary_health(flag_name: str, metrics: dict) -> dict:
    """
    Check health metrics for a canary deployment.
    
    Args:
        flag_name: Name of the feature flag
        metrics: Dictionary of health metrics
    
    Returns:
        dict: Health check result
    """
    result = {
        "flag": flag_name,
        "healthy": True,
        "errors": [],
        "warnings": [],
        "metrics": metrics
    }
    
    # Define thresholds
    thresholds = {
        "error_rate": 0.01,      # 1% error rate
        "latency_p99": 1000,      # 1000ms p99 latency
        "cpu_usage": 0.80,        # 80% CPU usage
        "memory_usage": 0.85,     # 85% memory usage
    }
    
    # Check error rate
    if metrics.get("error_rate", 0) > thresholds["error_rate"]:
        result["healthy"] = False
        result["errors"].append(
            f"Error rate {metrics['error_rate']:.2%} exceeds threshold {thresholds['error_rate']:.2%}"
        )
    
    # Check latency
    if metrics.get("latency_p99", 0) > thresholds["latency_p99"]:
        result["warnings"].append(
            f"P99 latency {metrics['latency_p99']}ms exceeds threshold {thresholds['latency_p99']}ms"
        )
    
    # Check CPU usage
    if metrics.get("cpu_usage", 0) > thresholds["cpu_usage"]:
        result["warnings"].append(
            f"CPU usage {metrics['cpu_usage']:.1%} exceeds threshold {thresholds['cpu_usage']:.1%}"
        )
    
    # Check memory usage
    if metrics.get("memory_usage", 0) > thresholds["memory_usage"]:
        result["healthy"] = False
        result["errors"].append(
            f"Memory usage {metrics['memory_usage']:.1%} exceeds threshold {thresholds['memory_usage']:.1%}"
        )
    
    return result


def get_canary_recommendation(health_results: list) -> str:
    """
    Get recommendation based on canary health checks.
    
    Args:
        health_results: List of health check results
    
    Returns:
        str: Recommendation (proceed, hold, rollback)
    """
    unhealthy_count = sum(1 for r in health_results if not r["healthy"])
    warning_count = sum(len(r["warnings"]) for r in health_results)
    
    if unhealthy_count > 0:
        return "rollback"
    elif warning_count > 3:
        return "hold"
    else:
        return "proceed"


def main():
    """Main entry point for canary guard."""
    print("=" * 60)
    print("Canary Deployment Guard")
    print("=" * 60)
    
    config = load_feature_flags()
    
    # Get all canary-enabled flags
    canary_flags = [
        flag_name
        for flag_name, flag_config in config["flags"].items()
        if flag_config.get("canary_enabled")
    ]
    
    if not canary_flags:
        print("\n⚠️  No canary deployments active")
        return 0
    
    print(f"\n🐦 Found {len(canary_flags)} canary deployments:")
    for flag in canary_flags:
        percentage = config["flags"][flag].get("canary_percentage", 0)
        print(f"   - {flag} ({percentage}% rollout)")
    
    # Simulate health checks (in production, fetch real metrics)
    print("\n🏥 Checking canary health...")
    
    health_results = []
    
    for flag_name in canary_flags:
        # In production, fetch real metrics from monitoring system
        # Example: metrics = fetch_metrics_from_datadog(flag_name)
        metrics = {
            "error_rate": 0.005,     # 0.5%
            "latency_p99": 450,      # 450ms
            "cpu_usage": 0.65,       # 65%
            "memory_usage": 0.72,    # 72%
            "request_count": 10000
        }
        
        health = check_canary_health(flag_name, metrics)
        health_results.append(health)
        
        status = "✅ HEALTHY" if health["healthy"] else "❌ UNHEALTHY"
        print(f"\n   {flag_name}: {status}")
        
        if health["errors"]:
            print("      Errors:")
            for error in health["errors"]:
                print(f"         - {error}")
        
        if health["warnings"]:
            print("      Warnings:")
            for warning in health["warnings"]:
                print(f"         - {warning}")
    
    # Get recommendation
    recommendation = get_canary_recommendation(health_results)
    
    print("\n" + "=" * 60)
    print("Canary Guard Recommendation")
    print("=" * 60)
    
    if recommendation == "proceed":
        print("✅ PROCEED - All canary deployments healthy")
        print("   Safe to increase canary percentage or promote to production")
        exit_code = 0
    elif recommendation == "hold":
        print("⚠️  HOLD - Some warnings detected")
        print("   Monitor closely before proceeding")
        exit_code = 0
    else:
        print("❌ ROLLBACK - Unhealthy canary detected")
        print("   Roll back canary deployment immediately")
        exit_code = 1
    
    print("\n⚠️  Note: This is a stub. Integrate with your monitoring system in production.")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
