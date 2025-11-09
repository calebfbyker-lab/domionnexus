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
