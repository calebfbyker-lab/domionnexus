import json, time, os, threading
LOCK=threading.Lock(); RUNS={}; PATH=os.environ.get("CODEX_EVENTS_PATH","events.log")
def add(run):
    with LOCK: RUNS[run.run_id]=run
def get(run_id):
    with LOCK: return RUNS.get(run_id)
def log(ev:dict):
    ev={"t":time.time()}|ev
    try:
        with open(PATH,"a",encoding="utf-8") as f: f.write(json.dumps(ev,separators=(",",":"))+"\n")
    except Exception: pass
def tail(n=100):
    try:
        with open(PATH,"r",encoding="utf-8") as f: lines=f.readlines()[-n:]
        return [json.loads(x) for x in lines]
    except Exception: return []
