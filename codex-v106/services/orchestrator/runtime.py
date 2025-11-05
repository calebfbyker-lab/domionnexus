import time, threading, json, hmac, hashlib, base64, os
from collections import defaultdict
from packages.core.src.codex_core.tenancy import get_quotas

LOCK = threading.Lock()
RUNNING = defaultdict(int)
WINDOW = defaultdict(list)  # tenant -> [timestamps]
WEBHOOK_URL = os.environ.get("CODEX_WEBHOOK_URL", "")
WEBHOOK_KEY = os.environ.get("CODEX_WEBHOOK_KEY", "dev-hmac")


def _now():
    return time.time()


def allow_start(tenant: str) -> bool:
    q = get_quotas(tenant)
    with LOCK:
        # concurrent cap
        if RUNNING[tenant] >= q.max_concurrent:
            return False
        # per-minute rate
        cutoff = _now() - 60
        WINDOW[tenant] = [t for t in WINDOW[tenant] if t > cutoff]
        if len(WINDOW[tenant]) >= q.per_minute:
            return False
        RUNNING[tenant] += 1
        WINDOW[tenant].append(_now())
        return True


def mark_done(tenant: str):
    with LOCK:
        RUNNING[tenant] = max(0, RUNNING[tenant] - 1)


def sign(b: bytes) -> str:
    mac = hmac.new(WEBHOOK_KEY.encode(), b, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")


def emit_webhook(event: dict):
    if not WEBHOOK_URL:
        return
    try:
        import urllib.request
        body = json.dumps(event, separators=(",", ":")).encode()
        req = urllib.request.Request(WEBHOOK_URL, data=body, headers={
            "Content-Type": "application/json",
            "X-Codex-Signature": sign(body)
        })
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass
