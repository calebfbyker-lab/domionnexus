// Verify ECCL License and Cryptographic Signatures
import * as jose from "jose";
import { SUBJECT_ID_SHA256 } from "../../lib/subject.js";

export async function handler(event) {
  if (event.httpMethod !== 'POST') {
    return jsonResponse({ error: 'Method not allowed' }, 405);
  }

  try {
    const { header, token, jws } = JSON.parse(event.body || '{}');
    
    // Structural verification
    const structural =
      header?.license === "ECCL-1.0" &&
      header?.subject_id_sha256 === SUBJECT_ID_SHA256 &&
      token?.subject_id_sha256 === SUBJECT_ID_SHA256 &&
      header?.artifact_sha256 === token?.artifact_sha256 &&
      String(header?.approval_token || "").startsWith("sig:CFBK::");
    
    if (!structural) {
      return jsonResponse({ ok: false, error: "structural_mismatch" });
    }
    
    // JWS signature verification (if provided)
    if (jws) {
      try {
        const jwk = JSON.parse(process.env.CFBK_PUBLIC_JWK || "{}");
        const { payload } = await jose.compactVerify(
          jws,
          await jose.importJWK(jwk, "EdDSA")
        );
        const claims = JSON.parse(new TextDecoder().decode(payload));
        
        if (claims.artifact_sha256 !== header.artifact_sha256) {
          return jsonResponse({ ok: false, error: "jws_mismatch" });
        }
      } catch (e) {
        return jsonResponse({ ok: false, error: "jws_invalid", details: String(e) });
      }
    }
    
    return jsonResponse({ ok: true, verified: !!jws });
  } catch (e) {
    return jsonResponse({ ok: false, error: String(e) }, 500);
  }
}

function jsonResponse(body, statusCode = 200) {
  return {
    statusCode,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  };
}
