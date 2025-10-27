exports.handler = async function (event) {
  const headers = event.headers || {};
  const key = headers['x-api-key'] || headers['X-API-KEY'] || '';
  const CODEX_API_KEY = process.env.CODEX_API_KEY || 'dev-key';
  if (key !== CODEX_API_KEY) {
    return {
      statusCode: 401,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ ok: false, error: 'invalid api key' }),
    };
  }
  return {
    statusCode: 200,
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ status: 'ok' }),
  };
};
