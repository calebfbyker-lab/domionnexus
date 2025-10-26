import hashlib, math, json

def _h(b: bytes)->bytes: return hashlib.sha256(b).digest()
def hhex(b: bytes)->str: return hashlib.sha256(b).hexdigest()

def leaves_hashes(lines):
    # lines: iterable of bytes (each a JSON line); return list of leaf hashes
    return [ _h(x if isinstance(x,bytes) else x.encode()) for x in lines ]

def merkle_root(leaf_hashes):
    if not leaf_hashes: return "0"*64
    level = leaf_hashes[:]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i+1] if i+1 < len(level) else level[i]
            nxt.append(_h(a+b))
        level = nxt
    return level[0].hex()

def proof_path(leaf_hashes, index):
    # return list of sibling hex digests and positions ("L"/"R")
    if index<0 or index>=len(leaf_hashes): return []
    path=[]
    level = leaf_hashes[:]
    idx = index
    while len(level) > 1:
        if idx % 2 == 0:
            sib_idx = idx+1 if idx+1<len(level) else idx
            sib = level[sib_idx]
            path.append({"pos":"R","hash":sib.hex()})
        else:
            sib_idx = idx-1
            sib = level[sib_idx]
            path.append({"pos":"L","hash":sib.hex()})
        # up
        nxt=[]
        for i in range(0,len(level),2):
            a = level[i]
            b = level[i+1] if i+1<len(level) else level[i]
            nxt.append(_h(a+b))
        idx //= 2
        level = nxt
    return path

def verify_inclusion(root_hex, line_bytes, index, path):
    node = _h(line_bytes)
    idx = index
    for step in path:
        sib = bytes.fromhex(step["hash"]) if isinstance(step, dict) else bytes.fromhex(step)
        if isinstance(step, dict) and step.get("pos")=="R":
            node = _h(node + sib)
        else:
            node = _h(sib + node)
        idx//=2
    return node.hex()==root_hex
