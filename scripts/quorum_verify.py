#!/usr/bin/env python3
import json, base64, hashlib, sys
from cryptography.hazmat.primitives import serialization
mf='codex/manifest.v96.json'
meta=json.load(open('codex/threshold.json'))
q=json.load(open('codex/quorum.json'))
digest=hashlib.sha256(open(mf,'rb').read()).digest()
oks=0
for s,pem in zip(meta['sigs'], meta['pubkeys']):
    pk = serialization.load_pem_public_key(pem.encode())
    try:
        pk.verify(base64.b64decode(s), digest)
        oks+=1
    except Exception:
        pass
if oks>=int(q['k']):
    print(f'QUORUM OK ({oks}/{q["n"]}) >= k={q["k"]}')
    sys.exit(0)
print(f'QUORUM FAIL ({oks}/{q["n"]}) < k={q["k"]}')
sys.exit(2)
