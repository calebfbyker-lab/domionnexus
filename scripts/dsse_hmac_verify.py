#!/usr/bin/env python3
import os, json, base64, hmac, hashlib, sys
key = os.getenv('CODEX_HMAC_KEY','dev-hmac').encode()
env = json.load(open('signed_provenance.dsse.json'))
payload = env['payload'].encode()
sig = base64.urlsafe_b64decode(env['signatures'][0]['sig'] + '==')
ok = hmac.compare_digest(hmac.new(key, payload, hashlib.sha256).digest(), sig)
print('OK' if ok else 'FAIL')
sys.exit(0 if ok else 2)
