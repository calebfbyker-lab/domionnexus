import threading, queue
def call_with_timeout(fn, timeout_s, **kw):
    q=queue.Queue()
    def run():
        try: q.put(("ok", fn(**kw)))
        except Exception as e: q.put(("err", str(e)))
    th=threading.Thread(target=run, daemon=True); th.start(); th.join(timeout_s)
    if th.is_alive(): return ("timeout", None)
    return q.get()
