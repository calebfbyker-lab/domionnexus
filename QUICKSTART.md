# Codex v98 "Orthos" Quickstart Guide

**Integrity with Teeth** — The service refuses to run if the code diverges from its manifest.

## 🎯 What's New in v98 "Orthos"

Codex v98 represents a major security and operational upgrade, introducing:

1. **Boot-time Self-Check** — Service verifies file integrity against manifest before starting
2. **HMAC Keyring** — Secure key rotation and management for request signing
3. **Shadow Deploy Metrics** — Progressive deployment with automatic rollback
4. **JUDGE Glyph** — Enhanced deployment gating with quality/security/performance checks
5. **TUF-lite Metadata** — Lightweight implementation of The Update Framework for secure artifact distribution
6. **GitOps Plan** — Kubernetes deployment configuration for cloud-native deployment

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.11+
- Git

### 1. Clone and Setup
```bash
git clone https://github.com/calebfbyker-lab/domionnexus.git
cd domionnexus

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Manifest (Required for Self-Check)
```bash
# Create integrity manifest
python scripts/hash_all.py

# Verify manifest is valid
python scripts/verify_manifest.py
```

### 3. Run Self-Check (New in v98)
```bash
# Verify code integrity before starting
python selfcheck.py
```

### 4. Start the Service
```bash
# Development mode
uvicorn app:app --reload --port 8000

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Verify It's Running
```bash
# Check health endpoint
curl http://localhost:8000/health

# Should return:
# {
#   "ok": true,
#   "ver": "Codex v98 · Orthos",
#   "features": ["boot-time-selfcheck", "hmac-keyring", ...]
# }
```

## 📋 Key Features & Usage

### 🔒 1. Boot-Time Self-Check

**What it does:** Verifies all files match the manifest before allowing the service to start.

**Usage:**
```bash
# Run self-check manually
python selfcheck.py

# Self-check also runs automatically on app startup
```

**How it works:**
- `scripts/hash_all.py` generates `manifest.json` with SHA256 hashes of all files
- `selfcheck.py` verifies files match the manifest
- Service refuses to start if critical files (like `app.py`) are modified

**Customize critical files:**
```python
# In selfcheck.py
CRITICAL_FILES = ["app.py", "selfcheck.py", "keyring.py"]
```

### 🔑 2. HMAC Keyring

**What it does:** Manages HMAC keys with automatic rotation support.

**Usage:**
```bash
# Check keyring status
curl -H "X-API-Key: dev-key" http://localhost:8000/keyring/status

# Rotate key
curl -X POST -H "X-API-Key: dev-key" http://localhost:8000/keyring/rotate
```

**Configuration:**
```bash
# Set initial HMAC key via environment variable
export CODEX_HMAC_KEY="your-secret-key"
```

**Keyring is stored in:** `config/keyring.json`

**Key rotation policy:** Keys auto-rotate after 30 days (configurable in `keyring.py`)

### 📊 3. Shadow Deploy Metrics

**What it does:** Tracks canary deployment metrics and triggers auto-rollback on errors.

**Usage:**
```bash
# Start a shadow deployment
curl -X POST -H "X-API-Key: dev-key" \
  "http://localhost:8000/rollout/start?percent=5"

# Check metrics
curl -H "X-API-Key: dev-key" http://localhost:8000/shadow/metrics

# Check for auto-rollback
curl -X POST -H "X-API-Key: dev-key" http://localhost:8000/shadow/check
```

**Auto-rollback triggers:**
- Error rate > 5%
- Health check failure rate > 50%

**Metrics stored in:** `rollout/shadow_metrics.json`

### ⚖️ 4. JUDGE Glyph (New Deployment Gate)

**What it does:** Evaluates deployment readiness across multiple criteria.

**Usage:**
```bash
# Run JUDGE gate for quality and security
curl -X POST http://localhost:8000/glyph \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "glyph": "judge:quality,security,performance",
    "dry_run": false
  }'
```

