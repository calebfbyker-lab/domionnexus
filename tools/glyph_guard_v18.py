#!/usr/bin/env python3
"""Glyph Guard v18 - Enhanced for Codex v96 · Aletheia
Features:
- Nonce tracking for replay protection
- Sanctify requirement for deploy actions
- Hot-reloadable policy
- Enhanced audit trail
"""
import argparse, os, sys, json, re, subprocess, yaml, time, hashlib

POLICY_FILE = "policy/glyph.yaml"
NONCE_DB = "policy/nonces.json"
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
        _cached_policy = {"max_steps":12,"deny_emojis":["💣","🧨"],"deny_patterns":[]}
    return _cached_policy

def load_maps():
    maps = {}
    for f in ("codex/glyphs/xtgs.yaml","codex/glyphs/tsg.yaml","codex/glyphs/tgs.yaml"):
        if os.path.exists(f):
            maps.update(yaml.safe_load(open(f)))
    maps.setdefault("🌞","invoke"); maps.setdefault("🌀","verify"); maps.setdefault("🌈","deploy"); maps.setdefault("🧾","audit")
    maps.setdefault("🔮","attest"); maps.setdefault("🛡","scan"); maps.setdefault("🛡‍🔥","sanctify")
    return maps

def parse(glyph, maps):
    toks=[t.strip() for t in re.split(r"[;\n]+", glyph) if t.strip()]
    acts=[]
    for t in toks:
        if t and t[0] in maps: acts.append(maps[t[0]]); continue
        head=t.split()[0].lower() if t.split() else t.lower(); acts.append(head)
    return acts

def check_nonce(nonce):
    """Check and record nonce to prevent replay attacks"""
    if nonce == "none" or not nonce:
        return True  # Allow 'none' for testing
    
    try:
        if os.path.exists(NONCE_DB):
            with open(NONCE_DB, 'r') as f:
                used = json.load(f)
        else:
            used = {"nonces": []}
        
        nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()
        if nonce_hash in used.get("nonces", []):
            return False
        
        used.setdefault("nonces", []).append(nonce_hash)
        # Keep only last 10000 nonces
        if len(used["nonces"]) > 10000:
            used["nonces"] = used["nonces"][-10000:]
        
        os.makedirs(os.path.dirname(NONCE_DB), exist_ok=True)
        with open(NONCE_DB, 'w') as f:
            json.dump(used, f)
        return True
    except Exception as e:
        print(json.dumps({"error":"nonce_check_failed","detail":str(e)}), file=sys.stderr)
        return True  # Fail open in case of errors

def enforce_policy(text, acts, pol):
    if any(ch in text for ch in pol.get("deny_emojis",[])):
        return False, {"policy":"deny_emoji"}
    if len(acts) > int(pol.get("max_steps",12)):
        return False, {"policy":"too_many_steps","max":pol.get("max_steps",12),"got":len(acts)}
    for pat in pol.get("deny_patterns",[]):
        if re.search(pat, text, flags=re.I):
            return False, {"policy":"deny_pattern", "pattern": pat}
    # v96 enhancement: deploy requires sanctify
    if "deploy" in acts and "sanctify" not in acts:
        return False, {"policy":"deploy_requires_sanctify"}
    return True, {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--glyph", required=True)
    ap.add_argument("--nonce", default="none", help="Nonce for replay protection")
    ap.add_argument("--dry-run", action="store_true")
    args=ap.parse_args()
    
    # Check nonce
    if not check_nonce(args.nonce):
        print(json.dumps({"error":"nonce_replay","nonce":args.nonce}), file=sys.stderr)
        sys.exit(4)
    
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
    dag=[{"step":a,"nonce":args.nonce} for a in acts]
    print(json.dumps({"actions":dag,"nonce":args.nonce,"timestamp":time.time()}, indent=2))
    if args.dry_run: return
    for a in acts:
        cmd=actions[a]["cmd"]
        rc=subprocess.call(cmd)
        if rc!=0: sys.exit(rc)

if __name__=="__main__": main()
