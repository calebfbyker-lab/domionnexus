import hashlib
def _h(b: bytes)->bytes:
    return hashlib.sha256(b).digest()

def leaves_hashes(lines):
    return [_h(x if isinstance(x,bytes) else x.encode()) for x in lines]

def merkle_root(leaf_hashes):
    if not leaf_hashes:
        return "0"*64
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
import hashlibimport hashlib

import json

def _h(b: bytes) -> bytes:

    return hashlib.sha256(b).digest()

def sha256(data: bytes) -> str:

def leaves_hashes(lines):    return hashlib.sha256(data).hexdigest()

    return [_h(x if isinstance(x, (bytes, bytearray)) else x.encode()) for x in lines]



def merkle_root(leaf_hashes):def merkle_root(leaves):

    if not leaf_hashes:    # leaves: list of bytes

        return "0" * 64    if not leaves:

    level = leaf_hashes[:]        return sha256(b"")

    while len(level) > 1:    level = [sha256(l).encode() for l in leaves]

        nxt = []    while len(level) > 1:

        for i in range(0, len(level), 2):        next_level = []

            a = level[i]        for i in range(0, len(level), 2):

            b = level[i + 1] if i + 1 < len(level) else a            left = level[i]

            nxt.append(_h(a + b))            right = level[i+1] if i+1 < len(level) else level[i]

        level = nxt            next_level.append(sha256(left + right).encode())

    return level[0].hex()        level = next_level

    return level[0].decode()

def proof_path(leaf_hashes, index):

    if index < 0 or index >= len(leaf_hashes):

        return []def leaf_hash(text: str) -> str:

    path = []    return sha256(text.encode())

    level = leaf_hashes[:]
    idx = index
    while len(level) > 1:
        if idx % 2 == 0:
            sib_idx = idx + 1 if idx + 1 < len(level) else idx
            pos = "R"
        else:
            sib_idx = idx - 1
            pos = "L"
        path.append({"pos": pos, "hash": level[sib_idx].hex()})
        nxt = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i + 1] if i + 1 < len(level) else a
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
                        b = level[i + 1] if i + 1 < len(level) else a
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
                        sib_idx = idx + 1 if idx + 1 < len(level) else idx
                        pos = "R"
                    else:
                        sib_idx = idx - 1
                        pos = "L"
                    path.append({"pos": pos, "hash": level[sib_idx].hex()})
                    nxt = []
                    for i in range(0, len(level), 2):
                        a = level[i]
                        b = level[i + 1] if i + 1 < len(level) else a
                        nxt.append(_h(a + b))
                    level = nxt
                    idx //= 2
                return path

            def verify_inclusion(root_hex, line_bytes, index, path):
                node = _h(line_bytes if isinstance(line_bytes, (bytes, bytearray)) else line_bytes.encode())
                for step in path:
                    sib = bytes.fromhex(step["hash"])
                    if step["pos"] == "R":
                        node = _h(node + sib)
                    else:
                        node = _h(sib + node)
                return node.hex() == root_hex
