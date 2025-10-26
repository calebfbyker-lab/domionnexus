# Codex v94 Deployment Guide

## Prerequisites

### Required Tools
- Python 3.11+
- Docker (for containerized deployment)
- kubectl (for Kubernetes deployment)
- Helm 3.x (for Helm deployment)

### Optional Tools (for enhanced features)
- Syft (for SBOM generation)
- Grype (for vulnerability scanning)
- Cosign (for signature verification)

## Local Development

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/calebfbyker-lab/domionnexus.git
cd domionnexus/v94

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Locally

```bash
# Start the server
python app.py

# Server runs on http://localhost:8000
# Health check: curl http://localhost:8000/health
```

### 3. Test Components

```bash
# Test Glyph Guard
python glyph_guard_v14.py "test-glyph"

# Generate SBOM
python generate_sbom.py

# Run build verification
./verify.sh
```

## Docker Deployment

### 1. Build Container

```bash
# Build image
docker build -t codex-v94:latest .

# Verify image
docker images | grep codex-v94
```

### 2. Run Container

```bash
# Run with default settings
docker run -p 8000:8000 codex-v94:latest

# Run with environment variables
docker run -p 8000:8000 \
  -e OIDC_ENABLED=true \
  -e JWKS_URL=https://your-issuer.com/.well-known/jwks.json \
  codex-v94:latest

# Run in detached mode
docker run -d -p 8000:8000 --name codex-v94 codex-v94:latest

# View logs
docker logs codex-v94

# Stop container
docker stop codex-v94
```

### 3. Push to Registry

```bash
# Tag for registry
docker tag codex-v94:latest ghcr.io/yourorg/codex-v94:latest

# Login to registry
docker login ghcr.io

# Push
docker push ghcr.io/yourorg/codex-v94:latest
```

## Kubernetes Deployment

### 1. Prepare Cluster

```bash
# Create namespace
kubectl create namespace codex-v94

# Verify namespace
kubectl get namespaces
```

### 2. Configure Secrets (if using OIDC)

```bash
# Create secret for JWKS URL
kubectl create secret generic codex-v94-secrets \
  --from-literal=jwks-url=https://your-issuer.com/.well-known/jwks.json \
  -n codex-v94

# Verify secret
kubectl get secrets -n codex-v94
```

### 3. Deploy Application

```bash
# Apply manifests
kubectl apply -f k8s/deployment-hardened.yaml

# Verify deployment
kubectl get all -n codex-v94

# Check pod status
kubectl get pods -n codex-v94

# View logs
kubectl logs -n codex-v94 -l app=codex-v94

# Check service
kubectl get svc -n codex-v94
```

### 4. Access Application

```bash
# Port forward for testing
kubectl port-forward -n codex-v94 svc/codex-v94-service 8000:80

# Test health endpoint
curl http://localhost:8000/health

# For production, configure Ingress or LoadBalancer
```

### 5. Update Deployment

```bash
# Update image
kubectl set image deployment/codex-v94-sentinel \
  codex=codex-v94:new-version \
  -n codex-v94

# Watch rollout
kubectl rollout status deployment/codex-v94-sentinel -n codex-v94

# Rollback if needed
kubectl rollout undo deployment/codex-v94-sentinel -n codex-v94
```

## Helm Deployment

### 1. Install Chart

```bash
# Install with defaults
helm install codex-v94 ./helm

# Install in specific namespace
helm install codex-v94 ./helm --namespace codex-v94 --create-namespace

# Install with custom values
helm install codex-v94 ./helm -f custom-values.yaml
```

### 2. Customize Values

Create `custom-values.yaml`:

```yaml
# custom-values.yaml
replicaCount: 3

image:
  repository: ghcr.io/yourorg/codex-v94
  tag: "v1.0.0"

config:
  oidcEnabled: true
  jwksUrl: "https://your-issuer.com/.well-known/jwks.json"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: codex.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
```

### 3. Upgrade Chart

```bash
# Upgrade with new values
helm upgrade codex-v94 ./helm -f custom-values.yaml

# Check upgrade status
helm status codex-v94

# View history
helm history codex-v94

# Rollback if needed
helm rollback codex-v94 1
```

### 4. Uninstall Chart

```bash
# Uninstall
helm uninstall codex-v94

# Verify cleanup
kubectl get all -n codex-v94
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Application port | 8000 | No |
| `OIDC_ENABLED` | Enable OIDC auth | false | No |
| `JWKS_URL` | JWKS endpoint URL | "" | If OIDC enabled |
| `GLYPH_POLICY_PATH` | Policy file path | glyph_policy.yaml | No |

### Glyph Policy

Edit `glyph_policy.yaml`:

```yaml
version: "v14"
strict_mode: true
max_glyph_length: 256
entropy_threshold: 0.8
forbidden_patterns:
  - "<script"
  - "javascript:"
  # Add more patterns as needed
```

### Kubernetes ConfigMap

Update the ConfigMap in `k8s/deployment-hardened.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: codex-v94-config
data:
  oidc_enabled: "true"
  jwks_url: "https://your-issuer.com/.well-known/jwks.json"
  glyph_policy: |
    # Your policy content
```

## Monitoring

### Health Checks

```bash
# Health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "94.0.0",
#   "features": {
#     "oidc_enabled": false,
#     "glyph_guard": true,
#     "sbom_gating": true,
#     "provenance_v4": true
#   }
# }
```

### Kubernetes Monitoring

```bash
# Pod status
kubectl get pods -n codex-v94 -w

