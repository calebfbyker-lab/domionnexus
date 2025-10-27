#!/usr/bin/env python3
import argparse, json, hashlib, time, os
ap=argparse.ArgumentParser(); ap.add_argument("--file", required=True); a=ap.parse_args()
sha=hashlib.sha256(open(a.file,"rb").read()).hexdigest()
os.makedirs("transparency", exist_ok=True)
entry={"ts":int(time.time()),"type":"manifest","file":a.file,"sha256":sha,"note":"rekor-ready entry"}
open("transparency/rekor-ready.jsonl","a",encoding="utf-8").write(json.dumps(entry)+"\n")
print("rekor-ready append:", entry)
