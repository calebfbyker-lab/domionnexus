// Verify a signature (base64) against an input file and base64-encoded public key.
// Usage:
//   export CFBK_PUBLIC_KEY_BASE64="$(cat keys/cfbk_pub.base64)"
//   node scripts/verify_with_node_tweetnacl.js seals/Solomon-001.canonical.json seals/Solomon-001.sig
import fs from "fs";
import nacl from "tweetnacl";

if (process.argv.length < 4) {
  console.error("Usage: node verify_with_node_tweetnacl.js <input-file> <sig-file-base64> [pubbase64-env]");
  process.exit(2);
}
const IN = process.argv[2];
const SIGFILE = process.argv[3];
const PUBB64 = process.env.CFBK_PUBLIC_KEY_BASE64 || process.env.CFBK_PUBLIC_JWK_BASE64;
if (!PUBB64) {
  console.error("CFBK_PUBLIC_KEY_BASE64 required in env to verify.");
  process.exit(2);
}
const pub = Buffer.from(PUBB64, "base64");
const msg = fs.readFileSync(IN);
const sig = Buffer.from(fs.readFileSync(SIGFILE, "utf8").trim(), "base64");
const ok = nacl.sign.detached.verify(new Uint8Array(msg), new Uint8Array(sig), new Uint8Array(pub));
console.log("signature valid?", ok);
process.exit(ok ? 0 : 3);
