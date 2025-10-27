#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Running publish script from $ROOT"

test -d /mnt/data || { echo "No /mnt/data mount found. Copy files into $ROOT manually or run this script where /mnt/data is available."; exit 1; }

cp "/mnt/data/Codex_Immortal_Master_Volume (5).html" "$ROOT/index.html"
cp /mnt/data/manifest.json "$ROOT/manifest.json"
cp /mnt/data/service-worker.js "$ROOT/service-worker.js"
mkdir -p "$ROOT/docs"
cp "/mnt/data/Codex_Glyph_Registry_Master.pdf" "$ROOT/docs/" || true
cp "/mnt/data/Codex_Immortal_333_Seals.pdf" "$ROOT/docs/" || true
cp "/mnt/data/Codex_Immortal_PWA_Poster_portrait_color.pdf" "$ROOT/docs/" || true

cd "$ROOT"
git init || true
git checkout -b main || true
git add .
git commit -m "Codex Immortal: finished bundle (provenanced & hashed)" || true

if command -v gh >/dev/null 2>&1; then
  echo "Attempting to create GitHub repo 'cfbk-codex-immortal' and push..."
  gh repo create cfbk-codex-immortal --public --source=. --remote=origin --push || true
  # enable pages (owner will be inferred by gh)
  USER_JSON=$(gh api user || true)
  owner=$(echo "$USER_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('login',''))" 2>/dev/null || true)
  if [ -n "$owner" ]; then
    echo "Enabling GitHub Pages for $owner/cfbk-codex-immortal"
    gh api repos/$owner/cfbk-codex-immortal -X PATCH -F has_pages=true || true
    gh api repos/$owner/cfbk-codex-immortal/pages -X POST -f source[branch]=main -f source[path]=/ || true
  else
    echo "gh not authenticated or owner unknown — please run 'gh auth login' and retry to enable Pages."
  fi
else
  echo "gh CLI not available; skipping GitHub repo creation steps."
fi

echo "Publish script finished."
