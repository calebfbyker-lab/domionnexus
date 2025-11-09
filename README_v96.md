# Codex v96 · Aletheia — Dominion Nexus

## Overview

Codex v96 "Aletheia" (Truth) is a production-ready deployment bundle featuring:

- **Merkle Audit Tree**: Cryptographically verifiable audit trail for all glyph executions
- **Deterministic Build Environment**: Reproducible builds with manifest verification
- **Keyless Signing**: Threshold signatures with 2-of-3 quorum verification
- **Policy VM**: Hot-reloadable glyph policies with nonce-based replay protection
- **Enclave Attestation**: Supply chain verification with SBOM, vulnerability scanning, and provenance
- **TSG/TGS/XTGS Glyphs**: Symbolic control language for orchestration

## Architecture

### Core Components

1. **FastAPI Application** (`app.py`)
   - Health endpoint with audit metrics
   - Glyph execution with policy enforcement
   - HMAC request signing support
   - Merkle tree-based audit trail

2. **Glyph Guard v18** (`tools/glyph_guard_v18.py`)
   - Nonce-based replay protection
   - Sanctify requirement for deploy actions
   - Hot-reloadable policy from `policy/glyph.yaml`
   - Action validation against manifest

3. **Supply Chain Scripts**
   - `scripts/hash_all.py`: Generate integrity manifest
   - `scripts/verify_manifest.py`: Verify file integrity
   - `scripts/sbom_syft_stub.py`: Generate SBOM
   - `scripts/vuln_gate.py`: Vulnerability threshold gate
   - `scripts/provenance_v4.py`: SLSA provenance generation
   - `scripts/threshold_sign.py`: Generate threshold signatures
   - `scripts/quorum_verify.py`: 2-of-3 quorum verification
   - `scripts/rekor_api.py`: Transparency log integration

### Configuration Files

- `codex/identity.json`: Subject identity binding
- `codex/LICENSE.spdx.json`: SPDX license manifest
- `codex/quorum.json`: Quorum configuration (n=3, k=2)
- `policy/glyph.yaml`: Glyph execution policy
- `policy/runtime.json`: Runtime policy (nonce, versioning)
- `plugins/manifest.json`: Action definitions

### Glyph Actions

| Glyph | Action | Description |
|-------|--------|-------------|
| 🌞 | invoke | Generate integrity manifest |
| 🌀 | verify | Verify manifest integrity |
| 🌈 | deploy | Create deployment archive |
| 🧾 | audit | Generate SBOM |
| 🔮 | attest | Generate provenance |
| 🛡 | scan | Vulnerability scanning |
| 🛡‍🔥 | sanctify | Quorum verification (required before deploy) |

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --host 0.0.0.0 --port 8000

# Test health endpoint
curl http://localhost:8000/health
```

### Docker Deployment

```bash
# Build image
docker build -t codex-v96 .

# Run container
docker run -p 8000:8000 \
  -e CODEX_API_KEY=your-api-key \
  -e CODEX_HMAC_KEY=your-hmac-key \
  codex-v96
```

### Environment Variables

- `CODEX_API_KEY`: API key for authentication (default: "dev-key")
- `CODEX_HMAC_KEY`: HMAC key for request signing (default: "dev-hmac")
- `GITHUB_WEBHOOK_SECRET`: Webhook secret for GitHub integration (default: "dev-webhook")

## API Usage

### Execute Glyph

```bash
curl -X POST http://localhost:8000/glyph \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: dev-key" \
  -d '{
    "glyph": "🌞",
    "dry_run": true,
    "nonce": "unique-nonce-value",
    "version": "1.0"
  }'
```

### Get Audit Root

```bash
curl http://localhost:8000/audit/root
```

### Get Audit Proof

```bash
curl 'http://localhost:8000/audit/proof?index=0'
```

## Security Features

### Nonce-Based Replay Protection

Each glyph execution requires a unique nonce. Reused nonces are rejected to prevent replay attacks.

### Deploy Sanctification

Deploy actions require prior sanctify action, which performs 2-of-3 quorum signature verification.

### Merkle Audit Trail

All glyph executions are recorded in a Merkle tree, providing:
- Tamper-evident audit log
- Cryptographic inclusion proofs
- Verifiable audit history

### Policy Enforcement

Glyph policies define:
- Maximum steps per execution
- Denied emojis and patterns
- Action dependencies (e.g., deploy requires sanctify)

## CI/CD Integration

### GitHub Actions

The repository includes two workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`)
   - Runs on push/PR
   - Validates manifest integrity
   - Generates SBOM and provenance
   - Performs vulnerability scanning
   - Verifies quorum signatures

2. **Release Workflow** (`.github/workflows/release.yml`)
   - Runs on version tags (v96*)
   - Builds and pushes Docker image
   - Publishes release artifacts
   - Records in transparency log

## Supply Chain Verification

### Integrity Manifest

```bash
# Generate manifest
python scripts/hash_all.py --root . --out codex/manifest.v96.json

# Verify manifest
python scripts/verify_manifest.py --root . --manifest codex/manifest.v96.json
```

### Threshold Signatures

```bash
# Generate 3 signatures
python scripts/threshold_sign.py

# Verify 2-of-3 quorum
python scripts/quorum_verify.py
```

### Provenance

```bash
# Generate SLSA provenance
python scripts/provenance_v4.py
```

## License

MIT License + EUCLEA Transparency Clause

Subject: caleb fedor byker konev|1998-10-27
Subject SHA256: `__SUBJECT_SHA__`

## Version History

- **v96 (Aletheia)**: Current - Enhanced security, quorum verification, Merkle audit
- **v95 (Aegis Mesh)**: Threshold signing, policy VM
- **v94 (Sentinel Prime)**: HMAC signing, rate limiting, JWKS

## Support

For issues and contributions, please use the GitHub repository.
