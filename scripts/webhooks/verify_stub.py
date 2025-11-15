#!/usr/bin/env python3
"""
Webhook Signature Verification Stub for Codex Immortal v26.0
Verifies HMAC-SHA256 webhook signatures.
⚠️ STUB: Wire to your KMS/Vault for secret management in production.
"""

import hashlib
import hmac
import json
import sys
import time


def verify_webhook_signature(payload, signature, timestamp, secret, tolerance=300):
    """
    Verify a webhook signature.
    
    Args:
        payload: The webhook payload (dict or string)
        signature: The signature to verify (string, format: "v1=<hex>")
        timestamp: The timestamp from the webhook (int)
        secret: The signing secret (string)
        tolerance: Maximum age of webhook in seconds (default: 300)
    
    Returns:
        dict: Verification result with status and details
    """
    result = {
        "valid": False,
        "errors": []
    }
    
    # Check timestamp tolerance (prevent replay attacks)
    current_time = int(time.time())
    age = current_time - timestamp
    
    if age > tolerance:
        result["errors"].append(f"Webhook too old: {age}s (max: {tolerance}s)")
        return result
    
    if age < -tolerance:
        result["errors"].append(f"Webhook timestamp in future: {abs(age)}s")
        return result
    
    # Serialize payload if dict
    if isinstance(payload, dict):
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    else:
        payload_str = str(payload)
    
    # Create signature payload: timestamp.payload
    sig_payload = f"{timestamp}.{payload_str}"
    
    # Generate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        sig_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Extract signature version and value
    if not signature.startswith("v1="):
        result["errors"].append("Invalid signature format (expected 'v1=...')")
        return result
    
    provided_sig = signature[3:]  # Remove "v1=" prefix
    
    # Constant-time comparison to prevent timing attacks
    if hmac.compare_digest(expected_signature, provided_sig):
        result["valid"] = True
        result["algorithm"] = "hmac-sha256"
        result["timestamp_age"] = age
    else:
        result["errors"].append("Signature mismatch")
    
    return result


def main():
    """Main entry point for webhook verification."""
    print("=" * 60)
    print("Webhook Signature Verifier (STUB)")
    print("=" * 60)
    
    # ⚠️ STUB: In production, fetch secret from KMS/Vault
    SECRET = "STUB_SIGNING_SECRET_REPLACE_WITH_KMS"
    
    print("⚠️  WARNING: Using stub secret. Wire to KMS/Vault in production!")
    
    # Example webhook data (from sign_stub.py)
    payload = {
        "event": "app.approved",
        "app_id": "example-app-123",
        "timestamp": int(time.time()),
        "data": {
            "status": "approved",
            "reviewer": "system"
        }
    }
    
    timestamp = int(time.time())
    
    # Generate a valid signature for testing
    payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    sig_payload = f"{timestamp}.{payload_str}"
    valid_signature = hmac.new(
        SECRET.encode('utf-8'),
        sig_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    signature = f"v1={valid_signature}"
    
    # Verify the signature
    result = verify_webhook_signature(payload, signature, timestamp, SECRET)
    
    print("\n📦 Webhook Payload:")
    print(json.dumps(payload, indent=2))
    
    print(f"\n🔐 Signature: {signature}")
    print(f"📅 Timestamp: {timestamp}")
    
    print("\n✅ Verification Result:")
    print(f"   Valid: {result['valid']}")
    if result.get('algorithm'):
        print(f"   Algorithm: {result['algorithm']}")
        print(f"   Age: {result['timestamp_age']}s")
    
    if result.get('errors'):
        print("\n❌ Errors:")
        for error in result['errors']:
            print(f"   - {error}")
    
    print("\n⚠️  SECURITY NOTES:")
    print("   - Always verify webhook signatures before processing")
    print("   - Implement timestamp tolerance to prevent replay attacks")
    print("   - Use constant-time comparison to prevent timing attacks")
    print("   - Log verification failures for security monitoring")
    
    return 0 if result['valid'] else 1


if __name__ == "__main__":
    sys.exit(main())
