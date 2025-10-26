# Codex Aeturnum — v106

**Orchestrator + API Gateway · Symbolic Workflow System**

This bundle provides a complete orchestration platform that compiles symbolic glyphs into deterministic workflows (DAGs), executes them via pluggable plugins, and exposes both orchestrator and API gateway services.

## Overview

Codex Aeturnum v106 integrates:
- **Symbolic Glyph Language**: Map glyphs (🌀,🌞,🧾, etc.) to workflow steps
- **DAG Compiler**: Transform glyphs into directed acyclic graphs
- **Orchestrator Service**: Execute workflows with pluggable tasks
- **API Gateway**: Frontend service for workflow submission and monitoring
- **Receipt Chain**: Cryptographically verifiable execution history

## Quickstart

### Run API Gateway

```bash
cd builds/codex-v106/services/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="$(git rev-parse --show-toplevel)/builds/codex-v106/packages/core/src"
uvicorn main:app --reload --port 8000
```

### Run Orchestrator

```bash
cd builds/codex-v106/services/orchestrator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="$(git rev-parse --show-toplevel)/builds/codex-v106/packages/core/src"
uvicorn app:app --reload --port 8010
```

### Using Makefile

```bash
cd builds/codex-v106
make api      # Start API gateway on :8000
make orch     # Start orchestrator on :8010
```

## API Endpoints

### API Gateway (:8000)
- `GET /` - Health check
- `POST /submit` - Submit workflow (body: `{"glyph":"🌀🌞🧾"}`)
- `GET /status/{run_id}` - Check run status

### Orchestrator (:8010)
- `GET /healthz` - Health check
- `POST /workflows/compile` - Compile glyph to DAG
- `POST /runs` - Execute workflow run
- `GET /events/stream` - SSE stream of execution events

## Glyph Mapping

| Glyph | Step | Purpose |
|-------|------|---------|
| 🌀 | verify | Verify inputs and prerequisites |
| 🌞 | invoke | Invoke the primary operation |
| 🧾 | audit | Generate audit trail |
| 🛡 | scan | Security scan |
| 🔮 | attest | Create attestation |
| 🛡‍🔥 | sanctify | Policy compliance check |
| 🚦 | rollout | Progressive rollout |
| ⚖️ | judge | Decision gate |
| 🌈 | deploy | Deploy to target |
| ♾ | continuum | Close and finalize |

## Architecture

```
codex-v106/
├── packages/core/src/codex_core/
│   ├── holonous.py       # Glyph-to-step compiler
│   ├── orch.py           # DAG engine, Run/Task/Receipt types
│   └── compile_dag.py    # Glyph→DAG conversion
├── services/
│   ├── api/              # API Gateway
│   │   ├── main.py
│   │   └── requirements.txt
│   └── orchestrator/     # Workflow Orchestrator
│       ├── app.py
│       ├── worker.py
│       ├── job_queue.py
│       ├── plugins.py
│       └── requirements.txt
└── Makefile
```

## Authorship

**Subject**: caleb fedor byker konev|1998-10-27  
**Subject ID (SHA256)**: 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a

## License

ECCL-1.0 — Eternal Cryptographic Commons License
