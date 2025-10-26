#!/usr/bin/env python3
import json, hashlib, time, glob, os
mf="codex/manifest.v94x.json"
sha=hashlib.sha256(open(mf,"rb").read()).hexdigest()
materials=[]
for p in sorted(glob.glob("**/*", recursive=True)):
    try:
        if not os.path.isfile(p) or p.startswith(".git"): continue
        h=hashlib.sha256(open(p,"rb").read()).hexdigest()
        materials.append({"uri":p,"digest":{"sha256":h}})
    except Exception: pass
stmt={
 "_type":"https://in-toto.io/Statement/v1",
 "subject":[{"name":mf,"digest":{"sha256":sha}}],
 "predicateType":"https://slsa.dev/provenance/v1",
 "predicate":{
   "buildDefinition":{"buildType":"codex/ci","externalParameters":{"ci":"github-actions"}},
   "runDetails":{"builder":{"id":"codex/v94x"},"metadata":{"invocationId":str(time.time())}},
   "materials": materials[:2000]
 }
}
open("provenance.v4.json","w").write(json.dumps(stmt,indent=2))
print("provenance.v4.json written")
