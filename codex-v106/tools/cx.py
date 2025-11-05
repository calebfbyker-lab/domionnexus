#!/usr/bin/env python3
import os, json, urllib.request, sys
ORCH=os.environ.get("CODEX_ORCH_URL","http://localhost:8010")
cmd=sys.argv[1] if len(sys.argv)>1 else "help"
def call(path, body=None):
  req=urllib.request.Request(ORCH+path, data=(json.dumps(body).encode() if body else None), headers={"Content-Type":"application/json"})
  return json.loads(urllib.request.urlopen(req, timeout=8).read())
if cmd=="run":
  glyph=sys.argv[2] if len(sys.argv)>2 else "🌀; 🌞; 🧾; 🛡; 🔮; 🛡‍🔥; 🚦; ⚖️; 🌈; ♾"
  print(json.dumps(call("/runs", {"tenant":"cfbk","prio":9,"glyph":glyph}), indent=2))
elif cmd=="tail":
  n=int(sys.argv[2]) if len(sys.argv)>2 else 10
  print(json.dumps(call(f"/events/tail?n={n}"), indent=2))
else:
  print("cx.py run [glyph] | tail [n]")
