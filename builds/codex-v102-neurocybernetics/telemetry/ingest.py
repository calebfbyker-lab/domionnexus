import json, csv
from telemetry.redact import scrub
STORE='telemetry/store.csv'

def ingest(rec:dict)->dict:
    safe=scrub(rec)
    with open(STORE,'a',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow([safe.get('subject_id_sha256'), safe.get('ts'), json.dumps(safe.get('eeg',[]))])
    return {"ok":True,"wrote":len(safe.get('eeg',[]))}
