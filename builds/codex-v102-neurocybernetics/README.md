# Codex Aeturnum — v102 · Neurocybernetics

**Focus:** cybernetics + neural sciences + telemetry — rigorous, auditable research scaffolding.
- Nonverbal interfaces (BCI) treated scientifically (no supernatural claims).
- Streaming telemetry pipeline with explicit consent & privacy by design.
- Decoder stubs, datasets, and evaluation harnesses.
- Integrates with v101/v100 glyph choreography (verify→invoke→audit→…→continuum).

Authorship anchor
subject: caleb fedor byker konev|1998-10-27
subject_id_sha256: REPLACE_ME
license: MIT + EUCLEA transparency clause

## Modules
- `neuro/` — BCI signal models, decoders, evaluation.
- `telemetry/` — ingest, schema, consent ledger, PII redaction.
- `policy/` — neuro-ethics & safety rules.
- `datasets/` — small synthetic EEG CSV for demos.
- `app.py` — FastAPI endpoints: ingest, stream, decode (stub), consent ops.
- `docs/` — scientific framing and safety checklist.

Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# grant telemetry scope for your subject (demo uses author id)
curl -s -X POST "http://localhost:8000/consent/grant?scope=telemetry" | jq

# send telemetry (synthetic)
curl -s -H "content-type: application/json" \
  -d '{"subject_id_sha256":"REPLACE_ME","ts":123.45,"eeg":[0.1,0.2,0.05]}' \
  http://localhost:8000/telemetry/ingest | jq

# run decoder stub on synthetic batch
curl -s -H "content-type: application/json" \
  -d '{"batch_path":"datasets/synthetic_eeg_small.csv"}' \
  http://localhost:8000/neuro/decode | jq
```
