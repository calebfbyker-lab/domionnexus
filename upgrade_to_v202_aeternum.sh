#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"; test -d "$ROOT" || { echo "❌ need codex-v106 (v131+ recommended)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v202 Nexus Aeturnum: ontology + constraints + temporal nous + AI synthesis"

w packages/ontology/src/codex_ontology/atlas.py <<'PY'
# Namespace → symbols (deterministic tags). Keep short; expand later via YAML plug-ins.
ELEMENTAL = ["earth","water","air","fire","aether"]
PLANETARY = ["mercury","venus","earth","mars","jupiter","saturn","uranus","neptune","luna","sol"]
STELLAR   = ["polaris","sirius","rigel","betelgeuse","vega","arcturus","antares","aldebaran"]
GEOMETRIC = ["point","line","triangle","square","pentagon","hexagon","heptagon","octagon"]
HARMONIC  = ["unison","octave","fifth","fourth","third","sixth","minor","major"]
ANGELIC   = ["watcher","messenger","guardian","judge","healer","scribe","builder"]
ALCHEMY   = ["calcination","solution","coagulation","sublimation","mortification","distillation","projection"]
GOETIC_DENY = ["exfiltrate_net","exec_shell","write_outside_workspace"]  # sandbox denies

def normalize(ns:str, value:str)->str:
    v=value.strip().lower()
    table={"elemental":ELEMENTAL,"planetary":PLANETARY,"stellar":STELLAR,"geometric":GEOMETRIC,
           "harmonic":HARMONIC,"angelic":ANGELIC,"alchemical":ALCHEMY}
    if ns not in table: return v
    return v if v in table[ns] else ""
PY

w packages/ontology/src/codex_ontology/constraints.py <<'PY'
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
@dataclass
class Clause: kind:str; data:Dict[str,Any]
def parse(lines:str)->List[Clause]:
    out=[]
    for raw in lines.splitlines():
        s=raw.strip()
        if not s or s.startswith("#"): continue
        if s.startswith("REQ "): out.append(Clause("REQ",{"step":s[4:].strip()}))
        elif s.startswith("ORDER "): out.append(Clause("ORDER",{"chain":[x.strip() for x in s[6:].split("<") if x.strip()]}))
        elif s.startswith("WITHIN "):
            tok=s[7:].split(":"); out.append(Clause("WITHIN",{"step":tok[0].strip(),"ms":int(tok[1].split("=")[1])}))
        elif s.startswith("TAG "):
            lhs, rhs = s[4:].split("->"); out.append(Clause("TAG",{"nsval":lhs.strip(),"w":float(rhs)}))
        elif s.startswith("DENY "): out.append(Clause("DENY",{"cap":s[5:].strip()}))
    return out

def enforce(plan:Dict[str,Any], clauses:List[Clause]) -> Tuple[Dict[str,Any], List[str], Dict[str,float], List[str]]:
    tasks=plan["tasks"]; edges=plan["edges"]
    steps=[name.split("_",1)[1] for name in sorted(tasks.keys())]
    errors=[]; warns=[]; bias={}
    for c in [x for x in clauses if x.kind=="REQ"]:
        if c.data["step"] not in steps: errors.append(f"missing:{c.data['step']}")
    for c in [x for x in clauses if x.kind=="ORDER"]:
        chain=c.data["chain"]; pos={s:i for i,s in enumerate(steps)}
        for a,b in zip(chain, chain[1:]):
            if a in pos and b in pos and not (pos[a]<pos[b]): errors.append(f"order:{a}<!{b}")
    for c in [x for x in clauses if x.kind=="WITHIN"]:
        st=c.data["step"]
        for k,v in tasks.items():
            if k.endswith("_"+st) and v.get("timeout_s",90)*1000>c.data["ms"]:
                tasks[k]["timeout_s"]=c.data["ms"]//1000; warns.append(f"timeout:{st}->{tasks[k]['timeout_s']}s")
    for c in [x for x in clauses if x.kind=="TAG"]:
        nsval=c.data["nsval"].lower(); w=c.data["w"]
        if nsval.startswith("elemental:fire"):   bias.update({"scan":w*0.2,"attest":w*0.1})
        if nsval.startswith("planetary:mercury"):bias.update({"invoke":w*0.2,"audit":w*0.1})
        if nsval.startswith("harmonic:fifth"):   bias.update({"judge":w*0.15})
        if nsval.startswith("angelic:guardian"): bias.update({"sanctify":w*0.2,"judge":w*0.1})
        if nsval.startswith("alchemical:distillation"): bias.update({"audit":w*0.2})
    denies=[c.data["cap"] for c in clauses if c.kind=="DENY"]
    return {"tasks":tasks,"edges":edges,"context":plan.get("context",{})}, errors, bias, denies
