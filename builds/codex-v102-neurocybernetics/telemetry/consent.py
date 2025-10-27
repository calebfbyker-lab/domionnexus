import json, time
LEDGER='telemetry/consent_ledger.jsonl'

def grant(subject_sha:str, scope:str)->dict:
    rec={"ts":time.time(),"subject_id_sha256":subject_sha,"scope":scope,"grant":True}
    with open(LEDGER,'a',encoding='utf-8') as f: f.write(json.dumps(rec,separators=(',',':'))+'\n')
    return rec

def revoke(subject_sha:str, scope:str)->dict:
    rec={"ts":time.time(),"subject_id_sha256":subject_sha,"scope":scope,"grant":False}
    with open(LEDGER,'a',encoding='utf-8') as f: f.write(json.dumps(rec,separators=(',',':'))+'\n')
    return rec

def status(subject_sha:str)->dict:
    scopes={}
    try:
        for ln in open(LEDGER,'r',encoding='utf-8').read().splitlines():
            r=json.loads(ln)
            if r.get('subject_id_sha256')==subject_sha:
                scopes[r['scope']]=r['grant']
    except FileNotFoundError:
        pass
    return {"subject_id_sha256":subject_sha,"scopes":scopes}
