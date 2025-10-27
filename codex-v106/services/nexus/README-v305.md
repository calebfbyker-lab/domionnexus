v305 adds:
- SQLite ledger (events + proofs)
- Token RBAC: header X-Auth with scopes: ingest, read, metrics
- /metrics Prometheus endpoint
- /ledger/list, /ledger/ingest_signed (HMAC or Ed25519)
- Backup/restore scripts
Mount with:
    from services.nexus.app_v305_patch import patch as v305_patch
    v305_patch(app)
Set env:
    export NEXUS_DB=./nexus.db
    export NEXUS_TOKENS="token123=ingest,read,metrics;tokenABC=read"
    export NEXUS_KEY="dev-hmac"
    # (optional ed25519)
    export NEXUS_PUB="<base64-verify-key>"
