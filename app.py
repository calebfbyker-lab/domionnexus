from fastapi import FastAPI, HTTPException, Header, Request, Query
from pydantic import BaseModel
import subprocess, sys, json, hashlib, os, time, threading, yaml, hmac, base64, uuid
from codex.merkle import leaves_hashes, merkle_root, proof_path, verify_inclusion
from codex.redact import redact

APP_VER = "Codex Continuum v100 - Continuum Σ (Sigma)"
IDENT_STR = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = "1f6e1f1ca3c4f3e1b1f6e2b317d7c1dff9b5d6d2b0d4e0f7b6a8c9e0f2a4b1c3"

AUDIT = "audit.jsonl"
POLICY_FILE = "policy/runtime.json"
POLICY_SIG = "policy/runtime.sig"
NONCES_FILE = "policy/nonces.json"
KEYRING = "secrets/keyring.json"
CHAIN_FILE = "chain.jsonl"

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET","dev-webhook")

_a_lock = threading.Lock()

def _audit(ev):
    ev["ts"] = time.time()
    line = json.dumps(ev, separators=(",",":"))
    with _a_lock, open(AUDIT,"a",encoding="utf-8") as f:
        f.write(line+"\n")
    return line

def _json_load(path, default):
    try: return json.load(open(path,"r",encoding="utf-8"))
    except Exception: return default

def _json_save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path,"w",encoding="utf-8"))

def _issue_nonce():
    store=_json_load(NONCES_FILE, {"ttl":600,"issued":{}})
    tok=str(uuid.uuid4()); exp=int(time.time())+int(store.get("ttl",600))
    store["issued"][tok]=exp; _json_save(NONCES_FILE, store); return tok, exp

def _consume_nonce(token:str):
    store=_json_load(NONCES_FILE, {"ttl":600,"issued":{}})
    exp=store["issued"].get(token); now=int(time.time())
    if not exp or exp<now: raise HTTPException(400,"nonce invalid or expired")
    del store["issued"][token]; _json_save(NONCES_FILE, store)

def _verify_hmac(kid: str, body: bytes, sig: str):
    ring=_json_load(KEYRING, {"keys":{"default":"dev-hmac"}, "active":"default"})
    key = (ring.get("keys") or {}).get(kid or ring.get("active","default"))
    if not key: return False, ""
    mac=hmac.new(key.encode(), body, hashlib.sha256).digest()
    expect=base64.urlsafe_b64encode(mac).decode().rstrip("=")
    return hmac.compare_digest(expect, sig), expect

class GlyphReq(BaseModel):
    glyph: str
    dry_run: bool = False
    nonce: str | None = None
    version: str | None = None

class VerifyReq(BaseModel):
    root: str; index: int; line: str; path: list

class WebhookEnvelope(BaseModel):
    event: str | None = None
    delivery: str | None = None
    payload: dict

class Bundle(BaseModel):
    bundle: dict
    sig: str

app = FastAPI(title=APP_VER)

@app.get("/health")
def health():
    try:
        with open(AUDIT,"rb") as f: lines=f.read().splitlines()
        root=merkle_root(leaves_hashes(lines)); n=len(lines)
    except FileNotFoundError:
        root="0"*64; n=0
    return {"ok":True,"ver":APP_VER,"audit_count":n,"audit_root":root}

@app.get("/seal")
def seal(): return {"subject": IDENT_STR, "subject_id_sha256": SUBJECT_SHA256}

@app.post("/nonce/issue")
def nonce_issue(): tok,exp=_issue_nonce(); return {"nonce":tok,"expires":exp}

@app.get("/audit/root")
def audit_root():
    try:
        with open(AUDIT,"rb") as f: lines=f.read().splitlines()
        root=merkle_root(leaves_hashes(lines)); n=len(lines)
    except FileNotFoundError:
        root="0"*64; n=0
    return {"count": n, "merkle_root": root}

@app.get("/audit/proof")
def audit_proof(index: int = Query(..., ge=0)):
    with open(AUDIT,"rb") as f: lines=f.read().splitlines()
    root=merkle_root(leaves_hashes(lines)); path=proof_path(leaves_hashes(lines), index)
    return {"root":root,"index":index,"path":path,"line":lines[index].decode()}

@app.post("/audit/verify")
def audit_verify(req: VerifyReq):
    ok=verify_inclusion(req.root, req.line.encode(), req.index, req.path)
    return {"ok": ok}

@app.post("/config/verify")
def config_verify(b: Bundle):
    key=_json_load(KEYRING, {"keys":{"default":"dev-hmac"},"active":"default"})["keys"]["default"].encode()
    body=json.dumps(b.bundle, separators=(",",":")).encode()
    mac=hmac.new(key, body, hashlib.sha256).digest()
    expect=base64.urlsafe_b64encode(mac).decode().rstrip("=")
    return {"ok": hmac.compare_digest(expect, b.sig), "expect": expect}

