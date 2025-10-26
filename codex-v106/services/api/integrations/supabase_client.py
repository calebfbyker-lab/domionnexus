import os
try:
    from supabase import create_client
except Exception:
    create_client = None

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_supabase():
    if not create_client or not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_row(table: str, row: dict):
    sb = get_supabase()
    if not sb:
        return {"mock": True, "table": table, "row": row}
    res = sb.table(table).insert(row).execute()
    return {"data": res.data, "status": res.status_code}
