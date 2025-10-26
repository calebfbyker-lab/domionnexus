#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"
test -d "$ROOT" || { echo "❌ $ROOT not found (install v106 first)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }
a(){ mkdir -p "$(dirname "$ROOT/$1")"; printf "%s\n" "$2" >> "$ROOT/$1"; }

echo "→ v114–v120 Ω: compressing, hardening, and finishing…"

# ───────────────── v114: Tiny typed config (YAML→env→defaults)
w services/common/config.py <<'PY'
import os, json
try:
  import yaml  # optional
except Exception:
  yaml=None
DEFAULTS={"HMAC_KEY":"dev-hmac","TOKEN_KEY":"dev-key","ORCH_URL":"http://localhost:8010"}
def load(path:str|None=None)->dict:
  cfg={}
  if path and yaml:
    try: cfg=yaml.safe_load(open(path)) or {}
    except Exception: cfg={}
  # env overrides
  for k,v in DEFAULTS.items():
    cfg[k]=os.environ.get(f"CODEX_{k}", cfg.get(k, v))
  return cfg
PY

# ───────────────── v115: 90-line plugin SDK (inputs/types/validate)
w services/orchestrator/sdk.py <<'PY'
from __future__ import annotations
from typing import Callable, Any, Dict, Optional, Tuple
REG: Dict[str, Callable[..., Any]] = {}
def task(name:str)->Callable[[Callable[...,Any]],Callable[...,Any]]:
  def deco(fn): REG[name]=fn; return fn
  return deco
class In:
  @staticmethod
  def num(x, lo=None, hi=None):
    x=float(x);
    if lo is not None and x<lo: raise ValueError("min")
    if hi is not None and x>hi: raise ValueError("max")
    return x
  @staticmethod
  def text(x, nonempty=False):
    x=str(x)
    if nonempty and not x.strip(): raise ValueError("empty")
    return x
def run(name:str, **kw)->Tuple[str,Any]:
  fn=REG.get(name)
  if not fn: return ("err", f"task:{name}:missing")
  try: return ("ok", fn(**kw))
  except Exception as e: return ("err", str(e))
PY

# ───────────────── v116: Core task pack (expressive but short)
w services/orchestrator/plugins_core.py <<'PY'
from .sdk import task, In
@task("core.verify")      # verify manifest/spec present
def v(**kw): return {"verified": True}
@task("core.invoke")      # simulate remote call stub
def i(url:str="https://example", **_): return {"invoked": In.text(url)}
@task("core.audit")       # SBOM stub
def a(**_): return {"sbom":"cyclonedx-1.5:stub"}
@task("core.scan")        # vuln summary stub
def s(**_): return {"vulns":0}
@task("core.attest")      # produce attestation digest stub
def t(payload:str="{}", **_): import hashlib;
# collapse minimal lines:
 return {"attestation":"sha256:"+hashlib.sha256(payload.encode()).hexdigest()}
@task("core.sanctify")    # policy gate
def x(**_): return {"policy":"pass"}
@task("core.rollout")     # progressive rollout %
def r(percent:int=10, **_): return {"rolled": max(0,min(100,int(percent)))}
@task("core.judge")       # final decision
def j(**_): return {"gate":"allow"}
@task("core.deploy")      # pretend deploy
def d(target:str="staging", **_): return {"target": In.text(target, True), "status":"ok"}
@task("core.continuum")   # close-out
def c(**_): return {"closing": True}
PY

# ───────────────── v117: Single-file packager (zip repo + provenance)
w tools/pack_release.py <<'PY'
#!/usr/bin/env python3
import os, json, zipfile, hashlib, time, sys
root = os.path.dirname(os.path.dirname(__file__))
out = os.path.join(root, f"codex_omega_{int(time.time())}.zip")
digests={}
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
  for dp,_,fs in os.walk(root):
    # skip venvs and build dirs
    if any(p in dp for p in (".venv","__pycache__",".git",".github/workflows")): continue
    for n in fs:
      p=os.path.join(dp,n)
      rel=os.path.relpath(p, root)
      with open(p,"rb") as f: b=f.read()
      digests[rel]=hashlib.sha256(b).hexdigest()
      z.writestr(rel, b)
meta={"subject":"caleb fedor byker konev|1998-10-27","subject_id_sha256":hashlib.sha256(b"caleb fedor byker konev|1998-10-27").hexdigest(),"digests":digests}
open(os.path.join(root,"codex_release_provenance.json"),"w").write(json.dumps(meta,indent=2))
print(out)
PY
chmod +x "$ROOT/tools/pack_release.py"

# ───────────────── v118: Deterministic build flags in gateway/orchestrator
w services/api/mw_hmac.py <<'PY'
import base64, hmac, hashlib, json
def sign(spec:dict, key:str)->str:
  body=json.dumps(spec, separators=(",",":")).encode()
  return base64.urlsafe_b64encode(hmac.new(key.encode(), body, hashlib.sha256).digest()).decode().rstrip("=")
PY

w services/api/main.py <<'PY'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os, json
from services.common.config import load
from .mw_hmac import sign
APP_VER="Codex Aeturnum Ω · Gateway"
cfg=load(os.path.join(os.path.dirname(__file__),"config","flags.yaml"))
app=FastAPI(title=APP_VER)
def _mount():
  import pkgutil, importlib, os
  pkg_path=os.path.join(os.path.dirname(__file__),"plugins")
  for _,m,_ in pkgutil.iter_modules([pkg_path]):
    if m.endswith("_router"): app.include_router(getattr(importlib.import_module("services.api.plugins."+m),"router"))
_mount()
@app.get("/")
def index():
  ann = (cfg.get("announce_versions") or ["v101","v102","v107","v113"])
  return HTMLResponse(f"<h1>{APP_VER}</h1><p>Versions: {', '.join(ann)}</p>")
@app.get("/openapi/signed")
def openapi_signed():
  spec = app.openapi()
  return {"sig": sign(spec, cfg.get("HMAC_KEY","dev-hmac")), "spec": spec}
PY

w services/api/config/flags.yaml <<'YAML'
HMAC_KEY: dev-hmac
announce_versions: ["v101","v102","v107","v113"]
YAML

# Orchestrator: short main with compact loop already at v113; just wire config
w services/orchestrator/app.py <<'PY'
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json, time, threading, uuid, os, hashlib
from services.common.config import load
from .sdk import run as run_task
from packages.core.src.codex_core.compile_dag import glyphs_to_dag
from packages.core.src.codex_core.orch import Run, StepReceipt
from .queue_prio import enqueue, drain
from .schema import glyph_req, run_req
from .registry import add as reg_add, get as reg_get, log as reg_log, tail as reg_tail

cfg=load(os.path.join(os.path.dirname(__file__),"flags.yaml"))
APP_VER="Codex Aeturnum Ω · Orchestrator"
EVENTS=[]; LOCK=threading.Lock(); STOP=False
def push(ev): reg_log(ev);
    global EVENTS;
    with LOCK: EVENTS=(EVENTS+ [ev])[-1000:]

app=FastAPI(title=APP_VER)

@app.get("/healthz")
def healthz(): return {"ok":True,"ver":APP_VER}

@app.get("/events/tail")
def tail(n:int=50): return reg_tail(n)

@app.get("/events/stream")
def stream():
  idx={"i":0}
  def gen():
    while True:
      time.sleep(0.2)
      with LOCK: chunk=EVENTS[idx["i"]:] ; idx["i"]=len(EVENTS)
      for ev in chunk: yield f"data: {json.dumps(ev)}\n\n"
  return StreamingResponse(gen(), media_type="text/event-stream")

@app.get("/runs/{rid}")
def get_run(rid:str):
  r=reg_get(rid);
  if not r: raise HTTPException(404,"run not found")
  return {"run_id":r.run_id,"state":r.state,"receipts":[x.__dict__ for x in r.receipts],"head":r.head()}

@app.post("/workflows/compile")
def compile_workflow(body:dict):
  dag = glyphs_to_dag(glyph_req(body))
  return {"ok":True, "dag_digest": dag.digest(), "tasks": list(dag.tasks)}

@app.post("/runs")
def create_run(body:dict):
  g, tenant, prio = run_req(body)
  dag = glyphs_to_dag(g); rid=str(uuid.uuid4()); run=Run(run_id=rid, dag_digest=dag.digest(), tenant=tenant)
  reg_add(run); enqueue({"dag":dag,"run":run}, prio=prio); push({"type":"run_enqueued","run":rid,"prio":prio})
  return {"run_id":rid,"state":run.state,"tenant":tenant,"prio":prio}

def _loop():
  while True:
    job=drain(0.2);
    if not job: continue
    dag, run = job["dag"], job["run"]; run.state="running"; push({"type":"run_start","run":run.run_id})
    ok=True
    for step in dag.topo():
      t = dag.tasks[step]; tag, out = run_task(f"core.{step.split('_',1)[1]}", **(t.inputs or {}))
      ts=time.time()
      if tag!="ok": ok=False; out=None
      dig = "" if out is None else hashlib.sha256(json.dumps(out,separators=(',',':')).encode()).hexdigest()
      run.receipts.append(StepReceipt(task=t.name, started=ts, ended=ts, ok=(tag=="ok"), output_digest=dig, log_digest="0"*64))
      push({"type":"step","task":t.name,"run":run.run_id,"ok":tag=="ok"})
      if not ok: break
    run.state = "succeeded" if ok else "failed"
    push({"type":"run_done","run":run.run_id,"ok":run.state=="succeeded","head":run.head()})
threading.Thread(target=_loop, daemon=True).start()
PY

w services/orchestrator/flags.yaml <<'YAML'
# reserved for future orchestration flags (kept tiny)
YAML

# ───────────────── v119: Ultra-short CLI (one file, two verbs)
w tools/cx.py <<'PY'
#!/usr/bin/env python3
import os, json, urllib.request, sys
ORCH=os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
cmd=sys.argv[1] if len(sys.argv)>1 else "help"
def call(path, body=None):
  req=urllib.request.Request(ORCH+path, data=(json.dumps(body).encode() if body else None), headers={"Content-Type":"application/json"})
  return json.loads(urllib.request.urlopen(req, timeout=8).read())
if cmd=="run":
  glyph=sys.argv[2] if len(sys.argv)>2 else "🌀; 🌞; 🧾; 🛡; 🔮; 🛡‍🔥; 🚦; ⚖️; 🌈; ♾"
  print(json.dumps(call("/runs", {"tenant":"cfbk","prio":9,"glyph":glyph}), indent=2))
elif cmd=="tail":
  n=int(sys.argv[2]) if len(sys.argv)>2 else 10
  print(json.dumps(call(f"/events/tail?n={n}"), indent=2))
else:
  print("cx.py run [glyph] | tail [n]")
PY
chmod +x "$ROOT/tools/cx.py"

# ───────────────── v120: Release profile + smoke e2e
w tools/smoke_e2e.sh <<'SH'
#!/usr/bin/env bash
set -e
ORCH="${CODEX_ORCH_URL:-http://localhost:8010}"
curl -s -X POST "$ORCH/runs" -H "content-type: application/json" \
  -d '{"tenant":"cfbk","prio":9,"glyph":"🌀; 🌞; 🧾; 🛡; 🔮; 🛡‍🔥; 🚦; ⚖️; 🌈; ♾"}' | jq -r .run_id
curl -s "$ORCH/events/tail?n=5" | jq
SH
chmod +x "$ROOT/tools/smoke_e2e.sh"

echo "✓ v114–v120 Ω applied to $ROOT"
