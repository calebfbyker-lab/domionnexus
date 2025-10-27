from typing import Dict, Any
import numpy as np
try:
    from packages.neuro.src.codex_neuro.ncs import ncs_vector, align_with_glyph_feat, bias_dict
except Exception:
    # fallbacks if the neuro package isn't present; simple local implementations
    def ncs_vector(X, fs=256, k=8):
        X = np.array(X, dtype=float)
        if X.ndim != 2: raise ValueError("samples must be 2D [channels x samples]")
        # tiny placeholder: channel means
        return np.mean(X, axis=1)[:k]
    def align_with_glyph_feat(ncs, glyph_feat):
        return 0.0
    def bias_dict(score):
        s = max(-1.0, min(1.0, score))
        return {"verify":0.1*s, "scan":0.25*s, "attest":0.2*s, "sanctify":0.2*s, "judge":0.15*s, "deploy":-0.1*s}

def _array(body: Dict[str, Any]) -> np.ndarray:
    X = np.array(body.get("samples", []), dtype=float)
    if X.ndim != 2: raise ValueError("samples must be 2D [channels x samples]")
    return X

def neuro_capture(body: Dict[str, Any]) -> Dict[str, Any]:
    if not bool(body.get("consent", False)):
        return {"ok": False, "reason": "consent_required"}
    X = _array(body); fs = int(body.get("fs", 256))
    vec = ncs_vector(X, fs=fs).tolist()
    return {"ok": True, "ncs": vec, "fs": fs}

def neuro_align(body: Dict[str, Any]) -> Dict[str, Any]:
    vec = np.array(body.get("ncs", []), dtype=float)
    gf  = body.get("glyph_features", {})
    score = align_with_glyph_feat(vec, gf)
    return {"ok": True, "score": float(score), "bias": bias_dict(score)}

def neuro_bias_for_context(body: Dict[str, Any]) -> Dict[str, Any]:
    bias = body.get("bias", {})
    return {"ok": True, "context_patch": {"_ncs_bias_dict": bias}}
