# ================================================================
# Codex Continuum - Build & Verification Makefile
# EUCELA Tri-License © 2025 Caleb Fedor Byker (Konev)
# ================================================================

.PHONY: all clean nexus-aeternum evolve-finish final-evolution verify help

# Default target
all: nexus-aeternum evolve-finish final-evolution

help:
	@echo "Codex Continuum Build Targets:"
	@echo "  nexus-aeternum     - Initialize the nexus and prepare build environment"
	@echo "  evolve-finish      - Complete the evolution process"
	@echo "  final-evolution    - Generate final artifacts and OMEGA_LOCK.json"
	@echo "  verify             - Verify integrity of all artifacts"
	@echo "  all                - Run complete build pipeline (default)"
	@echo "  clean              - Remove generated artifacts"

# Initialize nexus - prepare environment and verify dependencies
nexus-aeternum:
	@echo "🌌 Initializing Nexus Aeternum..."
	@mkdir -p chain releases artifacts site
	@python3 --version > /dev/null 2>&1 || (echo "ERROR: Python 3 required" && exit 1)
	@test -f chain/attestations.jsonl || touch chain/attestations.jsonl
	@echo "✓ Nexus initialized"

# Complete evolution process
evolve-finish:
	@echo "🔄 Completing Evolution Process..."
	@python3 tools/adaptive_intelligence.py
	@python3 tools/update_external_data.py
	@echo "✓ Evolution complete"

# Generate final artifacts
final-evolution: nexus-aeternum evolve-finish
	@echo "🚀 Generating Final Evolution Artifacts..."
	@python3 tools/omega_finalize.py
	@test -f OMEGA_LOCK.json || (echo "ERROR: OMEGA_LOCK.json not generated" && exit 1)
	@python3 -m json.tool OMEGA_LOCK.json > /dev/null || (echo "ERROR: Invalid JSON in OMEGA_LOCK.json" && exit 1)
	@test -f codex_omega_bundle.zip || (echo "ERROR: codex_omega_bundle.zip not generated" && exit 1)
	@test -f codex_capsule.txt || (echo "ERROR: codex_capsule.txt not generated" && exit 1)
	@test -f chain/attestations.jsonl || (echo "ERROR: chain/attestations.jsonl missing" && exit 1)
	@echo "✓ Final evolution complete"

# Verify integrity
verify:
	@echo "🔐 Verifying Artifact Integrity..."
	@python3 tools/monetization_verify.py
	@echo "✓ Verification complete"

# Clean generated artifacts (but preserve chain history)
clean:
	@echo "🧹 Cleaning generated artifacts..."
	@rm -f OMEGA_LOCK.json codex_omega_bundle.zip codex_capsule.txt
	@rm -rf releases/*.zip
	@echo "✓ Clean complete (chain history preserved)"
