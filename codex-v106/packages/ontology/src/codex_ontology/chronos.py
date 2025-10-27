from __future__ import annotations
from typing import Dict, Any
import math, time
def phase(now:float|None=None)->Dict[str,float]:
    t = now or time.time()
    day = (t % 86400.0) / 86400.0
    lunar = ((t / 86400.0) % 29.530588) / 29.530588
    harmonic = (math.sin(2*math.pi*day) + math.sin(3*math.pi*day)) * 0.5
    return {"day":day,"lunar":lunar,"harmonic":harmonic}
def chrono_bias(ph:Dict[str,float])->Dict[str,float]:
    b={}
    if ph["lunar"]<0.1 or ph["lunar"]>0.9:
        b.update({"verify":0.15,"scan":0.10})
    if ph["harmonic"]>0.6:
        b.update({"rollout":0.05,"deploy":0.05})
    if ph["day"]>0.75:
        b.update({"judge":0.05})
    return b
