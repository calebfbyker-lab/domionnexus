import os, time, base64, hmac, hashlib
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
KEY=os.environ.get("CODEX_TOKEN_KEY","")
WINDOW=int(os.environ.get("CODEX_TOKEN_WINDOW","300"))
def _ok(token:str, path:str)->bool:
    if not KEY: return True
    try:
        ts, sig = token.split(".",1)
        if abs(time.time()-float(ts))>WINDOW: return False
        mac=hmac.new(KEY.encode(), (ts+path).encode(), hashlib.sha256).digest()
        exp=base64.urlsafe_b64encode(mac).decode().rstrip("=")
        return hmac.compare_digest(sig, exp)
    except Exception: return False
class TokenMaybeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        tok = request.headers.get("X-Codex-Token","")
        if not _ok(tok, request.url.path): return Response("unauthorized", status_code=401)
        return await call_next(request)
