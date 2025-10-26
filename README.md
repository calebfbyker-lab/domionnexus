# 🌌 Domion Nexus — Codex v98 "Orthos"

**Integrity with Teeth** — The service refuses to run if the code diverges from its manifest.

> A cryptographically licensed AI orchestration and deployment platform with enhanced security, integrity verification, and progressive deployment capabilities.

**Current Version:** Codex v98 "Orthos"  
**License:** ECCL-1.0 (Eternal Creative Covenant License)

---

## 🎯 What's New in v98 "Orthos"

Codex v98 "Orthos" introduces enterprise-grade security and deployment features:

1. **🔒 Boot-time Self-Check** — Verifies file integrity against manifest before service starts
2. **🔑 HMAC Keyring** — Secure key rotation and management for request signing
3. **📊 Shadow Deploy Metrics** — Progressive deployment with automatic rollback on errors
4. **⚖️ JUDGE Glyph** — Enhanced deployment gating with quality/security/performance checks
5. **🎯 TUF-lite Metadata** — Secure artifact distribution with cryptographic verification
6. **☸️ GitOps Ready** — Complete Kubernetes deployment configuration

**Previous Version:** v97 "Praetorian" — Tenant-aware auth, policy engine, rollout management

---

## ✨ Quick Start

**5-minute setup:**

```bash
# Clone repository
git clone https://github.com/calebfbyker-lab/domionnexus.git
cd domionnexus

# Install dependencies
pip install -r requirements.txt

# Generate integrity manifest
python scripts/hash_all.py

# Run self-check
python selfcheck.py

# Start service
uvicorn app:app --reload --port 8000
```

**Verify it's running:**
```bash
curl http://localhost:8000/health
# Returns: {"ok": true, "ver": "Codex v98 · Orthos", "features": [...]}
```

📖 **[Read the Complete Quickstart Guide →](QUICKSTART.md)**

---

## 🏗️ Architecture

### Core Application
- **FastAPI** web framework with async support
- **Uvicorn** ASGI server for production deployment
- **Python 3.11+** runtime environment

### Security & Integrity (v98)
- **Self-Check Module** (`selfcheck.py`) — Boot-time integrity verification
- **HMAC Keyring** (`keyring.py`) — Cryptographic key management with rotation
- **Glyph Guard v22** (`tools/glyph_guard_v22.py`) — Enhanced deployment policy enforcement

### Deployment & Operations (v98)
- **Shadow Metrics** (`shadow_metrics.py`) — Canary deployment tracking with auto-rollback
- **TUF-lite** (`tuf_lite.py`) — Secure artifact distribution
- **GitOps Plan** (`gitops_plan.py`) — Kubernetes deployment templates

### Existing Features
- **Policy Engine** — Multi-tenant authorization with rule evaluation
- **Glyph System** — Symbolic command language for deployment operations
- **Audit Logging** — JSONL-based audit trail for all operations
- **Rollout Management** — Progressive deployment API

---

## 📁 Project Structure

```
domionnexus/
├── app.py                      # Main FastAPI application (v98)
├── selfcheck.py                # Boot-time integrity verification (NEW v98)
├── keyring.py                  # HMAC key management (NEW v98)
├── shadow_metrics.py           # Canary deployment tracking (NEW v98)
├── tuf_lite.py                 # Secure artifact distribution (NEW v98)
├── gitops_plan.py              # Kubernetes deployment guide (NEW v98)
├── QUICKSTART.md               # Complete quickstart guide (NEW v98)
├── requirements.txt            # Python dependencies
├── tools/
│   ├── glyph_guard_v22.py     # Enhanced glyph guard with JUDGE (NEW v98)
│   └── glyph_guard_v19.py     # Previous version
├── scripts/
│   ├── hash_all.py            # Generate integrity manifest
│   ├── verify_manifest.py     # Verify file integrity
│   ├── provenance_v4.py       # Build provenance generation
│   ├── dsse_hmac_sign.py      # HMAC signature for provenance
│   ├── vuln_gate.py           # Vulnerability checking
│   └── ...
├── policy/
│   ├── glyph.yaml             # Glyph policy configuration
│   └── ...
└── .github/workflows/
    └── ci.yml                 # CI/CD pipeline
```

---

## 🔒 Security Features (v98)

### 1. Boot-time Self-Check
The service **refuses to start** if code diverges from the manifest:

```bash
python selfcheck.py
# [Orthos Self-Check] Verifying integrity...
# [Orthos Self-Check] ✓ Integrity verified
```

