#!/usr/bin/env python3
import argparse, os, sys, json, re, subprocess, yaml, hashlib

POLICY = "policy/glyph.yaml"
CHAIN = "chain.jsonl"


def load_policy():
    if os.path.exists(POLICY):
        return yaml.safe_load(open(POLICY)) or {}
    return {"max_steps":16, "deny_emojis":["💣","🧨"], "deny_patterns":[]}


def load_maps():
    maps = {}
    for f in ("codex/glyphs/xtgs.yaml", "codex/glyphs/tsg.yaml", "codex/glyphs/tgs.yaml"):
        if os.path.exists(f):
            maps.update(yaml.safe_load(open(f)))
    # defaults
    maps.setdefault("🌞", "invoke"); maps.setdefault("🌀", "verify"); maps.setdefault("🧾", "audit")
    maps.setdefault("🛡", "scan"); maps.setdefault("🔮", "attest"); maps.setdefault("🛡‍🔥", "sanctify")
    maps.setdefault("🚦", "rollout"); maps.setdefault("⚖️", "judge"); maps.setdefault("🌈", "deploy"); maps.setdefault("♾", "continuum")
    return maps


def parse(glyph, maps):
    toks = [t.strip() for t in re.split(r"[;\n]+", glyph) if t.strip()]
    acts = []
    for t in toks:
        if t and t[0] in maps:
            acts.append(maps[t[0]]);
            continue
        head = t.split()[0].lower(); acts.append(head)
    return acts


def enforce_policy(text, acts, pol):
    if any(ch in text for ch in pol.get("deny_emojis", [])):
        return False, {"policy":"deny_emoji"}
    if len(acts) > int(pol.get("max_steps", 16)):
        return False, {"policy":"too_many_steps"}
    for pat in pol.get("deny_patterns", []):
        if re.search(pat, text, flags=re.I):
            return False, {"policy":"deny_pattern", "pattern": pat}
    needed = ["verify","invoke","audit","scan","attest","sanctify","rollout","judge","deploy","continuum"]
    seq = [a for a in acts if a in needed]
    if seq != needed[:len(seq)]:
        return False, {"policy":"bad_sequence", "have": seq, "want": needed}
    return True, {}


def head():
    try:
        last = None
        with open(CHAIN, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip(): last = json.loads(line)
        return (last or {}).get("current") or "0" * 64
    except FileNotFoundError:
        return "0" * 64


def append(prev, current, meta):
    with open(CHAIN, "a", encoding="utf-8") as f:
        f.write(json.dumps({"prev": prev, "current": current, "meta": meta}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glyph", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    pol = load_policy(); maps = load_maps()
    actions = json.load(open("plugins/manifest.json"))["actions"]
    acts = parse(args.glyph, maps)
    ok, why = enforce_policy(args.glyph, acts, pol)
    if not ok:
        print(json.dumps(why), file=sys.stderr); sys.exit(3)
    print(json.dumps({"steps":acts}, indent=2))
    if args.dry_run: return
    prev = head()
    for a in acts:
        cmd = actions[a]["cmd"]
        cmd_hash = hashlib.sha256((" ".join(cmd)).encode()).hexdigest()
        current = hashlib.sha256((prev + cmd_hash).encode()).hexdigest()
        rc = subprocess.call(cmd)
        if rc != 0:
            print(json.dumps({"error":"action_failed","action":a,"rc":rc}), file=sys.stderr)
            sys.exit(rc)
        append(prev, current, {"action": a, "cmd": cmd})
        prev = current

if __name__ == "__main__":
    main()
