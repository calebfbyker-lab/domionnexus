import json, os, hmac, hashlib, base64
key = os.environ.get('CODEX_HMAC_KEY','secret-hmac-key')
with open('provenance.v4.json','rb') as f:
    payload = f.read()
sig = hmac.new(key.encode(), payload, hashlib.sha256).hexdigest()
envelope = {'payload': base64.b64encode(payload).decode(), 'signatures': [{'sig': sig, 'method': 'hmac-sha256'}]}
with open('provenance.v4.dsse.json','w') as f:
    json.dump(envelope, f, indent=2)
print('provenance signed (dsse) -> provenance.v4.dsse.json')
