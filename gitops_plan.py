"""
GitOps Deployment Plan for Codex v98 Orthos
Kubernetes deployment configuration and workflow
"""

GITOPS_PLAN = """
# GitOps Deployment Plan - Codex v98 Orthos

## Overview
This plan outlines the GitOps workflow for deploying Codex v98 Orthos to Kubernetes.

## Architecture
- **GitOps Tool**: ArgoCD or FluxCD
- **Repository**: Git repository as source of truth
- **Target**: Kubernetes cluster
- **Deployment Strategy**: Progressive delivery with shadow metrics

## Deployment Workflow

### 1. Pre-Deployment Checks
```bash
# Run self-check
python selfcheck.py

# Verify integrity
python scripts/verify_manifest.py

# Check vulnerabilities
python scripts/vuln_gate.py

# Build provenance
python scripts/provenance_v4.py
```

### 2. Build Container Image
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run self-check at build time
RUN python selfcheck.py

# Verify manifest
RUN python scripts/verify_manifest.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Kubernetes Manifests

#### Deployment (deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-orthos
  namespace: domionnexus
  labels:
    app: codex
    version: v98
    codename: orthos
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: codex
  template:
    metadata:
      labels:
        app: codex
        version: v98
    spec:
      initContainers:
      - name: selfcheck
        image: codex-orthos:v98
        command: ["python", "selfcheck.py"]
        volumeMounts:
        - name: app-data
          mountPath: /app
      containers:
      - name: app
        image: codex-orthos:v98
        ports:
        - containerPort: 8000
        env:
        - name: CODEX_API_KEY
          valueFrom:
            secretKeyRef:
              name: codex-secrets
              key: api-key
        - name: CODEX_HMAC_KEY
          valueFrom:
            secretKeyRef:
              name: codex-secrets
              key: hmac-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: app-data
          mountPath: /app/data
        - name: config
          mountPath: /app/config
      volumes:
      - name: app-data
        emptyDir: {}
      - name: config
        configMap:
          name: codex-config
```

#### Service (service.yaml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: codex-orthos
  namespace: domionnexus
spec:
  type: ClusterIP
  selector:
    app: codex
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

#### Ingress (ingress.yaml)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: codex-orthos
  namespace: domionnexus
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - codex.domionnexus.io
    secretName: codex-tls
  rules:
  - host: codex.domionnexus.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: codex-orthos
            port:
              number: 80
```

#### ConfigMap (configmap.yaml)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: codex-config
  namespace: domionnexus
data:
  app.config: |
    {
      "version": "v98",
      "codename": "Orthos",
      "features": [
        "boot-time-selfcheck",
        "hmac-keyring",
        "shadow-deploy",
        "auto-rollback",
        "judge-glyph",
        "tuf-lite"
      ]
    }
```

#### Secrets (secrets.yaml - template)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: codex-secrets
  namespace: domionnexus
type: Opaque
stringData:
  api-key: "YOUR_API_KEY"
  hmac-key: "YOUR_HMAC_KEY"
```

### 4. Progressive Deployment Strategy

#### Canary Deployment
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: codex-orthos
  namespace: domionnexus
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codex-orthos
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 95
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: judge-gate
      url: http://codex-orthos/glyph
      type: pre-rollout
      body: |
        {
          "glyph": "judge:quality,security",
          "dry_run": false
        }
```

### 5. ArgoCD Application
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: codex-orthos
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/calebfbyker-lab/domionnexus
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: domionnexus
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

## Rollout Phases

### Phase 1: Canary (5% traffic)
- Deploy to 5% of users
- Monitor shadow metrics
- Run JUDGE gate checks
- Duration: 15 minutes

### Phase 2: Progressive Rollout (10% → 50%)
- If canary passes, increase to 10%
- Continue monitoring
- Advance in 10% increments every 10 minutes
- Auto-rollback if error rate > 5%

### Phase 3: Full Rollout (100%)
- Complete deployment to all users
- Continue monitoring for 24 hours
- Keep previous version ready for quick rollback

## Monitoring

### Key Metrics
- Request success rate (target: >95%)
- Error rate (threshold: <5%)
- Response time p95 (threshold: <500ms)
- Health check success rate (target: >99%)

### Alerts
- Critical: Error rate >5% → Auto-rollback
- Warning: Response time >500ms
- Info: Deployment progress updates

## Rollback Procedure

### Automatic Rollback
```bash
# Triggered automatically by shadow_metrics.py
python shadow_metrics.py
```

### Manual Rollback
```bash
# Using kubectl
kubectl rollout undo deployment/codex-orthos -n domionnexus

# Using glyph
curl -X POST http://codex-orthos/glyph \
  -H "X-API-Key: $CODEX_API_KEY" \
  -d '{"glyph": "rollback:previous"}'
```

## Post-Deployment

1. Verify deployment:
   ```bash
   kubectl get pods -n domionnexus
   kubectl logs -f deployment/codex-orthos -n domionnexus
   ```

2. Run smoke tests:
   ```bash
   curl https://codex.domionnexus.io/health
   curl https://codex.domionnexus.io/seal
   ```

3. Update TUF metadata:
   ```bash
   python tuf_lite.py update
   ```

4. Create deployment attestation:
   ```bash
   curl -X POST http://codex-orthos/glyph \
     -H "X-API-Key: $CODEX_API_KEY" \
     -d '{"glyph": "sanctify:v98-orthos"}'
   ```

## Security Considerations

1. **Integrity**: Self-check runs at container startup
2. **Secrets**: Stored in Kubernetes secrets, rotated monthly
3. **HMAC Keys**: Managed by keyring with automatic rotation
4. **Network**: Ingress with TLS, internal services use ClusterIP
5. **RBAC**: Service account with minimal permissions

## References
- Kubernetes Documentation: https://kubernetes.io/docs/
- ArgoCD: https://argo-cd.readthedocs.io/
- Flagger (Progressive Delivery): https://flagger.app/
"""

if __name__ == "__main__":
    print(GITOPS_PLAN)
