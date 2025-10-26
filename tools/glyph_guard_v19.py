import json

def evaluate_glyph(glyph: str, nonce: str = None):
    # tiny parser: glyph "deploy:service@v1" -> action
    parts = glyph.split(":")
    action = parts[0] if parts else "noop"
    detail = parts[1] if len(parts) > 1 else ""
    steps = []
    if action == "deploy":
        steps.append({"step": "verify_policy", "ok": True})
        steps.append({"step": f"deploy {detail}", "ok": True})
        steps.append({"step": "sanctify", "ok": True})
    elif action == "sanctify":
        steps.append({"step": "create_attestation", "ok": True})
    else:
        steps.append({"step": "noop", "ok": True})
    return {"glyph": glyph, "nonce": nonce, "steps": steps}
