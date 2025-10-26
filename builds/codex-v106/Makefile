.PHONY: help api orch api-install orch-install

help:
	@echo "Codex Aeturnum v106 - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  api           - Run API gateway on port 8000"
	@echo "  orch          - Run orchestrator on port 8010"
	@echo "  api-install   - Install API gateway dependencies"
	@echo "  orch-install  - Install orchestrator dependencies"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Python 3.8+"
	@echo "  - Create virtual environments in services/api and services/orchestrator"
	@echo ""

api-install:
	@echo "Installing API gateway dependencies..."
	cd services/api && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

orch-install:
	@echo "Installing orchestrator dependencies..."
	cd services/orchestrator && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

api:
	@echo "Starting API Gateway on http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	cd services/api && \
	export PYTHONPATH="$$(git rev-parse --show-toplevel)/builds/codex-v106/packages/core/src" && \
	. .venv/bin/activate && \
	uvicorn main:app --reload --port 8000

orch:
	@echo "Starting Orchestrator on http://localhost:8010"
	@echo "Press Ctrl+C to stop"
	cd services/orchestrator && \
	export PYTHONPATH="$$(git rev-parse --show-toplevel)/builds/codex-v106/packages/core/src" && \
	. .venv/bin/activate && \
	uvicorn app:app --reload --port 8010
