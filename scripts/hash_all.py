#!/usr/bin/env python3
import argparse, os, hashlib, json, datetime
SKIP={'.git','.venv','__pycache__','.github'}
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
ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.');
ap.add_argument('--out',default='codex/manifest.v96.json'); a=ap.parse_args()
items=[]; root=os.path.abspath(a.root)
for rel in sorted(walk(root)):
    p=os.path.join(root,rel)
    if os.path.isfile(p): items.append({"path":rel,"size":os.path.getsize(p),"sha256":sha(p)})
m={"title":"Codex v96 — Integrity Manifest","subject_id_sha256":"__SUBJECT_SHA__","generated_utc":datetime.datetime.utcnow().isoformat()+"Z","items":items}
os.makedirs(os.path.dirname(a.out), exist_ok=True)
open(a.out,'w',encoding='utf-8').write(json.dumps(m, indent=2))
print("wrote", len(items), "items to", a.out)
