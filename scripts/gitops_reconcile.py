#!/usr/bin/env python3
import json, os, hashlib

CUR='codex/manifest.v98.json'
PREV='codex/manifest.prev.json'
OUT='gitops-diff.json'

def load(p):
    try: return json.load(open(p,encoding='utf-8'))
    except Exception: return {'items':[]}

cur=load(CUR)
prev=load(PREV)
cur_set={i['path']:i for i in cur.get('items',[])}
prev_set={i['path']:i for i in prev.get('items',[])}
added=[]; removed=[]; changed=[]
for p,i in cur_set.items():
    if p not in prev_set: added.append(p)
    elif i.get('sha256')!=prev_set[p].get('sha256'): changed.append(p)
for p in prev_set:
    if p not in cur_set: removed.append(p)
out={'added':added,'removed':removed,'changed':changed}
open(OUT,'w',encoding='utf-8').write(json.dumps(out, indent=2))
print('gitops-diff written')
