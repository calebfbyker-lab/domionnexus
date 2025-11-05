import heapq, time
H=[]
def enqueue(item, prio:int=5):
    heapq.heappush(H, (-int(prio), time.time(), item))
def drain(timeout=0.1):
    t0=time.time()
    while time.time()-t0<timeout:
        if H: _,_,it=heapq.heappop(H); return it
        time.sleep(0.01)
    return None
