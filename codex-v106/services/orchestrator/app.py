from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json, time, threading, uuid, os

USE_REDIS = os.environ.get("CODEX_USE_REDIS", "0") == "1"
if USE_REDIS:
    from .queue_redis import enqueue
else:
    from .queue import enqueue

from packages.core.src.codex_core.compile_dag import glyphs_to_dag
from packages.core.src.codex_core.orch import Run
from .worker import run_loop

APP_VER = "Codex Aeturnum v107 · Orchestrator"
EVENTS = []
LOCK = threading.Lock()


def push(ev):
    with LOCK:
        EVENTS.append(ev)
        if len(EVENTS) > 5000:
            EVENTS.pop(0)

thr = threading.Thread(target=run_loop, kwargs={"event_cb": push}, daemon=True)
thr.start()
app = FastAPI(title=APP_VER)

@app.get("/healthz")
def healthz():
    return {"ok": True, "ver": APP_VER, "redis": USE_REDIS}

@app.get("/tenants")
def tenants():
    from packages.core.src.codex_core.tenancy import TENANTS
    return {k: vars(v) for k, v in TENANTS.items()}

@app.post("/workflows/compile")
def compile_workflow(body: dict):
    g = body.get("glyph", "")
    dag = glyphs_to_dag(g)
    return {"ok": True, "dag_digest": dag.digest(), "tasks": list(dag.tasks)}

@app.post("/runs")
def create_run(body: dict):
    g = body.get("glyph", "")
    tenant = body.get("tenant", "public")
    dag = glyphs_to_dag(g)
    rid = str(uuid.uuid4())
    run = Run(run_id=rid, dag_digest=dag.digest(), tenant=tenant)
    enqueue({"dag": dag, "run": run})
    return {"run_id": rid, "dag_digest": dag.digest(), "state": run.state, "tenant": tenant}

@app.get("/events/stream")
def events_stream():
    def gen():
        idx = 0
        while True:
            time.sleep(0.2)
            with LOCK:
                chunk = EVENTS[idx:]
                idx = len(EVENTS)
            for ev in chunk:
                yield f"data: {json.dumps(ev)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
