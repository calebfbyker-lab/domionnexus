# v94 Bundle Structure

## Directory Layout
```
v94/
├── app.py                          # FastAPI application with JWKS verification
├── glyph_guard_v14.py              # Glyph policy enforcement
├── glyph_policy.yaml               # Policy configuration
├── generate_sbom.py                # SBOM generator
├── scan_vulnerabilities.py         # Grype wrapper
├── cosign_wrapper.py               # Signature verification
├── generate_provenance.py          # SLSA Provenance v4
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image definition
├── build.py                        # Build orchestration script
├── verify.sh                       # Quick verification script
├── .github/workflows/
│   └── build-and-verify.yml        # CI/CD pipeline
├── k8s/
│   └── deployment-hardened.yaml    # Hardened Kubernetes manifests
├── helm/
│   ├── Chart.yaml                  # Helm chart metadata
│   └── values.yaml                 # Helm configuration values
└── README.md                       # Complete documentation
```

## Quick Start

1. **Verify bundle integrity**
   ```bash
   ./verify.sh
   ```

2. **Build locally**
   ```bash
   python build.py
   ```

3. **Run with Docker**
   ```bash
   docker build -t codex-v94:latest .
   docker run -p 8000:8000 codex-v94:latest
   ```

4. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/deployment-hardened.yaml
   ```

5. **Deploy with Helm**
   ```bash
   helm install codex-v94 ./helm
   ```

## Key Features

- ✅ JWKS-by-kid verification
- ✅ Glyph Guard v14 with strict policy
- ✅ SBOM generation (Syft/manual)
- ✅ Vulnerability scanning (Grype)
- ✅ Cosign verification wrapper
- ✅ SLSA Provenance v4
- ✅ Hardened Kubernetes deployment
- ✅ Helm chart stubs
- ✅ Comprehensive CI/CD workflow
