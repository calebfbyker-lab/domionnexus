#!/usr/bin/env python3
"""
Model Registration for Codex Immortal v26.0
Register AI models with validation against schema.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import re


def load_schema():
    """Load model entry JSON schema."""
    schema_path = Path(__file__).parent.parent.parent / "schemas" / "model_entry.schema.json"
    if not schema_path.exists():
        print(f"❌ Schema not found at {schema_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_model_entry(model_data: Dict) -> tuple[bool, list]:
    """
    Validate model entry against schema.
    
    Args:
        model_data: Model registration data
    
    Returns:
        tuple: (is_valid, errors)
    """
    schema = load_schema()
    errors = []
    
    # Check required fields
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in model_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate model_id pattern
    if "model_id" in model_data:
        pattern = schema["properties"]["model_id"]["pattern"]
        if not re.match(pattern, model_data["model_id"]):
            errors.append(f"Invalid model_id format: {model_data['model_id']}")
    
    # Validate version pattern
    if "version" in model_data:
        pattern = schema["properties"]["version"]["pattern"]
        if not re.match(pattern, model_data["version"]):
            errors.append(f"Invalid version format: {model_data['version']} (use semver)")
    
    # Validate provider enum
    if "provider" in model_data:
        valid_providers = schema["properties"]["provider"]["enum"]
        if model_data["provider"] not in valid_providers:
            errors.append(f"Invalid provider: {model_data['provider']}")
    
    # Validate type enum
    if "type" in model_data:
        valid_types = schema["properties"]["type"]["enum"]
        if model_data["type"] not in valid_types:
            errors.append(f"Invalid type: {model_data['type']}")
    
    return len(errors) == 0, errors


def register_model(model_data: Dict) -> Dict:
    """
    Register a new model.
    
    Args:
        model_data: Model registration data
    
    Returns:
        dict: Registration result
    """
    # Add registration metadata
    model_data["registered_at"] = datetime.utcnow().isoformat() + "Z"
    if "registered_by" not in model_data:
        model_data["registered_by"] = "system"
    
    # Validate
    is_valid, errors = validate_model_entry(model_data)
    
    if not is_valid:
        return {
            "success": False,
            "errors": errors,
            "model_id": model_data.get("model_id")
        }
    
    # In production, save to database
    # Example: db.models.insert_one(model_data)
    
    print(f"✅ Model registered: {model_data['model_id']}")
    
    return {
        "success": True,
        "model_id": model_data["model_id"],
        "registered_at": model_data["registered_at"]
    }


def main():
    """Main entry point for model registration."""
    print("=" * 60)
    print("Model Registration")
    print("=" * 60)
    
    # Example model registration
    model_data = {
        "model_id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "version": "1.0.0",
        "provider": "openai",
        "type": "chat",
        "description": "Fast, affordable, and intelligent small model for lightweight tasks",
        "capabilities": [
            "function-calling",
            "streaming",
            "vision",
            "json-mode"
        ],
        "context_window": 128000,
        "max_output_tokens": 16384,
        "pricing": {
            "input_per_1k_tokens": 0.00015,
            "output_per_1k_tokens": 0.0006,
            "currency": "USD"
        },
        "metadata": {
            "training_data_cutoff": "2023-10-01",
            "languages": ["en", "es", "fr", "de", "zh", "ja"],
            "license": "Proprietary",
            "homepage": "https://openai.com/models/gpt-4o-mini"
        }
    }
    
    print("\n📦 Model Data:")
    print(json.dumps(model_data, indent=2))
    
    print("\n🔍 Validating against schema...")
    result = register_model(model_data)
    
    print("\n" + "=" * 60)
    print("Registration Result")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    
    if result["success"]:
        print("\n✅ Model registration successful!")
        return 0
    else:
        print("\n❌ Model registration failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
