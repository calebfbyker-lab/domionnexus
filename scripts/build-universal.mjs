// Build Universal Artifact
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { createHash } from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const root = join(__dirname, '..');

function sha256(data) {
  return createHash('sha256').update(data).digest('hex');
}

function loadJSON(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (e) {
    console.warn(`Failed to load ${path}:`, e.message);
    return null;
  }
}

function findJSONFiles(dir) {
  const files = [];
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        files.push(...findJSONFiles(fullPath));
      } else if (entry.name.endsWith('.json')) {
        files.push(fullPath);
      }
    }
  } catch (e) {
    console.warn(`Failed to read directory ${dir}:`, e.message);
  }
  return files;
}

console.log('🔨 Building Universal Codex Artifact...');

// Load seals
const sealsDir = join(root, 'seals');
const sealFiles = existsSync(sealsDir) ? findJSONFiles(sealsDir) : [];
const seals = sealFiles.map(f => loadJSON(f)).filter(Boolean);
console.log(`  Loaded ${seals.length} seals`);

// Load glyphs
const glyphsPath = join(root, 'grimoire', 'glyphs.json');
const glyphs = loadJSON(glyphsPath) || [];
console.log(`  Loaded ${Array.isArray(glyphs) ? glyphs.length : Object.keys(glyphs).length} glyphs`);

// Load star seeds
const starsPath = join(root, 'data', 'starseeds.json');
const stars = loadJSON(starsPath) || [];
console.log(`  Loaded ${Array.isArray(stars) ? stars.length : 0} star seeds`);

// Create universal artifact
const artifactData = JSON.stringify({ seals, glyphs, stars });
const artifactHash = sha256(Buffer.from(artifactData));

const universal = {
  artifact_sha256: artifactHash,
  issued_utc: new Date().toISOString(),
  license: 'ECCL-1.0',
  subject_id_sha256: '2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a',
  seals,
  glyphs,
  stars
};

// Write artifact
const dataDir = join(root, 'data');
const artifactPath = join(dataDir, 'Codex_Universal.json');
writeFileSync(artifactPath, JSON.stringify(universal, null, 2));

console.log(`✅ Artifact created: ${artifactHash}`);
console.log(`📦 Written to: ${artifactPath}`);
console.log(`📊 Stats: ${seals.length} seals, ${Array.isArray(glyphs) ? glyphs.length : Object.keys(glyphs).length} glyphs, ${Array.isArray(stars) ? stars.length : 0} stars`);
