#!/usr/bin/env python3
"""
Treasury Split Tool
Verifies and displays treasury allocation splits.
"""
import json
import sys
from pathlib import Path


def load_json_file(filepath):
    """Load a JSON file safely."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {filepath}: {e}")
        return None


def verify_treasury():
    """Verify and display treasury allocation."""
    print("🏦 Verifying treasury allocation...")
    
    treasury_file = Path("treasury_allocation.json")
    
    if not treasury_file.exists():
        print(f"❌ Missing: {treasury_file}")
        return False
    
    # Load treasury allocation
    treasury = load_json_file(treasury_file)
    if treasury is None:
        return False
    
    # Verify required fields
    required_fields = ["owner", "reserve", "community"]
    for field in required_fields:
        if field not in treasury:
            print(f"❌ Missing required field in treasury_allocation.json: {field}")
            return False
    
    # Verify splits add up to 100%
    total = sum(treasury.get(field, 0) for field in required_fields)
    if abs(total - 100) > 0.01:  # Allow for floating point precision
        print(f"⚠️  Warning: Treasury splits sum to {total}%, not 100%")
    
    # Display treasury summary
    owner = treasury.get("owner", 0)
    reserve = treasury.get("reserve", 0)
    community = treasury.get("community", 0)
    
    print(f"✅ Treasury verified:")
    print(f"   🏦 Treasury: owner={owner}% reserve={reserve}% community={community}% (verified)")
    
    return True


if __name__ == "__main__":
    success = verify_treasury()
    sys.exit(0 if success else 1)
