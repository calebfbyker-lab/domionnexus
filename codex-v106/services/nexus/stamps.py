def attach_ontology(ev:dict, context:dict)->dict:
    keep={"tenant","prio","risk","subject_sha256"}
    ctx={k:v for k,v in (context or {}).items() if k in keep}
    tags=[k for k in (context or {}).get("tags",[])]
    denies=(context or {}).get("deny_caps",[])
    ev.update({"ctx":ctx,"tags":tags,"deny":denies})
    return ev
