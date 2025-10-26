# Codex Continuum — v100 · Continuum Σ (Sigma)

**Release:** Stable Excellence - "Boring is Beautiful"

**Goal:** A production-ready, policy-driven continuous deployment platform with zero-trust runners, hermetic builds, and comprehensive security gates.

## Authorship Anchor
- **Subject:** Caleb Fedor Byker Konev | 1998-10-27
- **Subject ID (SHA256):** `1f6e1f1ca3c4f3e1b1f6e2b317d7c1dff9b5d6d2b0d4e0f7b6a8c9e0f2a4b1c3`
- **License:** MIT + EUCLEA transparency clause

## Canonical Pipeline
🌀 VERIFY → 🌞 INVOKE → 🧾 AUDIT → 🛡 SCAN → 🔮 ATTEST → 🛡‍🔥 SANCTIFY → 🚦 ROLLOUT → ⚖️ JUDGE → 🌈 DEPLOY → ♾ CONTINUUM

## 🎯 What's New in v100

### Core Features
- **Policy-as-Code** (`policy/sigma.yaml`) — Declarative security and compliance rules
- **Zero-Trust Runners** — Three execution modes with increasing isolation:
  - `local.py` — Process isolation with command whitelisting
  - `sandbox.py` — Container-based execution
  - `http.py` — Remote webhook execution with TLS enforcement
- **Feature Flags** (`config/flags.json`) — Gradual rollout control
- **Hermetic Builds** — Fully isolated, reproducible builds
- **Multi-Target Rollouts** — Staged deployment across environments

### Security & Compliance
- **SBOM Generation** (`scripts/sbom_gen.py`) — Software Bill of Materials
- **Vulnerability Gating** (`scripts/vuln_gate.py`) — Automated security checks
- **Artifact Signing** (`scripts/sign.py`) — Cryptographic signatures
- **Glyph Guard v26** (`tools/glyph_guard_v26.py`) — Enhanced policy enforcement

### Build & Verification
- **v100 Manifest** (`scripts/hash_v100.py`) — Comprehensive file hashing
- **Integrity Verification** (`scripts/verify_v100.py`) — Manifest validation
- **Provenance Tracking** (`scripts/provenance_v4.py`) — Build metadata

## 🚀 Quick Start

### Installation
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Generate v100 Bundle
```bash
# 1. Generate SBOM
python scripts/sbom_gen.py . sbom.json

# 2. Check vulnerabilities
python scripts/vuln_gate.py sbom.json

# 3. Create manifest
python scripts/hash_v100.py . codex/manifest.v100.json

# 4. Sign artifacts
python scripts/sign.py codex/manifest.v100.json

# 5. Verify integrity
python scripts/verify_v100.py codex/manifest.v100.json .
```

### Run the Application
```bash
# Start the FastAPI server
uvicorn app:app --reload --port 8000

# Access the API
curl http://localhost:8000/
```

## 📁 Project Structure

```
domionnexus/
├── app.py                      # FastAPI application
├── requirements.txt            # Python dependencies
├── policy/
│   ├── sigma.yaml             # v100 policy-as-code
│   ├── glyph.yaml             # Glyph processing rules
│   └── runtime.json           # Runtime policy
├── config/
│   ├── flags.json             # Feature flags
│   └── domains.json           # Domain configuration
├── runners/
│   ├── local.py               # Zero-trust local runner
│   ├── sandbox.py             # Container sandbox runner
│   └── http.py                # HTTP webhook runner
├── scripts/
│   ├── hash_v100.py           # v100 manifest generator
│   ├── verify_v100.py         # Manifest verification
│   ├── sbom_gen.py            # SBOM generator
│   ├── vuln_gate.py           # Vulnerability gating
│   ├── sign.py                # Artifact signing
│   ├── provenance_v4.py       # Provenance generation
│   ├── rollout.py             # Deployment rollout
│   ├── judge.py               # Deployment decision logic
│   └── continuum.py           # Continuum orchestration
├── tools/
│   └── glyph_guard_v26.py     # Glyph policy enforcement
└── codex/
    ├── merkle.py              # Merkle tree operations
    ├── redact.py              # PII redaction
    └── glyphs/                # Glyph definitions
```

## 🔐 Security Model

### Zero-Trust Runners
Each runner enforces increasing levels of isolation:

1. **Local Runner** — Whitelisted commands, pattern denial, audit logging
2. **Sandbox Runner** — Container isolation, no network access, capability dropping
3. **HTTP Runner** — TLS required, HMAC signatures, remote execution

