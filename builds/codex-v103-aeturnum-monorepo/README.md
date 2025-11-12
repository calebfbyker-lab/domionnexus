# Codex Aeturnum — v103 · Monorepo Prime

**Goal:** unify v101 / v101.x / v102 / v102.x into a single, boringly reproducible monorepo.
Everything is split into packages and services, with reusable CI, container images, and a small docs site.

Authorship & seal
subject: caleb fedor byker konev|1998-10-27
subject_id_sha256: 0f9d6b0c0e9f07e6a4cd3f8cc7e5c8a8f1e3b3f6f4b5a6c7d8e9f0a1b2c3d4e5
license: MIT + EUCLEA transparency clause

## Layout
codex-v103-aeturnum-monorepo/
├─ packages/
│ ├─ core/ # tetra-helix, chrono, glyph compiler
│ └─ neuro/ # neurocybernetics: signal/decoder/sim
├─ services/
│ └─ api/ # FastAPI gateway mounting v101/v102 routers
├─ docs/ # lightweight static docs
├─ .github/workflows/ # per-package CI + reusable workflow
├─ tools/ # lint/format hooks, semantic diff
└─ docker/ # compose for local dev

