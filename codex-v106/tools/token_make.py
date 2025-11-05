#!/usr/bin/env python3
import os, time, base64, hmac, hashlib, sys
key=(os.environ.get("CODEX_TOKEN_KEY") or "dev-key").encode()
ts=str(time.time())
sig=base64.urlsafe_b64encode(hmac.new(key, (ts+"/runs").encode(), hashlib.sha256).digest()).decode().rstrip("=")
print(f"{ts}.{sig}")
