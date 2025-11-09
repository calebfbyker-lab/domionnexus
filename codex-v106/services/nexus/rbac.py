import os
TOK=os.environ.get("NEXUS_TOKENS","").strip()
# format: "token123=ingest,read,metrics;tokenABC=read"
def _map():
    out={}
    for row in (TOK.split(";") if TOK else []):
        if not row: continue
        tok,sc=row.split("=",1); out[tok.strip()]=set(x.strip() for x in sc.split(","))
    return out
TOKMAP=_map()
def allowed(token:str, scope:str)->bool:
    return bool(token and token in TOKMAP and scope in TOKMAP[token])
