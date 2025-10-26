// Proxy for Rekor Scout API. Configure SCOUT_BASE_URL in environment variables.
// It forwards requests made to /.netlify/functions/scout-proxy/* (Netlify will map /api/scout/* to this function)
const { Buffer } = require('buffer');

exports.handler = async function (event) {
  const SCOUT_BASE_URL = process.env.SCOUT_BASE_URL;
  if (!SCOUT_BASE_URL) {
    return { statusCode: 500, body: JSON.stringify({ ok: false, error: 'SCOUT_BASE_URL not configured' }) };
  }

  try {
    // derive target path: remove any prefix up to /api/scout
    const incomingPath = event.path || '';
    const m = incomingPath.match(/\/api\/scout(\/.*)?$/);
    const forwardPath = (m && m[1]) ? m[1] : '/';
    const url = new URL(forwardPath, SCOUT_BASE_URL);

    // copy query params
    if (event.queryStringParameters) {
      for (const [k,v] of Object.entries(event.queryStringParameters)) {
        url.searchParams.set(k, v);
      }
    }

    const method = event.httpMethod || 'GET';

    const headers = {};
    // forward select headers (authorization, accept, content-type)
    const inHeaders = event.headers || {};
    for (const h of ['authorization','accept','content-type','x-api-key']) {
      const v = inHeaders[h] || inHeaders[h.toUpperCase()] || inHeaders[h.split('-').map(s=>s.charAt(0).toUpperCase()+s.slice(1)).join('-')];
      if (v) headers[h] = v;
    }

    const fetchOpts = { method, headers };
    if (event.body) {
      fetchOpts.body = event.isBase64Encoded ? Buffer.from(event.body, 'base64') : event.body;
    }

    const res = await fetch(url.toString(), fetchOpts);
    const contentType = res.headers.get('content-type') || '';

    // If image or other binary, return base64
    if (contentType.startsWith('image/') || contentType === 'application/octet-stream') {
      const buf = await res.arrayBuffer();
      const b64 = Buffer.from(buf).toString('base64');
      return {
        statusCode: res.status,
        headers: { 'content-type': contentType },
        isBase64Encoded: true,
        body: b64,
      };
    }

    // default: return JSON or text
    const text = await res.text();
    let body = text;
    try { body = JSON.parse(text); }
    catch (e) { /* not json */ }
    return {
      statusCode: res.status,
      headers: { 'content-type': contentType || 'application/json' },
      body: typeof body === 'string' ? body : JSON.stringify(body),
    };
  } catch (e) {
    return { statusCode: 502, body: JSON.stringify({ ok: false, error: String(e) }) };
  }
};