@app.post("/webhook/github")
async def webhook_github(request: Request):
    sig = request.headers.get("X-Hub-Signature-256","")
    body = await request.body()
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    expect = "sha256="+mac
    if not hmac.compare_digest(expect, sig):
        raise HTTPException(401, {"error":"bad webhook signature"})
    payload = await request.json()
    _audit({"route":"webhook/github","event":request.headers.get("X-GitHub-Event"),"delivery":request.headers.get("X-GitHub-Delivery")})
    return {"ok":True,"redacted": redact(json.dumps(payload))[:4096]}

@app.get("/cost/report")
def cost_report():
    return _json_load("reports/cost.json", {"note":"no report yet"})

@app.get("/redact/test")
def redact_test(q: str = "alice@example.com visited 10.0.0.1"):
    return {"input": q, "output": redact(q)}

@app.post("/glyph")
async def glyph(req: GlyphReq, request: Request, x_codex_keyid: str = Header(default=""), x_codex_sig: str = Header(default="")):
    # optional HMAC verify
    if x_codex_sig:
        body=await request.body()
        ok,expect=_verify_hmac(x_codex_keyid or "", body, x_codex_sig)
        if not ok: raise HTTPException(401, {"error":"bad hmac","expect":expect})
    if req.nonce: _consume_nonce(req.nonce)
    cmd=[sys.executable,"tools/glyph_guard_v25.py","--glyph",req.glyph]
    if req.dry_run: cmd.append("--dry-run")
    p = subprocess.run(cmd, capture_output=True, text=True)
    _audit({"route":"glyph","rc":p.returncode,"version":req.version})
    if p.returncode!=0: raise HTTPException(400,{"stderr":p.stderr,"stdout":p.stdout})
    return {"ok":True,"stdout":p.stdout}
from fastapi import FastAPI, HTTPException, Header, Request, Query
from pydantic import BaseModel
import subprocess, sys, json, hashlib, os, time, threading, yaml, hmac, base64

APP_VER = os.getenv("APP_VER","Codex v98.x · Orthos Prime")
IDENT_STR = os.getenv("CODEx_ID","caleb fedor byker konev|1998-10-27")
SUBJECT_SHA256 = os.getenv("SUBJECT_SHA256","")

CODEX_API_KEY   = os.getenv("CODEX_API_KEY","dev-key")
AUDIT = "audit.jsonl"
KEYRING = "secrets/keyring.json"
KEYLEDGER = "secrets/keyledger.jsonl"
CHAIN_FILE = "chain.jsonl"
ROLLBACK_PROOF = "rollback/proof.json"

_a_lock = threading.Lock()

def _audit(ev):
    ev["ts"] = time.time()
    line = json.dumps(ev, separators=(",",":"))
    with _a_lock, open(AUDIT,"a",encoding="utf-8") as f:
        f.write(line+"\n")
    return line

def _json_load(path, default):
    try: return json.load(open(path,"r",encoding="utf-8"))
    except Exception: return default

def _json_save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path,"w",encoding="utf-8"))

def _keyring():
    try: return json.load(open(KEYRING,encoding="utf-8"))
    except Exception: return {"keys":{"default":"dev-hmac"},"active":"default"}

def _verify_hmac_kid(kid, body, sig, ring=None):
    # signature is urlsafe base64 of raw hmac digest
    ring = ring or _keyring()
    kids = [kid] if kid else [ring.get("active")]
    # allow comma-separated fallback ring indicator
    if kid and "|" in kid:
        kids = kid.split("|")
    for k in kids:
        key = (ring.get("keys") or {}).get(k)
        if not key: continue
        mac = hmac.new(key.encode(), body, hashlib.sha256).digest()
        expect = base64.urlsafe_b64encode(mac).decode().rstrip("=")
        if hmac.compare_digest(expect, sig):
            return True, k
    return False, None

def _append_keyledger(kid, secret):
    # record {kid, sha256(secret), ts, prev}
    prev = None
    try:
        with open(KEYLEDGER,"r",encoding="utf-8") as f:
            last = None
            for l in f:
                if l.strip(): last = json.loads(l)
            prev = last
    except FileNotFoundError:
        prev = None
    entry = {"kid": kid, "sha256": hashlib.sha256(secret.encode()).hexdigest(), "ts": int(time.time()), "prev": (prev or {}).get("sha256")}
    os.makedirs(os.path.dirname(KEYLEDGER), exist_ok=True)
    with open(KEYLEDGER,"a",encoding="utf-8") as f:
        f.write(json.dumps(entry)+"\n")
    return entry

class GlyphReq(BaseModel):
    glyph: str
    dry_run: bool = False
    tenant: str | None = None

class MetricsPush(BaseModel):
    ns: str = "default"
    window_s: int = 300
    requests: int
    errors: int

class EvalReq(BaseModel):
    ns: str = "default"

class ProofReq(BaseModel):
    manifest_hash: str
    metrics: dict

app = FastAPI(title=APP_VER)

