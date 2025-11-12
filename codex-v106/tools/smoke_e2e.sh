#!/usr/bin/env bash
set -e
ORCH="${CODEX_ORCH_URL:-http://localhost:8010}"
curl -s -X POST "$ORCH/runs" -H "content-type: application/json" \
  -d '{"tenant":"cfbk","prio":9,"glyph":"🌀; 🌞; 🧾; 🛡; 🔮; 🛡‍🔥; 🚦; ⚖️; 🌈; ♾"}' | jq -r .run_id
curl -s "$ORCH/events/tail?n=5" | jq
