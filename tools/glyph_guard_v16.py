
#!/usr/bin/env python3
import argparse, os, json, re, sys, yaml, subprocess

POLICY = 'policy/glyph.yaml'

def load_policy():
    if os.path.exists(POLICY):
        return yaml.safe_load(open(POLICY)) or {}
    return {'max_steps':12, 'deny_emojis':['💣','🧨'], 'deny_patterns': []}

def load_maps():
    maps = {}
    for f in ('codex/glyphs/xtgs.yaml','codex/glyphs/tsg.yaml','codex/glyphs/tgs.yaml'):
        if os.path.exists(f): maps.update(yaml.safe_load(open(f)))
    maps.setdefault('🌞','invoke')
    maps.setdefault('🌀','verify')
    maps.setdefault('🌈','deploy')
    maps.setdefault('🧾','audit')
    maps.setdefault('🔮','attest')
    maps.setdefault('🛡','scan')
    maps.setdefault('🛡‍🔥','sanctify')
    return maps

def parse(glyph, maps):
    toks=[t.strip() for t in re.split(r'[;
]+', glyph) if t.strip()]
    acts=[]
    for t in toks:
        if t and t[0] in maps:
            acts.append(maps[t[0]]); continue
        acts.append(t.split()[0].lower())
    return acts

def enforce_policy(text, acts, pol):
    if any(ch in text for ch in pol.get('deny_emojis', [])):
        return False, {'policy':'deny_emoji'}
    if len(acts) > int(pol.get('max_steps',12)):
        return False, {'policy':'too_many_steps'}
    for pat in pol.get('deny_patterns', []):
        if re.search(pat, text, flags=re.I):
            return False, {'policy':'deny_pattern', 'pattern': pat}
    if 'deploy' in acts and 'sanctify' not in acts:
        return False, {'policy':'deploy_requires_sanctify'}
    return True, {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--glyph', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a=ap.parse_args()
    pol = load_policy()
    maps = load_maps()
    acts = parse(a.glyph, maps)
    ok, why = enforce_policy(a.glyph, acts, pol)
    if not ok:
        print(json.dumps(why), file=sys.stderr); sys.exit(3)
    actions = json.load(open('plugins/manifest.json'))['actions']
    for act in acts:
        if act not in actions:
            print(json.dumps({'error':'unknown_action','action':act}), file=sys.stderr); sys.exit(2)
    print(json.dumps([{'step':x} for x in acts], indent=2))
    if a.dry_run: return
    for act in acts:
        cmd = actions[act]['cmd']
        rc = subprocess.call(cmd)
        if rc != 0: sys.exit(rc)

if __name__=='__main__': main()
