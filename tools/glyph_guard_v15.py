#!/usr/bin/env python3
import argparse, os, sys, json, re, subprocess, yaml, time

POLICY_FILE = "policy/glyph.yaml"
_last_mtime = 0
_cached_policy = None

def load_policy():
    global _last_mtime, _cached_policy
    try:
        m = os.path.getmtime(POLICY_FILE)
        if not _cached_policy or m != _last_mtime:
            _cached_policy = yaml.safe_load(open(POLICY_FILE)) or {}
            _last_mtime = m
    except Exception:
        _cached_policy = {"max_steps":10,"deny_emojis":["💣","🧨"],"deny_patterns":[]}
    return _cached_policy

def load_maps():
    maps = {}
    for f in ("codex/glyphs/xtgs.yaml","codex/glyphs/tsg.yaml","codex/glyphs/tgs.yaml"):
        if os.path.exists(f):
            maps.update(yaml.safe_load(open(f)))
    maps.setdefault("🌞","invoke"); maps.setdefault("🌀","verify"); maps.setdefault("🌈","deploy"); maps.setdefault("🧾","audit")
    maps.setdefault("🔮","attest"); maps.setdefault("🛡","scan")
    return maps

def parse(glyph, maps):
    toks=[t.strip() for t in re.split(r"[;\n]+", glyph) if t.strip()]
    acts=[]
    for t in toks:
        if t and t[0] in maps: acts.append(maps[t[0]]); continue
        head=t.split()[0].lower(); acts.append(head)
    return acts

def enforce_policy(text, acts, pol):
    if any(ch in text for ch in pol.get("deny_emojis",[])):
        return False, {"policy":"deny_emoji"}
    if len(acts) > int(pol.get("max_steps",10)):
        return False, {"policy":"too_many_steps"}
    for pat in pol.get("deny_patterns",[]):
        if re.search(pat, text, flags=re.I):
            return False, {"policy":"deny_pattern", "pattern": pat}
    return True, {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--glyph", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args=ap.parse_args()
    pol=load_policy()
    maps=load_maps()
    actions=json.load(open("plugins/manifest.json"))["actions"]
    acts=parse(args.glyph, maps)
    ok, why=enforce_policy(args.glyph, acts, pol)
    if not ok:
        print(json.dumps(why), file=sys.stderr); sys.exit(3)
    for a in acts:
        if a not in actions:
            print(json.dumps({"error":"unknown_action","action":a}), file=sys.stderr); sys.exit(2)
    dag=[{"step":a} for a in acts]
    print(json.dumps(dag, indent=2))
    if args.dry_run: return
    for a in acts:
        cmd=actions[a]["cmd"]
        rc=subprocess.call(cmd)
        if rc!=0: sys.exit(rc)
if __name__=="__main__": main()
