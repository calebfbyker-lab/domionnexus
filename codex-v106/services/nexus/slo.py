import time
START=time.time()
def liveness(): return {"ok":True,"uptime_s":int(time.time()-START)}
def readiness(): return {"ok":True}
# latency budget check (stub for alerting)
LAST_LAT=0.0
def record_latency(ms:float):
    global LAST_LAT; LAST_LAT=ms
def budget(): 
    return {"p_last_ms": LAST_LAT, "budget_ms": 250.0, "ok": LAST_LAT<=250.0}
