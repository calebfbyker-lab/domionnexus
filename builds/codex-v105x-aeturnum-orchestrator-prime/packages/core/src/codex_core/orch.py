from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal
import hashlib, json, time

RunState = Literal["queued","running","succeeded","failed","canceled"]

def _h(x: bytes)->str: return hashlib.sha256(x).hexdigest()

@dataclass
class Task:
    name: str
    inputs: Dict[str, object] = field(default_factory=dict)
    plugin: str = "core.echo"
    timeout_s: int = 120

@dataclass
class Edge:
    frm: str
    to: str

@dataclass
class DAG:
    tasks: Dict[str, Task]
    edges: List[Edge]
    meta: Dict[str, object] = field(default_factory=dict)
    def topo(self)->List[str]:
        indeg = {t:0 for t in self.tasks}
        for e in self.edges: indeg[e.to]+=1
        q=[t for t,d in indeg.items() if d==0]; out=[]
        g = {}
        for e in self.edges: g.setdefault(e.frm,[]).append(e.to)
        while q:
            n=q.pop(0); out.append(n)
            for m in g.get(n,[]):
                indeg[m]-=1
                if indeg[m]==0: q.append(m)
        if len(out)!=len(self.tasks): raise ValueError("cycle detected")
        return out
    def digest(self)->str:
        blob=json.dumps({"t":{k:v.__dict__ for k,v in self.tasks.items()},
                         "e":[e.__dict__ for e in self.edges],
                         "m":self.meta}, separators=(',',':')).encode()
        return _h(blob)

@dataclass
class StepReceipt:
    task: str
    started: float
    ended: float
    ok: bool
    output_digest: str
    log_digest: str
    def digest(self)->str:
        b=json.dumps(self.__dict__,separators=(',',':')).encode()
        return _h(b)

@dataclass
class Run:
    run_id: str
    dag_digest: str
    tenant: str
    state: RunState = "queued"
    receipts: List[StepReceipt] = field(default_factory=list)
    created_ts: float = field(default_factory=lambda: time.time())
    def head(self)->str:
        prev="0"*64
        for r in self.receipts:
            prev=_h((prev+r.digest()).encode())
        return prev
