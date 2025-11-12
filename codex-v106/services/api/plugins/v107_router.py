from fastapi import APIRouter, HTTPException
import os, json, urllib.request
router = APIRouter(prefix="/v107", tags=["v107"])
ORCH = os.environ.get("CODEX_ORCH_URL", "http://localhost:8010")


def _j(url, method="GET", data=None):
    req = urllib.request.Request(url, data=(json.dumps(data).encode() if data is not None else None),
                                 headers={"Content-Type": "application/json", "Accept": "application/json"},
                                 method=method)
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


@router.get("/tenants")
def tenants():
    return _j(f"{ORCH}/tenants")


@router.post("/compile")
def compile(body: dict):
    return _j(f"{ORCH}/workflows/compile", "POST", body)


@router.post("/runs")
def runs(body: dict):
    return _j(f"{ORCH}/runs", "POST", body)
