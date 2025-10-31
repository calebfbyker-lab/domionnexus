# Changelog

All notable changes to Domion Nexus — Codex Immortal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [26.0.0] - 2025-10-23

### Added

#### Marketplace & SDKs
- **Marketplace**: Full marketplace platform with app submission and review workflow
  - App review gate with automated security scanning
  - Multi-stage approval process (automated → manual → final)
  - Marketplace policy configuration with compliance rules
- **Webhook Signing**: HMAC-SHA256 webhook signature generation and verification
  - Sign stub for webhook payload signing
  - Verify stub for signature validation
  - Timestamp-based replay attack prevention
- **SDK Generation**: Multi-language SDK client generator stubs
  - Support for Python, TypeScript, Go, and Java
  - OpenAPI 3.0.3 specification for Codex API v26.0
  - Integration ready for openapi-generator

#### Feature Management
- **Feature Flags**: Comprehensive feature flag system with canary deployments
  - Canary targeting by user, organization, and region
  - Percentage-based rollout support
  - Environment-specific overrides (production, staging, development)
  - Flag evaluation with context support
- **Canary Guard**: Automated canary deployment health monitoring
  - Error rate, latency, CPU, and memory thresholds
  - Automatic rollback recommendations
  - Integration points for monitoring systems

#### AI Model Registry
- **Model Registration**: AI model registry with JSON schema validation
  - Support for multiple providers (OpenAI, Anthropic, Google, Meta, Mistral, Cohere)
  - Model types: text-generation, chat, embedding, image, audio, multimodal
  - Pricing and performance metadata tracking
- **Model Evaluation**: Smoke tests and quality evaluation framework (stub)
  - Integration ready for HELM and LM Eval Harness
  - Basic generation, error handling, and streaming tests

#### Sustainability
- **Green Operations**: Carbon-aware workload scheduling and monitoring
  - Carbon intensity tracking by region
  - Renewable energy percentage monitoring
  - Optimal region selection for workload placement
  - Integration ready for Electricity Map and WattTime APIs
  - Carbon neutrality goals and PUE targets

#### Internationalization
- **i18n Support**: Multi-language translation system
  - English (en) and Spanish (es) translations
  - Key consistency checker for translation completeness
  - Runtime loading support via feature flags

#### Compliance & Security
- **Data Residency**: Enforcement of data residency rules for regulated regions
  - GDPR (EU), CCPA/HIPAA (US), UK-GDPR, PDPA (APAC) support
  - Region-specific storage path enforcement
  - Cross-region transfer validation
- **Compliance Controls**: Automated compliance checking
  - ECCL-1.0 license verification
  - Security controls validation
  - Data residency rule checks
- **Constraints Evaluation**: System constraints and requirements validation
  - API, SDK, marketplace, feature flag, and model constraints
  - Version consistency checks

#### Validation Framework
- **Triune Validation**: Three-fold validation system
  - Structure: Directory and file structure validation
  - Security: Webhook signing, secret detection
  - Semantics: JSON validity, version consistency
- **Merkle Tree**: Artifact integrity verification
  - SHA-256 hashing of all artifacts
  - Merkle tree construction and verification
  - Manifest generation for integrity checks

#### CI/CD
- **Release Workflow**: Tag-triggered GitHub Actions workflow
  - Controls & Contracts validation
  - Triune, Merkle, and Ninefold gate validation
  - Marketplace self-check and SDK generation
  - i18n, canary guard, green ops, and model eval checks
  - Automatic GitHub release creation with artifacts

### Security Notes
- ⚠️ **No private keys or secrets committed to repository**
- ⚠️ **All crypto/webhook signing stubs are placeholders**
- ⚠️ **Must wire to KMS/Vault for secret management in production**
- ⚠️ **Scripts are stubs and templates for infrastructure integration**
- ⚠️ **Review before enabling release workflows that expose secrets**

### Integration Requirements
Before deploying to production, integrate with:
1. **KMS/Vault**: For webhook signing secret management
2. **OpenAPI Generator**: For full SDK client code generation
3. **Electricity Map/WattTime**: For real carbon intensity data
4. **Monitoring System**: For canary deployment metrics (Datadog, New Relic, etc.)
5. **Eval Framework**: For comprehensive model evaluation (HELM, LM Eval Harness)
6. **Cloud Storage**: For data residency enforcement (S3, GCS, Azure Storage)

### Files Added
- `api/openapi.json` - OpenAPI 3.0.3 specification
- `scripts/sdk/generate_clients_stub.py` - SDK generator
- `config/marketplace_policy.json` - Marketplace intake policy
- `scripts/webhooks/sign_stub.py` - Webhook signing
- `scripts/webhooks/verify_stub.py` - Webhook verification
- `scripts/marketplace/app_review.py` - App review workflow
- `config/feature_flags.json` - Feature flags configuration
- `scripts/feature/flag_eval.py` - Flag evaluation
- `scripts/feature/canary_guard.py` - Canary monitoring
- `schemas/model_entry.schema.json` - Model entry schema
- `scripts/models/register_model.py` - Model registration
- `scripts/models/run_evals_stub.py` - Model evaluation
- `config/greenops.json` - Green ops configuration
- `scripts/green/guard.py` - Green ops guard
- `i18n/en.json` - English translations
- `i18n/es.json` - Spanish translations
- `scripts/i18n/check_keys.py` - i18n key checker
- `scripts/residency/enforce_paths_stub.py` - Data residency enforcement
- `scripts/compliance/check_controls.py` - Compliance checker
- `scripts/constraints/evaluate.py` - Constraints evaluator
- `scripts/triune_validate.py` - Triune validator
- `scripts/merkle_build.py` - Merkle tree builder
- `scripts/merkle_verify.py` - Merkle tree verifier
- `.github/workflows/v26_release.yml` - Release workflow
- `trust/overview.json` - Trust framework overview
- `CHANGELOG.md` - This changelog

### License
ECCL-1.0 (Eternal Creative Covenant License)
Subject ID: `2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a`

---

## [Previous Versions]
See git history for earlier releases.
