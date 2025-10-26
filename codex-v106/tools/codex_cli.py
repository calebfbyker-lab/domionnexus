#!/usr/bin/env python3
import sys, json, urllib.request, os
ORCH=os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
cmd=sys.argv[1] if len(sys.argv)>1 else "help"
if cmd=="compile":
    glyph=sys.argv[2] if len(sys.argv)>2 else "🌀; 🌞; 🧾; 🛡; 🔮; 🛡‍🔥; 🚦; ⚖️; 🌈; ♾"
    body=json.dumps({"glyph":glyph}).encode()
    r=urllib.request.urlopen(urllib.request.Request(f"{ORCH}/workflows/compile", data=body, headers={"Content-Type":"application/json"}))
    print(r.read().decode())
elif cmd=="run":
    tenant=os.environ.get("CODEX_TENANT","public")
    glyph=sys.argv[2] if len(sys.argv)>2 else "🌀; 🌞; 🧾; 🛡; 🔮; 🛡‍🔥; 🚦; ⚖️; 🌈; ♾"
    body=json.dumps({"tenant":tenant,"glyph":glyph}).encode()
    r=urllib.request.urlopen(urllib.request.Request(f"{ORCH}/runs", data=body, headers={"Content-Type":"application/json"}))
    print(r.read().decode())
else:
    print("codex_cli.py compile|run [glyph...]")
