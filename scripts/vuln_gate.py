import json, sys
# Minimal vuln gate: pass if sbom exists
try:
    with open('sbom.json') as f:
        sbom = json.load(f)
    print('vuln_gate: OK (stub)')
except Exception as e:
    print('vuln_gate: missing sbom', e)
    sys.exit(1)
