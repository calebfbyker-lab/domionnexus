from .holonous import compile_glyphs
from .orch import DAG, Task, Edge

def glyphs_to_dag(glyph_text: str) -> DAG:
    c = compile_glyphs(glyph_text)
    if not c.get("ok"):
        raise ValueError("glyph order invalid")
    steps = c["steps"]
    tasks = { f"{i:02d}_{s}": Task(name=f"{i:02d}_{s}", plugin=f"core.{s}") for i,s in enumerate(steps) }
    edges = [ Edge(frm=f"{i:02d}_{steps[i]}", to=f"{i+1:02d}_{steps[i+1]}") for i in range(len(steps)-1) ]
    return DAG(tasks=tasks, edges=edges, meta={"source":"glyphs","explain":c.get("explain")})
