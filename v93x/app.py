from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import subprocess, sys, json, hashlib, os, time, threading, yaml, re, requests

try:
    import jwt
    from jwt import PyJWKClient
except Exception:
    jwt = None

APP_VER = "Codex v93.x · Constellation"
IDENT_STR = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a"
CODEX_API_KEY = os.getenv("CODEX_API_KEY", "dev-key")
OIDC_JWKS_URL = os.getenv("OIDC_JWKS_URL", "")
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "")
OIDC_AUDIENCE = os.getenv("OIDC_AUDIENCE", "")

AUDIT = "audit.jsonl"
_a_lock = threading.Lock()
_last = "0" * 64


def _audit(ev):
    global _last
    ev["ts"] = time.time()
    body = json.dumps(ev, separators=(",", ":"))
    d = hashlib.sha256(body.encode()).hexdigest()
    root = hashlib.sha256((_last + d).encode()).hexdigest()
    _last = root
    with _a_lock, open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps({**ev, "sha256": d, "root": root}) + "\n")


def _oidc_ok(token: str) -> bool:
    if not jwt or not OIDC_JWKS_URL:
        return False
    try:
        jwk_client = PyJWKClient(OIDC_JWKS_URL)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(token, signing_key.key, algorithms=["RS256", "EdDSA"], audience=OIDC_AUDIENCE or None, issuer=OIDC_ISSUER or None)
        return True
    except Exception:
        return False


def _auth(perm: str):
    def dep(authorization: str = Header(default=""), x_api_key: str = Header(default="")):
        # API key first
        if x_api_key and x_api_key == CODEX_API_KEY:
            return True
        # Bearer token (optional OIDC)
        if authorization and authorization.startswith("Bearer "):
            tok = authorization.split(" ", 1)[1]
            if _oidc_ok(tok):
                return True
        raise HTTPException(status_code=401, detail="unauthorized")

    return dep


class GlyphReq(BaseModel):
    glyph: str
    dry_run: bool = False


class NousReq(BaseModel):
    prompt: str
    dry_run: bool = True


app = FastAPI(title=APP_VER)


@app.get("/health")
def health():
    return {"ok": True, "ver": APP_VER}


@app.get("/seal")
def seal():
    return {"subject": IDENT_STR, "subject_id_sha256": SUBJECT_SHA256}


@app.post("/glyph", dependencies=[Depends(_auth("glyph.run"))])
def glyph(req: GlyphReq):
    cmd = [sys.executable, "tools/glyph_guard_v13.py", "--glyph", req.glyph]
    if req.dry_run:
        cmd.append("--dry-run")
    p = subprocess.run(cmd, capture_output=True, text=True)
    _audit({"route": "glyph", "rc": p.returncode})
    if p.returncode != 0:
        raise HTTPException(status_code=400, detail={"stderr": p.stderr, "stdout": p.stdout})
    return {"ok": True, "stdout": p.stdout}


def phrase_to_glyph(prompt: str):
    mapping = yaml.safe_load(open("codex/glyphs/xtgs.yaml"))
    seq = []
    for word in re.split(r"[\s,;]+", prompt.lower()):
        if not word:
            continue
        if "verify" in word:
            seq.append(mapping.get("🌀", "verify"))
        elif "invoke" in word or "build" in word:
            seq.append(mapping.get("🌞", "invoke"))
        elif "deploy" in word or "release" in word:
            seq.append(mapping.get("🌈", "deploy"))
        elif "audit" in word or "sbom" in word or "check" in word:
            seq.append(mapping.get("🧾", "audit"))
        elif "attest" in word or "provenance" in word:
            seq.append(mapping.get("🔮", "attest"))
    return seq


@app.post("/nous", dependencies=[Depends(_auth("glyph.run"))])
def nous(req: NousReq):
    seq = phrase_to_glyph(req.prompt)
    dag = [{"step": s} for s in seq]
    if not req.dry_run:
        for s in seq:
            p = subprocess.run([sys.executable, "tools/glyph_guard_v13.py", "--glyph", s], capture_output=True, text=True)
            if p.returncode != 0:
                raise HTTPException(status_code=400, detail={"stderr": p.stderr, "stdout": p.stdout})
    return {"prompt": req.prompt, "glyphs": seq, "dag": dag}
