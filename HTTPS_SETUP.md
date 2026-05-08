# ✅ HTTPS Configuration Complete

## What Was Done

### 1. **Generated Self-Signed SSL Certificates**
- Location: `certs/key.pem` and `certs/cert.pem`
- Commands: `npm run generate-certs`
- Valid for 365 days (localhost testing)

### 2. **Updated Server to Support HTTPS**
- Modified `src/server/index.js` to load SSL certificates
- Server automatically detects and uses HTTPS if certificates exist
- Falls back to HTTP if no certificates (for backward compatibility)

### 3. **Updated Frontend for HTTPS**
- Invite links now use `https://` protocol
- All CDN dependencies (Socket.io, simple-peer) loaded via HTTPS
- Improved protocol detection

---

## How to Run with HTTPS

### First Time Setup:
```bash
npm run generate-certs     # Generate self-signed certificates
npm start                   # Start server with HTTPS
```

### Access the App:
```
https://localhost:3000
```

---

## ⚠️ Browser Certificate Warning

When you open `https://localhost:3000`, your browser will show:
- **"Your connection is not private"** or similar message
- This is **normal and expected** for self-signed certificates

### How to Proceed:

**Chrome/Edge:**
1. Click "Advanced" button
2. Click "Proceed to localhost (unsafe)" or similar

**Safari:**
1. Click "Show Details"
2. Click "Visit this website"

**Firefox:**
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

---

## For Your Friend's Invite Link

**Invite format:**
```
https://192.168.x.x:3000/?room=TIGER-42
```

✅ Uses HTTPS for security
✅ Works on same WiFi network
✅ No HTTP mixed content warnings

---

## Security Benefits

✅ **Camera/Mic Permission** — Now works properly with HTTPS requirement
✅ **Encrypted Connection** — Between browser and server  
✅ **Self-Signed Certificate** — Good for local testing
⚠️ **Production Note** — Use CA-signed certificate for public deployment

---

## Files Modified

- `src/server/index.js` — Added HTTPS support
- `public/index.html` — Updated link generation for HTTPS
- `package.json` — Added `npm run generate-certs` script
- `scripts/generate-certs.js` — New certificate generation utility
- `certs/` — New directory with key.pem and cert.pem

---

## Testing Checklist

- [ ] Open `https://localhost:3000` in browser
- [ ] Accept self-signed certificate warning
- [ ] Permissions dialog should now appear properly
- [ ] Grant camera/microphone access
- [ ] Generate and copy invite link
- [ ] Test with friend on same WiFi

---

## Troubleshooting

### "Can't load the app"
→ Make sure server is running: `npm start`

### "Certificate error persists"
→ Clear browser cache: Ctrl+Shift+Delete (Chrome/Edge)
→ Then refresh: Ctrl+F5

### "Camera/mic still not working"
→ Double-check browser is accessed via HTTPS
→ Look for warning icon in address bar
→ Click and allow permissions if prompted

### "Can't regenerate certificates"
→ Delete `certs/` folder
→ Run `npm run generate-certs` again

