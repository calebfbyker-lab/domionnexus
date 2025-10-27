from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import time
from services.nexus.migrations import migrate
from services.nexus.ratelimit import allow as rl_allow
from services.nexus.rbac_v2 import check as tok_check, allow_ip
from services.nexus.slo import liveness, readiness, budget, record_latency

def patch(app: FastAPI):
    migrate()

    @app.get("/health/live")
    def live(): return liveness()

    @app.get("/health/ready")
    def ready(): return readiness()

    @app.middleware("http")
    async def guards(request: Request, call_next):
        t0=time.time()
        # IP allowlist
        client_ip = request.client.host if request.client else "0.0.0.0"
        if not allow_ip(client_ip):
            raise HTTPException(403,"ip_forbidden")
        # rate limiting (by token or ip)
        tok = request.headers.get("X-Auth","") or client_ip
        if not rl_allow(tok):
            raise HTTPException(429,"rate_limited")
        # optional scope check for write endpoints
        path=request.url.path
        if path.endswith("/ingest_signed") and not tok_check(request.headers.get("X-Auth",""), "ingest"):
            raise HTTPException(403,"forbidden")
        resp = await call_next(request)
        record_latency((time.time()-t0)*1000.0)
        return resp

    @app.get("/slo/budget")
    def slo_budget(): return JSONResponse(budget())
