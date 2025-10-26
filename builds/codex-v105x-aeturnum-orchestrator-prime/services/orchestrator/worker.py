import json, time, hashlib
from services.orchestrator.plugins import REG
from services.orchestrator.queue import drain
from packages.core.src.codex_core.orch import StepReceipt

def run_loop(event_cb=lambda ev: None):
    while True:
        job = drain()
        if not job:
            time.sleep(0.05); continue
        dag, run = job["dag"], job["run"]
        for step in dag.topo():
            t = dag.tasks[step]
            fn = REG.get(t.plugin)
            if not fn: raise RuntimeError(f"missing plugin {t.plugin}")
            s = time.time()
            out = fn(**(t.inputs or {}))
            o = json.dumps(out, separators=(",",":")).encode()
            e = time.time()
            rec = StepReceipt(task=t.name, started=s, ended=e, ok=True,
                              output_digest=hashlib.sha256(o).hexdigest(),
                              log_digest=hashlib.sha256(b"").hexdigest())
            run.receipts.append(rec)
            event_cb({"type":"step", "task":t.name, "digest":rec.digest(), "run":run.run_id})
        run.state = "succeeded"
        event_cb({"type":"run_done","head":run.head(),"run":run.run_id})
