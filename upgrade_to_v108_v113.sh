#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"
test -d "$ROOT" || { echo "❌ $ROOT not found (install v106 first)"; exit 1; }

w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }
a(){ mkdir -p "$(dirname "$ROOT/$1")"; printf "%s\n" "$2" >> "$ROOT/$1"; }

echo "→ v108–v113: shorter code, more power. Applying deltas…"

# v108: Minimal schema + run registry
w services/orchestrator/schema.py <<'PY'
# tiny typed validators without external deps
def _num(x, lo=None, hi=None):
    x=float(x);
    if lo is not None and x<lo: raise ValueError("min")
    if hi is not None and x>hi: raise ValueError("max")
    return x
def glyph_req(body:dict)->str:
    g=(body or {}).get("glyph"," ").strip()
    if not g: raise ValueError("glyph required")
    return g
def run_req(body:dict):
    g=glyph_req(body); t=(body or {}).get("tenant","public").strip() or "public"
    p=int((body or {}).get("prio",5)); p=max(0,min(10,p))
    return g,t,p
PY

# v108 registry
w services/orchestrator/registry.py <<'PY'
import json, time, os, threading
LOCK=threading.Lock(); RUNS={}; PATH=os.environ.get("CODEX_EVENTS_PATH","events.log")
def add(run):
    with LOCK: RUNS[run.run_id]=run
def get(run_id):
    with LOCK: return RUNS.get(run_id)
def log(ev:dict):
    ev={"t":time.time()}|ev
    try:
        with open(PATH,"a",encoding="utf-8") as f: f.write(json.dumps(ev,separators=(",",":"))+"\n")
    except Exception: pass
def tail(n=100):
    try:
        with open(PATH,"r",encoding="utf-8") as f: lines=f.readlines()[-n:]
        return [json.loads(x) for x in lines]
    except Exception: return []
PY

# v109 sandbox wrapper
w services/orchestrator/sandbox.py <<'PY'
import threading, queue
def call_with_timeout(fn, timeout_s, **kw):
    q=queue.Queue()
    def run():
        try: q.put(("ok", fn(**kw)))
        except Exception as e: q.put(("err", str(e)))
    th=threading.Thread(target=run, daemon=True); th.start(); th.join(timeout_s)
    if th.is_alive(): return ("timeout", None)
    return q.get()
PY

# v110 edge exchange
w services/orchestrator/edge.py <<'PY'
import time
PENDING=[]
def offer(job): PENDING.append(job)
def take_one()->dict|None:
    return PENDING.pop(0) if PENDING else None
PY

