#!/usr/bin/env python3
import hashlib, json, base64, time, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

os.makedirs('codex', exist_ok=True)
manifest = os.environ.get('MANIFEST_PATH', 'codex/manifest.v91x.json')
if not os.path.exists(manifest):
    # create a minimal manifest if missing
    open(manifest, 'w').write(json.dumps({'placeholder': True}, indent=2))

with open(manifest, 'rb') as f:
    sha = hashlib.sha256(f.read()).hexdigest()

priv = Ed25519PrivateKey.generate()
pub = priv.public_key()
sig = priv.sign(sha.encode())

payload = {
    "subject": "caleb fedor byker konev|1998-10-27",
    "subject_id_sha256": hashlib.sha256(b"caleb fedor byker konev|1998-10-27").hexdigest(),
    "manifest": manifest,
    "sha256": sha,
    "ed25519_signature": base64.urlsafe_b64encode(sig).decode(),
    "pubkey": pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode(),
    "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ")
}

outf = 'codex/astro_crypto_seal.v91x.json'
open(outf, 'w').write(json.dumps(payload, indent=2))
print(f'astro-crypto seal written -> {outf}')
