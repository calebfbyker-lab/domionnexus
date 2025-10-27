import os
from fastapi import Header, HTTPException

CODEX_API_KEY = os.getenv("CODEX_API_KEY", "dev-key")


def _auth(perm: str):
    def dep(x_api_key: str = Header(default="")):
        if x_api_key != CODEX_API_KEY:
            raise HTTPException(status_code=401, detail="invalid api key")
        return True

    return dep
