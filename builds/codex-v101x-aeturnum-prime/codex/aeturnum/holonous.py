import re
GLYPH_MAP={'🌀':'verify','🌞':'invoke','🧾':'audit','🛡':'scan','🔮':'attest','🛡‍🔥':'sanctify','🚦':'rollout','⚖️':'judge','🌈':'deploy','♾':'continuum'}
NEEDED=['verify','invoke','audit','scan','attest','sanctify','rollout','judge','deploy','continuum']
def compile_glyphs(text:str):
    toks=[t.strip() for t in re.split(r'[;\n]+', text) if t.strip()]
    steps=[]
    for t in toks:
        if t and t[0] in GLYPH_MAP: steps.append(GLYPH_MAP[t[0]]); continue
        steps.append(t.split()[0].lower())
    seq=[s for s in steps if s in NEEDED]
    ok = seq == NEEDED[:len(seq)]
    return {'ok':ok,'steps':steps,'explain':'glyphs mapped then order-checked'}
