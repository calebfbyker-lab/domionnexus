#!/usr/bin/env python3
import argparse, yaml, re, json, subprocess, sys, os

maps = {}
glyph_files = [
    'codex/glyphs/xtgs.yaml',
    'codex/glyphs/tsg.yaml',
    'codex/glyphs/tgs.yaml',
]
for f in glyph_files:
    if not os.path.exists(f):
        continue
    with open(f, 'r') as fh:
        data = yaml.safe_load(fh) or {}
        maps.update(data)

def parse(glyphs: str):
    toks = [t.strip() for t in re.split(r"[;\n]+", glyphs) if t.strip()]
    out = []
    for t in toks:
        ch = t[0]
        mapped = maps.get(ch)
        if mapped:
            out.append(mapped)
        else:
            # fallback: first token word lowercased
            out.append(t.split()[0].lower())
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glyph", required=True)
    ap.add_argument("--dry-run", action='store_true')
    args = ap.parse_args()
    acts = parse(args.glyph)
    actions = {}
    if os.path.exists('plugins/manifest.json'):
        try:
            actions = json.load(open('plugins/manifest.json')).get('actions', {})
        except Exception:
            actions = {}
    for a in acts:
        if a not in actions:
            print(f"unknown glyph action: {a}", file=sys.stderr)
            sys.exit(3)
    print(json.dumps([{"step": a} for a in acts], indent=2))
    if args.dry_run:
        return
    for a in acts:
        cmd = actions[a]["cmd"]
        print("→", " ".join(cmd))
        rc = subprocess.call(cmd)
        if rc != 0:
            sys.exit(rc)

if __name__ == '__main__':
    main()