PY

w packages/ontology/src/codex_ontology/chronos.py <<'PY'
from __future__ import annotations
from typing import Dict, Any
import math, time
def phase(now:float|None=None)->Dict[str,float]:
    t = now or time.time()
    day = (t % 86400.0) / 86400.0
    lunar = ((t / 86400.0) % 29.530588) / 29.530588
    harmonic = (math.sin(2*math.pi*day) + math.sin(3*math.pi*day)) * 0.5
    return {"day":day,"lunar":lunar,"harmonic":harmonic}
def chrono_bias(ph:Dict[str,float])->Dict[str,float]:
    b={}
    if ph["lunar"]<0.1 or ph["lunar"]>0.9:
        b.update({"verify":0.15,"scan":0.10})
    if ph["harmonic"]>0.6:
        b.update({"rollout":0.05,"deploy":0.05})
    if ph["day"]>0.75:
        b.update({"judge":0.05})
    return b
PY

w services/orchestrator/v202_adapter.py <<'PY'
from fastapi import APIRouter, HTTPException
from packages.core.src.codex_core.master_algorithm import plan as MA_PLAN
from packages.ontology.src.codex_ontology.atlas import normalize
from packages.ontology.src.codex_ontology.constraints import parse, enforce
from packages.ontology.src.codex_ontology.chronos import phase, chrono_bias
from services.common.subject import SUBJECT, subject_fingerprint

router = APIRouter(prefix="/v202", tags=["v202"])

@router.post("/plan")
def v202_plan(body: dict):
    if not isinstance(body, dict): raise HTTPException(400,"bad request")
    glyph = (body.get("glyph") or "").strip()
    if not glyph: raise HTTPException(400,"glyph required")
    tags = body.get("tags", {})
    seals = {k:1 for k in tags.keys()}
    ctx   = {"tenant": body.get("tenant","cfbk"),
             "prio":   body.get("prio",9),
             "risk":   body.get("risk","high"),
             "subject": SUBJECT, "subject_sha256": subject_fingerprint()}
    out = MA_PLAN(glyph, ctx, seals, rules={"profile":"aeturnum"})
    dsl  = body.get("constraints","")
    plan, errors, bias, denies = enforce(out, parse(dsl))
    tb = chrono_bias(phase())
    merged_bias = {}
    for k in set(bias)|set(tb): merged_bias[k]=bias.get(k,0.0)+tb.get(k,0.0)
    plan["context"]["_ncs_bias_dict"]=merged_bias
    plan["context"]["deny_caps"]=denies
    plan["predicted"]=out["predicted"]; plan["edges"]=out["edges"]
    return {"ok": (len(errors)==0), "errors": errors, "plan": plan, "bias": merged_bias, "denies": denies}
PY

w services/api/plugins/v202_router.py <<'PY'
from fastapi import APIRouter
import os, json, urllib.request
router = APIRouter(prefix="/v202", tags=["v202"])
ORCH = os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
def _post(p,b):
    req=urllib.request.Request(ORCH+p, data=json.dumps(b).encode(), headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r: return json.loads(r.read())
@router.post("/plan")
def plan(b:dict): return _post("/v202/plan", b or {})
PY

w services/nexus/stamps.py <<'PY'
def attach_ontology(ev:dict, context:dict)->dict:
    keep={"tenant","prio","risk","subject_sha256"}
    ctx={k:v for k,v in (context or {}).items() if k in keep}
    tags=[k for k in (context or {}).get("tags",[])]
    denies=(context or {}).get("deny_caps",[])
    ev.update({"ctx":ctx,"tags":tags,"deny":denies})
    return ev
PY

echo "✓ v202 files written. Now: mount routers in orchestrator & gateway."
