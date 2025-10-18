# DomionNexus - Deployment Guide

## 🌌 Overview

This deployment includes:
- **Vite + React Three Fiber Sigil Engine UI**: Interactive 3D visualization
- **Provenance-aware Agent Runner**: OpenAI-powered agent with CFBK binding
- **Netlify Functions**: `run-agent` and `orchestrator` serverless endpoints
- **Integrity Generator**: Build-time verification via `dist/integrity.json`

**Workflow Reference**: `wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e` version=5  
**Subject ID (CFBK)**: `2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a`

---

## 📋 Prerequisites

- Node.js ≥ 18
- Netlify account
- OpenAI API key

---

## 🚀 Deployment Steps

### 1. Set Environment Variables in Netlify

Navigate to: **Site Settings → Environment Variables**

Add the following variables:

```bash
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4o-mini
HUMAN_IN_LOOP=true
AGENT_MAX_RUNS=10
CFBK_PUBLIC_JWK={"kty":"OKP","crv":"Ed25519","x":"BASE64URL_PUBLIC_KEY"}
```

**Important Security Notes**:
- Keep `HUMAN_IN_LOOP=true` in production until gating and audits are in place
- Rotate any exposed keys immediately
- Never commit secrets to the repository

### 2. Connect Repository to Netlify

1. Go to Netlify Dashboard
2. Click **Add new site** → **Import an existing project**
3. Connect to your Git provider (GitHub)
4. Select the `domionnexus` repository
5. Configure build settings:
   - **Build command**: `npm run netlify:build`
   - **Publish directory**: `dist`
   - **Functions directory**: `netlify/functions` (auto-detected)

### 3. Deploy

Once environment variables are set, click **Deploy site**

Netlify will:
1. Run `npm install`
2. Execute `npm run netlify:build` which:
   - Builds the Vite app to `dist/`
   - Generates `dist/integrity.json` with file hashes and provenance metadata
3. Deploy the static site from `dist/`
4. Deploy serverless functions from `netlify/functions/`

### 4. Verify Deployment

After deployment completes, check:

- **Site URL**: `https://your-site.netlify.app/`
- **Integrity Manifest**: `https://your-site.netlify.app/integrity.json`
- **Functions**:
  - `https://your-site.netlify.app/.netlify/functions/run-agent`
  - `https://your-site.netlify.app/.netlify/functions/orchestrator`

---

## 🧪 Testing

### Test the UI

1. Navigate to your deployed site URL
2. You should see the Sigil Engine 3D visualization
3. The right panel shows the Agent Runner interface

### Test the Agent Function

```bash
curl -X POST https://your-site.netlify.app/.netlify/functions/run-agent \
  -H 'Content-Type: application/json' \
  -d '{
    "input_as_text": "wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e version=5: propose an integration plan to ingest and index the 407 seals into DomionNexus knowledge store for safe orchestration."
  }'
```

Expected response structure:
```json
{
  "success": true,
  "provenance": {
    "subject_id_sha256": "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a",
    "workflow_ref": "wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e",
    "workflow_version": 5,
    "timestamp_utc": "...",
    "human_in_loop": true,
    "max_runs": 10
  },
  "runs": [...],
  "total_runs": 1,
  "final_output": "..."
}
```

### Test the Orchestrator Function

```bash
curl https://your-site.netlify.app/.netlify/functions/orchestrator
```

Expected response:
```json
{
  "subject_id_sha256": "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a",
  "timestamp_utc": "...",
  "action": "status",
  "status": "operational",
  "version": "1.0.0",
  "capabilities": [
    "run-agent",
    "task-management",
    "provenance-tracking"
  ]
}
```

---

## 🏗️ Local Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```

Access at: `http://localhost:5173`

### Build Locally
```bash
npm run netlify:build
```

This will:
1. Build the app to `dist/`
2. Generate `dist/integrity.json`

### Test Functions Locally (with Netlify CLI)

```bash
npm install -g netlify-cli
netlify dev
```

Access at: `http://localhost:8888`

---

## 📁 Project Structure

```
domionnexus/
├── src/
│   ├── main.jsx              # React entry point
│   ├── App.jsx               # Main app component
│   ├── App.css               # App styles
│   ├── index.css             # Global styles
│   └── components/
│       └── SigilEngine.jsx   # R3F 3D visualization
├── netlify/
│   └── functions/
│       ├── run-agent.mjs     # Agent runner endpoint
│       └── orchestrator.mjs  # Orchestration endpoint
├── scripts/
│   └── generate-integrity.mjs # Build integrity generator
├── dist/                     # Build output (gitignored)
│   ├── index.html
│   ├── assets/
│   └── integrity.json        # Generated at build time
├── index.html                # Vite entry point
├── vite.config.js            # Vite configuration
├── netlify.toml              # Netlify configuration
├── package.json              # Dependencies and scripts
└── .env.example              # Environment variables template

```

---

## 🔐 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Human-in-the-Loop**: Keep `HUMAN_IN_LOOP=true` until proper gating is implemented
3. **Rate Limiting**: Consider implementing rate limiting for production
4. **Key Rotation**: Rotate exposed keys immediately
5. **Integrity Verification**: The `integrity.json` provides build-time verification
6. **Subject Binding**: All operations are bound to CFBK subject ID

---

## 🔍 Integrity Manifest

The `dist/integrity.json` file contains:
- Subject ID binding (CFBK)
- Workflow reference and version
- SHA-256 hashes of all built files
- Build timestamp and metadata

This provides cryptographic verification of the build artifacts.

---

## 🛠️ Troubleshooting

### Functions not working
- Verify environment variables are set in Netlify
- Check function logs in Netlify dashboard
- Ensure `OPENAI_API_KEY` is valid

### Build fails
- Check Node.js version (≥18 required)
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check build logs for specific errors

### 3D visualization not loading
- Check browser console for errors
- Ensure WebGL is supported in browser
- Try refreshing the page

---

## 📚 Additional Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React Three Fiber Documentation](https://docs.pmnd.rs/react-three-fiber/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

## 📄 License

ECCL-1.0 (Eternal Creative Covenant License)  
Bound to subject: `2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a`
