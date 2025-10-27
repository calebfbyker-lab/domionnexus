from fastapi import APIRouter, HTTPException
from services.orchestrator.plugins_neuro import neuro_capture, neuro_align, neuro_bias_for_context

router = APIRouter(prefix="/v131/neuro", tags=["v131.neuro"])

@router.post("/capture")
def capture(body: dict):
    out = neuro_capture(body or {})
    if not out.get("ok"): raise HTTPException(400, out.get("reason","bad_request"))
    return out

@router.post("/align")
def align(body: dict):
    out = neuro_align(body or {})
    if not out.get("ok"): raise HTTPException(400, "align_failed")
    return out

@router.post("/context-bias")
def context_bias(body: dict):
    return neuro_bias_for_context(body or {})
