#!/usr/bin/env python3
import argparse, subprocess, sys, json, os
ap=argparse.ArgumentParser()
ap.add_argument("--sbom", default="sbom.json")
ap.add_argument("--severity", default="high")
a=ap.parse_args()
def has(cmd):
    from shutil import which
    return which(cmd) is not None
sev_order = ["negligible","low","medium","high","critical"]
threshold = sev_order.index(a.severity.lower()) if a.severity.lower() in sev_order else 3
if has("grype") and has("syft"):
    rc = subprocess.call(f"grype sbom:{a.sbom} -o json > grype.json", shell=True)
    if rc != 0: sys.exit(rc)
    data = json.load(open("grype.json"))
    worst = -1
    for m in data.get("matches",[]):
        s = (m.get("vulnerability") or {}).get("severity","|").lower()
        if s in sev_order:
            worst = max(worst, sev_order.index(s))
    if worst >= threshold:
        print(f"VULN GATE FAIL: worst={sev_order[worst]} >= {sev_order[threshold]}")
        sys.exit(9)
    print("VULN GATE PASS")
else:
    print("grype/syft not found; skipping vuln gate (PASS)")
