#!/usr/bin/env python3
import argparse, json, hashlib, time, os, requests
ap=argparse.ArgumentParser()
ap.add_argument("--file", required=True)
ap.add_argument("--check-root", action="store_true")
ap.add_argument("--url", default=os.getenv("REKOR_URL",""))
a=ap.parse_args()
def offline_append(p):
    sha=hashlib.sha256(open(p,"rb").read()).hexdigest()
    os.makedirs("transparency", exist_ok=True)
    entry={"ts":int(time.time()),"type":"manifest","file":p,"sha256":sha,"note":"rekor-ready entry"}
    open("transparency/rekor-ready.jsonl","a",encoding="utf-8").write(json.dumps(entry)+"\n")
    print("offline transparency append:", entry)
if a.check_root:
    if not a.url: print("no REKOR_URL; skip"); raise SystemExit(0)
    r=requests.get(a.url+"/api/v1/log", timeout=5)
    print("rekor log:", r.json()); raise SystemExit(0)
if not a.url:
    offline_append(a.file); raise SystemExit(0)
sha=hashlib.sha256(open(a.file,"rb").read()).hexdigest()
payload={"apiVersion":"0.0.1","kind":"hashedrekord","spec":{"data":{"hash":{"algorithm":"sha256","value":sha}}}}
r=requests.post(a.url+"/api/v1/log/entries", json=payload, timeout=10)
print("rekor status:", r.status_code)
print(r.text)
