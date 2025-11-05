#!/usr/bin/env python3
import os, json, zipfile, hashlib, time, sys
root = os.path.dirname(os.path.dirname(__file__))
out = os.path.join(root, f"codex_omega_{int(time.time())}.zip")
digests={}
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
  for dp,_,fs in os.walk(root):
    # skip venvs and build dirs
    if any(p in dp for p in (".venv","__pycache__",".git",".github/workflows")): continue
    for n in fs:
      p=os.path.join(dp,n)
      rel=os.path.relpath(p, root)
      with open(p,"rb") as f: b=f.read()
      digests[rel]=hashlib.sha256(b).hexdigest()
      z.writestr(rel, b)
meta={"subject":"caleb fedor byker konev|1998-10-27","subject_id_sha256":hashlib.sha256(b"caleb fedor byker konev|1998-10-27").hexdigest(),"digests":digests}
open(os.path.join(root,"codex_release_provenance.json"),"w").write(json.dumps(meta,indent=2))
print(out)
