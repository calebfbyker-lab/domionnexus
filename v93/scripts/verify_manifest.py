#!/usr/bin/env python3
import argparse, os, hashlib, json, sys

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536),b''): h.update(ch)
    return h.hexdigest()

ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.');
ap.add_argument('--manifest',default='codex/manifest.v93.json'); a=ap.parse_args()
m=json.load(open(a.manifest)); errs=[]
for it in m.get("items",[]):
    p=os.path.join(a.root,it["path"])
    if not os.path.exists(p): errs.append("MISSING "+it["path"]); continue
    if sha(p)!=it["sha256"]: errs.append("MISMATCH "+it["path"])
if errs: print("INTEGRITY FAILED\n"+"\n".join(errs)); sys.exit(2)
print("INTEGRITY PASSED")