**Available JUDGE criteria:**
- `quality` — Code quality metrics (coverage, lint errors)
- `security` — Security scan results (vulnerabilities)
- `performance` — Performance benchmarks (latency, throughput)

**Direct CLI usage:**
```bash
python tools/glyph_guard_v22.py --glyph "judge:quality,security"
```

### 🎯 5. TUF-lite Metadata

**What it does:** Provides secure artifact distribution with cryptographic verification.

**Usage:**
```bash
# Initialize TUF metadata
python tuf_lite.py init

# Add an artifact
python tuf_lite.py add path/to/artifact.tar.gz

# List all artifacts
python tuf_lite.py list

# Verify an artifact
python tuf_lite.py verify artifact.tar.gz
```

**Metadata stored in:** `tuf/metadata/`
**Artifacts stored in:** `tuf/targets/`

### ☸️ 6. GitOps Deployment

**What it does:** Provides Kubernetes manifests and ArgoCD configuration.

**View the plan:**
```bash
python gitops_plan.py
```

**Key features:**
- Progressive rollout (5% → 100%)
- Init container runs self-check
- Secrets management via Kubernetes
- ArgoCD/FluxCD ready
- Flagger integration for canary deployments

## 🔄 Complete Deployment Workflow

### Development Cycle
```bash
# 1. Make code changes
vim app.py

# 2. Update manifest
python scripts/hash_all.py

# 3. Verify integrity
python selfcheck.py

# 4. Run CI checks
python scripts/determinism_env.py
python scripts/verify_manifest.py
python scripts/sbom_syft_stub.py
python scripts/vuln_gate.py
python scripts/provenance_v4.py

# 5. Test locally
uvicorn app:app --reload

# 6. Commit changes
git add .
git commit -m "feat: update for v98"
git push
```

### Production Deployment
```bash
# 1. Build container
docker build -t codex-orthos:v98 .

# 2. Push to registry
docker push your-registry/codex-orthos:v98

# 3. Deploy to Kubernetes
kubectl apply -f k8s/

# 4. Start canary deployment
curl -X POST -H "X-API-Key: $API_KEY" \
  "https://codex.example.com/rollout/start?percent=5"

# 5. Monitor metrics
watch curl -H "X-API-Key: $API_KEY" \
  https://codex.example.com/shadow/metrics

# 6. Advance rollout
curl -X POST -H "X-API-Key: $API_KEY" \
  "https://codex.example.com/rollout/advance?step=10"

# 7. Complete deployment
# (Automatic at 100% or manual verification)
```

## 🛡️ Security Best Practices

### 1. Manifest Integrity
- **Always** regenerate `manifest.json` after code changes
- Run `selfcheck.py` before deployment
- Use strict mode in production: `selfcheck(strict=True)`

### 2. HMAC Key Management
- Set strong `CODEX_HMAC_KEY` in production
- Rotate keys every 30 days (automatic)
- Store keyring backups securely
- Never commit `config/keyring.json` to git

### 3. API Key Protection
- Use strong API keys in production
- Rotate `CODEX_API_KEY` regularly
- Use different keys per environment
- Store keys in Kubernetes secrets or vault

### 4. Deployment Safety
- Start with 5% canary deployments
- Monitor metrics before advancing
- Set up alerts for auto-rollback
- Keep previous version ready for quick rollback

### 5. Artifact Distribution
- Use TUF-lite for all artifact distribution
- Verify artifacts before deployment: `tuf_lite.py verify`
- Update metadata after adding artifacts
- Keep metadata in version control

## 🧪 Testing

### Run All Tests
```bash
# CI pipeline
python scripts/determinism_env.py
python scripts/hash_all.py
python scripts/verify_manifest.py
python scripts/sbom_syft_stub.py
python scripts/vuln_gate.py
python scripts/provenance_v4.py
python scripts/dsse_hmac_sign.py
```

### Test Self-Check
```bash
# Should pass
python selfcheck.py

# Modify a file to test failure
echo "# test" >> app.py
python selfcheck.py  # Should fail

# Restore
git checkout app.py
```

