#!/usr/bin/env python3
import argparse, os, sys, json, re, subprocess

def load_maps():
    maps = {}
    try:
        import yaml
    except Exception:
        yaml = None
    for f in ("codex/glyphs/xtgs.yaml","codex/glyphs/tsg.yaml","codex/glyphs/tgs.yaml"):
        if os.path.exists(f) and yaml:
            maps.update(yaml.safe_load(open(f)))
    maps.setdefault("🌞","invoke"); maps.setdefault("🌀","verify"); maps.setdefault("🌈","deploy"); maps.setdefault("🧾","audit")
    return maps

def parse(glyph, maps):
    toks=[t.strip() for t in re.split(r"[;\n]+", glyph) if t.strip()]
    acts=[]
    for t in toks:
        if t and t[0] in maps:
            acts.append(maps[t[0]]); continue
        head=t.split()[0].lower(); acts.append(head)
    return acts

def apply_limits():
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (30,30))
        try: resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
        except Exception: pass
        resource.setrlimit(resource.RLIMIT_CORE, (0,0))
    except Exception:
        pass

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--glyph", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args=ap.parse_args()
    maps=load_maps()
    actions=json.load(open("plugins/manifest.json"))["actions"]
    acts=parse(args.glyph, maps)

    deny_emoji=set(["💣","🧨"])
    if any(ch in args.glyph for ch in deny_emoji):
        print(json.dumps({"deny":"emoji"}), file=sys.stderr); sys.exit(3)
    if len(acts)>12:
        print(json.dumps({"deny":"too_many_steps"}), file=sys.stderr); sys.exit(3)
    for a in acts:
        if a not in actions:
            print(json.dumps({"error":"unknown_action","action":a}), file=sys.stderr); sys.exit(2)

    dag=[{"step":a} for a in acts]
    print(json.dumps(dag, indent=2))
    if args.dry_run: return

    for a in acts:
        cmd=actions[a]["cmd"]
        pid=os.fork()
        if pid==0:
            try:
                apply_limits()
                os.execvp(cmd[0], cmd)
            except Exception as e:
                print("exec error:", e, file=sys.stderr)
                os._exit(111)
        else:
            _,status=os.waitpid(pid,0)
            if status!=0: sys.exit(os.WEXITSTATUS(status))

if __name__=="__main__": main()
