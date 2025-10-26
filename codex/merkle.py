import hashlib
import json


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def merkle_root(leaves):
    # leaves: list of bytes
    if not leaves:
        return sha256(b"")
    level = [sha256(l).encode() for l in leaves]
    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else level[i]
            next_level.append(sha256(left + right).encode())
        level = next_level
    return level[0].decode()


def leaf_hash(text: str) -> str:
    return sha256(text.encode())
