import sqlite3, os, json, time
DB=os.environ.get("NEXUS_DB","./nexus.db")

def _conn(): 
    c=sqlite3.connect(DB); c.execute("PRAGMA journal_mode=WAL;"); return c

def init():
    c=_conn()
    c.executescript("""
    create table if not exists events(
        id integer primary key autoincrement,
        kind text, node text, ts integer, payload text
    );
    create index if not exists ix_events_ts on events(ts);
    create table if not exists proofs(
        id integer primary key autoincrement,
        run_id text, head text, proof_sha256 text, ts integer, bundle text
    );
    """); c.commit(); c.close()

def add_event(kind:str, node:str, payload:dict):
    c=_conn()
    c.execute("insert into events(kind,node,ts,payload) values(?,?,?,?)",
              (kind,node,int(time.time()), json.dumps(payload, separators=(',',':'))))
    c.commit(); c.close()

def add_proof(run_id:str, head:str, proof_sha256:str, bundle:dict):
    c=_conn()
    c.execute("insert into proofs(run_id,head,proof_sha256,ts,bundle) values(?,?,?,?,?)",
              (run_id,head,proof_sha256,int(time.time()), json.dumps(bundle, separators=(',',':'))))
    c.commit(); c.close()

def tail_events(n:int=50):
    c=_conn(); rows=c.execute("select kind,node,ts,payload from events order by id desc limit ?", (n,)).fetchall(); c.close()
    return [ {"kind":k,"node":d,"ts":ts,"payload":json.loads(p)} for (k,d,ts,p) in rows ]

def list_proofs(n:int=50):
    c=_conn(); rows=c.execute("select run_id,head,proof_sha256,ts,bundle from proofs order by id desc limit ?",(n,)).fetchall(); c.close()
    return [ {"run_id":r,"head":h,"proof_sha256":p,"ts":ts,"bundle":json.loads(b)} for (r,h,p,ts,b) in rows ]
