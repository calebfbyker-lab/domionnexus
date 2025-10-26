#!/usr/bin/env python3
import json, hashlib, time
mf="codex/manifest.v93.json"
sha=hashlib.sha256(open(mf,"rb").read()).hexdigest()
stmt={
 "_type":"https://in-toto.io/Statement/v1",
 "subject":[{"name":mf,"digest":{"sha256":sha}}],
 "predicateType":"https://slsa.dev/provenance/v1",
 "predicate":{
   "buildDefinition":{"buildType":"codex/ci","externalParameters":{"ci":"github-actions"}},
   "runDetails":{"builder":{"id":"codex/v93"},"metadata":{"invocationId":str(time.time())}}
 }
}
open("provenance.v3.json","w").write(json.dumps(stmt,indent=2))
print("provenance.v3.json written")
