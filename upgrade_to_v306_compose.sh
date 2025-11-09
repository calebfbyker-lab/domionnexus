#!/usr/bin/env bash
set -euo pipefail
ROOT="codex-v106"; test -d "$ROOT" || { echo "❌ need codex-v106 (v300–v305.x applied)"; exit 1; }
w(){ mkdir -p "$(dirname "$ROOT/$1")"; cat > "$ROOT/$1"; }

echo "→ v306 Mesh-in-a-Box: Dockerfiles + Compose + Prometheus + Grafana"

# ───────────── Per-service Dockerfiles (tiny) ─────────────
w services/api/Dockerfile <<'DOCKER'
FROM python:3.11-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app/../..:/app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
DOCKER

w services/orchestrator/Dockerfile <<'DOCKER'
FROM python:3.11-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app/../..:/app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8010
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8010"]
DOCKER

w services/nexus/Dockerfile <<'DOCKER'
FROM python:3.11-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app/../..:/app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8020
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8020"]
DOCKER

# ───────────── Compose env (edit to taste) ─────────────
w docker/.env.example <<'ENV'
# === Mesh node identity & secrets ===
CODEX_NODE_ID=node-A
CODEX_ORCH_URL=http://orchestrator:8010
CODEX_NEXUS_URL=http://nexus:8020

# Nexus persistence + access
NEXUS_DB=/var/lib/nexus/nexus.db
NEXUS_TOKENS="token123=ingest,read,metrics;viewer=read"
NEXUS_TOKENS_V2="k1:devA:ingest,read,metrics;k2:devB:read"
NEXUS_KEY=dev-hmac
# Optional ed25519 public key (Base64 verify key). Leave blank to use HMAC.
NEXUS_PUB=
NEXUS_IP_ALLOW=0.0.0.0/0
NEXUS_RPS=8
NEXUS_RPS_WIN=1.0

# Prometheus scrape interval
PROM_SCRAPE=15s
ENV

# ───────────── Prometheus config ─────────────
w docker/prometheus/prometheus.yml <<'YML'
global:
  scrape_interval: ${PROM_SCRAPE}
scrape_configs:
  - job_name: 'nexus'
    static_configs:
      - targets: ['nexus:8020']
    metrics_path: /metrics
    scheme: http
  - job_name: 'orchestrator'
    static_configs:
      - targets: ['orchestrator:8010']
    metrics_path: /metrics
  - job_name: 'gateway'
    static_configs:
      - targets: ['gateway:8000']
    metrics_path: /metrics
YML

# ───────────── Grafana provisioning (one tiny dashboard) ─────────────
w docker/grafana/provisioning/datasources/datasource.yml <<'YML'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
YML

w docker/grafana/provisioning/dashboards/dashboard.yml <<'YML'
apiVersion: 1
providers:
  - name: codex
    type: file
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
YML

w docker/grafana/dashboards/nexus.json <<'JSON'
{
  "annotations":{"list":[{"type":"dashboard","builtIn":1,"name":"Annotations & Alerts","hide":true}]},
  "panels":[
    {"type":"stat","title":"Nexus events","targets":[{"expr":"nexus_events_total"}],"gridPos":{"h":4,"w":8,"x":0,"y":0}},
    {"type":"stat","title":"AEON proofs","targets":[{"expr":"nexus_proofs_total"}],"gridPos":{"h":4,"w":8,"x":8,"y":0}},
    {"type":"timeseries","title":"Event rate","targets":[{"expr":"rate(nexus_events_total[5m])"}],"gridPos":{"h":8,"w":16,"x":0,"y":4}}
  ],
  "schemaVersion":36,
  "version":1,
  "title":"Codex · Nexus"
}
JSON

# ───────────── Compose file ─────────────
w docker/docker-compose.yml <<'YML'
version: "3.9"
services:
  gateway:
    build:
      context: ../services/api
      dockerfile: Dockerfile
    container_name: codex-gateway
    environment:
      CODEX_ORCH_URL: ${CODEX_ORCH_URL}
      CODEX_NEXUS_URL: ${CODEX_NEXUS_URL}
    ports: ["8000:8000"]
    depends_on: [orchestrator, nexus]

  orchestrator:
    build:
      context: ../services/orchestrator
      dockerfile: Dockerfile
    container_name: codex-orchestrator
    environment:
      CODEX_NODE_ID: ${CODEX_NODE_ID}
      CODEX_ORCH_URL: http://orchestrator:8010
      CODEX_NEXUS_URL: ${CODEX_NEXUS_URL}
    ports: ["8010:8010"]
    depends_on: [nexus]

  nexus:
    build:
      context: ../services/nexus
      dockerfile: Dockerfile
    container_name: codex-nexus
    environment:
      NEXUS_DB: ${NEXUS_DB}
      NEXUS_TOKENS: ${NEXUS_TOKENS}
      NEXUS_TOKENS_V2: ${NEXUS_TOKENS_V2}
      NEXUS_KEY: ${NEXUS_KEY}
      NEXUS_PUB: ${NEXUS_PUB}
      NEXUS_IP_ALLOW: ${NEXUS_IP_ALLOW}
      NEXUS_RPS: ${NEXUS_RPS}
      NEXUS_RPS_WIN: ${NEXUS_RPS_WIN}
    volumes:
      - nexus-data:/var/lib/nexus
    ports: ["8020:8020"]

  prometheus:
    image: prom/prometheus:latest
    container_name: codex-prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command: ["--config.file=/etc/prometheus/prometheus.yml"]
    ports: ["9090:9090"]
    depends_on: [gateway, orchestrator, nexus]

  grafana:
    image: grafana/grafana:latest
    container_name: codex-grafana
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    ports: ["3000:3000"]
    depends_on: [prometheus]

volumes:
  nexus-data:
  grafana-data:
YML

# ───────────── Make helpers ─────────────
w Makefile <<'MK'
.PHONY: up down logs ps
up:
	cd docker && cp -n .env.example .env || true && docker compose up -d --build
down:
	cd docker && docker compose down -v
logs:
	cd docker && docker compose logs -f --tail=200
ps:
	cd docker && docker compose ps
MK

echo "✓ v306 files written."
echo "→ Next:"
echo "   1) cd codex-v106/docker && cp .env.example .env && edit secrets"
echo "   2) make up   # starts the full mesh"