# Resource usage
kubectl top pods -n codex-v94

# Events
kubectl get events -n codex-v94

# Describe pod
kubectl describe pod <pod-name> -n codex-v94
```

## Security Best Practices

### 1. Enable OIDC Authentication

```bash
# Set environment variables
export OIDC_ENABLED=true
export JWKS_URL=https://your-issuer.com/.well-known/jwks.json
```

### 2. Run Vulnerability Scans

```bash
# Generate SBOM
python generate_sbom.py

# Scan for vulnerabilities
python scan_vulnerabilities.py --sbom sbom.json --fail-on high
```

### 3. Verify Signatures

```bash
# Verify container image
python cosign_wrapper.py --image codex-v94:latest --keyless

# Verify artifacts
python cosign_wrapper.py \
  --blob artifact.tar.gz \
  --signature artifact.sig \
  --key cosign.pub
```

### 4. Generate Provenance

```bash
# Create provenance
python generate_provenance.py bundle.tar.gz --output provenance.json

# Verify provenance
cat provenance.json | jq .predicate.buildDefinition
```

### 5. Network Policies

The hardened deployment includes network policies that:
- Restrict ingress to Istio/ingress controller only
- Allow egress for HTTPS (443) and DNS (53)
- Block all other traffic by default

### 6. Security Contexts

All pods run with:
- Non-root user (UID 10001)
- Read-only root filesystem
- Dropped capabilities (ALL)
- AppArmor and Seccomp profiles

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs codex-v94

# Common issues:
# 1. Port already in use - change PORT env var
# 2. Missing dependencies - rebuild image
# 3. Configuration errors - check env vars
```

### Pod CrashLoopBackOff

```bash
# Check pod logs
kubectl logs -n codex-v94 <pod-name>

# Check events
kubectl describe pod -n codex-v94 <pod-name>

# Common issues:
# 1. Image pull errors - check registry access
# 2. Health check failures - verify /health endpoint
# 3. Resource limits - adjust in values.yaml
```

### OIDC Authentication Fails

```bash
# Verify JWKS URL is accessible
curl https://your-issuer.com/.well-known/jwks.json

# Check logs for JWT verification errors
kubectl logs -n codex-v94 -l app=codex-v94 | grep "Token verification"

# Ensure token has correct format
# Bearer <token>
```

### Glyph Guard Rejections

```bash
# Test glyph locally
python glyph_guard_v14.py "your-glyph-text"

# Check policy configuration
cat glyph_policy.yaml

# Adjust policy if needed
# - Increase max_glyph_length
# - Adjust entropy_threshold
# - Modify forbidden_patterns
```

## CI/CD Integration

### GitHub Actions

The bundle includes `.github/workflows/build-and-verify.yml`:

1. **Lint**: Code quality checks
2. **Security Scan**: Trivy scanning
3. **Build**: Dependency installation
4. **SBOM**: Generate SBOM
5. **Vuln Scan**: Grype scanning
6. **Container Build**: Docker image
7. **Provenance**: SLSA Provenance v4
8. **Deploy**: Staging deployment

### Custom CI/CD

```bash
# Build pipeline example
./verify.sh                          # Verification
python build.py                      # Build
python generate_sbom.py              # SBOM
python scan_vulnerabilities.py       # Scan
docker build -t codex-v94:latest .   # Container
python generate_provenance.py ...    # Provenance
kubectl apply -f k8s/...             # Deploy
```

## Performance Tuning

### Resource Limits

Adjust in `helm/values.yaml`:

```yaml
resources:
  limits:
    cpu: 1000m      # 1 core
    memory: 1Gi     # 1 GB
  requests:
    cpu: 200m       # 0.2 cores
    memory: 256Mi   # 256 MB
```

### Scaling

```yaml
# Horizontal Pod Autoscaler
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Database Connection Pooling

If adding database support:
- Use connection pooling
- Set appropriate pool sizes
- Configure timeouts

## Backup and Recovery

### Configuration Backup

```bash
# Backup ConfigMaps and Secrets
kubectl get configmap -n codex-v94 -o yaml > backup-configmaps.yaml
kubectl get secret -n codex-v94 -o yaml > backup-secrets.yaml

# Restore
kubectl apply -f backup-configmaps.yaml
kubectl apply -f backup-secrets.yaml
```

### State Recovery

The application is stateless, but:
- Maintain SBOM records
- Keep provenance artifacts
- Archive container images

## Production Checklist

- [ ] OIDC authentication configured and tested
- [ ] Glyph policy customized for your use case
- [ ] SBOM generated and stored
- [ ] Vulnerability scan passed
- [ ] Container images signed with Cosign
- [ ] Provenance generated and verified
- [ ] Kubernetes manifests reviewed
- [ ] Network policies tested
- [ ] Resource limits appropriate
- [ ] Health checks verified
- [ ] Monitoring configured
- [ ] Logging aggregation set up
- [ ] Backup procedures documented
- [ ] Incident response plan ready

## Support

For issues or questions:
1. Check logs: `kubectl logs -n codex-v94 -l app=codex-v94`
2. Verify configuration: `kubectl get configmap -n codex-v94`
3. Review documentation: `v94/README.md`
4. Check release notes: `V94_RELEASE_NOTES.md`

---

**Deploy with confidence** 🚀
