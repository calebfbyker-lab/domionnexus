import hashlib

def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

def leaves_hashes(lines):
    return [_h(x if isinstance(x, (bytes, bytearray)) else x.encode()) for x in lines]

def merkle_root(leaf_hashes):
    if not leaf_hashes:
        return "0" * 64
    level = leaf_hashes[:]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i+1] if i+1 < len(level) else a
            nxt.append(_h(a + b))
        level = nxt
    return level[0].hex()

def proof_path(leaf_hashes, index):
    if index < 0 or index >= len(leaf_hashes):
        return []
    path = []
    level = leaf_hashes[:]
    idx = index
    while len(level) > 1:
        if idx % 2 == 0:
            sib_idx = idx+1 if idx+1 < len(level) else idx
            pos = "R"
        else:
            sib_idx = idx-1
            pos = "L"
        path.append({"pos": pos, "hash": level[sib_idx].hex()})
        nxt = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i+1] if i+1 < len(level) else a
            nxt.append(_h(a + b))
        level = nxt
        idx //= 2
    return path

def verify_inclusion(root_hex, line_bytes, index, path):
    node = _h(line_bytes if isinstance(line_bytes, (bytes, bytearray)) else line_bytes.encode())
    for step in path:
        sib = bytes.fromhex(step["hash"])
        if step.get("pos") == "R":
            node = _h(node + sib)
        else:
            node = _h(sib + node)
    return node.hex() == root_hex
