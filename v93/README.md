# Codex Immortal × Dominion Nexus — v93 · Celestial Verity

What v93 adds: sandboxed glyph execution (resource limits), unified XTGS/TSG/TGS glyph maps,
OPA/Rego policy stubs, provenance v3 statement, drift detection, SPDX + lineage + SBOM, and
copy‑paste CI/CD for GitHub → GHCR → Kubernetes.

Binding model (plain): authorship = SHA-256 of subject string; manifests, SBOM, and provenance
carry that identity. “Seals/sigils” are implemented as signatures/lineage/logs. Myth stays poetic;
enforcement is math and automation.

Glyphs in a sentence → verified actions → sandboxed execution → attestations → deploy.

Quickstart
---------
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# health + identity
curl http://localhost:8000/health
curl http://localhost:8000/seal

# glyph pipeline (dry-run)
python tools/glyph_guard_v13.py --glyph "🌀 VERIFY; 🌞 INVOKE; 🌈 DEPLOY; 🧾 AUDIT; 🔮 ATTEST" --dry-run
```
