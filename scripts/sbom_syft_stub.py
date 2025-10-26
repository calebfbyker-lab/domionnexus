import json
# Minimal SBOM stub
sbom = {"sbom": {"tool": "syft-stub", "packages": []}}
with open('sbom.json','w') as f:
    json.dump(sbom, f, indent=2)
print('sbom.json created (stub)')
