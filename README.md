# BabelCam - Live Video Translation

Real-time peer-to-peer video calls with live Hindi/English subtitle translation.

## Stack
- **Frontend**: Plain HTML + CSS + Vanilla JS
- **Backend**: FastAPI + native WebSockets
- **Speech**: Browser media capture + optional local Whisper transcription
- **Translation**: LibreTranslate
- **Video**: WebRTC via `simple-peer`

## Setup

### 1. Install Python dependencies

```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 2. Configure environment
```cmd
copy .env.example .env
```

Update `.env` if you want to point translation at a local LibreTranslate instance:
- `LIBRETRANSLATE_URL=http://localhost:5000/translate`

Optional Whisper settings are also listed in `.env.example`. If Whisper is not installed, the app still works with manual text and quick phrases.

### 3. Run the FastAPI server
```cmd
# Production
python -m app.main

# Development (auto-reload)
python -m app.main --reload
```

If `certs/key.pem` and `certs/cert.pem` exist, the server starts with HTTPS automatically. Otherwise it runs on HTTP.

#### "Regenerate certificates"
→ Delete `certs/` folder
→ Run `npm run generate-certs` again

### 4. Open the app
- Open `http://localhost:3000` or `https://localhost:3000` in two Chrome/Edge tabs
- Join the same room code in both tabs
- Allow camera and microphone access
- Start speaking, or use quick phrases/manual text if Whisper is unavailable

## Architecture

```text
app/main.py          FastAPI backend
  |- GET  /                  Serve the single-page app
  |- POST /translate         Translate text through LibreTranslate
  |- POST /transcribe        Optional local Whisper transcription
  |- GET  /transcribe/status Report STT availability
  '- WS   /ws                Room, signaling, and subtitle relay

public/index.html    Single-page frontend
  |- Lobby and call UI
  |- Native WebSocket client
  |- simple-peer WebRTC client
  '- Push-to-talk / manual text subtitle flow
```

## Notes
- Chrome or Edge is still the best fit for the current media and speech flow.
- LAN use works without TURN servers; internet/NAT traversal may still need TURN for some networks.
- Translation stays server-side so API keys never reach the browser.
"# live-video-call-translator" 
