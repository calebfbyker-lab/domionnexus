import os, time, hmac, hashlib, base64, json
# TOKENS_V2: csv of records: kid:key:scopes
#   e.g., "k1:secretA:ingest,read,metrics;k2:secretB:read"
REC=os.environ.get("NEXUS_TOKENS_V2","").strip()
ALLOW=os.environ.get("NEXUS_IP_ALLOW","").strip()  # "127.0.0.1,10.0.0.0/8"
def _parse():
    D={}
    for r in (REC.split(";") if REC else []):
        if not r: continue
        kid,key,sc = r.split(":",2)
        D[kid] = {"key":key, "scopes": set(s.strip() for s in sc.split(","))}
    return D
SECRETS=_parse()

def _hmac(k:bytes,b:bytes)->str:
    return base64.urlsafe_b64encode(hmac.new(k,b,hashlib.sha256).digest()).decode().rstrip("=")

def mint(kid:str, scopes:list[str], ttl_s:int=3600)->str:
    if kid not in SECRETS: raise ValueError("kid unknown")
    payload={"kid":kid,"scopes":scopes,"exp":int(time.time())+ttl_s}
    b=json.dumps(payload,separators=(",",":")).encode()
    sig=_hmac(SECRETS[kid]["key"].encode(), b)
    return base64.urlsafe_b64encode(b).decode().rstrip(".")+"."+sig

def allow_ip(remote:str)->bool:
    if not ALLOW: return True
    if remote in [a.strip() for a in ALLOW.split(",") if ":" not in a]: return True
    # bare minimum CIDR (/8,/16,/24)
    if "/" in ALLOW:
        net,mask=ALLOW.split("/",1); mask=int(mask)
        import ipaddress
        try: return ipaddress.ip_address(remote) in ipaddress.ip_network(ALLOW, strict=False)
        except Exception: return False
    return False

def check(token:str, scope:str)->bool:
    try:
        b64,sig = token.split(".",1)
        b=base64.urlsafe_b64decode(b64+"==")
        payload=json.loads(b)
        kid=payload["kid"]; exp=int(payload["exp"])
        if time.time()>exp: return False
        rec=SECRETS.get(kid); 
        if not rec: return False
        if _hmac(rec["key"].encode(), b)!=sig: return False
        return scope in rec["scopes"]
    except Exception:
        return False
