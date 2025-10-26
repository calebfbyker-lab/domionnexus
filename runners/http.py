#!/usr/bin/env python3
"""
HTTP webhook runner with TLS enforcement
Codex Continuum v100 - Continuum Σ (Sigma)
"""
import requests
import json
import sys
import hashlib
import hmac
import time

def run(cmd: list, tls_required: bool = True, verify_ssl: bool = True, 
        hmac_secret: str = None, audit_log: str = None) -> int:
    """
    Execute a webhook call with security controls
    
    Args:
        cmd: ["http", "METHOD", "URL", "JSON_BODY"]
        tls_required: Require HTTPS
        verify_ssl: Verify SSL certificates
        hmac_secret: Optional secret for HMAC signing
        audit_log: Optional path to audit log file
    
    Returns:
        0 on success, non-zero on failure
    """
    try:
        if len(cmd) < 4 or cmd[0] != "http":
            print("⛔ Invalid http command format", file=sys.stderr)
            print("Usage: ['http', 'METHOD', 'URL', 'JSON_BODY']", file=sys.stderr)
            return 1
        
        method = cmd[1].upper()
        url = cmd[2]
        body_str = " ".join(cmd[3:])
        body = json.loads(body_str)
        
        # TLS enforcement
        if tls_required and not url.startswith("https://"):
            print("⛔ TLS required but URL is not HTTPS", file=sys.stderr)
            return 1
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Codex-Continuum-v100/runner-http"
        }
        
        # Add HMAC signature if secret provided
        if hmac_secret:
            body_bytes = json.dumps(body, separators=(',', ':')).encode('utf-8')
            signature = hmac.new(
                hmac_secret.encode('utf-8'),
                body_bytes,
                hashlib.sha256
            ).hexdigest()
            headers["X-Hub-Signature-256"] = f"sha256={signature}"
        
        # Audit the request
        if audit_log:
            try:
                with open(audit_log, 'a') as f:
                    entry = {
                        "runner": "http",
                        "method": method,
                        "url": url,
                        "tls_required": tls_required,
                        "timestamp": int(time.time())
                    }
                    f.write(json.dumps(entry) + "\n")
            except Exception as e:
                print(f"⚠️  Audit logging failed: {e}", file=sys.stderr)
        
        # Make the request
        print(f"🌐 HTTP {method} to {url}")
        response = requests.request(
            method,
            url,
            json=body,
            headers=headers,
            timeout=30,
            verify=verify_ssl
        )
        
        print(f"✅ Status: {response.status_code}")
        if response.status_code >= 400:
            print(f"⚠️  Response: {response.text[:200]}")
        
        return 0 if response.ok else 2
        
    except json.JSONDecodeError as e:
        print(f"⛔ Invalid JSON body: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.SSLError as e:
        print(f"⛔ SSL verification failed: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.Timeout:
        print("⛔ Request timed out", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as e:
        print(f"⛔ HTTP request failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"⛔ Unexpected error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: http.py http METHOD URL JSON_BODY")
        sys.exit(1)
    
    exit_code = run(sys.argv[1:], audit_log="audit.jsonl")
    sys.exit(exit_code)
