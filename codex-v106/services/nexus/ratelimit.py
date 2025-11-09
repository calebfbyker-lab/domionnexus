import time, collections, os
CAP=int(os.environ.get("NEXUS_RPS","5"))
WIN=float(os.environ.get("NEXUS_RPS_WIN","1.0"))
BUCKET=collections.defaultdict(lambda: {"ts":0.0,"tokens":CAP})
def allow(key:str)->bool:
    now=time.time()
    b=BUCKET[key]; elapsed=now-b["ts"]
    b["ts"]=now; b["tokens"]=min(CAP, b["tokens"]+elapsed*(CAP/WIN))
    if b["tokens"]>=1.0: b["tokens"]-=1.0; return True
    return False
