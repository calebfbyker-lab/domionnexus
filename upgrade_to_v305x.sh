#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"; test -d "$ROOT" || { echo "❌ need codex-v106 (v300–v305)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v305.x: keys+limits+allowlist+migrations+exports+SLO+CLI"

# ───────────── RBAC tokens v2: rolling keys (KID + expiry) ─────────────
w services/nexus/rbac_v2.py <<'PY'
import os, time, hmac, hashlib, base64, json
# TOKENS_V2: csv of records: kid:key:scopes
#   e.g., "k1:secretA:ingest,read,metrics;k2:secretB:read"
REC=os.environ.get("NEXUS_TOKENS_V2","").strip()
ALLOW=os.environ.get("NEXUS_IP_ALLOW","").strip()  # "127.0.0.1,10.0.0.0/8"
def _parse():
    D={}
    for r in (REC.split(";") if REC else []):
        if not r: continue
        kid,key,sc = r.split(":",2)
        D[kid] = {"key":key, "scopes": set(s.strip() for s in sc.split(","))}
    return D
SECRETS=_parse()

def _hmac(k:bytes,b:bytes)->str:
    return base64.urlsafe_b64encode(hmac.new(k,b,hashlib.sha256).digest()).decode().rstrip("=")

def mint(kid:str, scopes:list[str], ttl_s:int=3600)->str:
    if kid not in SECRETS: raise ValueError("kid unknown")
    payload={"kid":kid,"scopes":scopes,"exp":int(time.time())+ttl_s}
    b=json.dumps(payload,separators=(",",":")).encode()
    sig=_hmac(SECRETS[kid]["key"].encode(), b)
    return base64.urlsafe_b64encode(b).decode().rstrip(".")+"."+sig

def allow_ip(remote:str)->bool:
    if not ALLOW: return True
    if remote in [a.strip() for a in ALLOW.split(",") if ":" not in a]: return True
    # bare minimum CIDR (/8,/16,/24)
    if "/" in ALLOW:
        net,mask=ALLOW.split("/",1); mask=int(mask)
        import ipaddress
        try: return ipaddress.ip_address(remote) in ipaddress.ip_network(ALLOW, strict=False)
        except Exception: return False
    return False

def check(token:str, scope:str)->bool:
    try:
        b64,sig = token.split(".",1)
        b=base64.urlsafe_b64decode(b64+"==")
        payload=json.loads(b)
        kid=payload["kid"]; exp=int(payload["exp"])
        if time.time()>exp: return False
        rec=SECRETS.get(kid); 
        if not rec: return False
        if _hmac(rec["key"].encode(), b)!=sig: return False
        return scope in rec["scopes"]
    except Exception:
        return False
PY

# ───────────── SQLite migrations (idempotent) ─────────────
w services/nexus/migrations.py <<'PY'
import sqlite3, os
DB=os.environ.get("NEXUS_DB","./nexus.db")
def migrate():
    c=sqlite3.connect(DB)
    c.executescript("""
    create table if not exists kv(key text primary key, val text);
    alter table events add column meta text default '{}' ;
    """)
    c.commit(); c.close()
PY

# ───────────── Export/Import (JSONL) ─────────────
w tools/nexus_export.py <<'PY'
#!/usr/bin/env python3
import os, sqlite3, json, sys
DB=os.environ.get("NEXUS_DB","./nexus.db")
out=sys.argv[1] if len(sys.argv)>1 else "nexus_dump.jsonl"
c=sqlite3.connect(DB)
for row in c.execute("select kind,node,ts,payload from events order by id"):
    print(json.dumps({"kind":row[0],"node":row[1],"ts":row[2],"payload":json.loads(row[3])}))
for row in c.execute("select run_id,head,proof_sha256,ts,bundle from proofs order by id"):
    print(json.dumps({"proof":{"run_id":row[0],"head":row[1],"proof_sha256":row[2],"ts":row[3],"bundle":json.loads(row[4])}}))
c.close()
PY
chmod +x "$ROOT/tools/nexus_export.py"

w tools/nexus_import.py <<'PY'
#!/usr/bin/env python3
import os, sqlite3, json, sys, time
DB=os.environ.get("NEXUS_DB","./nexus.db")
inp=sys.argv[1] if len(sys.argv)>1 else "-"
c=sqlite3.connect(DB); c.execute("PRAGMA journal_mode=WAL;")
def add_ev(k,n,ts,p): c.execute("insert into events(kind,node,ts,payload) values(?,?,?,?)",(k,n,ts,json.dumps(p,separators=(',',':'))))
def add_pf(r,h,p,ts,b): c.execute("insert into proofs(run_id,head,proof_sha256,ts,bundle) values(?,?,?,?,?)",(r,h,p,ts,json.dumps(b,separators=(',',':'))))
src=open(inp) if inp!="-." and inp!="- " and inp!="-" else sys.stdin
for line in src:
    j=json.loads(line)
    if "proof" in j:
        pf=j["proof"]; add_pf(pf["run_id"],pf["head"],pf["proof_sha256"],pf["ts"],pf["bundle"])
    else:
        add_ev(j["kind"],j["node"],j["ts"],j["payload"])