If files are modified:
```bash
# [Orthos Self-Check] ❌ INTEGRITY CHECK FAILED
# [Orthos Self-Check] Service will NOT start - code diverged from manifest
#   - MISMATCH: app.py (expected: abc123..., got: def456...)
```

### 2. HMAC Keyring with Rotation
Secure key management with automatic rotation:

```bash
# Check keyring status
curl -H "X-API-Key: dev-key" http://localhost:8000/keyring/status

# Rotate key
curl -X POST -H "X-API-Key: dev-key" http://localhost:8000/keyring/rotate
```

Keys auto-rotate after 30 days. All keys maintained for graceful transition.

### 3. JUDGE Glyph - Deployment Gating
Evaluate deployment readiness before promoting:

```bash
curl -X POST http://localhost:8000/glyph \
  -H "X-API-Key: dev-key" \
  -d '{"glyph": "judge:quality,security,performance"}'
```

Checks:
- **Quality**: Code coverage, lint errors
- **Security**: Vulnerability scan results
- **Performance**: Latency benchmarks

---

## 📊 Progressive Deployment (v98)

### Shadow Deploy with Auto-Rollback

Start canary deployment (5% traffic):
```bash
curl -X POST -H "X-API-Key: dev-key" \
  "http://localhost:8000/rollout/start?percent=5"
```

Monitor metrics:
```bash
curl -H "X-API-Key: dev-key" http://localhost:8000/shadow/metrics
```

**Auto-rollback triggers:**
- Error rate > 5%
- Health check failure rate > 50%

Check and auto-rollback if needed:
```bash
curl -X POST -H "X-API-Key: dev-key" http://localhost:8000/shadow/check
```

---

## 🎯 API Reference

### Core Endpoints
- `GET /health` — Service health and feature flags
- `GET /seal` — Subject identity and cryptographic hash
- `GET /features` — Detailed v98 feature information
- `GET /tenants` — List configured tenants

### Glyph System
- `POST /glyph` — Execute glyph command:
  - `deploy:service@v98` — Deploy with JUDGE gate
  - `judge:quality,security` — Run quality checks
  - `sanctify:v98-orthos` — Create deployment attestation
  - `rollback:previous` — Rollback deployment

### Rollout Management
- `POST /rollout/start?percent=5` — Start canary (5% traffic)
- `POST /rollout/advance?step=10` — Advance rollout (+10%)
- `GET /rollout/status` — Current rollout state

### v98 Security & Operations
- `GET /keyring/status` — HMAC keyring status
- `POST /keyring/rotate` — Rotate HMAC key
- `GET /shadow/metrics` — Canary deployment metrics
- `POST /shadow/check` — Check and auto-rollback if needed

### Policy
- `POST /policy/preview` — Preview policy evaluation

---

## ☸️ Kubernetes Deployment

View complete GitOps plan:
```bash
python gitops_plan.py
```

Includes:
- Deployment with init container for self-check
- Service and Ingress configuration
- Progressive rollout with Flagger
- ArgoCD Application manifest
- Health checks and resource limits
- Secret management

---

## 🛠️ Development

### Running Tests
```bash
# Run CI pipeline
python scripts/determinism_env.py
python scripts/hash_all.py
python scripts/verify_manifest.py
python scripts/sbom_syft_stub.py
python scripts/vuln_gate.py
python scripts/provenance_v4.py
python scripts/dsse_hmac_sign.py
```

### Testing Features

**Self-Check:**
```bash
python selfcheck.py
```

**JUDGE Glyph:**
```bash
python tools/glyph_guard_v22.py --glyph "judge:quality,security" --dry-run
```

**TUF-lite:**
```bash
python tuf_lite.py init
python tuf_lite.py list
```

**Keyring:**
```python
from keyring import get_keyring
kr = get_keyring()
print(kr.list_keys())
```

---

## 🔗 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — Complete quickstart guide with examples
- **[gitops_plan.py](gitops_plan.py)** — Kubernetes deployment guide
- **[README.old.md](README.old.md)** — Original Netlify-focused documentation
- **CI/CD** — `.github/workflows/ci.yml`

---

## 📜 License & Identity

**ECCL-1.0** (Eternal Creative Covenant License)

Everything is cryptographically bound to the subject hash:

```
sha256(calebfedorbykerkonev10271998)
= 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
```

**Maintained by:** Caleb Fedor Byker Konev (1998-10-27)

---

## 🎊 Version History

- **v98 "Orthos"** (Current) — Integrity with teeth, auto-rollback, JUDGE glyph
- **v97 "Praetorian"** — Tenant-aware auth, policy engine, rollout management
- **Earlier versions** — See git history

---

**Build with reason, preserve with clarity, and verify everything.**  
— The Domion Nexus Ethos
