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
