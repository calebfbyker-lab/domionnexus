from __future__ import annotations
import base64, hmac, hashlib, os
# Optional Ed25519 via pynacl (if installed). Otherwise fall back to HMAC.
try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import Base64Encoder
    _HAS_NACL=True
except Exception:
    _HAS_NACL=False

def ed25519_gen():
    if not _HAS_NACL: raise RuntimeError("pynacl not available")
    sk = SigningKey.generate()
    vk = sk.verify_key
    return (sk.encode(encoder=Base64Encoder).decode(), vk.encode(encoder=Base64Encoder).decode())

def ed25519_sign(priv_b64:str, body:bytes)->str:
    if not _HAS_NACL: raise RuntimeError("pynacl not available")
    sk = SigningKey(priv_b64.encode(), encoder=Base64Encoder)
    sig = sk.sign(body).signature
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")

def ed25519_verify(pub_b64:str, body:bytes, sig_b64:str)->bool:
    if not _HAS_NACL: return False
    try:
        vk = VerifyKey(pub_b64.encode(), encoder=Base64Encoder)
        sig = base64.urlsafe_b64decode(sig_b64 + "==")
        vk.verify(body, sig)
        return True
    except Exception:
        return False

def hmac_sign(key:str, body:bytes)->str:
    mac=hmac.new(key.encode(), body, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")

def hmac_verify(key:str, body:bytes, sig:str)->bool:
    try: 
        exp=hmac_sign(key, body)
        return hmac.compare_digest(exp, sig)
    except Exception:
        return False
