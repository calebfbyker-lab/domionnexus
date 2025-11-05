import os, json
try:
  import yaml  # optional
except Exception:
  yaml=None
DEFAULTS={"HMAC_KEY":"dev-hmac","TOKEN_KEY":"dev-key","ORCH_URL":"http://localhost:8010"}
def load(path:str|None=None)->dict:
  cfg={}
  if path and yaml:
    try: cfg=yaml.safe_load(open(path)) or {}
    except Exception: cfg={}
  # env overrides
  for k,v in DEFAULTS.items():
    cfg[k]=os.environ.get(f"CODEX_{k}", cfg.get(k, v))
  return cfg
