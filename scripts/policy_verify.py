#!/usr/bin/env python3
import os, base64, hmac, hashlib, sys
key = os.getenv('CODEX_HMAC_KEY','dev-hmac').encode()
try:
    body = open('policy/runtime.json','rb').read()
    sig = open('policy/runtime.sig','r').read().strip()
except FileNotFoundError:
    print('policy or signature missing'); sys.exit(2)
exp = base64.urlsafe_b64encode(hmac.new(key, body, hashlib.sha256).digest()).decode().rstrip('=')
ok = hmac.compare_digest(exp, sig)
print('OK' if ok else 'FAIL')
sys.exit(0 if ok else 2)
