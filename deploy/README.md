Codex Aeturnum — Deployment artifacts

This folder contains minimal Kubernetes manifests and deployment guidance for Codex Aeturnum bundles (v102..v104).

Authorship anchor: caleb fedor byker konev|1998-10-27
subject_id_sha256: 0f9d6b0c0e9f07e6a4cd3f8cc7e5c8a8f1e3b3f6f4b5a6c7d8e9f0a1b2c3d4e5

Includes:
- k8s/deployment.yaml — minimal Deployment + Service for the API gateway
- k8s/namespace.yaml — namespace with annotation binding the subject

Notes: These manifests are templates for demos. Replace image references and secrets with your registry and secrets manager.
