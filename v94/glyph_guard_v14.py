#!/usr/bin/env python3
"""
Glyph Guard v14 - Stricter policy enforcement for glyph validation
"""
import re
import yaml
from typing import Dict, Any, List

# Default strict policy
DEFAULT_POLICY = {
    "version": "v14",
    "strict_mode": True,
    "max_glyph_length": 256,
    "allowed_charsets": ["latin", "numeric", "symbolic"],
    "forbidden_patterns": [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onclick=",
        r"\$\{",  # template injection
        r"\.\./"   # path traversal
    ],
    "required_fields": ["glyph_id", "seal_ref"],
    "entropy_threshold": 0.8
}

def load_policy(policy_path: str) -> Dict[str, Any]:
    """Load glyph policy from YAML file"""
    try:
        with open(policy_path, 'r') as f:
            policy = yaml.safe_load(f)
            return {**DEFAULT_POLICY, **policy}
    except FileNotFoundError:
        print(f"Policy file not found: {policy_path}, using defaults")
        return DEFAULT_POLICY

def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of text"""
    if not text:
        return 0.0
    
    import math
    from collections import Counter
    
    counts = Counter(text)
    length = len(text)
    entropy = -sum((count/length) * math.log2(count/length) for count in counts.values())
    
    # Normalize to 0-1 range (max entropy for 256 chars is 8)
    return entropy / 8.0

def check_forbidden_patterns(text: str, patterns: List[str]) -> List[str]:
    """Check text against forbidden patterns"""
    violations = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(pattern)
    return violations

def verify_glyph_policy(glyph_text: str, policy_path: str = "glyph_policy.yaml") -> Dict[str, Any]:
    """
    Verify glyph against v14 policy
    
    Returns:
        dict: {
            "valid": bool,
            "violations": list,
            "entropy": float,
            "policy_version": str
        }
    """
    policy = load_policy(policy_path)
    violations = []
    
    # Length check
    if len(glyph_text) > policy["max_glyph_length"]:
        violations.append(f"Exceeds max length: {len(glyph_text)} > {policy['max_glyph_length']}")
    
    # Forbidden pattern check
    pattern_violations = check_forbidden_patterns(glyph_text, policy["forbidden_patterns"])
    if pattern_violations:
        violations.extend([f"Forbidden pattern: {p}" for p in pattern_violations])
    
    # Entropy check (detect random/suspicious data)
    entropy = calculate_entropy(glyph_text)
    if policy.get("entropy_threshold") and entropy > policy["entropy_threshold"]:
        violations.append(f"High entropy: {entropy:.3f} > {policy['entropy_threshold']}")
    
    # Charset validation
    if policy.get("strict_mode"):
        # In strict mode, apply additional checks
        if not glyph_text.strip():
            violations.append("Empty or whitespace-only glyph")
    
    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "entropy": entropy,
        "policy_version": policy["version"],
        "strict_mode": policy.get("strict_mode", False)
    }

def main():
    """CLI test interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python glyph_guard_v14.py <glyph_text>")
        sys.exit(1)
    
    glyph_text = sys.argv[1]
    result = verify_glyph_policy(glyph_text)
    
    print(f"Glyph Guard v14 Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Entropy: {result['entropy']:.3f}")
    print(f"  Policy: {result['policy_version']}")
    
    if result['violations']:
        print("  Violations:")
        for v in result['violations']:
            print(f"    - {v}")
    
    sys.exit(0 if result['valid'] else 1)

if __name__ == "__main__":
    main()
