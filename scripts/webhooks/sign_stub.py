#!/usr/bin/env python3
"""
Webhook Signature Generator Stub for Codex Immortal v26.0
Signs webhook payloads using HMAC-SHA256.
⚠️ STUB: Wire to your KMS/Vault for secret management in production.
"""

import hashlib
import hmac
import json
import sys
import time
from pathlib import Path


def sign_webhook(payload, secret, timestamp=None):
    """
    Sign a webhook payload using HMAC-SHA256.
    
    Args:
        payload: The webhook payload (dict or string)
        secret: The signing secret (string)
        timestamp: Optional timestamp (int). Uses current time if not provided.
    
    Returns:
        dict: Signed webhook with signature and metadata
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    # Serialize payload if dict
    if isinstance(payload, dict):
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    else:
        payload_str = str(payload)
    
    # Create signature payload: timestamp.payload
    sig_payload = f"{timestamp}.{payload_str}"
    
    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        secret.encode('utf-8'),
        sig_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "payload": payload,
        "timestamp": timestamp,
        "signature": f"v1={signature}",
        "algorithm": "hmac-sha256"
    }


def main():
    """Main entry point for webhook signing."""
    print("=" * 60)
    print("Webhook Signature Generator (STUB)")
    print("=" * 60)
    
    # ⚠️ STUB: In production, fetch secret from KMS/Vault
    # Example: secret = get_secret_from_vault("webhook_signing_key")
    SECRET = "STUB_SIGNING_SECRET_REPLACE_WITH_KMS"
    
    print("⚠️  WARNING: Using stub secret. Wire to KMS/Vault in production!")
    
    # Example webhook payload
    payload = {
        "event": "app.approved",
        "app_id": "example-app-123",
        "timestamp": int(time.time()),
        "data": {
            "status": "approved",
            "reviewer": "system"
        }
    }
    
    # Sign the webhook
    signed = sign_webhook(payload, SECRET)
    
    print("\n📦 Webhook Payload:")
    print(json.dumps(payload, indent=2))
    
    print("\n🔐 Signature:")
    print(f"   Algorithm: {signed['algorithm']}")
    print(f"   Timestamp: {signed['timestamp']}")
    print(f"   Signature: {signed['signature']}")
    
    print("\n✅ Webhook signed successfully!")
    print("\n⚠️  SECURITY NOTES:")
    print("   - Never commit signing secrets to version control")
    print("   - Use environment variables or KMS/Vault for secret management")
    print("   - Rotate signing secrets regularly")
    print("   - Implement signature verification on the receiving end")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
