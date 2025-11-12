import hashlib, time, json
class ChronoMerkle:
    def __init__(self): self.events=[]
    def add(self, info:dict):
        ts=time.time(); blob=json.dumps({"ts":ts,"info":info},separators=("," ,":" )).encode()
        prev=self.events[-1]["root"] if self.events else "0"*64
        h=hashlib.sha256(prev.encode()+blob).hexdigest()
        self.events.append({"ts":ts,"root":h,"info":info}); return h
    def head(self)->str: return self.events[-1]["root"] if self.events else "0"*64
