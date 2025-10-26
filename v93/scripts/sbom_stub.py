#!/usr/bin/env python3
import os, json, hashlib
ROOT='.'; arts=[]
for d,_,fs in os.walk(ROOT):
    if any(x in d for x in ['.git','.venv','__pycache__','.github']): continue
    for n in fs:
        p=os.path.join(d,n)
        with open(p,'rb') as f: h=hashlib.sha256(f.read()).hexdigest()
        arts.append({"path":os.path.relpath(p,ROOT).replace('\\','/'),"sha256":h})
open('sbom.json','w').write(json.dumps({"artifacts":arts},indent=2))
print("sbom.json written")
