from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ..integrations.openai_client import chat_completion
from ..integrations.supabase_client import insert_row

router = APIRouter(prefix="/v113")


@router.post("/ai/chat")
async def ai_chat(req: Request):
    body = await req.json()
    prompt = body.get("prompt", "Hello")
    out = chat_completion(prompt)
    return JSONResponse(out)


@router.post("/db/insert")
async def db_insert(req: Request):
    body = await req.json()
    table = body.get("table", "events")
    row = body.get("row", {})
    res = insert_row(table, row)
    return JSONResponse(res)
