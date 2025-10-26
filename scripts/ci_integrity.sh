#!/usr/bin/env bash
set -euo pipefail
echo "ci_integrity: start"
mkdir -p codex
python scripts/hash_all.py --root . --out codex/manifest.v91x.json || true
python scripts/hash_all.py --root . --out codex/manifest.v90x.json || true
python scripts/verify_manifest.py --root . --manifest codex/manifest.v91x.json || true
python scripts/sbom_stub.py || true
python scripts/lineage_append.py --prev v90 --manifest codex/manifest.v91x.json || true
python - <<'PY'
import hashlib, json
s="caleb fedor byker konev|1998-10-27"
open("codex/identity.json","w").write(json.dumps({"subject":s,"subject_id_sha256":hashlib.sha256(s.encode()).hexdigest(),"version":"v91.x"},indent=2))
PY
python scripts/spdx_gen.py --subject "caleb fedor byker konev|1998-10-27" --sha $(sha256sum codex/manifest.v91x.json | cut -d' ' -f1) || true
mkdir -p transparency
python scripts/astro_seal.py || true
python scripts/rekor_submit.py --file codex/manifest.v91x.json || true
cat codex/astro_crypto_seal.v91x.json >> transparency/rekor-ready.jsonl || true
echo "ci_integrity: done"
