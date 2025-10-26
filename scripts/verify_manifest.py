#!/usr/bin/env python3import json, hashlib

import argparse, os, hashlib, json, sys

with open('manifest.json','r') as fh:

def sha(p):    mf = json.load(fh)

    h = hashlib.sha256()errors = 0

    with open(p, 'rb') as f:for e in mf.get('files',[]):

        for ch in iter(lambda: f.read(65536), b''):    try:

            h.update(ch)        with open(e['path'],'rb') as f:

    return h.hexdigest()            d = f.read()

        if hashlib.sha256(d).hexdigest() != e['sha256']:

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.')            print('MISMATCH', e['path'])

ap.add_argument('--manifest', default='codex/manifest.continuum.json'); a = ap.parse_args()            errors += 1

m = json.load(open(a.manifest)); errs = []    except FileNotFoundError:

for it in m.get('items', []):        print('MISSING', e['path'])

    p = os.path.join(a.root, it['path'])        errors += 1

    if not os.path.exists(p): errs.append('MISSING ' + it['path']); continueprint('verify_manifest: errors=', errors)

    if sha(p) != it['sha256']: errs.append('MISMATCH ' + it['path'])if errors:

if errs:    raise SystemExit(2)

    print('INTEGRITY FAILED\n' + '\n'.join(errs)); sys.exit(2)
print('INTEGRITY PASSED')
