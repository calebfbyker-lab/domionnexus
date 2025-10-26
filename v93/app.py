from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import subprocess, sys, json, hashlib, os, time, threading

APP_VER = "Codex v93 · Celestial Verity"
IDENT_STR = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA256 = """2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a"""
CODEX_API_KEY = os.getenv("CODEX_API_KEY","dev-key")

AUDIT = "audit.jsonl"
_a_lock = threading.Lock()
_last = "0"*64

def _audit(ev):
    global _last
    ev["ts"] = time.time()
    body = json.dumps(ev, separators=(",",":"))
    import hashlib
    d = hashlib.sha256(body.encode()).hexdigest()
    root = hashlib.sha256((_last + d).encode()).hexdigest()
    _last = root
    with _a_lock, open(AUDIT,"a",encoding="utf-8") as f:
        f.write(json.dumps({**ev,"sha256":d,"root":root})+"\n")

def _auth(perm:str):
    def dep(x_api_key: str = Header(default="")):
        if x_api_key != CODEX_API_KEY:
            raise HTTPException(401,"invalid api key")
        return True
    return dep

class GlyphReq(BaseModel):
    glyph: str
    dry_run: bool = False

app = FastAPI(title=APP_VER)

@app.get("/health")
def health(): return {"ok":True,"ver":APP_VER}

@app.get("/seal")
def seal(): return {"subject": IDENT_STR, "subject_id_sha256": SUBJECT_SHA256}

@app.post("/glyph", dependencies=[Depends(_auth("glyph.run"))])
def glyph(req: GlyphReq):
    cmd=[sys.executable, "tools/glyph_guard_v13.py", "--glyph", req.glyph]
    if req.dry_run: cmd.append("--dry-run")
    p = subprocess.run(cmd, capture_output=True, text=True)
    _audit({"route":"glyph","rc":p.returncode})
    if p.returncode!=0:
        raise HTTPException(400,{"stderr":p.stderr,"stdout":p.stdout})
    return {"ok":True,"stdout":p.stdout}
