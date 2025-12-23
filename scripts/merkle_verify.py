#!/usr/bin/env python3
import json, hashlib
m=json.load(open("provenance/merkle.json"))
def fold(hs):
    out=[];
    for i in range(0,len(hs),2):
        pair=hs[i] if i+1==len(hs) else hs[i]+hs[i+1]
        out.append(hashlib.sha256(pair.encode()).hexdigest())
    return out
hs=[h for _,h in m["files"]]
while len(hs)>1: hs=fold(hs)
print("ok" if (hs[0] if hs else None)==m["root"] else "bad")
exit(0 if (hs[0] if hs else None)==m["root"] else 2)
