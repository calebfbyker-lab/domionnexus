# Architecture — domionnexus (scaffold)

Generated: 2025-10-26

Scope
- Target platform: Netlify (primary), Kubernetes (Helm chart) for production deploys, and local `netlify dev` / Docker for developer testing.

Components
- Frontend: static site under `public/` served by Netlify.
- Serverless APIs: `netlify/functions/*` (JS/Node) for verification, ledger, and universal artifact access.
- Engines: runtime workers (examples under `engines/`). The scaffold includes `python-engine` (FastAPI) as a runtime engine that exposes HTTP endpoints and uses an API-key guard.
- Nous/orchestrator: lightweight agent pattern (not yet added) that can call the engine endpoints and the serverless APIs.
- Integrations: Supabase/Postgres (ledger), Redis (cache), OpenAI connector (oracle). These are represented in manifests as environment variables and secret references.

Auth & Secrets
- Service-to-service auth uses an API key (`CODEX_API_KEY`) injected from Kubernetes secrets or GitHub Actions secrets.
- CI/CD pipeline signs artifacts and records transparency entries (stubbed in CI). The repo should add these secrets in GitHub → Settings → Secrets and variables → Actions.

Deploy Targets & Flow
1. Continuous Integration (GH Actions `ci.yml`) builds an artifact, creates an SBOM/lineage/spdx stub, signs a manifest, and pushes an image to GHCR.
2. Continuous Deployment (GH Actions `deploy.yml`) decodes `KUBE_CONFIG`, creates a `codex-secrets` secret with `CODEX_API_KEY`, and installs the Helm chart under namespace `codex`.
3. The Helm chart templates mount environment variables from the `codex-secrets` secret and exposes container port 8000.

Developer workflows
- Local run (engine):
  - cd engines/python-engine
  - python -m pip install -r requirements.txt
  - uvicorn app:app --reload --port 8000
- Build image locally (for testing):
  - docker build -t codex-local:latest engines/python-engine
  - docker run -e CODEX_API_KEY=dev-key -p 8000:8000 codex-local:latest

Notes & Next steps
- Add the `nous/` orchestrator service and `netlify/functions/` serverless implementations.
- Add observability (OpenTelemetry) and a production-grade SBOM generator.
- Replace CI placeholder scripts with real implementations for manifest hashing, verification, and Rekor submission.
