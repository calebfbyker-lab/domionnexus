# 🧠 Codex Continuum Build Agent

## Overview

The Codex Continuum Build Agent is an automated build, verification, and deployment system that ensures reproducible, verified, and compliant builds under the EUCELA Tri-License.

## Features

### ✅ Primary Capabilities

1. **Automated Build Pipeline**
   - Sequential execution: `nexus-aeternum` → `evolve-finish` → `final-evolution`
   - Generates cryptographically verified artifacts
   - Creates immutable attestation chain

2. **Integrity Verification**
   - SHA-256 digest computation for all artifacts
   - Validation of OMEGA_LOCK.json structure
   - Automated verification before deployment

3. **Artifact Management**
   - `OMEGA_LOCK.json` - Cryptographic manifest
   - `codex_omega_bundle.zip` - Complete source bundle
   - `codex_capsule.txt` - Build attestation
   - `chain/attestations.jsonl` - Append-only audit trail

4. **Automated Deployment**
   - GitHub Actions integration
   - Automatic release tagging with `vΩ-YYYYMMDD` format
   - GitHub Pages deployment for documentation
   - Archive branch creation for build history

## Usage

### Local Build

```bash
# Run complete build pipeline
make all

# Or run individual steps
make nexus-aeternum    # Initialize environment
make evolve-finish     # Run evolution process
make final-evolution   # Generate final artifacts
make verify           # Verify integrity

# View available targets
make help

# Clean generated artifacts (preserves chain history)
make clean
```

### GitHub Actions

The build agent runs automatically:

- **On push to main**: Full build, verification, and deployment
- **On pull request**: Build and verification only (no deployment)
- **Weekly schedule**: Adaptive intelligence refresh (Sundays at 00:00 UTC)
- **Manual trigger**: Via workflow_dispatch

### Build Output

After a successful build, you'll get:

```
OMEGA_LOCK.json              # Cryptographic manifest with Omega ID
codex_omega_bundle.zip       # Complete source bundle
codex_capsule.txt            # Human-readable attestation
chain/attestations.jsonl     # Append-only attestation chain
treasury_allocation.json     # Treasury allocation data
economy_monetization.json    # Monetization strategy
artifacts/                   # Additional generated artifacts
releases/                    # Deployable bundles
```

## Tools

### Python Scripts

Located in `tools/`:

1. **adaptive_intelligence.py**
   - Refreshes adaptive suggestions based on project state
   - Generates optimization recommendations
   - Run weekly via scheduled workflow

2. **update_external_data.py**
   - Updates external scientific data references
   - Maintains data source status
   - Run nightly via cron (optional)

3. **omega_finalize.py**
   - Core finalization script
   - Generates OMEGA_LOCK.json with unique Omega ID
   - Creates bundle and capsule
   - Appends to attestation chain

4. **monetization_verify.py**
   - Verifies integrity of all generated artifacts
   - Computes and validates SHA-256 hashes
   - Ensures OMEGA_LOCK.json is valid JSON

## Architecture

### Build Pipeline Flow

```
┌─────────────────────┐
│  nexus-aeternum     │  Initialize environment, create directories
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  evolve-finish      │  Run adaptive intelligence & data updates
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  final-evolution    │  Generate artifacts & attestations
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  verify             │  Validate integrity & hashes
└─────────────────────┘
```

### Attestation Chain

The `chain/attestations.jsonl` file is an **append-only ledger**:

- Each build appends a new attestation record
- Never modified or deleted (permanent audit trail)
- Contains Omega ID, artifact hashes, and verification status

Example attestation:
```json
{
  "timestamp": "2025-11-02T16:12:32.138605+00:00",
  "event": "final_evolution_build",
  "omega_id": "8df668fe10767bf5...",
  "artifacts": {
    "bundle": {
      "name": "codex_omega_bundle.zip",
      "sha256": "c52eee12e599..."
    },
    "capsule": {
      "name": "codex_capsule.txt",
      "sha256": "b3f51d2c3e83..."
    }
  },
  "verified": true,
  "license": "EUCELA Tri-License",
  "steward": "CFBK"
}
```

