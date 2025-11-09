"""Builder Part 1
Writes basic metadata and lightweight assets:
- README, requirements
- codex/glyphs (xtgs/tsg/tgs)
- policy/glyph.yaml
- plugins/manifest.json (placeholder)
- codex/identity.json and SPDX

Usage: python part1.py --root /path/to/output
"""
import os, json, argparse, hashlib

SUBJECT = "caleb fedor byker konev|1998-10-27"
SUBJECT_SHA = hashlib.sha256(SUBJECT.encode()).hexdigest()

def w(root, rel, content):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

def run(root):
    # README
    w(root, "README.md", f"""# Codex Immortal × Dominion Nexus — v95 · Aegis Mesh (part1)

Authorship anchor
subject: {SUBJECT}
subject_id_sha256: {SUBJECT_SHA}
""")

    # requirements
    w(root, "requirements.txt", """fastapi>=0.111.0
uvicorn[standard]>=0.30.0
pyyaml>=6.0.2
cryptography>=43.0.0
pyjwt[crypto]>=2.9.0
requests>=2.32.3
rich>=13.7.1
""")

    # glyph maps
    w(root, "codex/glyphs/xtgs.yaml", "🌞: invoke\n🌀: verify\n🌈: deploy\n🧾: audit\n🔮: attest\n🛡: scan\n🛡‍🔥: sanctify\n")
    w(root, "codex/glyphs/tsg.yaml", "🌞: invoke\n🌀: verify\n🌈: deploy\n🧾: audit\n")
    w(root, "codex/glyphs/tgs.yaml", "🌞: invoke\n🌀: verify\n🌈: deploy\n🧾: audit\n")

    # policy
    w(root, "policy/glyph.yaml", """max_steps: 12
deny_emojis: ["💣","🧨"]
deny_patterns:
  - "(?i)rm\\s+-rf\\s+/"
  - "(?i)drop\\s+database"
  - "(?i)chmod\\s+777"
""")

    # plugins manifest (placeholder actions)
    plugin = {
        "version": "v95.x",
        "actions": {
            "invoke": {"cmd": ["python", "scripts/hash_all.py", "--root", ".", "--out", "codex/manifest.v95x.json"]},
            "verify": {"cmd": ["python", "scripts/verify_manifest.py", "--root", ".", "--manifest", "codex/manifest.v95x.json"]},
            "audit": {"cmd": ["python", "scripts/sbom_syft_stub.py"]},
            "scan": {"cmd": ["python", "scripts/vuln_gate.py", "--sbom", "sbom.json", "--severity", "high"]},
            "attest": {"cmd": ["python", "scripts/provenance_v4.py"]},
            "sanctify": {"cmd": ["python", "scripts/quorum_verify.py"]},
            "deploy": {"cmd": ["python", "-c", "import shutil; shutil.make_archive('artifact-v95x','zip','.')"]}
        }
    }
    w(root, "plugins/manifest.json", json.dumps(plugin, indent=2))

    # identity + SPDX
    w(root, "codex/identity.json", json.dumps({"subject": SUBJECT, "subject_id_sha256": SUBJECT_SHA, "version": "v95.x"}, indent=2))
    spdx = {
        "spdxVersion": "SPDX-2.3",
        "name": "Codex Aegis Mesh v95.x",
        "dataLicense": "CC0-1.0",
        "creationInfo": {"creators": ["Tool: codex-spdx-gen"]},
        "packages": [{"name": "codex-v95x", "licenseDeclared": "MIT", "externalRefs": [{"referenceLocator": "subject_sha256:" + SUBJECT_SHA}]}]
    }
    w(root, "codex/LICENSE.spdx.json", json.dumps(spdx, indent=2))

    print("part1: written metadata, glyphs, policy, plugin manifest, identity")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./build_output")
    a = ap.parse_args()
    run(a.root)
