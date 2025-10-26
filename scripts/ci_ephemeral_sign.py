#!/usr/bin/env python3
import base64, json, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

os.makedirs('keys', exist_ok=True)
priv = Ed25519PrivateKey.generate()
pub = priv.public_key()
open("keys/manifest_pub.pem","wb").write(
    pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
)
data = {}
os.makedirs('plugins', exist_ok=True)
open("plugins/manifest.json","w").write(json.dumps(data))
sig = priv.sign(json.dumps(data, separators=(',',':'), sort_keys=True).encode())
open("plugins/manifest.sig","w").write(base64.urlsafe_b64encode(sig).decode()+"\n")
print('ci_ephemeral_sign: done')
