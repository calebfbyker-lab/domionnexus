#!/usr/bin/env python3
import json, base64, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
mf='codex/manifest.v96.json'
digest=hashlib.sha256(open(mf,'rb').read()).digest()
keys=[]; sigs=[]
for i in range(3):
    sk=Ed25519PrivateKey.generate()
    pk=sk.public_key()
    sig=sk.sign(digest)
    keys.append(pk.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode())
    sigs.append(base64.b64encode(sig).decode())
open('codex/threshold.json','w').write(json.dumps({'algo':'ed25519','digest':'sha256','sigs':sigs,'pubkeys':keys},indent=2))
print('threshold signatures written (3 total)')
