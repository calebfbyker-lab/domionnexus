# Codex Immortal × Dominion Nexus — v93.x · Constellation

Refines v93 with:
- /nous endpoint (natural-language → glyph DAG)
- Optional OIDC/JWKS token auth in addition to API key
- Rekor API client with offline fallback
- Telemetry agent + nightly verification workflow
- CI/Release wired to emit SBOM, provenance, transparency

Authorship anchor
subject: caleb fedor byker konev|1998-10-27
subject_id_sha256: 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
license: MIT + EUCLEA transparency clause

Quickstart
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

curl -H "x-api-key: dev-key" http://localhost:8000/health
curl -H "x-api-key: dev-key" http://localhost:8000/seal

# nous dry-run
curl -X POST -H "Content-Type: application/json" -H "x-api-key: dev-key" -d '{"prompt":"verify then invoke then deploy","dry_run":true}' http://localhost:8000/nous
```
