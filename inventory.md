# Inventory — domionnexus

Generated: 2025-10-26

This file records a quick inventory of the repository and the initial findings used to plan platform scaffolding for Netlify, engine stubs, and integrations.

## Files and folders found (root)
- `.github/workflows/blank.yml` — placeholder workflow
- `README.md` — project README (detailed, Netlify-focused instructions and project overview)

No other files or folders were present in the workspace when scanned. The README references many expected directories (public, netlify/functions, data, lib, scripts), but those are not present in this repo snapshot.

## README summary (key points)
- Project is designed for Netlify: Netlify Functions, Netlify CI/CD, `netlify.toml`, and `public/` static pages.
- Main components described: Universal artifact (`data/Codex_Universal.json`), serverless API functions under `netlify/functions/`, scripts to build/sign the artifact, and dependencies (OpenAI, Supabase, jose).
- Environment variables expected: `OPENAI_API_KEY`, `OPENAI_MODEL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE`, `CFBK_PUBLIC_JWK`.
- The README includes a runnable blueprint (folder tree, function examples, `netlify.toml`, `package.json`) — intended to be copy/pasted to create a deployable repo.

## Current state vs. expected
- Expected but missing (per README): `public/`, `netlify/functions/`, `data/`, `lib/`, `scripts/`, `netlify.toml`, `package.json`, `.env.example`.
- Only existing files: `README.md` and a blank GitHub workflow.

## Assumptions (confirmed by user earlier)
- Target platform(s): Netlify (primary) plus local `netlify dev` for developer testing.
- Engines: create simple Python (FastAPI) and Node.js service stubs to represent worker/runtime engines.
- "Nous": an orchestration/agent component (lightweight Python service) that can call engines and integrations.
- Integrations: Postgres (or Supabase), Redis, OpenAI connector, and basic observability (OpenTelemetry/console logs).
- CI/CD: GitHub Actions for build/test and Netlify for deployment.

## Next actions (proposed)
1. Create a minimal scaffold matching the README blueprint: `public/`, `netlify/functions/`, `data/`, `lib/`, `scripts/`, `netlify.toml`, and `package.json`.
2. Implement lightweight, runnable stubs:
   - `netlify/functions/` sample JS functions: `verify.js`, `universal.js`, `oracle.js` (simple, no secrets).
   - `engines/` two example engines: `python-engine/` (FastAPI) and `node-engine/` (small ES module) with Dockerfiles.
   - `nous/` orchestration service (Python) that demonstrates calling an engine and a netlify function endpoint.
3. Add `.env.example`, basic GitHub Actions workflow for tests, and a `README.md` usage section.
4. Add simple tests (happy-path) and CI to run them.

## Notes and risks
- No secrets or cloud credentials are present; any cloud-specific manifests will be generated as generic manifests (Helm/k8s/Docker) and require user-supplied credentials for actual deployment.
- The README contains domain-specific content and licensing constraints (ECCL-1.0). Ensure that copying or publishing respects the license and subject-hash requirements.

---

I will now scaffold the architecture document and repository skeleton (next: `ARCHITECTURE.md` and initial scaffolding files). If you'd like different engines, platforms, or integrations, tell me now; otherwise I'll proceed with the assumed stack.
