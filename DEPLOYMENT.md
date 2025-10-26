# Deployment Guide - Domion Nexus

This guide covers deploying Domion Nexus to Netlify for production use.

## Prerequisites

- Node.js >= 20.0.0
- npm or yarn
- A Netlify account
- (Optional) Supabase account for ledger features
- (Optional) OpenAI API key for oracle features

## Quick Start - Netlify Deployment

### Option 1: GitHub Integration (Recommended)

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/domionnexus.git
   git push -u origin main
   ```

2. **Connect to Netlify**
   - Go to https://app.netlify.com
   - Click "Add new site" → "Import an existing project"
   - Select your GitHub repository
   - Configure build settings:
     - Build command: `npm run build`
     - Publish directory: `public`
     - Functions directory: `netlify/functions`

3. **Set Environment Variables**
   
   In Netlify dashboard → Site settings → Environment variables, add:
   
   ```
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   SUPABASE_URL=https://YOUR-PROJECT.supabase.co
   SUPABASE_SERVICE_ROLE=YOUR_SERVICE_ROLE_SECRET
   CFBK_PUBLIC_JWK={"kty":"OKP","crv":"Ed25519","x":"BASE64URL_PUBLIC_KEY"}
   ```

4. **Deploy**
   - Click "Deploy site"
   - Netlify will build and deploy automatically
   - Your site will be available at `https://YOUR-SITE.netlify.app`

### Option 2: Netlify CLI

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify**
   ```bash
   netlify login
   ```

3. **Initialize Site**
   ```bash
   netlify init
   ```

4. **Deploy**
   ```bash
   netlify deploy --prod
   ```

### Option 3: Manual ZIP Upload

1. **Build Locally**
   ```bash
   npm install
   npm run build
   ```

2. **Create Deployment Package**
   ```bash
   zip -r domionnexus-deploy.zip . -x "node_modules/*" ".git/*"
   ```

3. **Upload to Netlify**
   - Go to Netlify dashboard
   - Drag and drop the ZIP file
   - Configure as needed

## Build Process

The build process (`npm run build`) will:

1. Scan the `seals/` directory for seal JSON files
2. Load `grimoire/glyphs.json` if available
3. Load `data/starseeds.json` if available
4. Compile everything into `data/Codex_Universal.json`
5. Generate a cryptographic hash (SHA-256) of the artifact
6. Bind to subject ID: `2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a`

## Post-Deployment Configuration

### Custom Domain

1. In Netlify → Domain settings
2. Add your domain (e.g., `domionnexus.com`)
3. Update DNS records as instructed
4. SSL is automatic via Let's Encrypt

### Continuous Deployment

- Netlify auto-deploys on every push to main branch
- Configure deploy contexts in `netlify.toml`
- Set up deploy previews for pull requests

### Functions

Netlify Functions are available at:
- `/api/verify` - ECCL license verification
- `/api/universal` - Universal codex search
- Additional functions can be added to `netlify/functions/`

## Testing Locally

```bash
# Install dependencies
npm install

# Run local development server
npm run dev

# Access at http://localhost:8888
```

## Troubleshooting

### Build Fails

- Check Node.js version: `node --version` (must be >= 20)
- Verify all dependencies are installed: `npm install`
- Check build logs in Netlify dashboard

### Functions Not Working

- Verify environment variables are set in Netlify
- Check function logs in Netlify dashboard
- Test locally with `netlify dev`

### Missing Data

- Ensure `data/` directory exists
- Run `npm run build` to generate `Codex_Universal.json`
- Verify JSON files are valid

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit secrets** to the repository
2. Use Netlify environment variables for all sensitive data
3. The `.env` file is gitignored - keep it that way
4. ECCL-1.0 license requires cryptographic binding
5. All artifacts must be signed with proper keys

## Monitoring

- **Netlify Analytics**: Enable in site settings
- **Function Logs**: Available in Netlify dashboard
- **Build Logs**: Check for errors during deployment

## Scaling

Netlify provides:
- Automatic CDN distribution
- Edge functions for low latency
- Automatic scaling
- 99.99% uptime SLA (on paid plans)

## Support

For deployment issues:
- Netlify Support: https://support.netlify.com
- Documentation: https://docs.netlify.com

For application issues:
- Repository: https://github.com/calebfbyker-lab/domionnexus
- License: ECCL-1.0

---

**Licensed under ECCL-1.0**  
Cryptographically bound to: `sha256(calebfedorbykerkonev10271998) = 2948fbc4...770282a`
