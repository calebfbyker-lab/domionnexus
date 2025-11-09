#!/usr/bin/env python3
import os, sys, json, urllib.request
from services.nexus.rbac_v2 import mint
def http(method, url, data=None, tok=""):
    req=urllib.request.Request(url, data=(json.dumps(data).encode() if data is not None else None), method=method,
        headers={"Content-Type":"application/json","X-Auth":tok} if tok else {})
    with urllib.request.urlopen(req, timeout=8) as r: 
        ct=r.headers.get("content-type","")
        return r.read().decode() if "text/plain" in ct else json.loads(r.read())
def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else "help"
    if cmd=="mint":
        kid=sys.argv[2]; scopes=sys.argv[3].split(","); ttl=int(sys.argv[4]) if len(sys.argv)>4 else 3600
        print(mint(kid, scopes, ttl))
    elif cmd=="metrics":
        url=os.environ.get("NEX","http://localhost:8020")+"/metrics"
        tok=os.environ.get("TOK",""); print(http("GET",url,tok=tok))
    else:
        print("archon_cli mint <kid> <scopesCSV> [ttl] | metrics")
if __name__=="__main__": main()
