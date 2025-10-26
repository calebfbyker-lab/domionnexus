import hashlib, json, os

root = os.getcwd()
manifest = {"files": []}
for dirpath, dirnames, filenames in os.walk(root):
    # skip .git and node_modules
    if '.git' in dirpath:
        continue
    for fn in filenames:
        if fn.endswith('.pyc'):
            continue
        # Skip manifest.json itself to avoid self-reference
        if fn == 'manifest.json':
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, 'rb') as f:
                data = f.read()
            h = hashlib.sha256(data).hexdigest()
            manifest['files'].append({'path': os.path.relpath(path, root), 'sha256': h})
        except Exception:
            pass
with open('manifest.json', 'w') as fh:
    json.dump(manifest, fh, indent=2)
print('manifest.json written, %d entries' % len(manifest['files']))
