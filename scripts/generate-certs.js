/**
 * Generate self-signed SSL certificates for local HTTPS development
 * Run: npm run generate-certs
 */

const fs = require("fs");
const path = require("path");

const certsDir = path.join(__dirname, "..", "certs");
const keyFile = path.join(certsDir, "key.pem");
const certFile = path.join(certsDir, "cert.pem");

// Create certs directory if it doesn't exist
if (!fs.existsSync(certsDir)) {
  fs.mkdirSync(certsDir, { recursive: true });
}

// Check if certs already exist
if (fs.existsSync(keyFile) && fs.existsSync(certFile)) {
  console.log("✅ SSL certificates already exist at:");
  console.log(`   📄 ${keyFile}`);
  console.log(`   📄 ${certFile}`);
  process.exit(0);
}

console.log("🔐 Generating self-signed SSL certificates for localhost...\n");

async function generateCerts() {
  try {
    const selfsigned = require("selfsigned");
    
    const attrs = [{ name: "commonName", value: "localhost" }];
    // Note: generate() is async and returns a Promise
    const pems = await selfsigned.generate(attrs, {
      days: 365,
      keySize: 2048,
      algorithm: "sha256"
    });
    
    // Write certificate files
    fs.writeFileSync(keyFile, pems.private);
    fs.writeFileSync(certFile, pems.cert);
    
    console.log("✅ SSL certificates generated successfully!\n");
    console.log("📄 Key:  certs/key.pem");
    console.log("📄 Cert: certs/cert.pem");
    console.log("\n🚀 Now run: npm start");
    console.log("   Server will use HTTPS at https://localhost:3000\n");
    console.log("⚠️  Note: Browser will show certificate warning.");
    console.log("   This is normal. Click 'Advanced' on Chrome/Edge to proceed.\n");
    
  } catch (err) {
    console.error("❌ Error:", err.message || err);
    console.error("\nMake sure the 'selfsigned' package is installed:");
    console.error("  npm install --save-dev selfsigned");
    process.exit(1);
  }
}

generateCerts();
