import hashlib, json
class TetraHelix:
    def __init__(self):
        self.strands = {k: [] for k in ("logic","governance","learning","ethics")}
    @staticmethod
    def _h(b: bytes)->str: return hashlib.sha256(b).hexdigest()
    def add_event(self, strand:str, payload:dict):
        if strand not in self.strands: raise ValueError("unknown strand")
        line=json.dumps(payload, separators=("," ,":" )).encode()
        prev=self.strands[strand][-1]["hash"] if self.strands[strand] else "0"*64
        h=self._h(prev.encode()+line)
        rec={"prev":prev,"hash":h,"payload":payload}
        self.strands[strand].append(rec); return rec
    def braid(self)->str:
        tips="".join((self.strands[k][-1]["hash"] if self.strands[k] else "0"*64) for k in ("logic","governance","learning","ethics"))
        return self._h(tips.encode())
def demo_state():
    helix=TetraHelix()
    helix.add_event("logic", {"op":"manifest.hash"})
    helix.add_event("governance", {"op":"policy.verify"})
    helix.add_event("learning", {"op":"metrics.train"})
    helix.add_event("ethics", {"op":"grounding.check"})
    return {"state_hash": helix.braid(), "tips": {k:(v[-1]["hash"] if v else "0"*64) for k,v in helix.strands.items()}}
