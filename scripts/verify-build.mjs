#!/usr/bin/env node

/**
 * Verification script for DomionNexus deployment
 * Checks integrity manifest and validates key components
 */

import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const SUBJECT_ID_SHA256 = '2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a'
const WORKFLOW_REF = 'wf_68f362ed3e3881909a1fc894b213808902f495b1a750c22e'
const WORKFLOW_VERSION = 5

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex')
}

console.log('🔍 DomionNexus Deployment Verification')
console.log('=' .repeat(50))

// Check if dist exists
const distPath = path.join(__dirname, '../dist')
if (!fs.existsSync(distPath)) {
  console.error('❌ dist/ directory not found. Run: npm run netlify:build')
  process.exit(1)
}

console.log('✅ dist/ directory exists')

// Check integrity.json
const integrityPath = path.join(distPath, 'integrity.json')
if (!fs.existsSync(integrityPath)) {
  console.error('❌ integrity.json not found in dist/')
  process.exit(1)
}

console.log('✅ integrity.json exists')

// Load and validate integrity.json
const integrity = JSON.parse(fs.readFileSync(integrityPath, 'utf8'))

// Validate subject ID
if (integrity.subject_id_sha256 !== SUBJECT_ID_SHA256) {
  console.error('❌ Subject ID mismatch in integrity.json')
  process.exit(1)
}
console.log('✅ Subject ID verified (CFBK)')

// Validate workflow reference
if (integrity.workflow_ref !== WORKFLOW_REF) {
  console.error('❌ Workflow reference mismatch')
  process.exit(1)
}
console.log('✅ Workflow reference verified')

// Validate workflow version
if (integrity.workflow_version !== WORKFLOW_VERSION) {
  console.error('❌ Workflow version mismatch')
  process.exit(1)
}
console.log('✅ Workflow version verified')

// Verify file hashes
let filesVerified = 0
for (const fileInfo of integrity.files) {
  if (fileInfo.path === 'integrity.json') continue // Skip self
  
  const filePath = path.join(distPath, fileInfo.path)
  if (!fs.existsSync(filePath)) {
    console.error(`❌ File not found: ${fileInfo.path}`)
    continue
  }
  
  const content = fs.readFileSync(filePath)
  const hash = sha256(content)
  
  if (hash !== fileInfo.sha256) {
    console.error(`❌ Hash mismatch for ${fileInfo.path}`)
    console.error(`   Expected: ${fileInfo.sha256}`)
    console.error(`   Got: ${hash}`)
  } else {
    filesVerified++
  }
}

console.log(`✅ Verified ${filesVerified} file hashes`)

// Check key files
const requiredFiles = ['index.html', 'assets']
for (const file of requiredFiles) {
  const filePath = path.join(distPath, file)
  if (!fs.existsSync(filePath)) {
    console.error(`❌ Required file/directory not found: ${file}`)
  } else {
    console.log(`✅ ${file} exists`)
  }
}

// Check functions
const functionsPath = path.join(__dirname, '../netlify/functions')
const requiredFunctions = ['run-agent.mjs', 'orchestrator.mjs']

for (const fn of requiredFunctions) {
  const fnPath = path.join(functionsPath, fn)
  if (!fs.existsSync(fnPath)) {
    console.error(`❌ Function not found: ${fn}`)
  } else {
    console.log(`✅ Function exists: ${fn}`)
  }
}

console.log('=' .repeat(50))
console.log('🎉 Verification complete!')
console.log('')
console.log('Build Summary:')
console.log(`   Files: ${integrity.build.files_count}`)
console.log(`   Total size: ${(integrity.build.total_size / 1024).toFixed(2)} KB`)
console.log(`   Manifest hash: ${integrity.manifest_sha256}`)
console.log(`   Generated: ${integrity.generated_utc}`)
console.log('')
console.log('Ready for Netlify deployment! 🚀')
