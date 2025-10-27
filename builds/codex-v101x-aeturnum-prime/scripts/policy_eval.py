#!/usr/bin/env python3
import json, yaml, datetime as dt, sys
pset=sys.argv[1]; attrs=json.loads(open(sys.argv[2]).read()) if len(sys.argv)>2 else {}
pol=yaml.safe_load(open(pset)); now=dt.datetime.utcnow()
def timeok(rule):
    w=rule.get("window_utc"); 
    if not w: return True
    h=lambda t: dt.time(*map(int,t.split(":"))); t=now.time()
    return h(w["after"])<=t<=h(w["before"])
def dayok(rule):
    days=rule.get("days_allow"); 
    return True if not days else now.strftime("%a") in days
for r in pol.get("rules",[]):
    if r.get("match") and attrs.get("step")!=r["match"]: continue
    if "require_prev" in r and not set(r["require_prev"]).issubset(set(attrs.get("seen",[]))):
        print(json.dumps({"deny":r["id"],"msg":r["message"]})); sys.exit(3)
    if not timeok(r): print(json.dumps({"deny":r["id"],"msg":r["message"]})); sys.exit(3)
    if not dayok(r): print(json.dumps({"deny":r["id"],"msg":r["message"]})); sys.exit(3)
print(json.dumps({"allow":True}))
