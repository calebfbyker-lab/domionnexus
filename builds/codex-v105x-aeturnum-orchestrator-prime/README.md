# Codex Aeturnum — v105 · Orchestrator Prime

This bundle adds a minimal orchestrator service that compiles glyphs into DAGs, enqueues runs, executes steps via pluggable plugins, and emits SSE events and receipts.

Quickstart

```bash
cd builds/codex-v105x-aeturnum-orchestrator-prime/services/orchestrator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="$(git rev-parse --show-toplevel)/builds/codex-v105x-aeturnum-orchestrator-prime/packages/core/src"
uvicorn app:app --reload --port 8010
```

Endpoints
- POST /workflows/compile  (body: {"glyph":"..."})
- POST /runs  (body: {"glyph":"...","tenant":"..."})
- GET  /events/stream  (SSE of step/run events)

Authorship anchor: caleb fedor byker konev|1998-10-27
subject_id_sha256: 