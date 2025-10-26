from fastapi import FastAPI, HTTPException, Header, Depends, Request, Query
from pydantic import BaseModel
import subprocess, sys, json, hashlib, os, time, threading, yaml, hmac
from codex.merkle import leaves_hashes, merkle_root, proof_path, verify_inclusion

APP_VER = "Codex v96 · Aletheia"
IDENT_STR = "__SUBJECT__"
SUBJECT_SHA256 = "__SUBJECT_SHA__"

CODEX_API_KEY   = os.getenv("CODEX_API_KEY","dev-key")
CODEX_HMAC_KEY  = os.getenv("CODEX_HMAC_KEY","dev-hmac")
AUDIT = "audit.jsonl"
POLICY = "policy/runtime.json"

_a_lock = threading.Lock()

def _audit(ev):
    ev["ts"] = time.time()
    line = json.dumps(ev, separators=(",",":"))
    with _a_lock, open(AUDIT,"a",encoding="utf-8") as f:
        f.write(line+"\n")
    return line

def _audit_root_hex():
    try:
        with open(AUDIT,"rb") as f:
            lines=f.read().splitlines()
        root = merkle_root(leaves_hashes(lines))
        return root, len(lines)
    except FileNotFoundError:
        return "0"*64, 0

def _auth(x_api_key: str):
    if x_api_key != CODEX_API_KEY: raise HTTPException(401,"unauthorized")

class GlyphReq(BaseModel):
    glyph: str
    dry_run: bool = False
    nonce: str | None = None
    version: str | None = None

app = FastAPI(title=APP_VER)

@app.get("/health")
def health():
    root, n = _audit_root_hex()
    return {"ok":True,"ver":APP_VER,"audit_count":n,"audit_root":root}

@app.get("/seal")
def seal(): return {"subject": IDENT_STR, "subject_id_sha256": SUBJECT_SHA256}

@app.get("/audit/root")
def audit_root():
    root, n = _audit_root_hex()
    return {"count": n, "merkle_root": root}

@app.get("/audit/proof")
def audit_proof(index: int = Query(..., ge=0)):
    try:
        with open(AUDIT,"rb") as f: lines=f.read().splitlines()
        root = merkle_root(leaves_hashes(lines))
        path = proof_path(leaves_hashes(lines), index)
        return {"root": root, "index": index, "path": path, "line": lines[index].decode()}
    except Exception as e:
        raise HTTPException(400, f"unable to provide proof: {e}")

def _load_policy():
    try: return json.load(open(POLICY,"r",encoding="utf-8"))
    except Exception: return {"require_nonce": True, "monotonic_version": True, "last_version":"0"}

def _check_policy(nonce: str|None, version: str|None):
    pol = _load_policy()
    if pol.get("require_nonce") and not nonce:
        raise HTTPException(400,"nonce required by policy")
    if pol.get("monotonic_version"):
        last = pol.get("last_version","0")
        if not version: raise HTTPException(400,"version required by policy")
        if str(version) <= str(last): raise HTTPException(409, f"version not monotonic: {version} <= {last}")
        pol["last_version"]=version
        json.dump(pol, open(POLICY,"w",encoding="utf-8"))
    return True

@app.post("/glyph")
async def glyph(req: GlyphReq, request: Request, x_api_key: str = Header(default=""), x_codex_sig: str = Header(default="")):
    _auth(x_api_key)
    # HMAC body (optional)
    if x_codex_sig:
        body = await request.body()
        mac = hmac.new(CODEX_HMAC_KEY.encode(), body, hashlib.sha256).hexdigest()
        if x_codex_sig != mac: raise HTTPException(401,"bad hmac")
    _check_policy(req.nonce, req.version)
    cmd=[sys.executable,"tools/glyph_guard_v18.py","--glyph",req.glyph,"--nonce",req.nonce or "none"]
    if req.dry_run: cmd.append("--dry-run")
    p = subprocess.run(cmd, capture_output=True, text=True)
    _audit({"route":"glyph","rc":p.returncode,"nonce":req.nonce,"version":req.version})
    if p.returncode!=0: raise HTTPException(400,{"stderr":p.stderr,"stdout":p.stdout})
    return {"ok":True,"stdout":p.stdout}
