#!/usr/bin/env python3import json, os, hmac, hashlib, base64

import os, json, base64, hmac, hashlibkey = os.environ.get('CODEX_HMAC_KEY','secret-hmac-key')

key = os.getenv('CODEX_HMAC_KEY', 'dev-hmac').encode()with open('provenance.v4.json','rb') as f:

body = open('provenance.v4.json','rb').read()    payload = f.read()

payload = base64.b64encode(body).decode()sig = hmac.new(key.encode(), payload, hashlib.sha256).hexdigest()

sig = hmac.new(key, payload.encode(), hashlib.sha256).digest()envelope = {'payload': base64.b64encode(payload).decode(), 'signatures': [{'sig': sig, 'method': 'hmac-sha256'}]}

env = {"payloadType": "application/attestation-provenance+json", "payload": payload, "signatures": [{"keyid": "hmac:CODEX_HMAC_KEY", "sig": base64.urlsafe_b64encode(sig).decode().rstrip('=')} ]}with open('provenance.v4.dsse.json','w') as f:

open('signed_provenance.dsse.json','w').write(json.dumps(env, indent=2))    json.dump(envelope, f, indent=2)

print('signed_provenance.dsse.json written')print('provenance signed (dsse) -> provenance.v4.dsse.json')

