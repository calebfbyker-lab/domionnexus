#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"; test -d "$ROOT" || { echo "❌ need codex-v106 (v300..v303 installed)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v304 Ecliptica: executor, attestation hub, ws observer, verifier daemon"

# 1) Executor (TypeScript)
w packages/aeon/executor.ts <<'TS'
import { EventEmitter } from "node:events";

export type Task = { id:string; run:()=>Promise<any> };
export type RunResult = { id:string; ok:boolean; output?:any; error?:string };

export class Executor extends EventEmitter {
  constructor(private dag:Task[]){ super(); }
  async start(){
    for (const t of this.dag) {
      const t0 = Date.now();
      this.emit("step:start", t.id);
      try {
        const out = await t.run();
        this.emit("step:end", { id: t.id, ok: true, ms: Date.now()-t0, out });
      } catch(e:any) {
        this.emit("step:end", { id: t.id, ok: false, ms: Date.now()-t0, error: (e && e.message) || String(e) });
        throw e;
      }
    }
    this.emit("run:complete");
  }
}
TS

# 2) Attestation Hub (fan-out to Nexus peers)
w services/nexus/hub.py <<'PY'
import json, os, urllib.request, threading, queue, time
from packages.core.src.codex_core.aeon import covenant_proof

NODES = [n for n in os.environ.get("NEXUS_PEERS","http://localhost:8020").split(",") if n]

def _post(url, data):
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
            headers={"Content-Type":"application/json"})
        urllib.request.urlopen(req, timeout=6)
    except Exception:
        # best-effort; ignore peer failures
        pass

Q = queue.Queue()
def submit(ev:dict):
    Q.put(ev)

def _worker():
    while True:
        ev = Q.get()
        try:
            proof = covenant_proof(ev.get("head",""), ev.get("tenant",""), ev.get("subject_sha256",""), [])
            for node in NODES:
                try:
                    _post(node.rstrip('/') + "/ledger/ingest", {"event": {**ev, "proof": proof}, "sig": "local"})
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(0.1)

threading.Thread(target=_worker, daemon=True).start()
PY

# 3) Observer Gateway (WebSocket router)
w services/api/plugins/v304_ws_router.py <<'PY'
from fastapi import APIRouter, WebSocket
import asyncio, json

router = APIRouter(prefix="/v304/ws", tags=["v304"])
clients = set()

@router.websocket("/observe")
async def observe(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await asyncio.sleep(30)
    finally:
        clients.discard(ws)

def broadcast(ev: dict):
    dead = []
    for ws in list(clients):
        try:
            asyncio.create_task(ws.send_text(json.dumps(ev)))
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)
PY

# 4) Verifier daemon (periodic re-check using v303 verify core)
w services/daemon/verifier.py <<'PY'
import os, json, time, glob
from packages.core.src.codex_core.verify import recompute_proof_sha

LEDGER = os.environ.get("LEDGER_DIR", "./ledger")

def verify_all():
    for f in glob.glob(f"{LEDGER}/*.json"):
        try:
            data = json.load(open(f, "r", encoding="utf-8"))
            b = data.get("proof", {}).get("bundle", {})
            want = data.get("proof", {}).get("proof_sha256", "")
            got = recompute_proof_sha(b)
            if want != got:
                print("⚠️ integrity drift", f)
        except Exception as e:
            print("error verifying", f, e)

if __name__ == "__main__":
    while True:
        verify_all()
        time.sleep(600)
PY

echo "✓ v304 files written."
echo "Next steps:"
echo " - Wire Executor: import and use packages/aeon/executor.ts (build step) or a Node runner; listen to 'step:end' and 'run:complete' to call services/nexus/hub.submit(ev) and services.api.plugins.v304_ws_router.broadcast(ev)"
echo " - Start verifier daemon: python3 services/daemon/verifier.py (or run under systemd/supervisor)"
echo " - Mount v304 ws router into API gateway (plugins auto-load may pick it up if plugin discovery includes v304_ws_router.py)"
