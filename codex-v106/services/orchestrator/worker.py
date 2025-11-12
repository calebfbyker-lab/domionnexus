import json, time, hashlib, os, signal, threading
from .plugins import REG
from .queue import drain as drain_local
from .queue_redis import drain as drain_redis
from .runtime import allow_start, mark_done, emit_webhook
from packages.core.src.codex_core.orch import StepReceipt

STOP = False


def _graceful(*_):
    global STOP
    STOP = True

signal.signal(signal.SIGINT, _graceful)
signal.signal(signal.SIGTERM, _graceful)


def _next_job():
    try:
        j = drain_redis(block_ms=500)
    except Exception:
        j = None
    if j:
        return j
    return drain_local(0.1)


def run_loop(event_cb=lambda ev: None):
    while not STOP:
        job = _next_job()
        if not job:
            time.sleep(0.05)
            continue
        dag, run = job["dag"], job["run"]
        if not allow_start(run.tenant):
            # requeue local if quota denies
            from .queue import enqueue as re_enq
            re_enq(job)
            time.sleep(0.25)
            continue
        try:
            run.state = "running"
            event_cb({"type": "run_start", "run": run.run_id, "tenant": run.tenant})
            emit_webhook({"type": "run_start", "run": run.run_id, "tenant": run.tenant})
            for step in dag.topo():
                t = dag.tasks[step]
                fn = REG.get(t.plugin)
                if not fn:
                    raise RuntimeError(f"missing plugin {t.plugin}")
                attempt = 0
                while True:
                    s = time.time()
                    try:
                        out = fn(**(t.inputs or {}))
                        o = json.dumps(out, separators=(",", ":")).encode()
                        e = time.time()
                        rec = StepReceipt(task=t.name, started=s, ended=e, ok=True,
                                          output_digest=hashlib.sha256(o).hexdigest(),
                                          log_digest=hashlib.sha256(b"").hexdigest())
                        run.receipts.append(rec)
                        ev = {"type": "step", "task": t.name, "digest": rec.digest(), "run": run.run_id, "tenant": run.tenant}
                        event_cb(ev)
                        emit_webhook(ev)
                        break
                    except Exception:
                        attempt += 1
                        if attempt > getattr(t, "max_retries", 0):
                            run.state = "failed"
                            tip = run.head()
                            fin = {"type": "run_done", "ok": False, "head": tip, "run": run.run_id, "tenant": run.tenant}
                            event_cb(fin)
                            emit_webhook(fin)
                            raise
                        time.sleep(getattr(t, "backoff_s", 0.5) * attempt)
            run.state = "succeeded"
            tip = run.head()
            fin = {"type": "run_done", "ok": True, "head": tip, "run": run.run_id, "tenant": run.tenant}
            event_cb(fin)
            emit_webhook(fin)
        finally:
            mark_done(run.tenant)
