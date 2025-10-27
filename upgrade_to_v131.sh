#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"
test -d "$ROOT" || { echo "❌ $ROOT not found (install v106 first)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v131: Tri-Helix Convergence (predict → plan → policy → DAG)"

w services/common/subject.py <<'PY'
SUBJECT = "caleb fedor byker konev|1998-10-27"
def subject_fingerprint():
    import hashlib
    return hashlib.sha256(SUBJECT.encode()).hexdigest()
PY

w packages/core/src/codex_core/master_algorithm.py <<'PY'
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import json, math, hashlib, itertools

GLYPH_MAP = {"🌀":"verify","🌞":"invoke","🧾":"audit","🛡":"scan","🔮":"attest","🛡‍🔥":"sanctify","🚦":"rollout","⚖️":"judge","🌈":"deploy","♾":"continuum"}
ALIASES   = {"xtgs.verify":"verify","tsg.invoke":"invoke","tgs.audit":"audit","enochian.call":"invoke","solomonic.seal":"sanctify","kabbalah.sephirot":"judge","nexus.aeternum":"continuum"}
CORE = ["verify","invoke","audit","scan","attest","sanctify","rollout","judge","deploy","continuum"]

def normalize(glyph_text:str)->List[str]:
    import re
    toks=[t.strip() for t in re.split(r'[;,\n]+', glyph_text) if t.strip()]
    out=[]
    for t in toks:
        s = GLYPH_MAP.get(t[0]) if t and t[0] in GLYPH_MAP else ALIASES.get(t, t.lower())
        if s in CORE: out.append(s)
    return out

def features(steps:List[str], ctx:Dict[str,Any], seals:Dict[str,int])->Dict[str,float]:
    f={}; 
    for s in steps: f["u:"+s]=f.get("u:"+s,0)+1
    for a,b in zip(steps,steps[1:]): f["b:"+a+">"+b]=f.get("b:"+a+">"+b,0)+1
    f["len"]=float(len(steps)); f["uniq"]=float(len(set(steps)))
    run=max((len(list(g)) for _,g in itertools.groupby(steps)), default=1); f["run"]=float(run)
    for k in ("tenant","prio","risk"):
        if k in ctx: f["ctx:"+k+":"+str(ctx[k]).lower()]=1.0
    for k,v in (seals or {}).items(): f["seal:"+k]=float(v)
    return f

def predict_topk(feat:Dict[str,float], k:int=3)->List[Tuple[str,float]]:
    bias={s: 2.0-0.1*i for i,s in enumerate(CORE)}
    seen = {k for k in feat if k.startswith("u:")}
    logits=[]
    for s in CORE:
        z=bias[s] - (1.1 if "u:"+s in seen else 0.0)
        if feat.get("ctx:risk:high") and s in ("scan","attest","sanctify","judge"): z+=0.4
        logits.append((s,z))
    m=max(z for _,z in logits); ex=[(s, pow(2.71828, z-m)) for s,z in logits]; Z=sum(p for _,p in ex) or 1.0
    return sorted(((s,p/Z) for s,p in ex), key=lambda t:t[1], reverse=True)[:k]

@dataclass
class Edge: frm:str; to:str
@dataclass
class Task: name:str; plugin:str; inputs:Dict[str,Any]; timeout_s:int=90
@dataclass
class Plan: tasks:Dict[str,Task]; edges:List[Edge]; meta:Dict[str,Any]

def _mk_tasks(order:List[str], ctx:Dict[str,Any])->Dict[str,Task]:
    return { f"{i:02d}_{s}": Task(name=f"{i:02d}_{s}", plugin=f"core.{s}", inputs={"ctx":ctx}) for i,s in enumerate(order) }

def _mk_edges(order:List[str])->List[Edge]:
    return [Edge(frm=f"{i:02d}_{order[i]}", to=f"{i+1:02d}_{order[i+1]}") for i in range(len(order)-1)]

def policy_gate(order:List[str], ctx:Dict[str,Any])->List[str]:
    if str(ctx.get("risk","")).lower()=="high":
        need=["scan","attest","sanctify","judge"]
        for s in need:
            if s not in order:
                idx = CORE.index(s)
                order = sorted(set(order+[s]), key=lambda x: CORE.index(x))
    return order

def plan(glyph_text:str, ctx:Dict[str,Any], seals:Dict[str,int], rules:Dict[str,Any])->Dict[str,Any]:
    seq  = normalize(glyph_text)
    feat = features(seq, ctx, seals)
    preds= [s for s,_ in predict_topk(feat, k=3)]
    desired = [s for s in CORE if (s in seq or s in preds)]
    desired = policy_gate(desired, ctx)
    tasks=_mk_tasks(desired, ctx); edges=_mk_edges(desired)
    return {"ok":True,"tasks":{k:{"plugin":v.plugin,"inputs":v.inputs,"timeout_s":v.timeout_s} for k,v in tasks.items()},
            "edges":[e.__dict__ for e in edges], "predicted": preds, "context": ctx}
PY

w policies/v131_safety_elevated.yaml <<'YAML'
risk: high
require: ["scan","attest","sanctify","judge"]
YAML

w services/orchestrator/v131_adapter.py <<'PY'
from fastapi import APIRouter, HTTPException
from packages.core.src.codex_core.master_algorithm import plan as MA_PLAN
from services.common.subject import SUBJECT, subject_fingerprint
router = APIRouter(prefix="/v131", tags=["v131"])
@router.post("/plan")
def v131_plan(body: dict):
    glyph = (body or {}).get("glyph","" ).strip()
    if not glyph: raise HTTPException(400,"glyph required")
    ctx   = {"tenant": (body or {}).get("tenant","cfbk"),
             "prio":   (body or {}).get("prio",9),
             "risk":   (body or {}).get("risk","high"),
             "subject": SUBJECT, "subject_sha256": subject_fingerprint()}
    seals = (body or {}).get("seals", {})
    out = MA_PLAN(glyph, ctx, seals, rules={"profile":"safety_elevated"})
    return out
PY

w services/orchestrator/app_mount_v131.py <<'PY'
def mount_v131(app):
    from .v131_adapter import router as v131
    app.include_router(v131)
PY

w services/orchestrator/README-v131.md <<'MD'
v131 adds /v131/plan: glyphs → features → predictions → policy → DAG, with subject binding.
MD

w services/api/plugins/v131_router.py <<'PY'
from fastapi import APIRouter
import os, json, urllib.request
router = APIRouter(prefix="/v131", tags=["v131"])
ORCH = os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
def _j(path, data):
    req = urllib.request.Request(ORCH+path, data=json.dumps(data).encode(),
        headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())
@router.post("/plan")
def plan(body: dict): return _j("/v131/plan", body or {})
PY

w services/api/config/flags.yaml <<'YAML'
HMAC_KEY: dev-hmac
announce_versions: ["v101","v102","v107","v113","v131"]
YAML

echo "✓ v131 adapter and routers written. Next step: mount the v131 router in orchestrator app."
echo "   Edit services/orchestrator/app.py and import:  from .app_mount_v131 import mount_v131 ; then call mount_v131(app)"
