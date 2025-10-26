#!/usr/bin/env python3
import argparse, json, os, hashlib, time

KEYRING = 'secrets/keyring.json'
KEYLEDGER = 'secrets/keyledger.jsonl'

def load_keyring():
    try:
        return json.load(open(KEYRING,encoding='utf-8'))
    except Exception:
        return {'keys':{'default':'dev-hmac'}, 'active':'default'}

def save_keyring(r):
    os.makedirs(os.path.dirname(KEYRING), exist_ok=True)
    json.dump(r, open(KEYRING,'w',encoding='utf-8'), indent=2)

def append_ledger(kid, secret):
    os.makedirs(os.path.dirname(KEYLEDGER), exist_ok=True)
    prev=None
    try:
        with open(KEYLEDGER,'r',encoding='utf-8') as f:
            for l in f:
                if l.strip(): prev=json.loads(l)
    except FileNotFoundError:
        prev=None
    entry={'kid':kid, 'sha256':hashlib.sha256(secret.encode()).hexdigest(), 'ts':int(time.time()), 'prev': (prev or {}).get('sha256')}
    with open(KEYLEDGER,'a',encoding='utf-8') as f:
        f.write(json.dumps(entry)+"\n")
    return entry

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kid', required=True)
    ap.add_argument('--new-secret', required=True)
    ap.add_argument('--activate', action='store_true')
    a=ap.parse_args()
    ring = load_keyring()
    ring.setdefault('keys', {})
    ring['keys'][a.kid] = a.new_secret
    if a.activate:
        ring['active'] = a.kid
    save_keyring(ring)
    ent = append_ledger(a.kid, a.new_secret)
    print('rotated', a.kid, 'ledger-entry:', json.dumps(ent))

if __name__=='__main__': main()
