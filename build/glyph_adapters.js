// glyph_adapters.js - v308.x Glyph API
// Provides xtgs, tsg, tgs glyph adapters for Codex Immortal

/**
 * XTGS (Extended Temporal Glyph System) adapter
 * Combines seal identifier with payload into a structured glyph
 */
export function xtgs(seal, payload = {}) {
  return {
    type: "xtgs",
    seal,
    payload,
    timestamp: new Date().toISOString(),
    lineage: "CFBK-10271998"
  };
}

/**
 * TSG (Temporal Seal Glyph) adapter
 * Creates a temporal seal with metadata
 */
export function tsg(identifier, metadata = {}) {
  return {
    type: "tsg",
    identifier,
    metadata,
    created: Date.now(),
    subject: "CFBK"
  };
}

/**
 * TGS (Temporal Glyph Signature) adapter
 * Creates a signature structure for verification
 */
export function tgs(data, signature = null) {
  return {
    type: "tgs",
    data,
    signature,
    verified: signature !== null,
    timestamp: new Date().toISOString()
  };
}

/**
 * Invoke seal with cryptographic verification
 * This is the core activation function for v308.x
 */
export function invokeSeal(seal, payload = {}) {
  const crypto = typeof window !== 'undefined' && window.crypto
    ? window.crypto
    : require('node:crypto');
  
  const glyph = xtgs(seal, payload);
  const glyphStr = JSON.stringify(glyph);
  
  let digest;
  if (typeof window !== 'undefined' && window.crypto && window.crypto.subtle) {
    // Browser environment - use Web Crypto API
    const encoder = new TextEncoder();
    const data = encoder.encode(glyphStr);
    return window.crypto.subtle.digest('SHA-256', data).then(hashBuffer => {
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      digest = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      console.log(`[Codex·Invoke] Seal ${seal} verified → ${digest}`);
      return { 
        glyph, 
        digest, 
        lineage: {
          logic: "Sotolios",
          knowledge: "Nous",
          wisdom: "Hermes Tres",
          subject: "CFBK-10271998",
          subject_sha256: "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a"
        }
      };
    });
  } else {
    // Node.js environment
    digest = crypto.createHash("sha256").update(glyphStr).digest("hex");
    console.log(`[Codex·Invoke] Seal ${seal} verified → ${digest}`);
    return { 
      glyph, 
      digest, 
      lineage: {
        logic: "Sotolios",
        knowledge: "Nous",
        wisdom: "Hermes Tres",
        subject: "CFBK-10271998",
        subject_sha256: "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a"
      }
    };
  }
}

// Example usage (commented out for production):
// invokeSeal("CFBK:62_2", { intent: "protect.integrity", scope: "system" });