### Test JUDGE Glyph
```bash
# All criteria
python tools/glyph_guard_v22.py --glyph "judge:quality,security,performance"

# Single criterion
python tools/glyph_guard_v22.py --glyph "judge:quality"

# Dry run
python tools/glyph_guard_v22.py --glyph "deploy:service@v98" --dry-run
```

### Test Shadow Metrics
```python
from shadow_metrics import ShadowMetrics

metrics = ShadowMetrics()
dep_id = "test-deployment"

# Start deployment
metrics.start_deployment(dep_id, "v98", initial_percent=5)

# Record requests
for i in range(100):
    metrics.record_request(dep_id, success=True)

# Check rollback
should_rb, reason = metrics.should_rollback(dep_id)
print(f"Rollback needed: {should_rb}, Reason: {reason}")
```

## 📚 API Reference

### Core Endpoints
- `GET /health` — Service health and feature flags
- `GET /seal` — Subject identity and hash
- `GET /features` — Detailed v98 feature information

### Glyph System
- `POST /glyph` — Execute glyph command (deploy, judge, sanctify, rollback)

### Rollout Management
- `POST /rollout/start?percent=5` — Start canary deployment
- `POST /rollout/advance?step=10` — Advance rollout percentage
- `GET /rollout/status` — Get current rollout status

### HMAC Keyring (v98)
- `GET /keyring/status` — Get keyring status and key list
- `POST /keyring/rotate` — Rotate to new HMAC key

### Shadow Metrics (v98)
- `GET /shadow/metrics` — Get current deployment metrics
- `POST /shadow/check` — Check metrics and auto-rollback if needed

### Policy & Tenants
- `GET /tenants` — List configured tenants
- `POST /policy/preview` — Preview policy evaluation

## 🐛 Troubleshooting

### Self-Check Fails
```bash
# Regenerate manifest
python scripts/hash_all.py

# Check what changed
git status
git diff

# Verify specific file
python -c "import hashlib; print(hashlib.sha256(open('app.py','rb').read()).hexdigest())"
```

### Keyring Issues
```bash
# Reset keyring
rm config/keyring.json
# Restart app to reinitialize

# Check keyring file
cat config/keyring.json | jq
```

### Rollback Not Triggering
```bash
# Check metrics
curl -H "X-API-Key: dev-key" http://localhost:8000/shadow/metrics

# Manually trigger check
curl -X POST -H "X-API-Key: dev-key" http://localhost:8000/shadow/check

# Check threshold in shadow_metrics.py
# ROLLBACK_THRESHOLD = 0.05  # 5%
```

### JUDGE Glyph Not Working
```bash
# Test directly
python tools/glyph_guard_v22.py --glyph "judge:quality" --dry-run

# Check policy file
cat policy/glyph.yaml

# Enable judge in policy
echo "judge_enabled: true" > policy/glyph.yaml
```

## 🔗 Related Documentation

- **GitOps Plan**: Run `python gitops_plan.py` for full Kubernetes deployment guide
- **Original README**: See `README.md` for project overview and background
- **CI Configuration**: See `.github/workflows/ci.yml` for CI/CD pipeline

## 📝 Version History

- **v98 "Orthos"** (Current) — Integrity with teeth, auto-rollback, JUDGE glyph
- **v97 "Praetorian"** — Tenant-aware auth, policy engine, rollout management
- **Earlier versions** — See git history

## 🤝 Contributing

1. Fork the repository
2. Make changes on a feature branch
3. **Run self-check**: `python selfcheck.py`
4. **Update manifest**: `python scripts/hash_all.py`
5. **Run CI checks**: See `.github/workflows/ci.yml`
6. Submit pull request

## 📄 License

ECCL-1.0 (Eternal Creative Covenant License)

Cryptographically bound to:
```
sha256(calebfedorbykerkonev10271998)
= 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
```

---

**Build with reason, preserve with clarity, and verify everything.**
— The Domion Nexus Ethos