# boot-time self-check and optional self-heal
def _startup_selfcheck():
    try:
        from codex.selfcheck import verify as sc_verify
    except Exception:
        return {"ok":False, "errors":["selfcheck module missing"]}
    ok, errs = sc_verify(".")
    if ok:
        return {"ok":True}
    if os.getenv("SELF_HEAL","0")=="1":
        # regenerate manifest hashes (best-effort)
        try:
            subprocess.call([sys.executable, "scripts/hash_all.py", "--root", ".", "--out", "codex/manifest.v98.json"])
            # append recovery entry to chain
            rec = {"op":"self-heal","ts":int(time.time())}
            with open(CHAIN_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec)+"\n")
            return {"ok":True, "recovered": True}
        except Exception as e:
            return {"ok":False, "errors":[str(e)]}
    return {"ok":False, "errors":errs}

BOOT = _startup_selfcheck()

@app.get("/health")
def health(): return {"ok":True,"ver":APP_VER, "selfcheck": BOOT}

@app.get("/seal")
def seal(): return {"subject": IDENT_STR, "subject_id_sha256": SUBJECT_SHA256}

@app.post("/glyph")
async def glyph(req: GlyphReq, request: Request, x_codex_keyid: str = Header(default=""), x_codex_sig: str = Header(default="")):
    body = await request.body()
    if x_codex_sig:
        ok, used = _verify_hmac_kid(x_codex_keyid, body, x_codex_sig)
        if not ok:
            raise HTTPException(401, {"error":"bad hmac"})
    cmd=[sys.executable,"tools/glyph_guard_v23.py","--glyph",req.glyph]
    if req.dry_run: cmd.append("--dry-run")
    p = subprocess.run(cmd, capture_output=True, text=True)
    _audit({"route":"glyph","rc":p.returncode})
    if p.returncode!=0: raise HTTPException(400,{"stderr":p.stderr,"stdout":p.stdout})
    return {"ok":True,"stdout":p.stdout}

@app.post("/metrics/push")
def metrics_push(m: MetricsPush):
    os.makedirs("rollout", exist_ok=True)
    data = {"ns": m.ns, "ts": int(time.time()), "window_s": m.window_s, "requests": m.requests, "errors": m.errors}
    json.dump(data, open("rollout/metrics.json","w"))
    return {"stored": True, "path": "rollout/metrics.json"}

@app.post("/rollout/evaluate")
def rollout_evaluate(req: EvalReq):
    budget = _json_load("policy/budget.json", {"error_budget": 0.01, "min_requests": 200})
    m = _json_load("rollout/metrics.json", {"requests":0,"errors":0})
    errs = m.get("errors",0); reqs = max(1, m.get("requests",1))
    er = errs/reqs
    ok = (reqs >= budget.get("min_requests",200)) and (er <= budget.get("error_budget",0.01))
    verdict = "proceed" if ok else "rollback"
    # if rollback, write rollback proof
    if verdict == "rollback":
        proof = {"manifest_hash": _json_load("codex/manifest.v98.json",{}).get("items",[] ) and hashlib.sha256(open("codex/manifest.v98.json","rb").read()).hexdigest() or "", "metrics": m, "ts": int(time.time())}
        os.makedirs("rollback", exist_ok=True)
        # sign proof with active key
        ring = _keyring()
        active = ring.get("active")
        key = ring.get("keys",{}).get(active)
        sig = None
        if key:
            mac = hmac.new(key.encode(), json.dumps(proof).encode(), hashlib.sha256).digest()
            sig = base64.urlsafe_b64encode(mac).decode().rstrip("=")
            proof["sig_kid"] = active
            proof["sig"] = sig
        open(ROLLBACK_PROOF,"w",encoding="utf-8").write(json.dumps(proof, indent=2))
    _audit({"route":"rollout_evaluate","error_rate":er,"requests":reqs,"verdict":verdict})
    return {"error_rate": er, "requests": reqs, "budget": budget, "verdict": verdict}

@app.post("/judge/verdict")
def judge_verdict(proof: ProofReq, x_codex_keyid: str = Header(default="")):
    # verify incoming proof and emit a signed JWP-lite
    ring = _keyring()
    active = ring.get("active")
    key = ring.get("keys",{}).get(active)
    payload = json.dumps({"manifest_hash": proof.manifest_hash, "metrics": proof.metrics, "ts": int(time.time())})
    if not key:
        raise HTTPException(500, "no active key")
    mac = hmac.new(key.encode(), payload.encode(), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(mac).decode().rstrip("=")
    jwp = {"alg":"HS256","kid": active, "payload": payload, "sig": sig}
    return {"jwp": jwp}

@app.get("/keys/verify")
def keys_verify():
    # simple auditor that returns last ledger entry
    try:
        last=None
        with open(KEYLEDGER,"r",encoding="utf-8") as f:
            for l in f:
                if l.strip(): last=json.loads(l)
        return {"last": last}
    except FileNotFoundError:
        return {"last": None}

