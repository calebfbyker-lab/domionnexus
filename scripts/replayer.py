#!/usr/bin/env python3
import json, hashlib, os
AUDIT='audit.jsonl'

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536), b''):
            h.update(ch)
    return h.hexdigest()

try:
    with open(AUDIT,'rb') as f: lines = f.read().splitlines()
except FileNotFoundError:
    print(json.dumps({'audit_count':0,'audit_root':'0'*64}, indent=2)); raise SystemExit(0)
# compute simple merkle
import codex.merkle as m
root = m.merkle_root(m.leaves_hashes(lines))
print(json.dumps({'audit_count': len(lines), 'audit_root': root}, indent=2))
if os.path.exists('codex/manifest.continuum.json'):
    print(json.dumps({'manifest':'codex/manifest.continuum.json','sha256': sha('codex/manifest.continuum.json')}, indent=2))
