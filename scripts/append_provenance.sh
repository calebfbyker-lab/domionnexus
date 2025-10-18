#!/usr/bin/env bash
set -euo pipefail
CANON_FILE="${1:-seals/Solomon-001.canonical.json}"
SIG_FILE="${2:-seals/Solomon-001.sig}"
PUB_B64_FILE="${3:-keys/cfbk_pub.base64}"
WF_ID="${4:-wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e}"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
SHA=$(sha256sum "${CANON_FILE}" | awk '{print $1}')
if file "${SIG_FILE}" | grep -qi text; then
  SIG_B64=$(cat "${SIG_FILE}" | tr -d '\n')
else
  SIG_B64=$(base64 -w0 "${SIG_FILE}")
fi
PUB_B64=$(cat "${PUB_B64_FILE}" | tr -d '\n' 2>/dev/null || echo "")
PROV_JSON=$(jq -cn --arg evt "bind" --arg seal "Solomon-001" --arg actor "CFBK" --arg file "${CANON_FILE}" --arg sha "$SHA" --arg sig "$SIG_B64" --arg pub "$PUB_B64" --arg wf "$WF_ID" '{event:$evt,seal:$seal,actor:$actor,file:$file,sha256:$sha,sig:$sig,sig_algo:"ed25519",pub_b64:$pub,workflow:$wf}')
echo "- ${TS}  ${SHA}  ${PROV_JSON}" >> PROVENANCE.md
echo "Appended provenance entry to PROVENANCE.md"