# v112 token middleware
w services/orchestrator/mw_token.py <<'PY'
import os, time, base64, hmac, hashlib
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
KEY=os.environ.get("CODEX_TOKEN_KEY",")
WINDOW=int(os.environ.get("CODEX_TOKEN_WINDOW","300"))
def _ok(token:str, path:str)->bool:
    if not KEY: return True
    try:
        ts, sig = token.split(".",1)
        if abs(time.time()-float(ts))>WINDOW: return False
        mac=hmac.new(KEY.encode(), (ts+path).encode(), hashlib.sha256).digest()
        exp=base64.urlsafe_b64encode(mac).decode().rstrip("=")
        return hmac.compare_digest(sig, exp)
    except Exception: return False
class TokenMaybeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        tok = request.headers.get("X-Codex-Token","")
        if not _ok(tok, request.url.path): return Response("unauthorized", status_code=401)
        return await call_next(request)
PY

# v113 priority queue
w services/orchestrator/queue_prio.py <<'PY'
import heapq, time
H=[]
def enqueue(item, prio:int=5):
    heapq.heappush(H, (-int(prio), time.time(), item))
def drain(timeout=0.1):
    t0=time.time()
    while time.time()-t0<timeout:
        if H: _,_,it=heapq.heappop(H); return it
        time.sleep(0.01)
    return None
PY

# orchestrator app compact
w services/orchestrator/app.py <<'PY'
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json, time, threading, uuid
from .mw_token import TokenMaybeMiddleware
from .sandbox import call_with_timeout
from .queue_prio import enqueue, drain
from .edge import offer, take_one
from .schema import glyph_req, run_req
from .registry import add as reg_add, get as reg_get, log as reg_log, tail as reg_tail
from packages.core.src.codex_core.compile_dag import glyphs_to_dag
from packages.core.src.codex_core.orch import Run, StepReceipt
from .plugins import REG

APP_VER = "Codex Aeturnum v113 · Orchestrator (compact)"
EVENTS=[]; LOCK=threading.Lock(); STOP=False
def push(ev):
    reg_log(ev)
    with LOCK:
        EVENTS.append(ev)
        if len(EVENTS)>1000: EVENTS[:]=EVENTS[-1000:]

app = FastAPI(title=APP_VER)
app.add_middleware(TokenMaybeMiddleware)

def _stream(cb):
    while not STOP:
        time.sleep(0.2)
        with LOCK: data=cb()
        for ev in data: yield f"data: {json.dumps(ev)}\n\n"

@app.get("/healthz")
def healthz(): return {"ok": True, "ver": APP_VER}

@app.get("/events/tail")
def tail(n:int=100): return reg_tail(n)

@app.get("/events/stream")
def sse():
    idx={"i":0}
    def chunk():
        i=idx["i"]; idx["i"]=len(EVENTS); return EVENTS[i:]
    return StreamingResponse(_stream(chunk), media_type="text/event-stream")

@app.get("/runs/{rid}")
def get_run(rid:str):
    r = reg_get(rid)
    if not r: raise HTTPException(404, "run not found")
    return {"run_id": r.run_id, "state": r.state, "receipts": [x.__dict__ for x in r.receipts], "head": r.head()}

@app.post("/workflows/compile")
def compile_workflow(body: dict):
    dag = glyphs_to_dag(glyph_req(body))
    return {"ok": True, "dag_digest": dag.digest(), "tasks": list(dag.tasks)}

@app.post("/runs")
def create_run(body: dict):
    g, tenant, prio = run_req(body)
    dag = glyphs_to_dag(g)
    rid = str(uuid.uuid4()); run = Run(run_id=rid, dag_digest=dag.digest(), tenant=tenant)
    reg_add(run); enqueue({"dag": dag, "run": run}, prio=prio)
    push({"type":"run_enqueued","run":rid,"tenant":tenant,"prio":prio})
    return {"run_id": rid, "state": run.state, "tenant": tenant, "prio": prio}

def _loop():
    while not STOP:
        job = drain(0.2)
        if not job: continue
        dag, run = job["dag"], job["run"]
        run.state="running"; push({"type":"run_start","run":run.run_id,"tenant":run.tenant})
        ok=True
        for step in dag.topo():
            t = dag.tasks[step]
            fn = REG.get(t.plugin);
            if not fn: ok=False; break
            tag, out = call_with_timeout(fn, timeout_s=t.timeout_s, **(t.inputs or {}))
            ts=time.time()
            if tag!="ok": ok=False
            rec = StepReceipt(task=t.name, started=ts, ended=ts, ok=(tag=="ok"),
                              output_digest=("" if out is None else __import__("hashlib").sha256(json.dumps(out,separators=(",",":")).encode()).hexdigest()),
                              log_digest="0"*64)
            run.receipts.append(rec)
            push({"type":"step","task":t.name,"run":run.run_id,"ok":rec.ok})
            if not rec.ok: break
        run.state="succeeded" if ok else "failed"
        push({"type":"run_done","run":run.run_id,"ok":(run.state=='succeeded'),"head":run.head()})
threading.Thread(target=_loop, daemon=True).start()

@app.post("/edge/pull")
def edge_pull():
    job = take_one()
    return job or {}

@app.post("/edge/offer")
def edge_offer(body:dict):
    offer(body); return {"ok":True}
PY

# update flags.json
w services/api/config/flags.json <<'JSON'
{ "hmac_key":"dev-hmac", "announce_versions":["v101","v102","v107","v113"] }
JSON

# token helper
w tools/token_make.py <<'PY'
#!/usr/bin/env python3
import os, time, base64, hmac, hashlib, sys
key=(os.environ.get("CODEX_TOKEN_KEY") or "dev-key").encode()
ts=str(time.time())
sig=base64.urlsafe_b64encode(hmac.new(key, (ts+"/runs").encode(), hashlib.sha256).digest()).decode().rstrip("=")
print(f"{ts}.{sig}")
PY

chmod +x "$ROOT/tools/token_make.py"

echo "✓ v108–v113 applied to $ROOT"
