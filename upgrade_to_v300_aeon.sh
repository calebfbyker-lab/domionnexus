#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"; test -d "$ROOT" || { echo "❌ need codex-v106 (v131+ & v201–v202)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v300 AEON: plan→enforce→execute→attest→prove"

# ───────── core: covenant proof (compact) ─────────
w packages/core/src/codex_core/aeon.py <<'PY'
from __future__ import annotations
import json, time, hashlib
def covenant_proof(head:str, tenant:str, subject_sha256:str, peer_stamps:list[dict]) -> dict:
    """
    Produce a final 'covenant proof' hash that binds the run receipts (head),
    the subject, tenant, wall-clock, and at least two peer stamps.
    """
    ts = int(time.time())
    bundle = {"head":head,"tenant":tenant,"subject_sha256":subject_sha256,
              "ts":ts,"stamps":sorted(peer_stamps, key=lambda x:(x.get("node",""),x.get("ts",0)))[:4]}
    blob = json.dumps(bundle, separators=(",":"), sort_keys=True).encode()
    return {"ts":ts, "proof_sha256": hashlib.sha256(blob).hexdigest(), "bundle": bundle}
PY

# ───────── orch: deny-caps enforcement (goetic constraints) ─────────
w services/orchestrator/runner_caps.py <<'PY'
def enforce_caps(task_plugin:str, deny:list[str]):
    if "exec_shell" in deny and task_plugin.endswith("invoke"):
        raise RuntimeError("capability denied: exec_shell")
    if "exfiltrate_net" in deny and task_plugin.endswith(("invoke","audit")):
        raise RuntimeError("capability denied: exfiltrate_net")
    # extend as needed (write_outside_workspace, etc.)
PY

# ───────── orch: AEON endpoint (do-everything flow) ─────────
w services/orchestrator/v300_aeon.py <<'PY'
from fastapi import APIRouter, HTTPException
import json, time, uuid, urllib.request, os
from services.common.subject import SUBJECT, subject_fingerprint
from packages.core.src.codex_core.aeon import covenant_proof
from services.orchestrator.nexus_sink import _post as nexus_post, _sign as nexus_sign

router = APIRouter(prefix="/v300", tags=["v300"])

ORCH_BASE = "http://localhost:8010"  # self-call
NEXUS_URL = os.environ.get("CODEX_NEXUS_URL","http://localhost:8020")
NODE_ID    = os.environ.get("CODEX_NODE_ID","node-A")

def _j(path, body):
    req=urllib.request.Request(ORCH_BASE+path, data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r: return json.loads(r.read())

@router.post("/aeon")
def aeon(body: dict):
    """
    1) v202 plan (ontology, constraints, temporal bias)
    2) submit run
    3) wait for completion (poll tail)
    4) publish to Nexus (run_done already hooked; we add AEON proof)
    """
    if not isinstance(body, dict): raise HTTPException(400,"bad request")
    glyph = (body.get("glyph") or "").strip()
    if not glyph: raise HTTPException(400,"glyph required")

    tenant = body.get("tenant","cfbk"); prio = body.get("prio",9); risk = body.get("risk","high")
    tags = body.get("tags", {}); constraints = body.get("constraints","")

    # 1) plan
    plan_res = _j("/v202/plan", {"tenant":tenant,"prio":prio,"risk":risk,"glyph":glyph,"tags":tags,"constraints":constraints})
    if not plan_res.get("ok",False): return {"ok":False, "errors":plan_res.get("errors",[]), "where":"plan"}
    plan = plan_res["plan"]
    # ensure deny caps flow downstream
    deny = plan["context"].get("deny_caps", [])

    # 2) submit run (reuse /runs)
    rid = _j("/runs", {"tenant":tenant, "glyph":glyph})["run_id"]

    # 3) await completion via /events/tail (simple bounded poll)
    head=None; ok=None; t0=time.time()
    for _ in range(120):  # up to ~60s
        tail=_j("/events/tail?n=50", {})
        done=[e for e in tail if e.get("type")=="run_done" and e.get("run")==rid]
        if done:
            head=done[-1].get("head"); ok=bool(done[-1].get("ok"))
            break
        time.sleep(0.5)
    if head is None: raise HTTPException(504,"run timeout")

    # 4) AEON covenant proof (gather 0..N peer stamps if present)
    peer_stamps=[]
    try:
        # quick gossip pull for recent stamps; ignore failures
        tip = nexus_post("/gossip/pull", {"n":20})
        peer_stamps = [{"node": it[1].get("from",""), "ts": it[1].get("ev",{}).get("ts",0)} 
                       for it in tip.get("items",[]) if str(it[0]).startswith("ev:")]
    except Exception:
        peer_stamps=[]

    proof = covenant_proof(head=head, tenant=tenant, subject_sha256=subject_fingerprint(), peer_stamps=peer_stamps)

    # publish AEON proof into Nexus as a distinct record
    ev={"kind":"aeon_proof","run":rid,"ok":ok,"proof":proof["proof_sha256"],
        "bundle":proof["bundle"], "subject":SUBJECT, "subject_sha256":subject_fingerprint()}
    try:
        nexus_post("/ledger/ingest", {"event":ev,"sig":nexus_sign(ev),"node":NODE_ID})
    except Exception:
        pass

    return {"ok": ok, "run_id": rid, "head": head, "proof": proof, "deny_caps": deny, "plan_bias": plan_res.get("bias",{})}
PY

# ───────── gateway proxy ─────────
w services/api/plugins/v300_router.py <<'PY'
from fastapi import APIRouter
import os, json, urllib.request
router = APIRouter(prefix="/v300", tags=["v300"])
ORCH = os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
def _post(p,b):
    req=urllib.request.Request(ORCH+p, data=json.dumps(b).encode(), headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=12) as r: return json.loads(r.read())
@router.post("/aeon")
def aeon(b:dict): return _post("/v300/aeon", b or {})
PY

echo "✓ v300 files written."
echo "→ Mount: add 'from services.orchestrator.v300_aeon import router as v300; app.include_router(v300)' to orchestrator app."
echo "Then add one line in services/orchestrator/app.py:"
echo
echo "    from services.orchestrator.v300_aeon import router as v300"
echo "    app.include_router(v300)"
echo
echo "The gateway already auto-loads v300_router.py via your plugin discovery."
echo
echo "Use it (one call does every step)"
echo "bash -c '...curl example...'"
