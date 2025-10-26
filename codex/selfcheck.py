import os, json, hashlib

MANIFEST = os.getenv("CODEX_MANIFEST", "codex/manifest.v98.json")
DISABLE = os.getenv("DISABLE_SELF_CHECK","0") == "1"

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(65536),b''): h.update(ch)
    return h.hexdigest()

def verify(root="."):
    if DISABLE:
        return True, []
    try:
        m=json.load(open(MANIFEST,encoding='utf-8'))
    except Exception as e:
        return False, [f"manifest load failed: {e}"]
    errs=[]
    for it in m.get("items", []):
        p=os.path.join(root, it["path"])
        if not os.path.exists(p):
            errs.append("MISSING "+it["path"])
            continue
        try:
            if sha(p) != it["sha256"]:
                errs.append("MISMATCH "+it["path"])
        except Exception as e:
            errs.append(f"ERROR {it['path']}: {e}")
    return (len(errs)==0), errs
