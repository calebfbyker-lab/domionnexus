
#!/usr/bin/env python3
import argparse, json, os, time, hashlib
ap=argparse.ArgumentParser(); ap.add_argument('--image', required=True); ap.add_argument('--provenance', default='provenance.v4.json'); a=ap.parse_args()
sha=hashlib.sha256(open(a.provenance,'rb').read()).hexdigest()
out={'image':a.image,'predicate':'provenance.v4.json','sha256':sha,'ts':int(time.time())}
os.makedirs('oci', exist_ok=True)
open('oci/attest.json','w').write(json.dumps(out,indent=2))
print('oci/attest.json written')
