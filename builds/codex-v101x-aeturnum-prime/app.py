from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
import json, os, time, hmac, hashlib, base64, random
from codex.aeturnum.holonous import compile_glyphs
from codex.aeturnum.chronomerkl import ChronoMerkle
from codex.redact import scrub_obj

APP_VER = "Codex Aeturnum v101.x · Prime"
SUBJECT = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = "REPLACE_ME"

TENANTS="tenants/config.json"; FLAGS="config/flags.json"
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET","dev-webhook")

chrono = ChronoMerkle()
app = FastAPI(title=APP_VER)

class GlyphReq(BaseModel):
    glyph: str
    tenant: str | None = None
    channel: str | None = "stable"
    dry_run: bool = True

@app.get("/health")
def health():
    return {"ok":True,"ver":APP_VER,"subject_sha256":SUBJECT_SHA256,"flags":json.load(open(FLAGS))}

@app.get("/seal")
def seal(): return {"subject": SUBJECT, "subject_id_sha256": SUBJECT_SHA256}

@app.get("/flags/reload")
def flags_reload(): return json.load(open(FLAGS))

@app.get("/openapi/signed")
def openapi_signed():
    spec = app.openapi()
    body = json.dumps(spec, separators=(",",":")) .encode()
    key = os.getenv("CODEX_HMAC_KEY","dev-hmac").encode()
    sig = base64.urlsafe_b64encode(hmac.new(key, body, hashlib.sha256).digest()).decode().rstrip("=")
    return {"sig": sig, "spec": spec}

@app.post("/holonous/compile")
def holonous_compile(req: GlyphReq):
    res=compile_glyphs(req.glyph)
    if not res["ok"]:
        raise HTTPException(400, res)
    chrono.add({"event":"compile","steps":res["steps"],"dry_run":req.dry_run,"tenant":req.tenant,"channel":req.channel})
    return {"ok":True,"steps":res["steps"],"explain":res["explain"],"chrono_root":chrono.head()}

@app.get("/aeturnum/ledger")
def aeturnum_ledger():
    lines=open("codex/aeturnum/ledger.jsonl").read().strip().splitlines()
    return {"entries": len(lines), "head_preview": lines[-1] if lines else None}

@app.get("/aeturnum/query")
def aeturnum_query(q: str = ""):
    lines=open("codex/aeturnum/ledger.jsonl").read().strip().splitlines()
    hits=[ln for ln in lines if q in ln][:50]
    return {"q":q,"count":len(hits),"hits":hits}

@app.post("/webhook/github")
async def webhook_github(request: Request):
    sig = request.headers.get("X-Hub-Signature-256",
    "")
    body = await request.body()
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    expect = "sha256="+mac
    if not hmac.compare_digest(expect, sig):
        raise HTTPException(401, {"error":"bad webhook signature"})
    payload = await request.json()
    return {"ok":True,"redacted": scrub_obj(payload)}
