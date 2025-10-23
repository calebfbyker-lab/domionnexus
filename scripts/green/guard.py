#!/usr/bin/env python3
"""
Green Operations Guard for Codex Immortal v26.0
Carbon-aware workload scheduling and sustainability monitoring.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


def load_greenops_config():
    """Load green operations configuration."""
    config_path = Path(__file__).parent.parent.parent / "config" / "greenops.json"
    if not config_path.exists():
        print(f"❌ Green ops config not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)


def get_carbon_intensity(region: str) -> Dict:
    """
    Get current carbon intensity for a region.
    
    In production, integrate with:
    - Electricity Map API
    - Cloud provider carbon APIs
    - WattTime API
    
    Args:
        region: Cloud region identifier
    
    Returns:
        dict: Carbon intensity data
    """
    # Stub data (in production, fetch from API)
    stub_data = {
        "us-east-1": {
            "carbon_intensity_gco2_kwh": 420,
            "renewable_percentage": 0.35,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "eu-west-1": {
            "carbon_intensity_gco2_kwh": 180,
            "renewable_percentage": 0.72,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "ap-southeast-1": {
            "carbon_intensity_gco2_kwh": 520,
            "renewable_percentage": 0.28,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    return stub_data.get(region, {
        "carbon_intensity_gco2_kwh": 400,
        "renewable_percentage": 0.50,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


def evaluate_region(region: str, config: Dict) -> Dict:
    """
    Evaluate a region's carbon footprint.
    
    Args:
        region: Cloud region identifier
        config: Green ops configuration
    
    Returns:
        dict: Evaluation result
    """
    data = get_carbon_intensity(region)
    thresholds = config["thresholds"]
    
    carbon_intensity = data["carbon_intensity_gco2_kwh"]
    
    if carbon_intensity <= thresholds["optimal_carbon_intensity_gco2_kwh"]:
        status = "optimal"
        recommendation = "Excellent for running workloads"
    elif carbon_intensity <= thresholds["warning_carbon_intensity_gco2_kwh"]:
        status = "good"
        recommendation = "Good for running workloads"
    elif carbon_intensity <= thresholds["max_carbon_intensity_gco2_kwh"]:
        status = "warning"
        recommendation = "Consider deferring non-critical workloads"
    else:
        status = "critical"
        recommendation = "Defer workloads or switch to greener region"
    
    return {
        "region": region,
        "status": status,
        "carbon_intensity_gco2_kwh": carbon_intensity,
        "renewable_percentage": data["renewable_percentage"],
        "recommendation": recommendation,
        "timestamp": data["timestamp"]
    }


def select_optimal_region(regions: list, config: Dict) -> str:
    """
    Select the most carbon-optimal region.
    
    Args:
        regions: List of available regions
        config: Green ops configuration
    
    Returns:
        str: Optimal region identifier
    """
    evaluations = [evaluate_region(region, config) for region in regions]
    
    # Sort by carbon intensity (lower is better)
    evaluations.sort(key=lambda x: x["carbon_intensity_gco2_kwh"])
    
    return evaluations[0]["region"]


def main():
    """Main entry point for green ops guard."""
    print("=" * 60)
    print("Green Operations Guard")
    print("=" * 60)
    
    config = load_greenops_config()
    
    print(f"\n🌍 Carbon Tracking: {'✅ Enabled' if config['carbon_tracking']['enabled'] else '❌ Disabled'}")
    print(f"🎯 Goal: Carbon neutral by {config['sustainability_goals']['carbon_neutral_by']}")
    print(f"⚡ Renewable target: {config['sustainability_goals']['renewable_energy_target']:.0%}")
    
    # Evaluate all regions
    regions = config["carbon_tracking"]["regions"]
    
    print(f"\n📊 Evaluating {len(regions)} regions:")
    
    evaluations = []
    for region in regions:
        eval_result = evaluate_region(region, config)
        evaluations.append(eval_result)
        
        status_emoji = {
            "optimal": "🟢",
            "good": "🟡",
            "warning": "🟠",
            "critical": "🔴"
        }[eval_result["status"]]
        
        print(f"\n   {status_emoji} {region}")
        print(f"      Carbon: {eval_result['carbon_intensity_gco2_kwh']} gCO2/kWh")
        print(f"      Renewable: {eval_result['renewable_percentage']:.0%}")
        print(f"      {eval_result['recommendation']}")
    
    # Recommend optimal region
    optimal_region = select_optimal_region(regions, config)
    
    print("\n" + "=" * 60)
    print("Recommendation")
    print("=" * 60)
    print(f"\n✅ Optimal region: {optimal_region}")
    
    optimal_eval = next(e for e in evaluations if e["region"] == optimal_region)
    print(f"   Carbon intensity: {optimal_eval['carbon_intensity_gco2_kwh']} gCO2/kWh")
    print(f"   Renewable energy: {optimal_eval['renewable_percentage']:.0%}")
    
    print("\n⚠️  STUB MODE: Integrate with Electricity Map or WattTime API for real data")
    
    # Exit with success if we have at least one good region
    has_good_region = any(e["status"] in ["optimal", "good"] for e in evaluations)
    return 0 if has_good_region else 1


if __name__ == "__main__":
    sys.exit(main())
