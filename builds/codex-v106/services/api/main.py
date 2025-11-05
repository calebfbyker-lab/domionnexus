from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

APP_VER = "Codex Aeturnum v106 · API Gateway"
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8010")

app = FastAPI(title=APP_VER)

class SubmitRequest(BaseModel):
    glyph: str
    tenant: str = "public"

class StatusResponse(BaseModel):
    run_id: str
    status: str
    message: str = ""

@app.get("/")
def root():
    """Root endpoint - health check."""
    return {
        "ok": True,
        "service": APP_VER,
        "orchestrator": ORCHESTRATOR_URL
    }

@app.post("/submit")
async def submit_workflow(req: SubmitRequest):
    """
    Submit a workflow for execution.
    
    Request body:
        {"glyph": "🌀🌞🧾", "tenant": "public"}
    
    Returns:
        {"run_id": "uuid", "dag_digest": "sha256...", "state": "queued"}
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ORCHESTRATOR_URL}/runs",
                json={"glyph": req.glyph, "tenant": req.tenant},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Orchestrator error: {str(e)}")

@app.get("/status/{run_id}")
async def get_status(run_id: str):
    """
    Get the status of a workflow run.
    
    Note: In v106, this is a placeholder. Full status tracking would require
    persistent storage in the orchestrator.
    """
    return StatusResponse(
        run_id=run_id,
        status="unknown",
        message="Status tracking requires persistent storage - check orchestrator /events/stream"
    )

@app.get("/healthz")
def healthz():
    """Health check endpoint."""
    return {"ok": True, "ver": APP_VER}
