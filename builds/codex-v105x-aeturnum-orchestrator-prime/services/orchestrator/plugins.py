from typing import Callable, Dict
REG: Dict[str, Callable] = {}
def task(name: str):
    def deco(fn: Callable): REG[name]=fn; return fn
    return deco

@task("core.verify")
def t_verify(**kw): return {"verified": True}
@task("core.invoke")
def t_invoke(**kw): return {"invoked": True}
@task("core.audit")
def t_audit(**kw): return {"sbom": "stub"}
@task("core.scan")
def t_scan(**kw): return {"vulns": 0}
@task("core.attest")
def t_attest(**kw): return {"attestation": "sha256:deadbeef"}
@task("core.sanctify")
def t_sanctify(**kw): return {"policy": "pass"}
@task("core.rollout")
def t_rollout(percent: int = 10, **_): return {"rolled": percent}
@task("core.judge")
def t_judge(**_): return {"gate": "allow"}
@task("core.deploy")
def t_deploy(**_): return {"status": "ok"}
@task("core.continuum")
def t_continuum(**_): return {"closing": True}
