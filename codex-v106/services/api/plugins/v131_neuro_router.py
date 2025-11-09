from fastapi import APIRouter
import os, json, urllib.request
router = APIRouter(prefix="/v131/neuro", tags=["v131.neuro"])
ORCH = os.environ.get("CODEX_ORCH_URL","http://localhost:8010")

def _post(path, data):
    req = urllib.request.Request(ORCH+path, data=json.dumps(data).encode(),
        headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())

@router.post("/capture")
def capture(body: dict): return _post("/v131/neuro/capture", body or {})

@router.post("/align")
def align(body: dict): return _post("/v131/neuro/align", body or {})

@router.post("/context-bias")
def context_bias(body: dict): return _post("/v131/neuro/context-bias", body or {})
