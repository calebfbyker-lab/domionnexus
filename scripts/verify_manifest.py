import json, hashlib

with open('manifest.json','r') as fh:
    mf = json.load(fh)
errors = 0
for e in mf.get('files',[]):
    try:
        with open(e['path'],'rb') as f:
            d = f.read()
        if hashlib.sha256(d).hexdigest() != e['sha256']:
            print('MISMATCH', e['path'])
            errors += 1
    except FileNotFoundError:
        print('MISSING', e['path'])
        errors += 1
print('verify_manifest: errors=', errors)
if errors:
    raise SystemExit(2)
