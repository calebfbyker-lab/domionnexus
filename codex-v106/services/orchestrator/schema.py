# tiny typed validators without external deps
def _num(x, lo=None, hi=None):
    x=float(x);
    if lo is not None and x<lo: raise ValueError("min")
    if hi is not None and x>hi: raise ValueError("max")
    return x
def glyph_req(body:dict)->str:
    g=(body or {}).get("glyph"," ").strip()
    if not g: raise ValueError("glyph required")
    return g
def run_req(body:dict):
    g=glyph_req(body); t=(body or {}).get("tenant","public").strip() or "public"
    p=int((body or {}).get("prio",5)); p=max(0,min(10,p))
    return g,t,p
