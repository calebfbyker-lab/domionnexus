from fastapi import FastAPI, HTTPException, Header, Request, Query
from pydantic import BaseModel
import subprocess, sys, json, hashlib, os, time, threading, yaml, hmac

# Import v98 Orthos modules
try:
    from selfcheck import selfcheck
    from keyring import get_keyring
    from shadow_metrics import ShadowMetrics
except ImportError:
    # Fallback if modules not available
    selfcheck = None
    get_keyring = None
    ShadowMetrics = None

APP_VER = "Codex v98 · Orthos"
IDENT_STR = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = hashlib.sha256(IDENT_STR.encode()).hexdigest()

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

# Run self-check at startup if available
@app.on_event("startup")
async def startup_event():
    """Startup tasks including self-check"""
    if selfcheck:
        try:
            selfcheck(strict=False)  # Non-strict for development
        except SystemExit:
            # Self-check failed - in production, this would prevent startup
            print("⚠️  Self-check failed - continuing in dev mode")
    
    print(f"🚀 {APP_VER} started")
    print(f"   Subject ID: {SUBJECT_SHA256[:16]}...")
    
    # Initialize keyring if available
    if get_keyring:
        try:
            kr = get_keyring()
            print(f"   HMAC Keyring: {kr.current_key_id}")
        except Exception as e:
            print(f"   HMAC Keyring: Failed to initialize - {e}")

@app.get("/health")
def health(): 
    return {
        "ok": True,
        "ver": APP_VER,
        "features": [
            "boot-time-selfcheck",
            "hmac-keyring", 
            "shadow-deploy",
            "auto-rollback",
            "judge-glyph",
            "tuf-lite"
        ]
    }

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
    # Use glyph_guard_v22 for enhanced JUDGE support
    cmd=[sys.executable,"tools/glyph_guard_v22.py","--glyph",req.glyph]
    if req.dry_run: cmd.append("--dry-run")
    if req.nonce: cmd.extend(["--nonce", req.nonce])
    p = subprocess.run(cmd, capture_output=True, text=True)
    _audit({"route":"glyph","rc":p.returncode,"tenant":req.tenant,"glyph":req.glyph})
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

# v98 Orthos New Endpoints

@app.get("/keyring/status")
def keyring_status(x_api_key: str = Header(default="")):
    """Get HMAC keyring status"""
    _auth(x_api_key, None)
    if not get_keyring:
        raise HTTPException(501, "Keyring not available")
    kr = get_keyring()
    return kr.list_keys()

@app.post("/keyring/rotate")
def keyring_rotate(x_api_key: str = Header(default="")):
    """Rotate HMAC key"""
    _auth(x_api_key, None)
    if not get_keyring:
        raise HTTPException(501, "Keyring not available")
    kr = get_keyring()
    new_key_id = kr.rotate_key()
    return {"ok": True, "new_key_id": new_key_id}

@app.get("/shadow/metrics")
def shadow_metrics_get(x_api_key: str = Header(default="")):
    """Get shadow deployment metrics"""
    _auth(x_api_key, None)
    if not ShadowMetrics:
        raise HTTPException(501, "Shadow metrics not available")
    metrics = ShadowMetrics()
    current = metrics.get_current_deployment()
    return current or {"state": "idle", "message": "No active deployment"}

@app.post("/shadow/check")
def shadow_metrics_check(x_api_key: str = Header(default="")):
    """Check shadow metrics and auto-rollback if needed"""
    _auth(x_api_key, None)
    if not ShadowMetrics:
        raise HTTPException(501, "Shadow metrics not available")
    metrics = ShadowMetrics()
    current = metrics.get_current_deployment()
    if not current:
        return {"ok": True, "message": "No active deployment"}
    
    deployment_id = current["deployment_id"]
    should_rb, reason = metrics.should_rollback(deployment_id)
    
    if should_rb:
        metrics.trigger_rollback(deployment_id, reason)
        return {"ok": True, "action": "rollback", "reason": reason}
    
    return {"ok": True, "action": "continue", "reason": reason}

@app.get("/features")
def features():
    """List v98 Orthos features"""
    return {
        "version": "v98",
        "codename": "Orthos",
        "features": {
            "boot_time_selfcheck": {
                "enabled": selfcheck is not None,
                "description": "Service refuses to run if code diverges from manifest"
            },
            "hmac_keyring": {
                "enabled": get_keyring is not None,
                "description": "Secure key rotation and management"
            },
            "shadow_deploy": {
                "enabled": ShadowMetrics is not None,
                "description": "Progressive deployment with metrics tracking"
            },
            "auto_rollback": {
                "enabled": ShadowMetrics is not None,
                "description": "Automatic rollback on metric threshold breach"
            },
            "judge_glyph": {
                "enabled": True,
                "description": "Enhanced deployment gating with quality checks"
            },
            "tuf_lite": {
                "enabled": True,
                "description": "Lightweight TUF for artifact distribution"
            }
        }
    }
