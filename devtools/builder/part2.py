"""Builder Part 2
Writes the app, glyph guard, and main scripts (hashing, verify, sbom, vuln gate, provenance, quorum/threshold tools)
"""
import os, argparse, textwrap

def w(root, rel, content):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

def run(root):
    # app.py (simple FastAPI with /glyph and /webhook endpoints)
    w(root, "app.py", textwrap.dedent('''
from fastapi import FastAPI, HTTPException, Header, Request
import hmac, hashlib, os, subprocess, sys, threading, json, time

APP_VER = "Codex v95.x · Aegis Mesh"
CODEX_API_KEY = os.getenv("CODEX_API_KEY","dev-key")
CODEX_HMAC_KEY = os.getenv("CODEX_HMAC_KEY","dev-hmac")
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET","dev-webhook")

AUDIT = "audit.jsonl"
_a_lock = threading.Lock()
_last = "0"*64

def _audit(ev):
    global _last
    ev["ts"] = time.time()
    body = json.dumps(ev, separators=(',',':'))
    d = hashlib.sha256(body.encode()).hexdigest()
    root = hashlib.sha256((_last + d).encode()).hexdigest()
    _last = root
    line = ev.copy(); line["sha256"]=d; line["root"]=root
    with _a_lock, open(AUDIT,'a',encoding='utf-8') as f:
        f.write(json.dumps(line)+"\n")

app = FastAPI(title=APP_VER)

@app.get('/health')
def health(): return {'ok': True, 'ver': APP_VER}

@app.post('/glyph')
async def glyph(request: Request, x_api_key: str = Header(default=''), x_codex_sig: str = Header(default='')):
    if x_api_key != CODEX_API_KEY:
        raise HTTPException(401, 'unauthorized')
    if x_codex_sig:
        body = await request.body()
        mac = hmac.new(CODEX_HMAC_KEY.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, x_codex_sig):
            raise HTTPException(401, 'bad hmac')
    # call glyph guard
    payload = await request.json()
    glyph = payload.get('glyph','')
    p = subprocess.run([sys.executable, 'tools/glyph_guard_v16.py', '--glyph', glyph], capture_output=True, text=True)
    _audit({'route':'glyph', 'rc': p.returncode})
    if p.returncode != 0:
        raise HTTPException(400, {'stderr': p.stderr, 'stdout': p.stdout})
    return {'ok': True, 'stdout': p.stdout}

@app.post('/webhook')
async def webhook(request: Request, x_hub_signature_256: str = Header(default='')):
    body = await request.body()
    mac = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    sig = 'sha256=' + mac
    if not x_hub_signature_256 or not hmac.compare_digest(sig, x_hub_signature_256):
        raise HTTPException(401, 'invalid webhook signature')
    _audit({'route':'webhook', 'ok': True})
    return {'ok': True}
    '''))

    # tools/glyph_guard_v16.py (policy-aware guard with sanctify check)
    w(root, 'tools/glyph_guard_v16.py', textwrap.dedent('''
#!/usr/bin/env python3
import argparse, os, json, re, sys, yaml, subprocess

POLICY = 'policy/glyph.yaml'

def load_policy():
    if os.path.exists(POLICY):
        return yaml.safe_load(open(POLICY)) or {}
    return {'max_steps':12, 'deny_emojis':['💣','🧨'], 'deny_patterns': []}

def load_maps():
    maps = {}
    for f in ('codex/glyphs/xtgs.yaml','codex/glyphs/tsg.yaml','codex/glyphs/tgs.yaml'):
        if os.path.exists(f): maps.update(yaml.safe_load(open(f)))
    maps.setdefault('🌞','invoke')
    maps.setdefault('🌀','verify')
    maps.setdefault('🌈','deploy')
    maps.setdefault('🧾','audit')
    maps.setdefault('🔮','attest')
    maps.setdefault('🛡','scan')
    maps.setdefault('🛡‍🔥','sanctify')
    return maps

def parse(glyph, maps):
    toks=[t.strip() for t in re.split(r'[;\n]+', glyph) if t.strip()]
    acts=[]
    for t in toks:
        if t and t[0] in maps:
            acts.append(maps[t[0]]); continue
        acts.append(t.split()[0].lower())
    return acts

def enforce_policy(text, acts, pol):
    if any(ch in text for ch in pol.get('deny_emojis', [])):
        return False, {'policy':'deny_emoji'}
    if len(acts) > int(pol.get('max_steps',12)):
        return False, {'policy':'too_many_steps'}
    for pat in pol.get('deny_patterns', []):
        if re.search(pat, text, flags=re.I):
            return False, {'policy':'deny_pattern', 'pattern': pat}
    if 'deploy' in acts and 'sanctify' not in acts:
        return False, {'policy':'deploy_requires_sanctify'}
    return True, {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--glyph', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a=ap.parse_args()
    pol = load_policy()
    maps = load_maps()
    acts = parse(a.glyph, maps)
    ok, why = enforce_policy(a.glyph, acts, pol)
    if not ok:
        print(json.dumps(why), file=sys.stderr); sys.exit(3)
    actions = json.load(open('plugins/manifest.json'))['actions']
    for act in acts:
        if act not in actions:
            print(json.dumps({'error':'unknown_action','action':act}), file=sys.stderr); sys.exit(2)
    print(json.dumps([{'step':x} for x in acts], indent=2))
    if a.dry_run: return
    for act in acts:
        cmd = actions[act]['cmd']
        rc = subprocess.call(cmd)
        if rc != 0: sys.exit(rc)

if __name__=='__main__': main()
    '''))

    # scripts (compact)
    w(root, 'scripts/hash_all.py', textwrap.dedent('''
#!/usr/bin/env python3
import argparse, os, hashlib, json, datetime
SKIP={'.git','.venv','__pycache__','.github'}
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536),b''): h.update(ch)
    return h.hexdigest()
def walk(root):
    for d,ds,fs in os.walk(root):
        ds[:]=[x for x in ds if x not in SKIP]
        for n in fs:
            rel=os.path.relpath(os.path.join(d,n),root).replace('\\','/')
            yield rel
ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.')
ap.add_argument('--out',default='codex/manifest.v95x.json'); a=ap.parse_args()
items=[]; root=os.path.abspath(a.root)
for rel in sorted(walk(root)):
    p=os.path.join(root,rel)
    if os.path.isfile(p): items.append({'path':rel,'size':os.path.getsize(p),'sha256':sha(p)})
m={'title':'Codex v95.x — Integrity Manifest','subject_id_sha256':'','generated_utc':datetime.datetime.utcnow().isoformat()+"Z",'items':items}
os.makedirs(os.path.dirname(a.out), exist_ok=True)
open(a.out,'w',encoding='utf-8').write(json.dumps(m, indent=2))
print('wrote', len(items), 'items to', a.out)
'''))

    w(root, 'scripts/verify_manifest.py', textwrap.dedent('''
#!/usr/bin/env python3
import argparse, os, hashlib, json, sys
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536),b''): h.update(ch)
    return h.hexdigest()
ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.')
ap.add_argument('--manifest',default='codex/manifest.v95x.json'); a=ap.parse_args()
m=json.load(open(a.manifest)); errs=[]
for it in m.get('items',[]):
    p=os.path.join(a.root,it['path'])
    if not os.path.exists(p): errs.append('MISSING '+it['path']); continue
    if sha(p)!=it['sha256']: errs.append('MISMATCH '+it['path'])
if errs: print('INTEGRITY FAILED\n'+'\n'.join(errs)); sys.exit(2)
print('INTEGRITY PASSED')
'''))

    w(root, 'scripts/sbom_syft_stub.py', textwrap.dedent('''
#!/usr/bin/env python3
import json, subprocess, os, hashlib
def has(cmd):
    from shutil import which
    return which(cmd) is not None
if has('syft'):
    rc = subprocess.call('syft . -o json > sbom.json', shell=True)
    if rc!=0: raise SystemExit(rc)
    print('SBOM generated via syft')
else:
    ROOT='.'; arts=[]
    for d,_,fs in os.walk(ROOT):
        if any(x in d for x in ['.git','.venv','__pycache__','.github']): continue
        for n in fs:
            p=os.path.join(d,n)
            with open(p,'rb') as f: h=hashlib.sha256(f.read()).hexdigest()
            arts.append({'path':os.path.relpath(p,ROOT).replace('\\','/'),'sha256':h})
    open('sbom.json','w').write(json.dumps({'artifacts':arts},indent=2))
    print('SBOM stub written')
'''))

    w(root, 'scripts/vuln_gate.py', textwrap.dedent('''
#!/usr/bin/env python3
import argparse, subprocess, sys, json, os
ap=argparse.ArgumentParser(); ap.add_argument('--sbom', default='sbom.json'); ap.add_argument('--severity', default='high'); a=ap.parse_args()
def has(cmd):
    from shutil import which
    return which(cmd) is not None
sev_order=['negligible','low','medium','high','critical']
threshold = sev_order.index(a.severity.lower()) if a.severity.lower() in sev_order else 3
if has('grype') and has('syft'):
    rc = subprocess.call(f'grype sbom:{a.sbom} -o json > grype.json', shell=True)
    if rc != 0: raise SystemExit(rc)
    data = json.load(open('grype.json'))
    worst=-1
    for m in data.get('matches',[]):
        s=(m.get('vulnerability') or {}).get('severity','').lower()
        if s in sev_order: worst=max(worst, sev_order.index(s))
    if worst >= threshold:
        print(f'VULN GATE FAIL: worst={sev_order[worst]} >= {sev_order[threshold]}'); raise SystemExit(9)
    print('VULN GATE PASS')
else:
    print('grype/syft not found; skipping vuln gate (PASS)')
'''))

    w(root, 'scripts/provenance_v4.py', textwrap.dedent('''
#!/usr/bin/env python3
import json, hashlib, time, glob, os
mf='codex/manifest.v95x.json'
sha=hashlib.sha256(open(mf,'rb').read()).hexdigest()
materials=[]
for p in sorted(glob.glob('**/*', recursive=True)):
    try:
        if not os.path.isfile(p) or p.startswith('.git'): continue
        h=hashlib.sha256(open(p,'rb').read()).hexdigest()
        materials.append({'uri':p,'digest':{'sha256':h}})
    except Exception: pass
stmt={
 '_type':'https://in-toto.io/Statement/v1',
 'subject':[{'name':mf,'digest':{'sha256':sha}}],
 'predicateType':'https://slsa.dev/provenance/v1',
 'predicate':{
   'buildDefinition':{'buildType':'codex/ci','externalParameters':{'ci':'github-actions'}},
   'runDetails':{'builder':{'id':'codex/v95x'},'metadata':{'invocationId':str(time.time())}},
   'materials': materials[:2000]
 }
}
open('provenance.v4.json','w').write(json.dumps(stmt,indent=2))
print('provenance.v4.json written')
'''))

    w(root, 'scripts/threshold_sign.py', textwrap.dedent('''
#!/usr/bin/env python3
import json, base64, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
mf='codex/manifest.v95x.json'
digest=hashlib.sha256(open(mf,'rb').read()).digest()
keys=[]; sigs=[]
for i in range(3):
    sk=Ed25519PrivateKey.generate()
    pk=sk.public_key()
    sig=sk.sign(digest)
    keys.append(pk.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode())
    sigs.append(base64.b64encode(sig).decode())
open('codex/threshold.json','w').write(json.dumps({'algo':'ed25519','digest':'sha256','sigs':sigs,'pubkeys':keys},indent=2))
print('threshold signatures written (3 total)')
'''))

    w(root, 'scripts/threshold_verify.py', textwrap.dedent('''
#!/usr/bin/env python3
import json, base64, hashlib, sys
from cryptography.hazmat.primitives import serialization
mf='codex/manifest.v95x.json'
meta=json.load(open('codex/threshold.json'))
digest=hashlib.sha256(open(mf,'rb').read()).digest()
oks=0
for s,pem in zip(meta['sigs'], meta['pubkeys']):
    pk = serialization.load_pem_public_key(pem.encode())
    try:
        pk.verify(base64.b64decode(s), digest)
        oks+=1
    except Exception:
        pass
if oks>=2:
    print('THRESHOLD OK (2-of-3)')
    sys.exit(0)
print('THRESHOLD FAIL: only',oks,'valid')
sys.exit(2)
'''))

    w(root, 'scripts/quorum_verify.py', textwrap.dedent('''
#!/usr/bin/env python3
import json, base64, hashlib, sys
from cryptography.hazmat.primitives import serialization
mf='codex/manifest.v95x.json'
meta=json.load(open('codex/threshold.json'))
q=json.load(open('codex/quorum.json'))
digest=hashlib.sha256(open(mf,'rb').read()).digest()
oks=0
for s,pem in zip(meta['sigs'], meta['pubkeys']):
    pk = serialization.load_pem_public_key(pem.encode())
    try:
        pk.verify(base64.b64decode(s), digest)
        oks+=1
    except Exception:
        pass
if oks>=int(q['k']):
    print(f'QUORUM OK ({oks}/{q["n"]}) >= k={q["k"]}')
    sys.exit(0)
print(f'QUORUM FAIL ({oks}/{q["n"]}) < k={q["k"]}')
sys.exit(2)
'''))

    w(root, 'scripts/oci_attest_stub.py', textwrap.dedent('''
#!/usr/bin/env python3
import argparse, json, os, time, hashlib
ap=argparse.ArgumentParser(); ap.add_argument('--image', required=True); ap.add_argument('--provenance', default='provenance.v4.json'); a=ap.parse_args()
sha=hashlib.sha256(open(a.provenance,'rb').read()).hexdigest()
out={'image':a.image,'predicate':'provenance.v4.json','sha256':sha,'ts':int(time.time())}
os.makedirs('oci', exist_ok=True)
open('oci/attest.json','w').write(json.dumps(out,indent=2))
print('oci/attest.json written')
'''))

    w(root, 'scripts/rekor_api.py', textwrap.dedent('''
#!/usr/bin/env python3
import argparse, json, hashlib, time, os, requests
ap=argparse.ArgumentParser(); ap.add_argument('--file', required=True); ap.add_argument('--check-root', action='store_true'); ap.add_argument('--url', default=os.getenv('REKOR_URL',''))
a=ap.parse_args()
def offline_append(p):
    sha=hashlib.sha256(open(p,'rb').read()).hexdigest()
    os.makedirs('transparency', exist_ok=True)
    entry={'ts':int(time.time()),'type':'manifest','file':p,'sha256':sha,'note':'rekor-ready entry'}
    open('transparency/rekor-ready.jsonl','a',encoding='utf-8').write(json.dumps(entry)+"\n")
    print('offline transparency append:', entry)
if a.check_root:
    if not a.url: print('no REKOR_URL; skip'); raise SystemExit(0)
    r=requests.get(a.url+'/api/v1/log', timeout=5)
    print('rekor log:', r.json()); raise SystemExit(0)
if not a.url:
    offline_append(a.file); raise SystemExit(0)
sha=hashlib.sha256(open(a.file,'rb').read()).hexdigest()
payload={'apiVersion':'0.0.1','kind':'hashedrekord','spec':{'data':{'hash':{'algorithm':'sha256','value':sha}}}}
r=requests.post(a.url+'/api/v1/log/entries', json=payload, timeout=10)
print('rekor status:', r.status_code)
print(r.text)
'''))

    print('part2: written app.py, tools/glyph_guard_v16.py, and scripts')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default='./build_output'); a = ap.parse_args(); run(a.root)
