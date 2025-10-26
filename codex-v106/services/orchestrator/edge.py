import time
PENDING=[]
def offer(job): PENDING.append(job)
def take_one()->dict|None:
    return PENDING.pop(0) if PENDING else None
