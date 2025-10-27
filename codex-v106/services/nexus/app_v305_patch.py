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
        ev = body.get("event",{}); sig=body.get("sig",""); node=body.get("node",
                               "")
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
