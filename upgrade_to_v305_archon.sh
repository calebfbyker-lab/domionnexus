#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"; test -d "$ROOT" || { echo "❌ need codex-v106 (v300–v304 applied)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v305 Archon Keeper: persistence + scopes + ed25519(optional) + backups + metrics"

# ───────────────────────────────── Crypto (Ed25519 if available; fallback to HMAC) ─────────────────────────────────
w packages/core/src/codex_core/crypt.py <<'PY'
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
PY

# ───────────────────────────────── Nexus SQLite store (durable events/proofs) ─────────────────────────────────
w services/nexus/store_sqlite.py <<'PY'
import sqlite3, os, json, time
DB=os.environ.get("NEXUS_DB","./nexus.db")

def _conn(): 
    c=sqlite3.connect(DB); c.execute("PRAGMA journal_mode=WAL;"); return c

def init():
    c=_conn()
    c.executescript("""
    create table if not exists events(
        id integer primary key autoincrement,
        kind text, node text, ts integer, payload text
    );
    create index if not exists ix_events_ts on events(ts);
    create table if not exists proofs(
        id integer primary key autoincrement,
        run_id text, head text, proof_sha256 text, ts integer, bundle text
    );
    """); c.commit(); c.close()

def add_event(kind:str, node:str, payload:dict):
    c=_conn()
    c.execute("insert into events(kind,node,ts,payload) values(?,?,?,?)",
              (kind,node,int(time.time()), json.dumps(payload, separators=(',',':'))))
    c.commit(); c.close()

def add_proof(run_id:str, head:str, proof_sha256:str, bundle:dict):
    c=_conn()
    c.execute("insert into proofs(run_id,head,proof_sha256,ts,bundle) values(?,?,?,?,?)",
              (run_id,head,proof_sha256,int(time.time()), json.dumps(bundle, separators=(',',':'))))
    c.commit(); c.close()

def tail_events(n:int=50):
    c=_conn(); rows=c.execute("select kind,node,ts,payload from events order by id desc limit ?", (n,)).fetchall(); c.close()
    return [ {"kind":k,"node":d,"ts":ts,"payload":json.loads(p)} for (k,d,ts,p) in rows ]

def list_proofs(n:int=50):
    c=_conn(); rows=c.execute("select run_id,head,proof_sha256,ts,bundle from proofs order by id desc limit ?",(n,)).fetchall(); c.close()
    return [ {"run_id":r,"head":h,"proof_sha256":p,"ts":ts,"bundle":json.loads(b)} for (r,h,p,ts,b) in rows ]
PY

# ───────────────────────────────── Nexus metrics (Prometheus text) ─────────────────────────────────
w services/nexus/metrics.py <<'PY'
import sqlite3, os
DB=os.environ.get("NEXUS_DB","./nexus.db")
def render_metrics()->str:
    c=sqlite3.connect(DB)
    ev = c.execute("select count(*) from events").fetchone()[0]
    pr = c.execute("select count(*) from proofs").fetchone()[0]
    c.close()
    return "\n".join([
        "# HELP nexus_events_total Total events ingested",
        "# TYPE nexus_events_total counter",
        f"nexus_events_total {ev}",
        "# HELP nexus_proofs_total Total AEON proofs stored",
        "# TYPE nexus_proofs_total counter",
        f"nexus_proofs_total {pr}",
        ""
    ])
PY

# ───────────────────────────────── Nexus RBAC (header tokens with scopes) ─────────────────────────────────
w services/nexus/rbac.py <<'PY'
import os
TOK=os.environ.get("NEXUS_TOKENS","").strip()
# format: "token123=ingest,read,metrics;tokenABC=read"
def _map():
    out={}
    for row in (TOK.split(";") if TOK else []):
        if not row: continue
        tok,sc=row.split("=",1); out[tok.strip()]=set(x.strip() for x in sc.split(","))
    return out
TOKMAP=_map()
def allowed(token:str, scope:str)->bool:
    return bool(token and token in TOKMAP and scope in TOKMAP[token])
PY

# ───────────────────────────────── Nexus app: wire store + metrics + RBAC + ed25519 optional ─────────────────────────────────
w services/nexus/app_v305_patch.py <<'PY'
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
import json, os
from services.nexus.store_sqlite import init as db_init, add_event, add_proof, tail_events, list_proofs
from services.nexus.metrics import render_metrics
from services.nexus.rbac import allowed
from packages.core.src.codex_core.crypt import ed25519_verify, hmac_verify

