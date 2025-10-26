import json, os

manifest = {}
try:
    with open('manifest.json') as f:
        manifest = json.load(f)
except Exception:
    pass
sbom = {}
try:
    with open('sbom.json') as f:
        sbom = json.load(f)
except Exception:
    pass

prov = {
    'predicateType': 'https://slsa.dev/provenance/v0.2',
    'materials': manifest.get('files', []),
    'sbom': sbom,
    'builder': os.environ.get('USER','builder')
}
with open('provenance.v4.json', 'w') as f:
    json.dump(prov, f, indent=2)
print('provenance.v4.json written')
