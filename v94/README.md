# Codex v94 Bundle - Sentinel Edition

## 🚀 Overview

Codex v94 introduces comprehensive security hardening and supply chain integrity features:

- **JWKS-by-kid Verification**: Optional OIDC/JWT authentication with JWK Set verification
- **Glyph Guard v14**: Stricter policy enforcement for glyph validation
- **SBOM Generation**: Software Bill of Materials using Syft or manual generation
- **Vulnerability Gating**: Optional Grype scanning with configurable severity thresholds
- **Cosign Verification**: Wrapper for container image and artifact signature verification
- **Provenance v4**: SLSA Provenance generation with materials tracking
- **Hardened K8s**: Security-focused Kubernetes deployment configurations
- **Helm Charts**: Production-ready Helm chart stubs

## 📋 Features

### 1. Authentication Hardening

The v94 bundle includes optional OIDC/JWKS authentication:

```python
# Enable OIDC authentication
export OIDC_ENABLED=true
export JWKS_URL=https://your-issuer.com/.well-known/jwks.json

# Start the server
python app.py
```

Authentication is validated using JWKS-by-kid, ensuring only tokens signed with valid keys are accepted.

### 2. Glyph Guard v14

Enhanced glyph validation with stricter policies:

```bash
# Test glyph validation
python glyph_guard_v14.py "your-glyph-text"

# Configure policy
vim glyph_policy.yaml
```

**Policy Features:**
- Maximum glyph length enforcement
- Forbidden pattern detection (XSS, injection, path traversal)
- Entropy threshold for detecting suspicious random data
- Character set validation
- Required field enforcement

### 3. Supply Chain Security

#### SBOM Generation

```bash
# Generate SBOM with Syft (preferred)
python generate_sbom.py

# Or use manual requirements.txt parsing
python generate_sbom.py
```

#### Vulnerability Scanning

```bash
# Scan SBOM for vulnerabilities
python scan_vulnerabilities.py --sbom sbom.json --fail-on high

# Skip scan if Grype not installed
python scan_vulnerabilities.py --skip
```

### 4. Signature Verification

```bash
# Verify container image signature
python cosign_wrapper.py --image myimage:tag --key cosign.pub

# Verify with keyless (Fulcio/Rekor)
python cosign_wrapper.py --image myimage:tag --keyless

# Verify blob signature
python cosign_wrapper.py --blob artifact.tar.gz --signature artifact.sig --key cosign.pub
```

### 5. Provenance Generation

```bash
# Generate SLSA Provenance v4
python generate_provenance.py bundle.tar.gz --output provenance.json

# View provenance
cat provenance.json | jq .
```

## 🐳 Container Deployment

### Build Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy application
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY glyph_policy.yaml .

# Security: Non-root user
RUN useradd -u 10001 -m codex
USER codex

EXPOSE 8000

CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t codex-v94:latest .
docker run -p 8000:8000 codex-v94:latest
```

## ☸️ Kubernetes Deployment

### Hardened Deployment

The v94 bundle includes production-ready Kubernetes configurations with:

- **Security Context**: Non-root user, read-only filesystem, dropped capabilities
- **Network Policies**: Restricted ingress/egress
- **Pod Security**: AppArmor, Seccomp profiles
- **Resource Limits**: CPU and memory constraints
- **Health Checks**: Liveness and readiness probes
- **High Availability**: Pod anti-affinity, PodDisruptionBudget

Deploy:

```bash
# Apply hardened deployment
kubectl apply -f k8s/deployment-hardened.yaml

# Check deployment
kubectl get pods -n codex-v94
kubectl get svc -n codex-v94
```

### Helm Chart

Install using Helm:

```bash
# Install chart
helm install codex-v94 ./helm

# Customize values
helm install codex-v94 ./helm -f custom-values.yaml

# Upgrade
helm upgrade codex-v94 ./helm
```

## 🔐 Security Configuration

### Environment Variables

```bash
# Authentication
OIDC_ENABLED=false
JWKS_URL=

# Application
PORT=8000
GLYPH_POLICY_PATH=glyph_policy.yaml

# Kubernetes Secrets (for production)
kubectl create secret generic codex-v94-secrets \
  --from-literal=jwks-url=https://your-issuer.com/.well-known/jwks.json \
  -n codex-v94
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: codex-v94-config
data:
  oidc_enabled: "true"
  jwks_url: "https://your-issuer.com/.well-known/jwks.json"
```

## 🔧 Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/glyph/verify \
  -H "Content-Type: application/json" \
  -d '{"glyph": "test-glyph"}'
```

### Testing

```bash
# Test glyph guard
python glyph_guard_v14.py "safe-glyph"
python glyph_guard_v14.py "<script>alert('xss')</script>"

# Generate test SBOM
python generate_sbom.py

# Test vulnerability scanning
python scan_vulnerabilities.py --sbom sbom.json
```

## 📊 CI/CD Integration

The bundle includes a comprehensive GitHub Actions workflow (`.github/workflows/build-and-verify.yml`):

1. **Lint**: Code quality checks with flake8 and black
2. **Security Scan**: Trivy filesystem scanning
3. **Build**: Dependency installation and testing
4. **SBOM Generation**: Automated SBOM creation
5. **Vulnerability Scan**: Grype scanning with configurable thresholds
6. **Container Build**: Docker image building and pushing
7. **Provenance**: SLSA Provenance v4 generation
8. **Deploy**: Staging deployment (optional)

## 📦 Files Structure

```
v94/
├── app.py                      # FastAPI application
├── glyph_guard_v14.py          # Glyph validation
├── glyph_policy.yaml           # Policy configuration
├── generate_sbom.py            # SBOM generator
├── scan_vulnerabilities.py     # Vulnerability scanner
├── cosign_wrapper.py           # Signature verification
├── generate_provenance.py      # Provenance generator
├── requirements.txt            # Python dependencies
├── k8s/
│   └── deployment-hardened.yaml # Kubernetes manifests
├── helm/
│   ├── Chart.yaml              # Helm chart metadata
│   └── values.yaml             # Helm values
├── .github/workflows/
│   └── build-and-verify.yml    # CI/CD workflow
└── README.md                   # This file
```

## 🔒 Security Best Practices

1. **Always verify signatures** before deploying artifacts
2. **Run vulnerability scans** on every build
3. **Use read-only root filesystems** in containers
4. **Enable OIDC authentication** in production
5. **Apply network policies** to restrict traffic
6. **Monitor provenance** for supply chain integrity
7. **Use non-root users** in all containers
8. **Enable security contexts** in Kubernetes

## 📝 License

This bundle is part of the Domion Nexus project, subject to ECCL-1.0 licensing.

Cryptographically bound to:
```
sha256(calebfedorbykerkonev10271998)
= 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
```

## 🤝 Contributing

For contributions, please ensure:
- All code passes linting (flake8, black)
- Security scans pass without critical/high vulnerabilities
- SBOM is generated and included
- Provenance is generated for all artifacts
- Kubernetes manifests follow security best practices

## 📚 References

- [SLSA Provenance v1](https://slsa.dev/provenance/v1)
- [CycloneDX SBOM Specification](https://cyclonedx.org/)
- [Sigstore Cosign](https://github.com/sigstore/cosign)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [JWKS RFC 7517](https://datatracker.ietf.org/doc/html/rfc7517)

---

**Built with security, verified with confidence** 🛡️
