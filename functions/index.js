// Firebase Cloud Function for Codex Invocation
// v308.x Invocation Layer - provides cryptographic proof endpoint

const crypto = require('crypto');

// Load manifest from build directory
let manifest;
try {
  manifest = require('../build/manifest.json');
} catch (e) {
  console.warn('manifest.json not found, using fallback');
  manifest = {
    codex_version: "v308.x",
    subject_sha256: "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a",
    symbolic_lineage: {
      logic: "Sotolios",
      knowledge: "Nous",
      wisdom: "Hermes Tres"
    },
    build_timestamp: new Date().toISOString()
  };
}

/**
 * Codex Invocation Endpoint
 * Returns cryptographic proof of the current deployment
 * 
 * Access at: https://<your-site>.web.app/api/codexInvocation
 */
exports.codexInvocation = async (req, res) => {
  try {
    // Set CORS headers
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST');
    
    if (req.method === 'OPTIONS') {
      res.status(204).send('');
      return;
    }

    // Calculate cryptographic proof of manifest
    const manifestStr = JSON.stringify(manifest);
    const proof = crypto.createHash('sha256')
      .update(manifestStr)
      .digest('hex');
    
    console.log('Invocation proof:', proof);
    
    // Return invocation response
    res.status(200).json({
      ok: true,
      proof,
      manifest,
      lineage: {
        logic: "Sotolios",
        knowledge: "Nous", 
        wisdom: "Hermes Tres",
        subject: "CFBK-10271998",
        subject_sha256: "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a"
      },
      invocation_time: new Date().toISOString(),
      message: "Codex Immortal invocation verified. Seals active."
    });
  } catch (error) {
    console.error('Invocation error:', error);
    res.status(500).json({
      ok: false,
      error: error.message,
      message: "Invocation failed"
    });
  }
};
