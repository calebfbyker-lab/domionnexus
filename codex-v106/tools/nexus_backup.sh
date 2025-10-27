#!/usr/bin/env bash
set -e
DB="${NEXUS_DB:-./nexus.db}"
OUT="${1:-nexus_backup_$(date +%Y%m%d%H%M%S).tar.gz}"
tar -czf "$OUT" "$DB"
echo "backup: $OUT"
