#!/usr/bin/env python3
"""
Glyph Guard v26
Codex Continuum v100 - Continuum Σ (Sigma)

Policy enforcement for glyph processing with enhanced security
"""
import yaml
import re
import sys
import json
from typing import Dict, List, Tuple

def load_policy(policy_file: str = "policy/glyph.yaml") -> Dict:
    """Load glyph policy from YAML"""
    try:
        with open(policy_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️  Policy file not found: {policy_file}, using defaults", file=sys.stderr)
        return {
            "max_steps": 16,
            "deny_emojis": ["💣", "🧨"],
            "deny_patterns": [
                r"(?i)rm\s+-rf\s+/",
                r"(?i)drop\s+database",
                r"(?i)chmod\s+777"
            ]
        }
    except yaml.YAMLError as e:
        print(f"⛔ Policy YAML error: {e}", file=sys.stderr)
        sys.exit(1)

def validate_glyph(glyph: str, policy: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a glyph against policy
    
    Returns:
        (is_valid, violations)
    """
    violations = []
    
    # Check for denied emojis
    denied_emojis = policy.get("deny_emojis", [])
    for emoji in denied_emojis:
        if emoji in glyph:
            violations.append(f"Contains denied emoji: {emoji}")
    
    # Check for denied patterns
    denied_patterns = policy.get("deny_patterns", [])
    for pattern in denied_patterns:
        if re.search(pattern, glyph, re.IGNORECASE):
            violations.append(f"Matches denied pattern: {pattern}")
    
    # Check length/complexity if max_steps defined
    max_steps = policy.get("max_steps", None)
    if max_steps:
        # Count "steps" as newlines or semicolons
        steps = glyph.count('\n') + glyph.count(';')
        if steps > max_steps:
            violations.append(f"Exceeds max steps: {steps} > {max_steps}")
    
    return len(violations) == 0, violations

def process_glyph(glyph_text: str, policy_file: str = "policy/glyph.yaml") -> Dict:
    """Process and validate a glyph"""
    policy = load_policy(policy_file)
    
    print(f"🔮 Glyph Guard v26 - Processing")
    print(f"   Policy: {policy_file}")
    
    # Validate
    is_valid, violations = validate_glyph(glyph_text, policy)
    
    result = {
        "version": "v26",
        "glyph_length": len(glyph_text),
        "valid": is_valid,
        "violations": violations,
        "policy": policy_file
    }
    
    if is_valid:
        print("✅ Glyph validation PASSED")
    else:
        print("❌ Glyph validation FAILED")
        for violation in violations:
            print(f"   - {violation}")
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: glyph_guard_v26.py <glyph_text|glyph_file>")
        print("\nExamples:")
        print("  glyph_guard_v26.py 'echo hello'")
        print("  glyph_guard_v26.py glyph.txt")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    # Check if it's a file
    try:
        with open(input_arg, 'r') as f:
            glyph_text = f.read()
        print(f"📄 Loading glyph from file: {input_arg}")
    except FileNotFoundError:
        # Treat as direct glyph text
        glyph_text = input_arg
    
    # Process
    policy_file = sys.argv[2] if len(sys.argv) > 2 else "policy/glyph.yaml"
    result = process_glyph(glyph_text, policy_file)
    
    # Output JSON result
    print("\n📊 Result:")
    print(json.dumps(result, indent=2))
    
    # Exit code based on validation
    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__":
    main()
