from fastapi import FastAPI, Header, HTTPException, Depends
import os

CODEX_API_KEY = os.getenv("CODEX_API_KEY", "dev-key")


def _auth(perm: str):
    def dep(x_api_key: str = Header(default="")):
        if x_api_key != CODEX_API_KEY:
            raise HTTPException(status_code=401, detail="invalid api key")
        return True

    return dep


app = FastAPI(title="codex-python-engine")


@app.get("/health", dependencies=[Depends(_auth("read"))])
async def health():
    return {"status": "ok"}


@app.get("/seal", dependencies=[Depends(_auth("read"))])
async def get_seal():
    # demo endpoint to show the auth dependency working
    return {"seal": "demo-seal", "env_key_present": bool(os.getenv('CODEX_API_KEY'))}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