def patch(app: FastAPI):
    db_init()

    @app.get("/metrics")
    def metrics(req: Request):
        tok = req.headers.get("X-Auth","")
        if not allowed(tok, "metrics"): raise HTTPException(403,"forbidden")
        return PlainTextResponse(render_metrics(), media_type="text/plain; version=0.0.4")

    @app.get("/ledger/list")
    def ledger_list(n:int=50, request: Request=None):
        tok = request.headers.get("X-Auth","") if request else ""
        if not allowed(tok, "read"): raise HTTPException(403,"forbidden")
        return {"events": tail_events(n), "proofs": list_proofs(n)}

    @app.post("/ledger/ingest_signed")
    def ingest_signed(body: dict, request: Request):
        tok = request.headers.get("X-Auth","")
        if not allowed(tok, "ingest"): raise HTTPException(403,"forbidden")
        ev = body.get("event",{}); sig=body.get("sig",""); node=body.get("node",")
        mode = body.get("mode","hmac")  # "ed25519" or "hmac"
        key  = os.environ.get("NEXUS_KEY","dev-hmac")  # for hmac
        pub  = os.environ.get("NEXUS_PUB","")         # for ed25519
        b = str(ev).encode()
        ok = (ed25519_verify(pub, b, sig) if mode=="ed25519" else hmac_verify(key, b, sig))
        if not ok: raise HTTPException(401,"bad signature")
        add_event(kind=ev.get("kind","ev"), node=node, payload=ev)
        if ev.get("kind")=="aeon_proof":
            bundle = ev.get("bundle",{})
            add_proof(run_id=bundle.get("head","")[:16], head=bundle.get("head",""), proof_sha256=ev.get("proof",""), bundle=bundle)
        return {"ok":True}
PY

# ───────────────────────────────── Backup + restore helpers ─────────────────────────────────
w tools/nexus_backup.sh <<'SH'
#!/usr/bin/env bash
set -e
DB="${NEXUS_DB:-./nexus.db}"
OUT="${1:-nexus_backup_$(date +%Y%m%d%H%M%S).tar.gz}"
tar -czf "$OUT" "$DB"
echo "backup: $OUT"
SH
chmod +x "$ROOT/tools/nexus_backup.sh"

w tools/nexus_restore.sh <<'SH'
#!/usr/bin/env bash
set -e
ARCHIVE="$1"; test -f "$ARCHIVE" || { echo "usage: $0 <backup.tar.gz>"; exit 1; }
tar -xzf "$ARCHIVE"
echo "restored SQLite files from $ARCHIVE"
SH
chmod +x "$ROOT/tools/nexus_restore.sh"

# ───────────────────────────────── Gateway: quick proxy additions ─────────────────────────────────
w services/api/plugins/v305_nexus_router.py <<'PY'
from fastapi import APIRouter, Header
import os, json, urllib.request
router=APIRouter(prefix="/v305/nexus", tags=["v305.nexus"])
NEX=os.environ.get("CODEX_NEXUS_URL","http://localhost:8020")
def _post(path, data, tok):
    req=urllib.request.Request(NEX+path, data=json.dumps(data).encode(),
                               headers={"Content-Type":"application/json","X-Auth":tok})
    with urllib.request.urlopen(req, timeout=10) as r: import json as J; return J.loads(r.read())
def _get(path, tok):
    req=urllib.request.Request(NEX+path, headers={"X-Auth":tok})
    with urllib.request.urlopen(req, timeout=10) as r: import json as J; return J.loads(r.read())
@router.get("/list")
def list_(x_auth: str = Header(default="")): return _get("/ledger/list", x_auth)
@router.get("/metrics")
def metrics(x_auth: str = Header(default="")):
    req=urllib.request.Request(NEX+"/metrics", headers={"X-Auth":x_auth})
    with urllib.request.urlopen(req, timeout=8) as r: return r.read().decode()
@router.post("/ingest-signed")
def ingest_signed(body:dict, x_auth: str = Header(default="")):
    return _post("/ledger/ingest_signed", body or {}, x_auth)
PY

# ───────────────────────────────── Mount patches: nexus app ─────────────────────────────────
w services/nexus/README-v305.md <<'MD'
v305 adds:
- SQLite ledger (events + proofs)
- Token RBAC: header X-Auth with scopes: ingest, read, metrics
- /metrics Prometheus endpoint
- /ledger/list, /ledger/ingest_signed (HMAC or Ed25519)
- Backup/restore scripts
Mount with:
    from services.nexus.app_v305_patch import patch as v305_patch
    v305_patch(app)
Set env:
    export NEXUS_DB=./nexus.db
    export NEXUS_TOKENS="token123=ingest,read,metrics;tokenABC=read"
    export NEXUS_KEY="dev-hmac"
    # (optional ed25519)
    export NEXUS_PUB="<base64-verify-key>"
MD

echo "✓ v305 files written."
echo "→ Next: open services/nexus/app.py and add:"
echo "    from services.nexus.app_v305_patch import patch as v305_patch"
echo "    v305_patch(app)"
echo "Wire it (two tiny edits)"
echo "Nexus app (services/nexus/app.py):"
echo
echo "from services.nexus.app_v305_patch import patch as v305_patch"
echo "v305_patch(app)"
echo "Gateway auto-loads v305_nexus_router.py via your plugin discovery (nothing else to do)."