### Policy Enforcement
The `policy/sigma.yaml` defines rules for:
- Deployment security (no privileged containers)
- Resource limits enforcement
- Signed images requirement
- SBOM and provenance requirements
- Vulnerability thresholds
- Audit logging

### Vulnerability Gates
Enforced thresholds:
- **Critical:** 0 allowed
- **High:** ≤ 5 allowed
- **Medium:** ≤ 20 allowed (warning only)
- **Low:** Informational

## 🎛 Feature Flags

Control v100 features via `config/flags.json`:

- `hermetic_builds` — 100% rollout (stable)
- `zero_trust_runners` — 100% rollout (stable)
- `semantic_diffing` — 80% rollout
- `multi_target_rollout` — 100% rollout (stable)
- `advanced_policy_engine` — 50% rollout (canary)
- `provenance_v5` — 0% rollout (experimental)

## 📊 API Endpoints

### Core Endpoints
- `GET /` — Health check and version info
- `POST /nonce/issue` — Issue authentication nonce
- `POST /glyph/process` — Process and validate glyph
- `POST /webhook/github` — GitHub webhook handler

### Verification Endpoints
- `POST /config/verify` — Verify config bundle signature
- `GET /redact/test` — Test PII redaction
- `POST /attest` — Create attestation

### Monitoring
- `GET /cost/report` — Cost estimation report
- `GET /audit/export` — Export audit logs

## 🧪 Testing

```bash
# Test zero-trust runner
python runners/local.py echo "Hello v100"

# Test glyph guard
python tools/glyph_guard_v26.py "echo test"

# Test vulnerability gate
python scripts/sbom_gen.py . sbom.json
python scripts/vuln_gate.py sbom.json

# Test signing
python scripts/hash_v100.py . test.manifest.json
python scripts/sign.py test.manifest.json
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Codex v100 Pipeline
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate SBOM
        run: python scripts/sbom_gen.py . sbom.json
      - name: Vulnerability Gate
        run: python scripts/vuln_gate.py sbom.json
      - name: Create Manifest
        run: python scripts/hash_v100.py . manifest.json
      - name: Sign Artifacts
        run: python scripts/sign.py manifest.json
      - name: Verify Integrity
        run: python scripts/verify_v100.py manifest.json .
```

## 📦 Release Philosophy

**v100 - "Continuum Σ (Sigma)"** represents:

- **Stability:** Battle-tested components from v99.x
- **Security:** Zero-trust by default, comprehensive gates
- **Simplicity:** Clear policies, minimal configuration
- **Compliance:** Full audit trail, SBOM, provenance
- **Boring Excellence:** No surprises, just reliable operations

The Σ (Sigma) symbol represents the **summation** of all learnings from previous versions into a cohesive, production-ready release.

## 🛠 Development

```bash
# Format code
black app.py scripts/ runners/ tools/

# Lint
flake8 app.py scripts/ runners/ tools/

# Type check
mypy app.py scripts/ runners/ tools/
```

## 📚 Documentation

- **Policy Guide:** See `policy/sigma.yaml` for rule definitions
- **Runner Guide:** See `runners/` for execution modes
- **Security Guide:** Review zero-trust model and gates
- **API Docs:** Run server and visit `/docs` for OpenAPI spec

## 🌟 Philosophy

> "Make the right thing the easy thing. Make the wrong thing the hard thing."

v100 embodies this by:
- Making secure builds the default path
- Requiring explicit overrides for risky operations
- Providing clear feedback at every stage
- Automating compliance without friction

## 🤝 Contributing

This is a demonstration platform for modern DevSecOps practices. Contributions should:
1. Maintain zero-trust principles
2. Add comprehensive tests
3. Update policy definitions as needed
4. Document security implications

## 📄 License

MIT License + EUCLEA Transparency Clause

This project is cryptographically bound to the subject identity:
`1f6e1f1ca3c4f3e1b1f6e2b317d7c1dff9b5d6d2b0d4e0f7b6a8c9e0f2a4b1c3`

## 🎯 Roadmap

**Completed in v100:**
- ✅ Policy-as-code framework
- ✅ Zero-trust runner modes
- ✅ SBOM and vulnerability gating
- ✅ Hermetic build support
- ✅ Multi-target rollouts

**Future (v101+):**
- ⏳ Provenance v5 format
- ⏳ Quantum-resistant cryptography
- ⏳ Advanced OPA policy integration
- ⏳ Semantic diff engine
- ⏳ AI-assisted policy recommendations

---

**Built with precision. Verified with care. Deployed with confidence.**

*Codex Continuum v100 — Where boring is beautiful.* 🌌