## Security Rules

🔐 **Critical Security Requirements:**

1. ✅ **Never overwrite or delete** `chain/attestations.jsonl` (always append)
2. ✅ **Never modify hashes** in OMEGA_LOCK.json (regenerated each build)
3. ✅ **GPG-signed commits** required for steward operations (optional/future)
4. ✅ **Only publish artifacts** if all verification steps succeed
5. ✅ **Abort on hash mismatch** during integrity verification

## CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/codex-continuum.yml` workflow provides:

- **Build Job**: Runs full build pipeline and verification
- **Deploy Pages Job**: Deploys documentation to GitHub Pages
- **Create Release Job**: Tags releases and creates GitHub releases
- **Archive Job**: Creates archive branches for build history

### Release Format

Releases are tagged as: `vΩ-YYYYMMDD-HHMMSS`

Example: `vΩ-20251102-161232`

### Release Notes Template

```markdown
## 🚀 Codex Continuum Deployment Complete

Build verified and merged into main

**Ω-ID:** `8df668fe10767bf5...`

### Artifacts:
- ✅ codex_omega_bundle.zip
- ✅ codex_capsule.txt
- ✅ chain/attestations.jsonl (updated)

### Site
- 📄 Documentation deployed to GitHub Pages

---

**License:** EUCELA Tri-License © 2025 Caleb Fedor Byker (Konev)
```

## Treasury & Economy

### Treasury Allocation

Default allocation (configurable):
- 40% Development
- 30% Research
- 20% Community
- 10% Operations

### Monetization Strategy

- Open source with attribution requirement
- Commercial licensing available
- Consulting services available

## Optional Enhancements

### Scheduled Tasks

1. **Weekly Adaptive Intelligence Refresh**
   ```bash
   python tools/adaptive_intelligence.py
   ```

2. **Nightly External Data Updates**
   ```bash
   python tools/update_external_data.py
   ```

3. **Email/Webhook Notifications**
   - Send Omega ID and treasury summary
   - Notify on build completion or failure

## Merge Management (Future)

Planned features for automated merge management:

- Auto-merge feature branches when tests pass
- Conflict resolution using OMEGA_LOCK.json as canonical truth
- GPG signature verification for steward commits

## License

**EUCELA Tri-License © 2025 Caleb Fedor Byker (Konev)**

All builds, releases, and derivatives must include:
- EUCELA Tri-License attribution
- Verification of artifact hashes
- Proper steward attribution

## Commands Summary

Quick reference for agent operations:

```bash
# Full automated build
git fetch --all
make nexus-aeternum
make evolve-finish
make final-evolution
make verify

# With verification (recommended)
python tools/monetization_verify.py
python tools/omega_finalize.py

# Commit and tag (when ready)
git add .
git commit -am "Ω Evolution Build – verified"
git tag -a vΩ-$(date +%Y%m%d) -m "Codex Continuum build verified"
git push origin main --tags
```

## Troubleshooting

### Build Failures

1. **OMEGA_LOCK.json not generated**
   - Check that `omega_finalize.py` ran successfully
   - Verify Python 3.11+ is installed

2. **Invalid JSON in OMEGA_LOCK.json**
   - Check Python script for syntax errors
   - Validate JSON with: `python -m json.tool OMEGA_LOCK.json`

3. **Hash mismatch during verification**
   - Re-run the build pipeline from scratch
   - Check for file corruption
   - Ensure no manual modifications to artifacts

### CI/CD Issues

1. **GitHub Actions fails**
   - Check workflow logs in Actions tab
   - Verify Python version compatibility
   - Ensure all required files are committed

2. **Pages deployment fails**
   - Verify GitHub Pages is enabled in repository settings
   - Check Pages artifact size limits

## Support

For issues or questions:
- Review build logs in GitHub Actions
- Check attestation chain for build history
- Verify artifact integrity with `make verify`

---

**Build with reason, preserve with clarity, and verify everything.**
— The Codex Continuum Ethos
