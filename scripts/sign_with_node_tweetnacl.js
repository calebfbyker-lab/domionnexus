// Sign a canonical file using Ed25519 from a 32-byte seed (base64 in env var).
// Usage:
//   export CFBK_SIGNING_SEED_BASE64="$(cat /secure/path/seed.base64)"
//   node scripts/sign_with_node_tweetnacl.js seals/Solomon-001.canonical.json seals/Solomon-001.sig
import fs from "fs";
import nacl from "tweetnacl";

if (process.argv.length < 4) {
  console.error("Usage: node sign_with_node_tweetnacl.js <input-file> <out-sig>");
  process.exit(2);
}

const IN = process.argv[2];
const OUT = process.argv[3];
const seedB64 = process.env.CFBK_SIGNING_SEED_BASE64 || process.env.CFBK_SIGNING_SEED;
if (!seedB64) {
  console.error("CFBK_SIGNING_SEED_BASE64 environment variable is required (base64 32-byte seed).");
  process.exit(2);
}
const seed = Buffer.from(seedB64, "base64");
if (seed.length !== 32) {
  console.error("Seed must be 32 bytes (base64). Found length:", seed.length);
  process.exit(2);
}
const keypair = nacl.sign.keyPair.fromSeed(new Uint8Array(seed));
const msg = fs.readFileSync(IN);
const sig = nacl.sign.detached(new Uint8Array(msg), keypair.secretKey);
fs.writeFileSync(OUT, Buffer.from(sig).toString("base64"));
console.log("Wrote signature (base64) to", OUT);
console.log("Public key (base64):", Buffer.from(keypair.publicKey).toString("base64"));
