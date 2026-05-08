# 🚀 How to Invite a Friend to Use BabelCam

## Step 1: Start Your Server (You)

```bash
cd path/to/mp2\ try\ 2
npm start
```

You should see:
```
Live Translation Server running at http://localhost:3000
```

---

## Step 2: Open BabelCam (You)

1. Open browser: `http://localhost:3000`
2. You'll see the lobby screen with "BabelCam — Speak in any language. Be understood."

---

## Step 3: Generate a Room Code (You)

**Option A — Quick Generate:**
- Click 🎲 Random Room Code button
- You'll get something like: `MANGO-42`

**Option B — Custom Code:**
- Type your own room code in the text field
- Example: `OFFICE-2024`

---

## Step 4: Join the Room (You)

1. Click **"Join / Create Room"** button
2. A permission prompt will appear: **"BabelCam wants to use your camera and microphone"**
3. Click **"Allow"** for both camera AND microphone
4. You'll see your video preview on the left side
5. It says "Waiting for peer to join…"

---

## Step 5: Generate Invite Link (You)

1. Once in the call screen, look at the top right
2. You'll see a **🔗** button next to your room code
3. Click the **🔗** button
4. Toast appears: **"Invite link copied!"**

---

## Step 6: Send Link to Friend (You)

Send this link to your friend via:
- WhatsApp
- Email  
- SMS
- Slack
- Discord
- Any messaging app

The link looks like:
```
http://192.168.x.x:3000/?room=MANGO-42
```

---

## Step 7: Friend Opens the Link (Your Friend)

1. Friend clicks/pastes the link in their browser
2. They'll see the BabelCam lobby
3. The room code will be **pre-filled** (e.g., MANGO-42)

---

## Step 8: Friend Grants Permissions (Your Friend)

1. Click **"Join / Create Room"** button
2. **Camera & Microphone permission prompts appear**

**IMPORTANT:** They must click **"Allow"** for BOTH:
- ✅ "Allow camera access"
- ✅ "Allow microphone access"

### If permissions blocked:

**Windows 11/10:**
```
Settings 
→ Privacy & Security 
→ Camera (or Microphone)
→ Allow [Browser Name]
→ Close other apps using camera
→ Refresh the page
→ Try again
```

**Mac:**
```
System Preferences
→ Security & Privacy
→ Camera (or Microphone)
→ Add your browser
→ Refresh page
→ Try again
```

**Android:**
```
Settings
→ Apps
→ [Browser]
→ Permissions
→ Camera & Microphone → Allow
```

**iPhone:**
```
Settings
→ [Safari/Chrome]
→ Camera → Allow
→ Microphone → Allow
```

---

## Step 9: Video Call Connected! 🎉

Once permissions are granted:
1. Friend's video appears on your right side
2. Your video shows on their left side
3. **Real-time translation starts automatically**

### Controls (both of you):
- **🎙️** — Mute/unmute microphone
- **📷** — Turn camera off/on  
- **📵** — Leave the call
- **EN/हि** — Switch between English ↔ Hindi

---

## Troubleshooting

### Link doesn't work
**Problem:** Friend opens link but sees blank page

**Solution:**
- Make sure server is still running (see Step 1)
- Check they're on same WiFi network
- Try copying link again with 🔗 button
- If fails, share just the room code and manually type IP:
  - Find your computer's IP: run `ipconfig` in terminal
  - Friend visits: `http://YOUR_IP:3000/?room=ROOM-CODE`

### Camera/Mic not working
**Problem:** Friend gets "Permission Denied!" error

**Solution:** See "If permissions blocked" section in Step 8 above

### "Room is full" error
**Problem:** Error appears when trying to join

**Solution:**
- Maximum 2 people per room
- Create a new room with different code

### Video/Audio cutting out
**Problem:** Call quality drops

**Solution:**
- Move closer to WiFi router
- Close bandwidth-heavy apps (streaming, downloads)
- Restart call
- Make sure microphone isn't muted (check 🎙️ button)

---

## Security Notes ⚠️

✅ **Confirmed Safe:**
- Video stream is encrypted (WebRTC standard)
- Room codes are random & hard to guess
- No personal data stored
- No accounts needed

⚠️ **Important for Production:**
- App currently works on **same WiFi network only**
- To use over internet: need HTTPS + public domain
- See [SECURITY.md](SECURITY.md) for deployment guide

---

## Tips for Best Experience

1. **Good WiFi** — Use 5GHz band if available
2. **Good Lighting** — Ensure adequate lighting for video
3. **Quiet Location** — Find a quiet spot for better speech recognition
4. **Close Other Apps** — Especially other video/audio apps
5. **Test First** — Try calling yourself (different browser tabs) to test
6. **Use Latest Browser** — Chrome, Edge, or Safari for best compatibility

---

**Questions? Check [SECURITY.md](SECURITY.md) for more details!**

