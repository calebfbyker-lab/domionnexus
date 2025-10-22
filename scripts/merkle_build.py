#!/usr/bin/env python3
import os, json, hashlib
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(8192), b""): h.update(c)
    return h.hexdigest()
files=[]
for r,_,fs in os.walk("provenance"):
    for fn in fs:
        p=os.path.join(r,fn); files.append(("provenance/"+fn, sha(p)))
files.sort(key=lambda x: x[0])
nodes=[h for _,h in files]
def step(a):
    out=[]
    for i in range(0,len(a),2):
        pair=a[i] if i+1==len(a) else a[i]+a[i+1]
        out.append(hashlib.sha256(pair.encode()).hexdigest())
    return out
root=nodes[:]
while len(root)>1: root=step(root)
os.makedirs("provenance",exist_ok=True)
json.dump({"root":root[0] if root else None,"files":files}, open("provenance/merkle.json","w"), indent=2)
print("merkle_root:", root[0] if root else None)
