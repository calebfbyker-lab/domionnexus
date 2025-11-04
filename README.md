# 🌌 DomionNexus — Sigil Engine AI Orchestration Platform
**Vite + React Three Fiber Edition · ECCL-1.0 Licensed**

> A cryptographically licensed, provenance-aware AI orchestration platform featuring an interactive 3D Sigil Engine, built with modern web technologies and deployed on Netlify.

---

## ✳️ Overview

DomionNexus is a modern web application that combines:

- **Vite + React Three Fiber** — Interactive 3D Sigil Engine visualization  
- **Provenance-aware Agent Runner** — OpenAI-powered agent with CFBK binding  
- **Netlify Functions** — Serverless `run-agent` and `orchestrator` endpoints  
- **Integrity Generator** — Build-time verification via `dist/integrity.json`  
- **Subject ID Binding** — All operations cryptographically bound to CFBK identifier

**Workflow Reference**: `wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e` version=5

Everything is cryptographically bound to the subject hash:

```
sha256(calebfedorbykerkonev10271998)
= 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
```

---

## 🗂 Project Structure

```
domionnexus/
├── src/                      → React application source
│   ├── components/          → React components (SigilEngine)
│   ├── App.jsx              → Main app component
│   └── main.jsx             → Entry point
├── netlify/functions/       → Serverless API functions
│   ├── run-agent.mjs       → Agent runner endpoint
│   └── orchestrator.mjs     → Orchestration endpoint
├── scripts/                 → Build and verification utilities
│   ├── generate-integrity.mjs → Integrity manifest generator
│   └── verify-build.mjs     → Build verification tool
├── dist/                    → Build output (auto-generated)
│   └── integrity.json       → Build integrity manifest
├── netlify.toml            → Netlify build configuration
├── vite.config.js          → Vite build configuration
└── package.json            → Dependencies and scripts
```

---

## ⚙️ Setup (Local Development)

### Requirements
- Node ≥ 18  
- Git
- Netlify CLI (optional, for local function testing)

### Install
```bash
npm install
```

### Environment Variables
Create a `.env` file or configure these in Netlify → Site Settings → Environment Variables:

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
HUMAN_IN_LOOP=true
AGENT_MAX_RUNS=10
CFBK_PUBLIC_JWK={"kty":"OKP","crv":"Ed25519","x":"BASE64URL_PUBLIC_KEY"}
```

### Build & Run Locally
```bash
# Development server
npm run dev

# Build for production
npm run netlify:build

# Verify build
npm run verify
```

---

## 🚀 Deploy to Netlify

**Quick Start:**

1. **Set environment variables** in Netlify → Site Settings → Environment Variables
2. **Connect repository** to Netlify
3. **Configure build settings**:
   - Build command: `npm run netlify:build`
   - Publish directory: `dist`
4. **Deploy!**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 🧪 Testing

### Test the Agent Function

```bash
curl -X POST https://your-site.netlify.app/.netlify/functions/run-agent \
  -H 'Content-Type: application/json' \
  -d '{
    "input_as_text": "wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e version=5: propose an integration plan to ingest and index the 407 seals into DomionNexus knowledge store for safe orchestration."
  }'
```

### Test the Orchestrator

```bash
curl https://your-site.netlify.app/.netlify/functions/orchestrator
```

---

## 📋 Key Features

### 3D Sigil Engine
- Interactive WebGL visualization using React Three Fiber
- Animated toroidal geometry representing symbolic structures
- Particle field with dynamic rotation
- Orbital camera controls

### Provenance-aware Agent Runner
- OpenAI integration with configurable models
- Subject ID binding (CFBK) on all operations
- Workflow reference validation
- Human-in-the-loop safeguards
- Structured provenance metadata

### Integrity Manifest
- SHA-256 hashing of all build artifacts
- Cryptographic binding to subject ID
- Workflow reference tracking
- Build timestamp and metadata

---

## 🔐 Security Notes

- **Rotate any exposed keys immediately** (do not commit secrets)
- **Keep `HUMAN_IN_LOOP=true`** in production until gating and audits are in place
- All operations are bound to subject ID: `2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a`
- Build integrity verification via `dist/integrity.json`

---

## 📄 License

**ECCL-1.0** (Eternal Creative Covenant License)

This software, dataset, and all derivative artifacts are bound to the identity:
```
2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
```

---

## 🛠️ Developer Commands

```bash
npm run dev            # Start development server
npm run build          # Build for production (Vite only)
npm run netlify:build  # Build + generate integrity.json
npm run verify         # Verify build integrity
npm run preview        # Preview production build locally
```

---

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) — Detailed deployment instructions
- [Netlify Documentation](https://docs.netlify.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React Three Fiber Documentation](https://docs.pmnd.rs/react-three-fiber/)

---

**Build with reason, preserve with clarity, and verify everything.**  
— The DomionNexus Ethos
