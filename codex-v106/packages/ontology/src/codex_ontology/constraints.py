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
