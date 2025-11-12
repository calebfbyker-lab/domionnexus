# Codex Aeturnum — v102.x · Neurocybernetics Prime

Production polish on v102 with **live WebSocket streaming**, **multichannel EEG synth**, **topomap demo**,
**telemetry batching**, **adaptive PID autotune**, **metrics**, and a tiny **browser dashboard**.

Authorship anchor
subject: caleb fedor byker konev|1998-10-27
subject_id_sha256: 0f9d6b0c0e9f07e6a4cd3f8cc7e5c8a8f1e3b3f6f4b5a6c7d8e9f0a1b2c3d4e5
license: MIT + EUCLEA transparency clause

### Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# open dashboard
# http://localhost:8000
```

What's inside
- FastAPI app with websocket stream `/ws/stream`
- Multichannel EEG mock `/neuro/multi`
- Topomap demo `/neuro/topomap`
- Telemetry batch endpoint `/telemetry/batch` (PII scrub)
- PID autotune `/cyber/autotune`
- Tiny browser dashboard at `/` (static/index.html)

Grounding & guardrails: educational/demo code, not medical or predictive claims. Telemetry scrub removes emails, IP-like strings, and token-looking substrings.