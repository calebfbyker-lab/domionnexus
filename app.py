from fastapi import FastAPI, HTTPException, Header, Request, Query
from pydantic import BaseModel
import subprocess, sys, json, hashlib, os, time, threading, yaml, hmac

APP_VER = "Codex v97 · Praetorian"
IDENT_STR = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = ""

CODEX_API_KEY   = os.getenv("CODEX_API_KEY","dev-key")
CODEX_HMAC_KEY  = os.getenv("CODEX_HMAC_KEY","dev-hmac")
AUDIT = "audit.jsonl"
TENANTS_PATH = "policy/tenants.json"
POLICY_PATH  = "policy/praetorian.json"

_a_lock = threading.Lock()

def _audit(ev):
    ev["ts"] = time.time()
    line = json.dumps(ev, separators=(",",":"))
    with _a_lock, open(AUDIT,"a",encoding="utf-8") as f:
        f.write(line+"\n")
    return line

def _auth(x_api_key: str, tenant: str|None):
    # tenant-aware auth
    if x_api_key != CODEX_API_KEY:
        raise HTTPException(401,"unauthorized")
    if tenant:
        tenants = json.load(open(TENANTS_PATH)) if os.path.exists(TENANTS_PATH) else {}
        if tenant not in tenants.get("namespaces",{}):
            raise HTTPException(403, "unknown tenant")
    return True

def _json_load(path, default):
    try: return json.load(open(path,"r",encoding="utf-8"))
    except Exception: return default

def _json_save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path,"w",encoding="utf-8"))

class GlyphReq(BaseModel):
    glyph: str
    dry_run: bool = False
    nonce: str | None = None
    version: str | None = None
    tenant: str | None = None
    env: dict | None = None

class PolicyPreview(BaseModel):
    attrs: dict

app = FastAPI(title=APP_VER)

@app.get("/health")
def health(): return {"ok":True,"ver":APP_VER}

@app.get("/seal")
def seal(): return {"subject": IDENT_STR, "subject_id_sha256": SUBJECT_SHA256}

@app.get("/tenants")
def tenants(): return _json_load(TENANTS_PATH, {"namespaces":{}})

@app.post("/policy/preview")
def policy_preview(req: PolicyPreview):
    import scripts.policy_vm as vm
    pol = _json_load(POLICY_PATH, {"rules":[]})
    res = vm.evaluate(pol, req.attrs or {})
    return {"decision": res}

@app.post("/glyph")
async def glyph(req: GlyphReq, request: Request, x_api_key: str = Header(default="")):
    _auth(x_api_key, req.tenant)
    if req.env:
        for k,v in req.env.items(): os.environ[str(k)] = str(v)
    cmd=[sys.executable,"tools/glyph_guard_v20.py","--glyph",req.glyph]
    if req.dry_run: cmd.append("--dry-run")
    p = subprocess.run(cmd, capture_output=True, text=True)
    _audit({"route":"glyph","rc":p.returncode,"tenant":req.tenant})
    if p.returncode!=0: raise HTTPException(400,{"stderr":p.stderr,"stdout":p.stdout})
    return {"ok":True,"stdout":p.stdout}

@app.post("/rollout/start")
def rollout_start(percent: int = Query(5, ge=1, le=100), x_api_key: str = Header(default="")):
    _auth(x_api_key, None)
    st = {"started": int(time.time()), "progress": percent, "state":"canary"}
    _json_save("rollout/state.json", st)
    return st

@app.post("/rollout/advance")
def rollout_advance(step: int = Query(10, ge=1, le=100), x_api_key: str = Header(default="")):
    _auth(x_api_key, None)
    st = _json_load("rollout/state.json", {})
    if not st: raise HTTPException(400, "rollout not started")
    st["progress"] = min(100, int(st.get("progress",0)) + step)
    st["state"] = "complete" if st["progress"]>=100 else "canary"
    _json_save("rollout/state.json", st)
    return st

@app.get("/rollout/status")
def rollout_status():
    return _json_load("rollout/state.json", {"state":"idle","progress":0})
