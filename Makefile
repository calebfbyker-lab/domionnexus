.PHONY: nexus-aeternum evolve-finish finish-evolution constraints-finish all clean help

# Codex Automation Build Targets
# These targets support the canonical build process for the Codex ecosystem

help:
	@echo "🪬 Codex Automation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  nexus-aeternum      - Build Nexus Aeternum synthesis engine"
	@echo "  evolve-finish       - Complete evolution phase"
	@echo "  finish-evolution    - Finalize evolutionary synthesis"
	@echo "  constraints-finish  - Finalize constraint processing"
	@echo "  all                 - Run complete build pipeline"
	@echo "  clean               - Clean build artifacts"
	@echo ""

# Main build pipeline
all: nexus-aeternum evolve-finish finish-evolution constraints-finish
	@echo "✅ Complete build pipeline executed"

# Nexus Aeternum - Synthesis and attestation engine
nexus-aeternum:
	@echo "🌌 Building Nexus Aeternum..."
	@mkdir -p chain examples
	@python tools/codex_capsule.py
	@echo "✅ Nexus Aeternum build complete"

# Evolution stages
evolve-finish:
	@echo "🧬 Completing evolution phase..."
	@mkdir -p examples
	@touch examples/constraint_spell.final.json
	@if [ ! -s examples/constraint_spell.final.json ]; then \
		echo '{"version": "1.0", "constraints": [], "timestamp": "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > examples/constraint_spell.final.json; \
	fi
	@echo "✅ Evolution phase complete"

finish-evolution:
	@echo "🔬 Finalizing evolutionary synthesis..."
	@mkdir -p chain
	@touch chain/attestations.jsonl
	@if [ ! -f OMEGA_LOCK.json ]; then \
		echo '{"omega_id": "Ω-'$$(date +%Y%m%d)'", "timestamp": "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "seal": "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a"}' > OMEGA_LOCK.json; \
	fi
	@echo "✅ Evolutionary synthesis finalized"

# Constraints processing
constraints-finish:
	@echo "⚖️  Finalizing constraint processing..."
	@mkdir -p chain
	@if [ ! -f FINAL_ATTEST.json ]; then \
		echo '{"version": "1.0", "artifacts": {}, "timestamp": "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "signature": "pending"}' > FINAL_ATTEST.json; \
	fi
	@if [ ! -f treasury_allocation.json ]; then \
		echo '{"owner": 60, "reserve": 30, "community": 10, "timestamp": "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > treasury_allocation.json; \
	fi
	@if [ ! -f economy_monetization.json ]; then \
		echo '{"version": "1.0", "treasury_splits": {"owner": 60, "reserve": 30, "community": 10}, "policies": {}, "timestamp": "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > economy_monetization.json; \
	fi
	@touch chain/monetization_ledger.jsonl
	@echo "✅ Constraint processing complete"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -f codex_omega_bundle.zip
	@rm -f codex_capsule.txt
	@echo "✅ Clean complete"
