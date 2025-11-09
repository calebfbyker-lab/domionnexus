#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"; test -d "$ROOT" || { echo "❌ need codex-v106 (v300 installed)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v303 AEON: verifier, policy registry, covenant multisig"

# ───────────────── packages: verifier core ─────────────────
w packages/core/src/codex_core/verify.py <<'PY'
from __future__ import annotations
from typing import Dict, Any, List, Tuple
import json, hashlib, math

def recompute_proof_sha(bundle: Dict[str,Any]) -> str:
    blob = json.dumps(bundle, separators=(",":"), sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()

def approx_chrono_bias(ts:int) -> Dict[str,float]:
    day = (ts % 86400) / 86400.0
    lunar = ((ts / 86400.0) % 29.530588) / 29.530588
    harmonic = (math.sin(2*math.pi*day) + math.sin(3*math.pi*day)) * 0.5
    b={}
    if lunar<0.1 or lunar>0.9: b.update({"verify":0.15,"scan":0.10})
    if harmonic>0.6: b.update({"rollout":0.05,"deploy":0.05})
    if day>0.75: b.update({"judge":0.05})
    return b

def compare_bias(recorded: Dict[str,float], expected: Dict[str,float], tol: float=1e-6) -> Tuple[bool, List[str]]:
    errs=[]
    for k,v in expected.items():
        if abs(recorded.get(k,0.0)-v)>tol:
            errs.append(f"bias:{k}: {recorded.get(k,0.0)} != {v}")
    return (len(errs)==0, errs)

def constraints_ok(plan: Dict[str,Any], denies: List[str]) -> bool:
    # minimal static checks: deny caps are lists; timeouts are non-negative
    for cap in denies:
        if not isinstance(cap, str): return False
    for _,t in plan.get("tasks",{}).items():
        if t.get("timeout_s",0) < 0: return False
    return True
PY

# ───────────────── packages: multisig (HMAC m-of-n) ─────────────────
w packages/core/src/codex_core/multisig.py <<'PY'
from __future__ import annotations
from typing import List, Dict, Any
import hmac, hashlib, base64

def sign(body: bytes, key: str) -> str:
    mac=hmac.new(key.encode(), body, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")

def verify(body: bytes, sig: str, key: str) -> bool:
    try: 
        exp = sign(body, key)
        return hmac.compare_digest(sig, exp)
    except Exception:
        return False

def verify_m_of_n(event: dict, sigs: List[Dict[str,str]], keys: Dict[str,str], m_required: int) -> int:
    """
    event: dict to be signed; sigs: [{"node": "...", "sig": "..."}, ...]
    keys: node_id -> secret; returns number of valid signatures
    """
    b=str(event).encode()
    ok=0
    for s in sigs:
        node=s.get("node",""); sig=s.get("sig","")
        key = keys.get(node)
        if not key: continue
        if verify(b, sig, key): ok += 1
    return ok if ok>=m_required else 0
PY

# ───────────────── orchestrator: policy registry (small, file-backed) ─────────────────
w services/orchestrator/policies/README.md <<'MD'
Drop small constraint scripts here (v202 DSL). Example:
- safety_elevated.dsv
- fast_lane.dsv
- offline_covenant.dsv
MD

w services/orchestrator/policies/safety_elevated.dsv <<'DSL'
# v202 DSL
REQ sanctify
ORDER sanctify<judge<deploy
WITHIN judge:ms=5000
DSL

# ───────────────── orchestrator: v303 verify endpoints ─────────────────
w services/orchestrator/v303_verify.py <<'PY'
from fastapi import APIRouter, HTTPException
import os, json, glob
from packages.core.src.codex_core.verify import recompute_proof_sha, approx_chrono_bias, compare_bias, constraints_ok
from packages.core.src.codex_core.multisig import verify_m_of_n

router = APIRouter(prefix="/v303", tags=["v303"])

POLICY_DIR = os.path.join(os.path.dirname(__file__), "policies")
PEER_KEYS  = os.environ.get("CODEX_MULTISIG_KEYS","").strip()
# format: "nodeA=keyA,nodeB=keyB,..." (HMAC secrets per peer)
def _keys():
    d={}
    if not PEER_KEYS: return d
    for pair in PEER_KEYS.split(","):
        if not pair: continue
        node, key = pair.split("=",1)
        d[node.strip()] = key.strip()
    return d

@router.get("/policy")
def list_policies():
    if not os.path.isdir(POLICY_DIR): return {"policies":[]}
    files=sorted(glob.glob(os.path.join(POLICY_DIR, "*.dsv")))
    return {"policies":[os.path.basename(f) for f in files]}

@router.get("/policy/{name}")
def get_policy(name:str):
    path=os.path.join(POLICY_DIR, name)
    if not os.path.isfile(path): raise HTTPException(404,"not found")
    return {"name": name, "text": open(path,"r",encoding="utf-8").read()}

@router.post("/verify")
def verify(body: dict):
    """
    Input: {
      head, tenant, proof:{ts, proof_sha256, bundle:{...}},
      plan:{tasks,edges,context}, bias:{...}, denies:[...],
      sigs:[{node,sig},...], quorum:2
    }
    """
    if not isinstance(body, dict): raise HTTPException(400,"bad request")
    proof = body.get("proof",{})
    bundle= proof.get("bundle",{})
    want  = proof.get("proof_sha256","")
    have  = recompute_proof_sha(bundle)
    ok_hash = (want == have)

    # chrono check (bias must match approximate expected for recorded ts)
    expected = approx_chrono_bias(int(bundle.get("ts",0) or 0))
    recorded = body.get("bias",{})
    ok_bias, bias_errs = compare_bias(recorded, expected)

    # constraints/sandbox sanity
    ok_plan = constraints_ok(body.get("plan",{}), body.get("denies",[]))

    # multisig (if keys present)
    keys=_keys()
    valid=0
    if keys and body.get("sigs"):
        valid = verify_m_of_n({"kind":"aeon_proof","bundle":bundle}, body["sigs"], keys, int(body.get("quorum",2)))

    return {
      "ok": bool(ok_hash and ok_bias and ok_plan and ((not keys) or valid>0)),
      "hash_ok": ok_hash, "bias_ok": ok_bias, "plan_ok": ok_plan,
      "bias_errors": bias_errs, "valid_sigs": valid, "quorum": int(body.get("quorum",2))
    }
PY

# ───────────────── gateway: v303 proxy ─────────────────
w services/api/plugins/v303_router.py <<'PY'
from fastapi import APIRouter
import os, json, urllib.request
router=APIRouter(prefix="/v303", tags=["v303"])
ORCH=os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
def _get(p):
    with urllib.request.urlopen(ORCH+p, timeout=8) as r: 
        import json as J; return J.loads(r.read())
def _post(p,b):
    req=urllib.request.Request(ORCH+p, data=json.dumps(b).encode(), headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=12) as r: 
        import json as J; return J.loads(r.read())
@router.get("/policy")                 def list_policies(): return _get("/v303/policy")
@router.get("/policy/{name}")          def get_policy(name:str): return _get(f"/v303/policy/{name}")
@router.post("/verify")                def verify(b:dict): return _post("/v303/verify", b or {})
PY

echo "✓ v303 files written. Mount the v303 router in orchestrator (if not auto-mounted)."
echo "Mount (1 line)"
echo "In services/orchestrator/app.py, after other includes:"
echo
echo "    from services.orchestrator.v303_verify import router as v303"
echo "    app.include_router(v303)"
echo "The gateway will auto-load v303_router.py via plugin discovery."
