#!/usr/bin/env python3
import argparse, os, hashlib, json, datetime
SKIP={'.git','.venv','pycache','.github'}
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536),b''): h.update(ch)
    return h.hexdigest()
def walk(root):
    for d,ds,fs in os.walk(root):
        ds[:]=[x for x in ds if x not in SKIP]
        for n in fs:
            rel=os.path.relpath(os.path.join(d,n),root).replace('\\','/')
            yield rel
ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.')
ap.add_argument('--out',default='codex/manifest.continuum.json'); a=ap.parse_args()
items=[]; root=os.path.abspath(a.root)
total=0
for rel in sorted(walk(root)):
    p=os.path.join(root,rel)
    if os.path.isfile(p):
        size=os.path.getsize(p); total+=size
        items.append({"path":rel,"size":size,"sha256":sha(p)})
m={"title":"Codex Continuum v99.x — Unified Manifest","subject_id_sha256":"1f6e1f1ca3c4f3e1b1f6e2b317d7c1dff9b5d6d2b0d4e0f7b6a8c9e0f2a4b1c3",
"generated_utc":datetime.datetime.utcnow().isoformat()+"Z","total_bytes":total,"items":items}
os.makedirs(os.path.dirname(a.out), exist_ok=True)
open(a.out,'w',encoding='utf-8').write(json.dumps(m, indent=2))
print("wrote", len(items), "items to", a.out, "total bytes", total)
#!/usr/bin/env python3import hashlib, json, os

import argparse, os, hashlib, json, datetime

SKIP = {'.git', '.venv', '__pycache__', '.github'}root = os.getcwd()

manifest = {"files": []}

def sha(p):for dirpath, dirnames, filenames in os.walk(root):

    h = hashlib.sha256()    # skip .git and node_modules

    with open(p, 'rb') as f:    if '.git' in dirpath:

        for ch in iter(lambda: f.read(65536), b''):        continue

            h.update(ch)    for fn in filenames:

    return h.hexdigest()        if fn.endswith('.pyc'):

            continue

        path = os.path.join(dirpath, fn)

def walk(root):        try:

    for d, ds, fs in os.walk(root):            with open(path, 'rb') as f:

        ds[:] = [x for x in ds if x not in SKIP]                data = f.read()

        for n in fs:            h = hashlib.sha256(data).hexdigest()

            rel = os.path.relpath(os.path.join(d, n), root).replace('\\', '/')            manifest['files'].append({'path': os.path.relpath(path, root), 'sha256': h})

            yield rel        except Exception:

            pass

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.')with open('manifest.json', 'w') as fh:

ap.add_argument('--out', default='codex/manifest.continuum.json'); a = ap.parse_args()    json.dump(manifest, fh, indent=2)

items = []; root = os.path.abspath(a.root)print('manifest.json written, %d entries' % len(manifest['files']))

for rel in sorted(walk(root)):
    p = os.path.join(root, rel)
    if os.path.isfile(p):
        items.append({"path": rel, "size": os.path.getsize(p), "sha256": sha(p)})
m = {"title": "Codex Continuum v99 — Unified Manifest", "subject_id_sha256": "", "generated_utc": datetime.datetime.utcnow().isoformat() + "Z", "items": items}
os.makedirs(os.path.dirname(a.out), exist_ok=True)
open(a.out, 'w', encoding='utf-8').write(json.dumps(m, indent=2))
print("wrote", len(items), "items to", a.out)
