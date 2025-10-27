#!/usr/bin/env bash
set -euo pipefail

# Simple local Firebase deploy helper.
# Requirements:
# - npm & node installed
# - FIREBASE_SERVICE_ACCOUNT env contains the service account JSON (or point to file via SERVICE_ACCOUNT_FILE)
# - FIREBASE_PROJECT_ID and FIREBASE_SITE_ID set in env

SERVICE_ACCOUNT_FILE=${SERVICE_ACCOUNT_FILE:-/tmp/serviceAccount.json}
if [ -z "${FIREBASE_SERVICE_ACCOUNT:-}" ] && [ ! -f "$SERVICE_ACCOUNT_FILE" ]; then
  echo "Provide FIREBASE_SERVICE_ACCOUNT env (JSON) or set SERVICE_ACCOUNT_FILE to a JSON file path." >&2
  exit 1
fi

if [ -n "${FIREBASE_SERVICE_ACCOUNT:-}" ]; then
  echo "$FIREBASE_SERVICE_ACCOUNT" > "$SERVICE_ACCOUNT_FILE"
  chmod 600 "$SERVICE_ACCOUNT_FILE"
fi

: ${FIREBASE_PROJECT_ID:?Need FIREBASE_PROJECT_ID env}
: ${FIREBASE_SITE_ID:?Need FIREBASE_SITE_ID env}

echo "Checking firebase-tools..."
if ! command -v firebase >/dev/null 2>&1; then
  echo "Installing firebase-tools (may require npm)..."
  if command -v npm >/dev/null 2>&1; then
    npm install -g firebase-tools
  else
    echo "npm not found; install Node.js/npm and re-run." >&2
    exit 1
  fi
fi

export GOOGLE_APPLICATION_CREDENTIALS="$SERVICE_ACCOUNT_FILE"

echo "Deploying build/ to Firebase Hosting site: $FIREBASE_SITE_ID (project: $FIREBASE_PROJECT_ID)"

# Prefer using service account via gcloud if available
if command -v gcloud >/dev/null 2>&1; then
  echo "Activating service account via gcloud..."
  gcloud auth activate-service-account --key-file="$SERVICE_ACCOUNT_FILE"
  gcloud config set project "$FIREBASE_PROJECT_ID"
  firebase deploy --only hosting:"$FIREBASE_SITE_ID" --project "$FIREBASE_PROJECT_ID" --non-interactive --force
else
  # Try firebase CLI with application default creds
  firebase deploy --only hosting:"$FIREBASE_SITE_ID" --project "$FIREBASE_PROJECT_ID" --non-interactive --force || {
    echo "firebase deploy failed. If you don't have gcloud installed, authenticate with 'firebase login' or provide a CI token." >&2
    exit 1
  }
fi

echo "Deploy finished."
