from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os, json
from services.common.config import load
from .mw_hmac import sign
APP_VER="Codex Aeturnum Ω · Gateway"
cfg=load(os.path.join(os.path.dirname(__file__),"config","flags.yaml"))
app=FastAPI(title=APP_VER)
def _mount():
  import pkgutil, importlib, os
  pkg_path=os.path.join(os.path.dirname(__file__),"plugins")
  for _,m,_ in pkgutil.iter_modules([pkg_path]):
    if m.endswith("_router"): app.include_router(getattr(importlib.import_module("services.api.plugins."+m),"router"))
_mount()
@app.get("/")
def index():
  ann = (cfg.get("announce_versions") or ["v101","v102","v107","v113"])
  return HTMLResponse(f"<h1>{APP_VER}</h1><p>Versions: {', '.join(ann)}</p>")
@app.get("/openapi/signed")
def openapi_signed():
  spec = app.openapi()
  return {"sig": sign(spec, cfg.get("HMAC_KEY","dev-hmac")), "spec": spec}
