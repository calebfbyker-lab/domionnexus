from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict
import asyncio, time, json

from neuro.sim import eeg_synth, eeg_multichannel
from neuro.signal import psd, bandpower, zscore
from telemetry.privacy import scrub

APP_VER = "Codex Aeturnum v102.x · Neurocybernetics Prime"
SUBJECT = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = "0f9d6b0c0e9f07e6a4cd3f8cc7e5c8a8f1e3b3f6f4b5a6c7d8e9f0a1b2c3d4e5"

app = FastAPI(title=APP_VER)

# Models
class AnalyzeReq(BaseModel):
    fs: float
    channel: str = "Cz"
    samples: List[float] = Field(..., min_items=8)

class MultiReq(BaseModel):
    n: int = 8
    fs: float = 256.0
    seconds: float = 2.0
    alpha: float = 10.0
    beta: float = 20.0
    gamma: float = 40.0
    noise: float = 0.3

class TopoReq(BaseModel):
    fs: float
    channels: Dict[str, List[float]]  # name -> samples

class TeleBatch(BaseModel):
    items: List[Dict]

class AutoTuneReq(BaseModel):
    Ku: float  # ultimate gain (oscillation)
    Tu: float  # oscillation period (s)

# Endpoints
@app.get("/")
def index():
    try:
        html = open("static/index.html", "r", encoding="utf-8").read()
    except Exception:
        return HTMLResponse("<html><body><h1>Dashboard not found</h1></body></html>")
    return HTMLResponse(html)

@app.get("/health")
def health():
    return {"ok": True, "ver": APP_VER, "subject_sha256": SUBJECT_SHA256}

@app.get("/seal")
def seal():
    return {"subject": SUBJECT, "subject_id_sha256": SUBJECT_SHA256}

@app.get("/neuro/stream")
def neuro_stream(seconds: float = 2.0, fs: float = 256.0, alpha: float = 10.0, beta: float = 20.0, gamma: float = 40.0, noise: float = 0.3, blink: bool = False):
    t, x = eeg_synth(fs=fs, seconds=seconds, alpha=alpha, beta=beta, gamma=gamma, noise=noise, blink=blink)
    return {"ts": time.time(), "fs": fs, "channel": "Cz", "samples": x, "note": "synthetic EEG-like"}

@app.websocket("/ws/stream")
async def ws_stream(ws: WebSocket, fs: float = 256.0, alpha: float = 10.0, beta: float = 20.0, gamma: float = 40.0, noise: float = 0.3):
    await ws.accept()
    try:
        while True:
            _, x = eeg_synth(fs=fs, seconds=1.0, alpha=alpha, beta=beta, gamma=gamma, noise=noise, blink=False)
            await ws.send_json({"ts": time.time(), "fs": fs, "samples": x})
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return

@app.post("/neuro/analyze")
def neuro_analyze(req: AnalyzeReq):
    f, P = psd(req.samples, req.fs)
    feat = {
        "alpha": bandpower(f, P, 8, 12),
        "beta": bandpower(f, P, 13, 30),
        "gamma": bandpower(f, P, 31, 48)
    }
    z = zscore(req.samples)
    return {"features": feat, "zmean": float(sum(z) / len(z))}

@app.post("/neuro/multi")
def neuro_multi(req: MultiReq):
    return eeg_multichannel(n=req.n, fs=req.fs, seconds=req.seconds, alpha=req.alpha, beta=req.beta, gamma=req.gamma, noise=req.noise)

@app.post("/neuro/topomap")
def neuro_topomap(req: TopoReq):
    ch_names = sorted(req.channels.keys())
    grid = [[0.0] * 3 for _ in range(3)]
    idx = 0
    for r in range(3):
        for c in range(3):
            if idx < len(ch_names):
                s = req.channels[ch_names[idx]]
                f, P = psd(s, req.fs)
                grid[r][c] = bandpower(f, P, 8, 12)
            idx += 1
    return {"grid": grid, "note": "toy 3x3 topomap of alpha bandpower"}

@app.post("/telemetry/batch")
def telemetry_batch(batch: TeleBatch):
    safe = [scrub(x) for x in batch.items]
    size = sum(len(json.dumps(x, separators=(",", ":"))) for x in safe)
    return {"ok": True, "count": len(safe), "size": size}

@app.post("/cyber/autotune")
def cyber_autotune(r: AutoTuneReq):
    # Ziegler–Nichols classic tuning rules
    Ku, Tu = r.Ku, r.Tu
    kp = 0.6 * Ku
    ki = 1.2 * Ku / Tu
    kd = 0.075 * Ku * Tu
    return {"kp": kp, "ki": ki, "kd": kd}
