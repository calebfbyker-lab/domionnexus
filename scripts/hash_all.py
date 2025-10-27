#!/usr/bin/env python3
import sys, json, os
os.makedirs('codex', exist_ok=True)
out = None
if '--out' in sys.argv:
	i = sys.argv.index('--out')
	if i+1 < len(sys.argv):
		out = sys.argv[i+1]
if not out:
	out = 'codex/manifest.v91x.json'

content = {'generated_by': 'hash_all.py', 'root': os.path.abspath('.')}
open(out, 'w').write(json.dumps(content, indent=2))
print(f'hash_all: wrote {out}')

