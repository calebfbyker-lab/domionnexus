import re

GLYPH_MAP = {
    '🌀': 'verify',
    '🌞': 'invoke',
    '🧾': 'audit',
    '🛡': 'scan',
    '🔮': 'attest',
    '🛡‍🔥': 'sanctify',
    '🚦': 'rollout',
    '⚖️': 'judge',
    '🌈': 'deploy',
    '♾': 'continuum'
}

NEEDED = ['verify', 'invoke', 'audit', 'scan', 'attest', 'sanctify', 'rollout', 'judge', 'deploy', 'continuum']

def compile_glyphs(text: str):
    """
    Compile glyph text into a sequence of normalized step names.
    
    Args:
        text: String containing glyphs or step names separated by semicolons/newlines
        
    Returns:
        dict with keys:
            - ok: bool, whether the sequence follows the canonical order
            - steps: list of step names
            - explain: str, explanation of the compilation process
    """
    toks = [t.strip() for t in re.split(r'[;\n]+', text) if t.strip()]
    steps = []
    
    for t in toks:
        if not t:
            continue
        # Check if the token itself is a glyph (handles multi-char emojis)
        if t in GLYPH_MAP:
            steps.append(GLYPH_MAP[t])
            continue
        # Check if first character is a glyph (fallback)
        if t[0] in GLYPH_MAP:
            steps.append(GLYPH_MAP[t[0]])
            continue
        # Otherwise treat as text step name
        steps.append(t.split()[0].lower())
    
    seq = [s for s in steps if s in NEEDED]
    ok = seq == NEEDED[:len(seq)]
    
    return {
        "ok": ok,
        "steps": steps,
        "explain": "glyphs mapped then order-checked"
    }
