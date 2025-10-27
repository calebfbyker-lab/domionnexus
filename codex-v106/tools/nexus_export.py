#!/usr/bin/env python3
import os, sqlite3, json, sys
DB=os.environ.get("NEXUS_DB","./nexus.db")
out=sys.argv[1] if len(sys.argv)>1 else "nexus_dump.jsonl"
c=sqlite3.connect(DB)
for row in c.execute("select kind,node,ts,payload from events order by id"):
    print(json.dumps({"kind":row[0],"node":row[1],"ts":row[2],"payload":json.loads(row[3])}))
for row in c.execute("select run_id,head,proof_sha256,ts,bundle from proofs order by id"):
    print(json.dumps({"proof":{"run_id":row[0],"head":row[1],"proof_sha256":row[2],"ts":row[3],"bundle":json.loads(row[4])}}))
c.close()