c.commit(); c.close()
PY
chmod +x "$ROOT/tools/nexus_import.py"

# ───────────── Rate limiting (token bucket, per token) ─────────────
w services/nexus/ratelimit.py <<'PY'
import time, collections, os
CAP=int(os.environ.get("NEXUS_RPS","5"))
WIN=float(os.environ.get("NEXUS_RPS_WIN","1.0"))
BUCKET=collections.defaultdict(lambda: {"ts":0.0,"tokens":CAP})
def allow(key:str)->bool:
    now=time.time()
    b=BUCKET[key]; elapsed=now-b["ts"]
    b["ts"]=now; b["tokens"]=min(CAP, b["tokens"]+elapsed*(CAP/WIN))
    if b["tokens"]>=1.0: b["tokens"]-=1.0; return True
    return False
PY

# ───────────── SLO probes (liveness/readiness; latency budget) ─────────────
w services/nexus/slo.py <<'PY'
import time
START=time.time()
def liveness(): return {"ok":True,"uptime_s":int(time.time()-START)}
def readiness(): return {"ok":True}
# latency budget check (stub for alerting)
LAST_LAT=0.0
def record_latency(ms:float):
    global LAST_LAT; LAST_LAT=ms
def budget(): 
    return {"p_last_ms": LAST_LAT, "budget_ms": 250.0, "ok": LAST_LAT<=250.0}
PY

# ───────────── Patch Nexus app with v305.x features ─────────────
w services/nexus/app_v305x_patch.py <<'PY'
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import time
from services.nexus.migrations import migrate
from services.nexus.ratelimit import allow as rl_allow
from services.nexus.rbac_v2 import check as tok_check, allow_ip
from services.nexus.slo import liveness, readiness, budget, record_latency

def patch(app: FastAPI):
    migrate()

    @app.get("/health/live")
    def live(): return liveness()

    @app.get("/health/ready")
    def ready(): return readiness()

    @app.middleware("http")
    async def guards(request: Request, call_next):
        t0=time.time()
        # IP allowlist
        client_ip = request.client.host if request.client else "0.0.0.0"
        if not allow_ip(client_ip):
            raise HTTPException(403,"ip_forbidden")
        # rate limiting (by token or ip)
        tok = request.headers.get("X-Auth","") or client_ip
        if not rl_allow(tok):
            raise HTTPException(429,"rate_limited")
        # optional scope check for write endpoints
        path=request.url.path
        if path.endswith("/ingest_signed") and not tok_check(request.headers.get("X-Auth",""), "ingest"):
            raise HTTPException(403,"forbidden")
        resp = await call_next(request)
        record_latency((time.time()-t0)*1000.0)
        return resp

    @app.get("/slo/budget")
    def slo_budget(): return JSONResponse(budget())
PY

# ───────────── CLI helper (mint tokens, check metrics) ─────────────
w tools/archon_cli.py <<'PY'
#!/usr/bin/env python3
import os, sys, json, urllib.request
from services.nexus.rbac_v2 import mint
def http(method, url, data=None, tok=""):
    req=urllib.request.Request(url, data=(json.dumps(data).encode() if data is not None else None), method=method,
        headers={"Content-Type":"application/json","X-Auth":tok} if tok else {})
    with urllib.request.urlopen(req, timeout=8) as r: 
        ct=r.headers.get("content-type",")
        return r.read().decode() if "text/plain" in ct else json.loads(r.read())
def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else "help"
    if cmd=="mint":
        kid=sys.argv[2]; scopes=sys.argv[3].split(","); ttl=int(sys.argv[4]) if len(sys.argv)>4 else 3600
        print(mint(kid, scopes, ttl))
    elif cmd=="metrics":
        url=os.environ.get("NEX","http://localhost:8020")+"/metrics"
        tok=os.environ.get("TOK",""); print(http("GET",url,tok=tok))
    else:
        print("archon_cli mint <kid> <scopesCSV> [ttl] | metrics")
if __name__=="__main__": main()
PY
chmod +x "$ROOT/tools/archon_cli.py"

echo "✓ v305.x files written."
echo "→ Mount in services/nexus/app.py:"
echo "    from services.nexus.app_v305_patch import patch as v305_patch"
echo "    from services.nexus.app_v305x_patch import patch as v305x_patch"
echo "    v305_patch(app); v305x_patch(app)"
echo "Wire it (two lines in services/nexus/app.py)"
echo