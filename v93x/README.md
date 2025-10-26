# Codex Immortal × Dominion Nexus — v93.x · Constellation

Refines v93 with:
- **/nous endpoint** — natural-language → glyph DAG translation
- **Optional OIDC/JWKS** — token auth in addition to API key
- **Rekor API client** — with offline fallback for transparency logging
- **Telemetry agent** — monitoring and integrity verification
- **Nightly verification workflow** — automated continuous verification
- **CI/Release** — wired to emit SBOM, provenance, transparency logs

## Authorship Anchor

```
subject: caleb fedor byker konev|1998-10-27
subject_id_sha256: 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
license: MIT + EUCLEA transparency clause
```

## Features

### 1. Natural Language Processing (/nous endpoint)
Transform natural language prompts into executable glyph sequences:
```bash
curl -X POST -H "Content-Type: application/json" -H "x-api-key: dev-key" \
  -d '{"prompt":"verify then invoke then deploy","dry_run":true}' \
  http://localhost:8000/nous
```

### 2. Authentication
- **API Key**: Traditional header-based authentication (`x-api-key`)
- **OIDC/JWKS**: Optional Bearer token authentication via environment variables:
  - `OIDC_JWKS_URL` - JWKS endpoint URL
  - `OIDC_ISSUER` - Expected token issuer
  - `OIDC_AUDIENCE` - Expected token audience

### 3. Transparency & Integrity
- **Hash Manifests**: SHA-256 hashes of all files for integrity verification
- **SBOM**: SPDX-format Software Bill of Materials
- **Provenance**: SLSA provenance attestations
- **Rekor Integration**: Optional submission to Sigstore Rekor transparency log

### 4. Telemetry & Monitoring
Built-in telemetry agent tracks:
- Audit event count and chain integrity
- Manifest file count and version
- SBOM and provenance presence
- Critical file integrity checks

## Quickstart

### Local Development
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Test Endpoints
```bash
# Health check
curl -H "x-api-key: dev-key" http://localhost:8000/health

# Authorship seal
curl -H "x-api-key: dev-key" http://localhost:8000/seal

# Natural language processing (dry-run)
curl -X POST -H "Content-Type: application/json" -H "x-api-key: dev-key" \
  -d '{"prompt":"verify then invoke then deploy","dry_run":true}' \
  http://localhost:8000/nous

# Direct glyph execution (dry-run)
curl -X POST -H "Content-Type: application/json" -H "x-api-key: dev-key" \
  -d '{"glyph":"🌀","dry_run":true}' \
  http://localhost:8000/glyph
```

## Scripts

### Core Scripts
- **hash_all.py** - Generate comprehensive SHA-256 manifest
- **verify_manifest.py** - Verify file integrity against manifest
- **sbom_stub.py** - Generate SPDX-format SBOM
- **rekor_submit.py** - Generate provenance and submit to Rekor
- **telemetry_agent.py** - Collect metrics and verify integrity

### Usage Examples
```bash
# Generate manifest
python3 scripts/hash_all.py

# Verify integrity
python3 scripts/verify_manifest.py

# Generate SBOM
python3 scripts/sbom_stub.py

# Generate provenance
python3 scripts/rekor_submit.py

# Run telemetry
python3 scripts/telemetry_agent.py
```

## Glyph System

The v93.x bundle uses a symbolic glyph language for operations:

| Glyph | Action | Description |
|-------|--------|-------------|
| 🌀 | verify | Verify integrity and authenticity |
| 🌞 | invoke | Build and invoke operations |
| 🌈 | deploy | Deploy and release operations |
| 🧾 | audit | Generate SBOM and audit logs |
| 🔮 | attest | Generate provenance and attestation |

## CI/CD Workflows

### Build & Test (v93x-ci.yml)
Runs on every push and PR to v93x directory:
- Installs dependencies
- Generates manifest, SBOM, and provenance
- Tests all endpoints
- Uploads artifacts

### Nightly Verification (v93x-nightly.yml)
Runs daily at 2 AM UTC:
- Regenerates manifest
- Verifies integrity
- Checks for drift
- Collects telemetry
- Archives results

### Release (v93x-release.yml)
Triggers on version tags (v93.*):
- Generates release bundle
- Creates GitHub release with artifacts
- Builds and pushes Docker image to GHCR

## Docker Deployment

### Build Image
```bash
docker build -t codex-v93x:latest .
```

### Run Container
```bash
docker run -d -p 8000:8000 \
  -e CODEX_API_KEY=your-secure-key \
  -e OIDC_JWKS_URL=https://your-oidc-provider/.well-known/jwks.json \
  codex-v93x:latest
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| CODEX_API_KEY | No | dev-key | API key for authentication |
| OIDC_JWKS_URL | No | - | OIDC JWKS endpoint for token validation |
| OIDC_ISSUER | No | - | Expected OIDC token issuer |
| OIDC_AUDIENCE | No | - | Expected OIDC token audience |
| REKOR_URL | No | https://rekor.sigstore.dev | Rekor transparency log URL |

## Architecture

```
v93x/
├── app.py                      # FastAPI application
├── Dockerfile                  # Container image definition
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── codex/                      # Generated artifacts
│   ├── glyphs/                 # Glyph-to-action mappings
│   ├── manifest.v93x.json      # File integrity manifest
│   ├── sbom.spdx.json          # Software Bill of Materials
│   ├── provenance.json         # SLSA provenance
│   └── telemetry.json          # Telemetry data
├── plugins/                    # Plugin system
│   └── manifest.json           # Action definitions
├── scripts/                    # Utility scripts
│   ├── hash_all.py
│   ├── verify_manifest.py
│   ├── sbom_stub.py
│   ├── rekor_submit.py
│   └── telemetry_agent.py
└── tools/                      # Core tools
    └── glyph_guard_v13.py      # Glyph execution engine
```

## Security

- All API endpoints require authentication (API key or OIDC token)
- File integrity verified via SHA-256 manifests
- Glyph execution runs with resource limits (CPU, memory)
- Dangerous glyphs (💣, 🧨) are explicitly denied
- All operations logged to audit chain with hash linking
- SBOM and provenance enable supply chain security

## License

MIT + EUCLEA transparency clause

---

**Build Status**: [![v93x CI](../../actions/workflows/v93x-ci.yml/badge.svg)](../../actions/workflows/v93x-ci.yml)

**Subject Anchor**: 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
