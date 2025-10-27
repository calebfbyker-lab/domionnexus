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
    # optional neuro bias hook
    def apply_neuro_bias(logits_list, ncs_bias: Dict[str,float] | None):
        if not ncs_bias: return logits_list
        out=[]
        for s,z in logits_list:
            out.append((s, z + ncs_bias.get(s, 0.0)))
        return out

    # allow caller to supply a small bias dict via special feature key
    ncs_bias = feat.get("_ncs_bias_dict") if isinstance(feat, dict) else None
    logits = apply_neuro_bias(logits, ncs_bias)

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
