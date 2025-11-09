#!/usr/bin/env python3
import os, sqlite3, json, sys, time
DB=os.environ.get("NEXUS_DB","./nexus.db")
inp=sys.argv[1] if len(sys.argv)>1 else "-"
c=sqlite3.connect(DB); c.execute("PRAGMA journal_mode=WAL;")
def add_ev(k,n,ts,p): c.execute("insert into events(kind,node,ts,payload) values(?,?,?,?)",(k,n,ts,json.dumps(p,separators=(',',':'))))
def add_pf(r,h,p,ts,b): c.execute("insert into proofs(run_id,head,proof_sha256,ts,bundle) values(?,?,?,?,?)",(r,h,p,ts,json.dumps(b,separators=(',',':'))))
src=open(inp) if inp!="-." and inp!="- " and inp!="-" else sys.stdin
for line in src:
    j=json.loads(line)
    if "proof" in j:
        pf=j["proof"]; add_pf(pf["run_id"],pf["head"],pf["proof_sha256"],pf["ts"],pf["bundle"])
    else:
        add_ev(j["kind"],j["node"],j["ts"],j["payload"])
c.commit(); c.close()
