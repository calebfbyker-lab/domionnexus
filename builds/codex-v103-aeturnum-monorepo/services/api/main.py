from fastapi import FastAPI
from pydantic import BaseModel
import time, json, hashlib, sys, os

# Add monorepo packages to path
sys.path.append(os.path.join(os.path.dirname(__file__), "packages/core/src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "packages/neuro/src"))

from codex_core import demo_state, ChronoMerkle, compile_glyphs
from codex_neuro import psd, bandpower, zscore, eeg_synth

APP_VER = "Codex Aeturnum v103 · Monorepo Prime"
SUBJECT = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = "0f9d6b0c0e9f07e6a4cd3f8cc7e5c8a8f1e3b3f6f4b5a6c7d8e9f0a1b2c3d4e5"

app = FastAPI(title=APP_VER)
chrono = ChronoMerkle()

# Optional integrations (OpenAI, Supabase). If env vars are missing, endpoints return safe mocks.
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_openai = None
_supabase = None
if OPENAI_KEY:
    try:
        import openai
        openai.api_key = OPENAI_KEY
        _openai = openai
    except Exception:
        _openai = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        _supabase = None

class AnalyzeReq(BaseModel):
    fs: float
    samples: list[float]


class ChatReq(BaseModel):
    messages: list


class DBInsertReq(BaseModel):
    table: str
    payload: dict

@app.get("/health")
def health():
    return {"ok": True, "ver": APP_VER, "subject_sha256": SUBJECT_SHA256}

@app.get("/v101/helix")
def v101_helix(): return demo_state()

@app.post("/v101/glyphs")
def v101_glyphs(body: dict):
    g = body.get("glyph","")
    res = compile_glyphs(g)
    if res.get("ok"): chrono.add({"event":"glyphs","steps":res["steps"]})
    return res | {"chrono_root": chrono.head()}

@app.get("/v102/stream")
def v102_stream(seconds: float = 2.0, fs: float = 256.0, alpha: float = 10.0, beta: float = 20.0, gamma: float = 40.0, noise: float = 0.3, blink: bool = False):
    t,x = eeg_synth(fs=fs, seconds=seconds, alpha=alpha, beta=beta, gamma=gamma, noise=noise, blink=blink)
    return {"ts": time.time(), "fs": fs, "channel":"Cz", "samples": x, "note":"synthetic EEG-like"}

@app.post("/v102/analyze")
def v102_analyze(req: AnalyzeReq):
    f,P = psd(req.samples, req.fs)
    feat = {
        "alpha": bandpower(f,P,8,12),
        "beta": bandpower(f,P,13,30),
        "gamma": bandpower(f,P,31,48)
    }
    z = sum(zscore(req.samples))/max(1,len(req.samples))
    return {"features": feat, "zmean": float(z)}


@app.post("/v103/ai/chat")
def v103_ai_chat(req: ChatReq):
    """Call OpenAI Chat API if configured; otherwise return a safe echo mock."""
    if _openai is None:
        # echo back a deterministic mock
        summary = "|".join((m.get('content','')[:120] for m in req.messages))
        return {"mock": True, "response": f"ECHO: {summary}"}
    # minimal call using ChatCompletion (best-effort; requires keys and network in runtime)
    try:
        resp = _openai.ChatCompletion.create(model="gpt-4o-mini", messages=req.messages, max_tokens=256)
        return {"mock": False, "openai": resp}
    except Exception as e:
        return {"error": "openai call failed", "detail": str(e)}


@app.post("/v103/db/insert")
def v103_db_insert(req: DBInsertReq):
    """Insert a row into Supabase table if configured; otherwise return a safe stub ack."""
    if _supabase is None:
        return {"mock": True, "table": req.table, "payload": req.payload, "status": "skipped (SUPABASE not configured)"}
    try:
        res = _supabase.table(req.table).insert(req.payload).execute()
        return {"mock": False, "result": res}
    except Exception as e:
        return {"error": "supabase operation failed", "detail": str(e)}
