#!/usr/bin/env bash
set -euo pipefail
if [ -z "${OPENAI_API_KEY:-}" ] || [ -z "${OPENAI_PROJECT_ID:-}" ]; then
  echo "OPENAI_API_KEY or OPENAI_PROJECT_ID missing — skipping OpenAI project deploy"
  exit 0
fi
echo "Would deploy to OpenAI Project ${OPENAI_PROJECT_ID} (dry-run)"
# If you have the OpenAI CLI installed and configured, you could run:
# openai projects deploy --project $OPENAI_PROJECT_ID --source .
echo "(no-op)"
