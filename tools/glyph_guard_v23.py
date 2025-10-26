#!/usr/bin/env python3
import argparse, os, sys, json, re, subprocess, yaml

POLICY = "policy/glyph.yaml"

def load_policy():
    if os.path.exists(POLICY):
        return yaml.safe_load(open(POLICY)) or {}
    return {"max_steps":16,"deny_emojis":["💣","🧨"],"deny_patterns":[]}

def load_maps():
    maps = {}
    for f in ("codex/glyphs/xtgs.yaml","codex/glyphs/tsg.yaml","codex/glyphs/tgs.yaml"):
        if os.path.exists(f):
            maps.update(yaml.safe_load(open(f)))
    maps.setdefault("🌞","invoke"); maps.setdefault("🌀","verify"); maps.setdefault("🌈","deploy"); maps.setdefault("🧾","audit")
    maps.setdefault("🔮","attest"); maps.setdefault("🛡","scan"); maps.setdefault("🛡‍🔥","sanctify"); maps.setdefault("🚦","rollout"); maps.setdefault("⚖️","judge")
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
    if len(acts) > int(pol.get("max_steps",16)):
        return False, {"policy":"too_many_steps"}
    for pat in pol.get("deny_patterns",[]):
        import re
        if re.search(pat, text, flags=re.I):
            return False, {"policy":"deny_pattern", "pattern": pat}
    needed = ["verify","invoke","audit","scan","attest","sanctify","rollout","judge","deploy"]
    seq = [a for a in acts if a in needed]
    if seq != needed[:len(seq)]:
        return False, {"policy":"bad_sequence","have":seq,"want":needed}
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
    print(json.dumps({"steps":acts}, indent=2))
    if args.dry_run: return
    for a in acts:
        cmd=actions[a]["cmd"]
        rc=subprocess.call(cmd)
        if rc!=0:
            print(json.dumps({"error":"action_failed","action":a,"rc":rc}), file=sys.stderr)
            sys.exit(rc)

if __name__=="__main__": main()
