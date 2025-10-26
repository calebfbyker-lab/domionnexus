import threading
import queue

_q = queue.Queue()

def enqueue(item):
    """Add an item to the work queue."""
    _q.put(item)

def drain(timeout=0.1):
    """
    Remove and return an item from the queue.
    
    Args:
        timeout: Maximum time to wait for an item
        
    Returns:
        The item from the queue, or None if empty
    """
    try:
        return _q.get(timeout=timeout)
    except queue.Empty:
        return None
