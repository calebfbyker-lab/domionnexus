const { Buffer } = require('buffer');

exports.handler = async function (event) {
  const headers = event.headers || {};
  const key = headers['x-api-key'] || headers['X-API-KEY'] || '';
  const CODEX_API_KEY = process.env.CODEX_API_KEY || 'dev-key';
  if (key !== CODEX_API_KEY) {
    return { statusCode: 401, body: JSON.stringify({ ok: false, error: 'invalid api key' }) };
  }

  try {
    const body = event.body ? JSON.parse(event.body) : {};
    // Minimal structural validation similar to README example
    const header = body.header || {};
    const token = body.token || {};
    const structural = header.license === 'ECCL-1.0' && header.subject_id_sha256 && token.subject_id_sha256 && header.artifact_sha256 === token.artifact_sha256;
    if (!structural) return { statusCode: 400, body: JSON.stringify({ ok: false, error: 'structural_mismatch' }) };
    // In production verify the JWS using jose and CFBK_PUBLIC_JWK
    return { statusCode: 200, body: JSON.stringify({ ok: true }) };
  } catch (e) {
    return { statusCode: 500, body: JSON.stringify({ ok: false, error: String(e) }) };
  }
};
