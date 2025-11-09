#!/usr/bin/env bash
set -e
ARCHIVE="$1"; test -f "$ARCHIVE" || { echo "usage: $0 <backup.tar.gz>"; exit 1; }
tar -xzf "$ARCHIVE"
echo "restored SQLite files from $ARCHIVE"
