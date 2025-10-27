// Universal Codex API - Search across all data
import { readFileSync } from 'fs';
import { join } from 'path';

export async function handler(event) {
  try {
    const params = event.queryStringParameters || {};
    const limit = parseInt(params.limit || '100', 10);
    const query = params.q || '';
    
    // Try to load universal artifact
    let data;
    try {
      const artifactPath = join(process.cwd(), 'data', 'Codex_Universal.json');
      data = JSON.parse(readFileSync(artifactPath, 'utf8'));
    } catch (e) {
      // Artifact not yet built
      return jsonResponse({
        error: 'Artifact not built yet. Run: npm run build',
        artifact_sha256: null,
        results: []
      });
    }
    
    // Search across seals, glyphs, and stars
    const results = [];
    
    if (data.seals && Array.isArray(data.seals)) {
      results.push(...data.seals
        .filter(seal => !query || JSON.stringify(seal).toLowerCase().includes(query.toLowerCase()))
        .slice(0, limit)
        .map(seal => ({ type: 'seal', ...seal }))
      );
    }
    
    if (data.glyphs && Array.isArray(data.glyphs)) {
      results.push(...data.glyphs
        .filter(glyph => !query || JSON.stringify(glyph).toLowerCase().includes(query.toLowerCase()))
        .slice(0, limit)
        .map(glyph => ({ type: 'glyph', ...glyph }))
      );
    }
    
    if (data.stars && Array.isArray(data.stars)) {
      results.push(...data.stars
        .filter(star => !query || JSON.stringify(star).toLowerCase().includes(query.toLowerCase()))
        .slice(0, limit)
        .map(star => ({ type: 'star', ...star }))
      );
    }
    
    return jsonResponse({
      artifact_sha256: data.artifact_sha256,
      license: data.license,
      issued_utc: data.issued_utc,
      count: results.length,
      results: results.slice(0, limit)
    });
  } catch (e) {
    return jsonResponse({ error: String(e) }, 500);
  }
}

function jsonResponse(body, statusCode = 200) {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify(body)
  };
}
