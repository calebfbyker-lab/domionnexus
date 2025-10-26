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
def push(ev):
  reg_log(ev)
  global EVENTS
  with LOCK:
    EVENTS = (EVENTS + [ev])[-1000:]

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
