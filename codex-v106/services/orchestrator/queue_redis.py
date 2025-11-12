import json, os
from typing import Optional
from redis import Redis

REDIS_URL = os.environ.get("CODEX_REDIS_URL", "redis://localhost:6379/0")
STREAM = os.environ.get("CODEX_REDIS_STREAM", "codex:v107:runs")


def client() -> Optional[Redis]:
    try:
        return Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        return None


def enqueue(item):
    r = client()
    if r is None:
        raise RuntimeError("Redis unavailable")
    r.xadd(STREAM, {"job": json.dumps(item, separators=(",", ":"))})


def drain(block_ms=2000):
    r = client()
    if r is None:
        return None
    # read from stream, simple consumer that reads newest
    msgs = r.xread({STREAM: "0-0"}, block=block_ms, count=1)
    if not msgs:
        return None
    _, entries = msgs[0]
    _id, fields = entries[0]
    # best-effort delete
    try:
        r.xdel(STREAM, _id)
    except Exception:
        pass
    return json.loads(fields["job"])
