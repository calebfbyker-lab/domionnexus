#!/usr/bin/env python3
import json, subprocess, os, hashlib, sys
def has(cmd):
    from shutil import which
    return which(cmd) is not None
if has("syft"):
    rc = subprocess.call("syft . -o json > sbom.json", shell=True)
    if rc!=0: sys.exit(rc)
    print("SBOM generated via syft")
else:
    import os, json, hashlib
    ROOT='.'; arts=[]
    for d,_,fs in os.walk(ROOT):
        if any(x in d for x in ['.git','.venv','__pycache__','.github']): continue
        for n in fs:
            p=os.path.join(d,n)
            with open(p,'rb') as f: h=hashlib.sha256(f.read()).hexdigest()
            arts.append({"path":os.path.relpath(p,ROOT).replace('\\','/'),"sha256":h})
    open('sbom.json','w').write(json.dumps({"artifacts":arts},indent=2))
    print("SBOM stub written")
