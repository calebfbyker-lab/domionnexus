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
