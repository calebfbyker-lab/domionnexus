import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Subject ID binding (CFBK)
const SUBJECT_ID_SHA256 = '2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a'
const WORKFLOW_REF = 'wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e'
const WORKFLOW_VERSION = 5

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex')
}

function getFileHash(filePath) {
  try {
    const content = fs.readFileSync(filePath)
    return sha256(content)
  } catch (error) {
    return null
  }
}

function scanDirectory(dir, baseDir = dir) {
  const files = []
  
  if (!fs.existsSync(dir)) {
    return files
  }

  const items = fs.readdirSync(dir)

  for (const item of items) {
    const fullPath = path.join(dir, item)
    const stat = fs.statSync(fullPath)

    if (stat.isDirectory()) {
      files.push(...scanDirectory(fullPath, baseDir))
    } else if (stat.isFile()) {
      const relativePath = path.relative(baseDir, fullPath)
      const hash = getFileHash(fullPath)
      
      if (hash) {
        files.push({
          path: relativePath.replace(/\\/g, '/'), // Normalize path separators
          sha256: hash,
          size: stat.size,
          modified_utc: stat.mtime.toISOString()
        })
      }
    }
  }

  return files
}

function generateIntegrity() {
  console.log('🔒 Generating integrity manifest...')

  const distDir = path.join(__dirname, '../dist')
  
  if (!fs.existsSync(distDir)) {
    console.error('❌ Error: dist directory does not exist. Run build first.')
    process.exit(1)
  }

  // Scan all files in dist
  const files = scanDirectory(distDir)
  
  // Calculate overall manifest hash
  const filesJson = JSON.stringify(files.map(f => ({ path: f.path, sha256: f.sha256 })))
  const manifestHash = sha256(filesJson)

  // Build integrity manifest
  const integrity = {
    subject_id_sha256: SUBJECT_ID_SHA256,
    workflow_ref: WORKFLOW_REF,
    workflow_version: WORKFLOW_VERSION,
    manifest_sha256: manifestHash,
    generated_utc: new Date().toISOString(),
    build: {
      files_count: files.length,
      total_size: files.reduce((sum, f) => sum + f.size, 0)
    },
    files: files.sort((a, b) => a.path.localeCompare(b.path))
  }

  // Write integrity.json to dist
  const integrityPath = path.join(distDir, 'integrity.json')
  fs.writeFileSync(integrityPath, JSON.stringify(integrity, null, 2))

  console.log('✅ Integrity manifest generated:')
  console.log(`   Files: ${integrity.build.files_count}`)
  console.log(`   Size: ${(integrity.build.total_size / 1024).toFixed(2)} KB`)
  console.log(`   Manifest hash: ${manifestHash}`)
  console.log(`   Output: ${integrityPath}`)

  return integrity
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    generateIntegrity()
  } catch (error) {
    console.error('❌ Error generating integrity manifest:', error)
    process.exit(1)
  }
}

export default generateIntegrity
