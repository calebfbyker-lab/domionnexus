def staff_action(glyph, spoken_word):
    translation = {
        ("⚡", "strike"): "Emit alchemical energy/lightning",
        ("🛡️", "ward"): "Activate barrier",
        ("⚙️", "transform"): "Transmute material—wood→metal",
        ("🌊", "heal"): "Emit healing/soothing flow",
        ("⭐", "guide"): "Quantum guidance/assist",
    }
    effect = translation.get((glyph, spoken_word.lower()))
    if effect:
        print(f"Staff response [{glyph}]: {effect} ({datetime.datetime.utcnow().isoformat()})")
    else:
        print("No encoded action.")