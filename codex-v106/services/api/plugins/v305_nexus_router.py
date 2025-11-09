from fastapi import APIRouter, Header
import os, json, urllib.request
router=APIRouter(prefix="/v305/nexus", tags=["v305.nexus"])
NEX=os.environ.get("CODEX_NEXUS_URL","http://localhost:8020")
def _post(path, data, tok):
    req=urllib.request.Request(NEX+path, data=json.dumps(data).encode(),
                               headers={"Content-Type":"application/json","X-Auth":tok})
    with urllib.request.urlopen(req, timeout=10) as r: import json as J; return J.loads(r.read())
def _get(path, tok):
    req=urllib.request.Request(NEX+path, headers={"X-Auth":tok})
    with urllib.request.urlopen(req, timeout=10) as r: import json as J; return J.loads(r.read())
@router.get("/list")
def list_(x_auth: str = Header(default="")): return _get("/ledger/list", x_auth)
@router.get("/metrics")
def metrics(x_auth: str = Header(default="")):
    req=urllib.request.Request(NEX+"/metrics", headers={"X-Auth":x_auth})
    with urllib.request.urlopen(req, timeout=8) as r: return r.read().decode()
@router.post("/ingest-signed")
def ingest_signed(body:dict, x_auth: str = Header(default="")):
    return _post("/ledger/ingest_signed", body or {}, x_auth)
