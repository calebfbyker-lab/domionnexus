import threading, queue
_q = queue.Queue()

def enqueue(item): _q.put(item)

def drain(timeout=0.1):
    try: return _q.get(timeout=timeout)
    except queue.Empty: return None
