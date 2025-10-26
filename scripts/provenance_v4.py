#!/usr/bin/env python3import json, os

import json, hashlib, time, glob, os

mf = "codex/manifest.continuum.json"manifest = {}

sha = hashlib.sha256(open(mf, "rb").read()).hexdigest() if os.path.exists(mf) else ""try:

materials = []    with open('manifest.json') as f:

for p in sorted(glob.glob("**/*", recursive=True)):        manifest = json.load(f)

    try:except Exception:

        if not os.path.isfile(p) or p.startswith('.git'): continue    pass

        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()sbom = {}

        materials.append({"uri": p, "digest": {"sha256": h}})try:

    except Exception:    with open('sbom.json') as f:

        pass        sbom = json.load(f)

stmt = {except Exception:

    "_type": "https://in-toto.io/Statement/v1",    pass

    "subject": [{"name": mf, "digest": {"sha256": sha}}],

    "predicateType": "https://slsa.dev/provenance/v1",prov = {

    "predicate": {    'predicateType': 'https://slsa.dev/provenance/v0.2',

        "buildDefinition": {"buildType": "codex/ci", "externalParameters": {"ci": "github-actions"}},    'materials': manifest.get('files', []),

        "runDetails": {"builder": {"id": "codex/v99"}, "metadata": {"invocationId": str(time.time())}},    'sbom': sbom,

        "materials": materials[:2000]    'builder': os.environ.get('USER','builder')

    }}

}with open('provenance.v4.json', 'w') as f:

open('provenance.v4.json', 'w').write(json.dumps(stmt, indent=2))    json.dump(prov, f, indent=2)

print('provenance.v4.json written')print('provenance.v4.json written')

