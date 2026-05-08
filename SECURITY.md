# BabelCam — Security & Deployment Guide

## Issues Fixed ✅

### 1. **Permission Handling** 
- ✅ Added specific error messages for different permission denial scenarios
- ✅ Implemented retry mechanism when permissions are denied
- ✅ Added user guidance on the lobby screen about permissions

### 2. **Invite Link Generation**
- ✅ Improved fallback chain for retrieving server address
- ✅ Now uses `window.location.hostname` instead of just `window.location.origin`
- ✅ Better timeout handling for `/server-info` endpoint
- ✅ Multiple fallbacks ensure link works even if IP detection fails

### 3. **CORS Security**
- ✅ Restricted CORS to only allow localhost/127.0.0.1
- ✅ Production environment will strict security by default
- ✅ Easy to add your domain for production deployment

---

## For Your Friend to Join ✅

1. **Share this link** (copy from call screen):
   - Format: `http://[your-ip]:3000/?room=ROOM-CODE`
   - Works on same WiFi network

2. **When prompt appears:**
   - Click "Allow" for camera permission
   - Click "Allow" for microphone permission
   - If permissions blocked, see Troubleshooting below

3. **Enter the same room code** your friend shared

---

## Production Deployment (Important for Security)

### Before Going Live:

1. **Use HTTPS** (required for camera/mic outside localhost)
   ```bash
   # Generate SSL certificates
   # Then update src/server/index.js to use https module
   ```

2. **Update CORS Configuration:**
   - Edit `src/server/index.js` line ~17
   - Replace `'http://example.com'` with your actual domain
   - Set `NODE_ENV=production` to enforce restrictions

3. **Set Translation Service:**
   - Free: Use `https://libretranslate.de/translate` (rate limited)
   - Better: Self-host LibreTranslate locally
   - Update `LIBRETRANSLATE_URL` in `.env`

---

## Troubleshooting Permission Issues

### ❌ "Permission Denied!"
**On Windows:**
- Settings → Privacy & Security → Camera → Allow BabelCam
- Settings → Privacy & Security → Microphone → Allow BabelCam
- Close other apps using camera/mic (Zoom, Teams, etc.)
- Refresh page and try again

**On Mac:**
- System Preferences → Security & Privacy → Camera → Add browser
- System Preferences → Security & Privacy → Microphone → Add browser
- Refresh page and try again

**On Linux:**
- No system-level permission prompt
- Browser may ask; click "Allow"
- Check browser settings if blocked

**On Mobile:**
- iOS: Settings → [App Name] → Camera/Microphone → Allow
- Android: Settings → Apps → [Browser] → Permissions → Camera/Microphone

### ❌ "No camera/microphone found"
- Plug in USB camera/microphone
- Check if external device is recognized by system

### ❌ "Camera/mic already in use"
- Close other apps: Zoom, Teams, OBS, etc.
- Or use different browsers for each call

---

## Network Requirements

✅ **Same WiFi:** Works perfectly with the auto-generated LAN IP link
⚠️ **Different Networks:** Requires server publicly accessible (HTTPS + domain)
⚠️ **Behind Corporate Firewall:** May need NAT/port forwarding configuration

---

## Security Best Practices

- ✅ NO personal data stored on server
- ✅ P2P encrypted video (WebRTC standard)
- ✅ Room codes are random (non-guessable)
- ✅ Session-only (no permanent accounts)
- 🔒 Use HTTPS in production
- 🔒 Restrict CORS to your domain
- 🔒 Consider self-hosting translation service

---

## Testing Checklist

- [ ] Test on same device (different browser tabs)
- [ ] Test on different device on same WiFi
- [ ] Test permission denial and recovery
- [ ] Test link generation
- [ ] Test language switching mid-call
- [ ] Test microphone mute/unmute
- [ ] Test camera on/off

