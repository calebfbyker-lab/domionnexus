# Changelog

All notable changes to Domion Nexus - Codex Immortal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v33.33] - 2025-10-23

### Added
- Continuous Verification & Deployment artifacts for v33.33 release
- Build status verification script (`scripts/release/build_status.py`)
- Deployment stub script (`scripts/release/deploy_stub.py`)
- Integrity verification script (`scripts/release/verify_integrity.py`)
- Constraint evaluation script (`scripts/constraints/evaluate.py`)
- Triune validation script (`scripts/triune_validate.py`)
- Merkle tree build and verification scripts
- Provenance manifest with cryptographic binding
- GitHub Actions workflow for automated verification
- CODEOWNERS file for repository governance

### Security Notes
- ⚠️ All sealed keys and attestation stubs are placeholders
- ⚠️ Must be wired to KMS/HSM/enclave in production
- ⚠️ Release/deploy stubs are simulations only
- ⚠️ Must be replaced with real deploy hooks for production use
- ✅ No secrets or private keys have been committed
- ✅ All verification steps must pass before production deployment

### Validation Steps
To validate this release locally, run the following commands:
```bash
python3 scripts/release/build_status.py
python3 scripts/release/verify_integrity.py
python3 scripts/release/deploy_stub.py
python3 scripts/constraints/evaluate.py
python3 scripts/triune_validate.py
python3 scripts/merkle_build.py && python3 scripts/merkle_verify.py
```

### References
- Subject Hash: `2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a`
- License: ECCL-1.0
- Repository: calebfbyker-lab/domionnexus
