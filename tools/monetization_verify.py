#!/usr/bin/env python3
"""
Monetization Verification Tool
Verifies the integrity and consistency of the monetization system.
"""
import json
import sys
import os
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


def verify_monetization():
    """Verify monetization configuration and ledger."""
    print("🔍 Verifying monetization system...")
    
    # Check if required files exist
    economy_file = Path("economy_monetization.json")
    ledger_file = Path("chain/monetization_ledger.jsonl")
    
    if not economy_file.exists():
        print(f"❌ Missing: {economy_file}")
        return False
    
    if not ledger_file.exists():
        print(f"⚠️  Warning: {ledger_file} does not exist yet")
        # Create empty ledger if it doesn't exist
        ledger_file.parent.mkdir(parents=True, exist_ok=True)
        ledger_file.touch()
        print(f"✅ Created empty ledger: {ledger_file}")
    
    # Verify economy configuration
    economy = load_json_file(economy_file)
    if economy is None:
        return False
    
    # Check required fields
    required_fields = ["version", "treasury_splits", "policies"]
    for field in required_fields:
        if field not in economy:
            print(f"❌ Missing required field in economy_monetization.json: {field}")
            return False
    
    print("✅ Economy monetization configuration is valid")
    
    # Verify ledger integrity (check it's valid JSONL)
    try:
        with open(ledger_file, 'r') as f:
            line_count = 0
            for line in f:
                if line.strip():  # Skip empty lines
                    json.loads(line)  # Verify each line is valid JSON
                    line_count += 1
        print(f"✅ Monetization ledger verified ({line_count} entries)")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSONL in {ledger_file}: {e}")
        return False
    
    print("✅ Monetization system verified successfully")
    return True


if __name__ == "__main__":
    success = verify_monetization()
    sys.exit(0 if success else 1)
