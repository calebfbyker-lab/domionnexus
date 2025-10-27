from fastapi import APIRouter
import os, json, urllib.request
router = APIRouter(prefix="/v202", tags=["v202"])
ORCH = os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
def _post(p,b):
    req=urllib.request.Request(ORCH+p, data=json.dumps(b).encode(), headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r: return json.loads(r.read())
@router.post("/plan")
def plan(b:dict): return _post("/v202/plan", b or {})
