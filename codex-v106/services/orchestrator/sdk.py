from __future__ import annotations
from typing import Callable, Any, Dict, Optional, Tuple
REG: Dict[str, Callable[..., Any]] = {}
def task(name:str)->Callable[[Callable[...,Any]],Callable[...,Any]]:
  def deco(fn): REG[name]=fn; return fn
  return deco
class In:
  @staticmethod
  def num(x, lo=None, hi=None):
    x=float(x);
    if lo is not None and x<lo: raise ValueError("min")
    if hi is not None and x>hi: raise ValueError("max")
    return x
  @staticmethod
  def text(x, nonempty=False):
    x=str(x)
    if nonempty and not x.strip(): raise ValueError("empty")
    return x
def run(name:str, **kw)->Tuple[str,Any]:
  fn=REG.get(name)
  if not fn: return ("err", f"task:{name}:missing")
  try: return ("ok", fn(**kw))
  except Exception as e: return ("err", str(e))
