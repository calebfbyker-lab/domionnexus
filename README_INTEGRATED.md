# 🌌 Domion Nexus - Integrated Deployment

**Codex Immortal AI Orchestration Platform - ECCL-1.0 Licensed**

> A cryptographically licensed, symbolically rich AI orchestration platform integrating multiple versions of the Codex system into a unified, deployable application.

## 📋 Overview

This repository contains an integrated version of the Domion Nexus project, consolidating features from multiple development branches (v93-v106) into a production-ready deployment.

### Key Features

- ✅ **Universal Artifact System** - Single JSON manifest containing all seals, glyphs, and star seeds
- ✅ **ECCL-1.0 License Gate** - Verifiable license system using Ed25519 JWS signatures
- ✅ **Netlify Deployment** - Serverless functions and automatic CI/CD
- ✅ **TSG Glyph Syntax** - Compact symbolic language parser
- ✅ **Cryptographic Binding** - All artifacts bound to subject hash

### Subject Identity

All code and artifacts are cryptographically bound to:

```
sha256(calebfedorbykerkonev10271998)
= 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
```

## 🚀 Quick Start

### Prerequisites

- Node.js >= 20.0.0
- npm or yarn
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/calebfbyker-lab/domionnexus.git
cd domionnexus

# Install dependencies
npm install

# Build the universal artifact
npm run build

# Run local development server
npm run dev

# Access at http://localhost:8888
```

### Deploy to Netlify

#### Option 1: GitHub Integration (Recommended)

1. Push this repository to your GitHub account
2. Go to [Netlify](https://app.netlify.com)
3. Click "Add new site" → "Import an existing project"
4. Select your GitHub repository
5. Configure:
   - Build command: `npm run build`
   - Publish directory: `public`
6. Add environment variables (see below)
7. Deploy!

#### Option 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize and deploy
netlify init
netlify deploy --prod
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment instructions.

## 🗂️ Project Structure

```
domionnexus/
├── public/                 # Static HTML pages
│   ├── index.html         # Portal homepage
│   └── .well-known/       # Identity verification
├── netlify/functions/     # Serverless API functions
│   ├── verify.js         # ECCL license verification
│   └── universal.js      # Universal codex search
├── lib/                   # Shared libraries
│   ├── subject.js        # Cryptographic identity
│   └── tsg.js            # TSG glyph parser
├── scripts/              # Build and utility scripts
│   └── build-universal.mjs # Artifact compiler
├── data/                 # Data files
│   ├── starseeds.json    # Star seed data
│   └── Codex_Universal.json # Generated artifact
├── grimoire/             # Symbolic data
│   └── glyphs.json       # Glyph definitions
├── seals/                # Seal JSON files
├── netlify.toml          # Netlify configuration
├── package.json          # Dependencies
└── .github/workflows/    # CI/CD workflows
    ├── deploy.yml        # Deployment workflow
    └── quality.yml       # Code quality checks
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (or configure in Netlify dashboard):

```env
# Optional: OpenAI Integration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Optional: Supabase Ledger
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_SERVICE_ROLE=YOUR_SERVICE_ROLE_SECRET

# Required: ECCL License Verification
CFBK_PUBLIC_JWK={"kty":"OKP","crv":"Ed25519","x":"BASE64URL_PUBLIC_KEY"}
```

### Build Configuration

The build process (`npm run build`):

1. Scans `seals/` directory for JSON files
2. Loads `grimoire/glyphs.json`
3. Loads `data/starseeds.json`
4. Compiles into `data/Codex_Universal.json`
5. Generates SHA-256 hash
6. Binds to ECCL-1.0 subject ID

## 📡 API Endpoints

Once deployed, these endpoints are available:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/verify` | POST | ECCL license verification |
| `/api/universal` | GET | Search universal codex |

### Example: Universal Search

```bash
curl https://your-site.netlify.app/api/universal?q=dragon&limit=10
```

Response:
```json
{
  "artifact_sha256": "2d9fc23a...",
  "license": "ECCL-1.0",
  "count": 3,
  "results": [
    {"type": "seal", "name": "..."},
    {"type": "glyph", "symbol": "🌀"},
    {"type": "star", "name": "Alpha Draconis"}
  ]
}
```

## 🔒 Security & License

### ECCL-1.0 License

This software is licensed under the **Eternal Creative Covenant License v1.0**.

Key points:
- All artifacts cryptographically bound to subject ID
- Redistribution requires recorded approval (signed JWS)
- Builds must embed subject hash + artifact SHA-256
- Purpose: preservation of knowledge, research, and attribution integrity

### No Supernatural Claims

All content is **symbolic and educational**. No metaphysical or supernatural claims are made. This is a digital library for cultural and symbolic study.

## 🧪 Testing

```bash
# Run tests (when implemented)
npm test

# Check code quality
npm run lint

# Verify build
npm run build
```

## 📚 Integration Notes

This repository integrates features from multiple development branches:

- **v93.x**: Natural language processing, OIDC auth, supply chain transparency
- **v94**: JWKS verification, glyph policy enforcement, SBOM/provenance
- **v96**: Threshold signatures, nonce replay protection
- **v98**: Boot-time integrity verification, HMAC keyring
- **v100**: Policy-driven deployment, zero-trust execution
- **v102**: Neurocybernetics telemetry and consent ledger
- **v106**: Orchestrator + API gateway with symbolic glyph workflows

All features have been consolidated into a unified, production-ready deployment structure.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📖 Documentation

- [Deployment Guide](./DEPLOYMENT.md) - Comprehensive deployment instructions
- [LICENSE](./LICENSE.md) - ECCL-1.0 legal text
- [PROVENANCE](./PROVENANCE.md) - Cryptographic provenance tracking

## 🔗 Links

- Repository: https://github.com/calebfbyker-lab/domionnexus
- Issues: https://github.com/calebfbyker-lab/domionnexus/issues
- Netlify: https://www.netlify.com

## 📞 Support

For deployment issues:
- Netlify Support: https://support.netlify.com
- Netlify Docs: https://docs.netlify.com

For application issues:
- GitHub Issues: https://github.com/calebfbyker-lab/domionnexus/issues

---

**Built with cryptographic integrity. Licensed under ECCL-1.0.**

```
sha256(calebfedorbykerkonev10271998)
= 2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a
```

© Caleb Fedor Byker Konev (1998-10-27) - ECCL-1.0 Licensed
