import argparse
import asyncio
import json
import os
import socket
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

import uvicorn
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"
CERTS_DIR = BASE_DIR / "certs"
KEY_FILE = CERTS_DIR / "key.pem"
CERT_FILE = CERTS_DIR / "cert.pem"

load_dotenv(BASE_DIR / ".env")

PORT = int(os.getenv("PORT", "3000"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_BACKEND = os.getenv("WHISPER_BACKEND", "auto")
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.de/translate")
LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "")

_whisper_model: WhisperModel | None = None

WHISPER_LANG_MAP = {
    "en": "en",
    "ja": "ja",
    "de": "de",
}

SUPPORTED_TRANSLATION_PAIRS = {"en-ja", "ja-en", "en-de", "de-en"}

SIMPLE_TRANSLATIONS = {
    "en-ja": {
        "hello": "こんにちは",
        "hi": "こんにちは",
        "how are you": "お元気ですか",
        "thank you": "ありがとうございます",
        "thanks": "ありがとうございます",
        "goodbye": "さようなら",
        "bye": "さようなら",
        "yes": "はい",
        "no": "いいえ",
        "ok": "わかりました",
        "okay": "わかりました",
        "good": "良い",
        "bad": "悪い",
        "i am fine": "元気です",
        "sorry": "すみません",
        "please": "お願いします",
        "help": "助けて",
        "welcome": "ようこそ",
        "good morning": "おはようございます",
        "good night": "おやすみなさい",
        "i don't understand": "わかりません",
    },
    "ja-en": {
        "こんにちは": "hello",
        "お元気ですか": "how are you",
        "ありがとうございます": "thank you",
        "さようなら": "goodbye",
        "はい": "yes",
        "いいえ": "no",
        "わかりました": "ok",
        "良い": "good",
        "悪い": "bad",
        "助けて": "help",
        "すみません": "sorry",
        "お願いします": "please",
        "おはようございます": "good morning",
        "おやすみなさい": "good night",
    },
    "en-de": {
        "hello": "hallo",
        "hi": "hallo",
        "how are you": "wie geht es dir",
        "thank you": "danke",
        "thanks": "danke",
        "goodbye": "auf wiedersehen",
        "bye": "tschuss",
        "yes": "ja",
        "no": "nein",
        "ok": "ok",
        "okay": "in ordnung",
        "good": "gut",
        "bad": "schlecht",
        "i am fine": "mir geht es gut",
        "sorry": "entschuldigung",
        "please": "bitte",
        "help": "hilfe",
        "welcome": "willkommen",
        "good morning": "guten morgen",
        "good night": "gute nacht",
        "i don't understand": "ich verstehe nicht",
    },
    "de-en": {
        "hallo": "hello",
        "wie geht es dir": "how are you",
        "danke": "thank you",
        "auf wiedersehen": "goodbye",
        "tschuss": "bye",
        "ja": "yes",
        "nein": "no",
        "in ordnung": "okay",
        "gut": "good",
        "schlecht": "bad",
        "hilfe": "help",
        "entschuldigung": "sorry",
        "bitte": "please",
        "guten morgen": "good morning",
        "gute nacht": "good night",
    },
}

HAS_TLS = KEY_FILE.exists() and CERT_FILE.exists()
SERVER_PROTOCOL = "https" if HAS_TLS else "http"

app = FastAPI(title="AnyTalk FastAPI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_whisper_backend: str | None = None
rooms: dict[str, list[str]] = {}
clients: dict[str, dict[str, Any]] = {}
rooms_lock = asyncio.Lock()


def get_whisper_model() -> WhisperModel | None:
    global _whisper_model
    if not WHISPER_AVAILABLE:
        return None
    if _whisper_model is None:
        try:
            log(f"Loading Whisper model: {WHISPER_MODEL}")
            _whisper_model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type="int8" if WHISPER_DEVICE == "cpu" else "float16")
            log("Whisper model loaded successfully")
        except Exception as e:
            log(f"Failed to load Whisper model: {e}")
            return None
    return _whisper_model


def log(message: str) -> None:
    print(message, flush=True)


def transcribe_audio_file(audio_path: Path, lang_code: str) -> dict[str, str]:
    model = get_whisper_model()
    if not model:
        raise RuntimeError("Whisper model not available.")

    whisper_lang = WHISPER_LANG_MAP.get(lang_code.lower())
    if not whisper_lang:
        raise RuntimeError(f"Unsupported language selection: {lang_code}")

    try:
        segments, info = model.transcribe(
            str(audio_path),
            language=whisper_lang,
            beam_size=1,
            best_of=1,
            temperature=0,
            condition_on_previous_text=False,
            vad_filter=True,
        )
        text = " ".join(segment.text for segment in segments).strip()

        return {
            "text": text,
            "language": whisper_lang,
        }
    except Exception as e:
        log(f"Transcription error: {e}")
        return {"text": "", "language": lang_code}


def translate_text(text: str, source_lang: str | None, target_lang: str) -> str:
    if not text.strip():
        return ""

    normalized_source = source_lang.lower() if source_lang else None
    normalized_target = target_lang.lower()

    if normalized_source and normalized_source == normalized_target:
        return text

    if normalized_source:
        pair_key = f"{normalized_source}-{normalized_target}"
        if pair_key not in SUPPORTED_TRANSLATION_PAIRS:
            raise ValueError(f"Unsupported translation pair: {pair_key}")

    pair = f"{normalized_source or 'auto'}-{normalized_target}"
    local_match = SIMPLE_TRANSLATIONS.get(pair, {}).get(text.lower().strip())
    if local_match:
        return local_match

    payload = json.dumps(
        {
            "q": text,
            "source": normalized_source or "auto",
            "target": normalized_target,
            "format": "text",
            **({"api_key": LIBRETRANSLATE_API_KEY} if LIBRETRANSLATE_API_KEY else {}),
        }
    ).encode("utf-8")

    request = urllib_request.Request(
        LIBRETRANSLATE_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    libre_result = text
    try:
        with urllib_request.urlopen(request, timeout=12) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body or "{}")
    except (urllib_error.URLError, urllib_error.HTTPError, TimeoutError, json.JSONDecodeError):
        data = {}

    libre_result = str(
        data.get("translatedText")
        or data.get("data", {}).get("translatedText")
        or data.get("result")
        or text
    )

    if libre_result.strip() and libre_result.strip().lower() != text.strip().lower():
        return libre_result

    try:
        google_result = GoogleTranslator(source=normalized_source or "auto", target=normalized_target).translate(text)
        if google_result and google_result.strip():
            return google_result
    except Exception:
        pass

    return libre_result


def get_local_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()
    hostname = socket.gethostname()

    try:
        for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                addresses.add(ip)
    except socket.gaierror:
        pass

    return sorted(addresses)


async def send_message(client_id: str, payload: dict[str, Any]) -> None:
    client = clients.get(client_id)
    if not client:
        return

    websocket: WebSocket = client["websocket"]
    await websocket.send_json(payload)


async def remove_client(client_id: str) -> None:
    async with rooms_lock:
        client = clients.pop(client_id, None)
        if not client:
            return

        room_code = client.get("room_code")
        if not room_code or room_code not in rooms:
            return

        remaining = [member_id for member_id in rooms[room_code] if member_id != client_id]
        if remaining:
            rooms[room_code] = remaining
        else:
            rooms.pop(room_code, None)

    for other_id in remaining if "remaining" in locals() else []:
        try:
            await send_message(other_id, {"type": "peer-disconnected"})
        except RuntimeError:
            continue


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(PUBLIC_DIR / "index.html")


@app.get("/r/{room_code}")
async def redirect_room(room_code: str) -> RedirectResponse:
    return RedirectResponse(url=f"/?room={room_code}")


@app.get("/server-info")
async def server_info() -> JSONResponse:
    return JSONResponse({"port": PORT, "ips": get_local_ipv4_addresses(), "protocol": SERVER_PROTOCOL})


@app.get("/transcribe/status")
async def transcribe_status() -> JSONResponse:
    model = get_whisper_model()
    return JSONResponse(
        {
            "available": model is not None,
            "backend": "faster-whisper" if WHISPER_AVAILABLE else "none",
            "model": WHISPER_MODEL,
            "device": WHISPER_DEVICE,
            "languages": sorted(WHISPER_LANG_MAP),
            "install": None if WHISPER_AVAILABLE else "pip install faster-whisper",
        }
    )


@app.post("/translate")
async def translate(payload: dict[str, Any]) -> JSONResponse:
    text = str(payload.get("text", ""))
    source_lang = payload.get("sourceLang")
    target_lang = payload.get("targetLang")

    if not target_lang:
        raise HTTPException(status_code=400, detail="targetLang is required")

    try:
        translated = await asyncio.to_thread(translate_text, text, source_lang, target_lang)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JSONResponse({"translatedText": translated})


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), lang: str = Form(...)) -> JSONResponse:
    if lang.lower() not in WHISPER_LANG_MAP:
        return JSONResponse(
            {"error": "Unsupported speech language. Use English, Japanese, or German.", "text": ""},
            status_code=400,
        )

    suffix = Path(audio.filename or "speech.webm").suffix or ".webm"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = Path(temp_file.name)

    try:
        while chunk := await audio.read(1024 * 1024):
            temp_file.write(chunk)
    finally:
        temp_file.close()

    try:
        transcript = await asyncio.to_thread(transcribe_audio_file, temp_path, lang)
        return JSONResponse(transcript)
    except RuntimeError as exc:
        return JSONResponse({"error": str(exc), "text": ""}, status_code=503)
    except Exception as exc:
        return JSONResponse({"error": str(exc) or "Whisper transcription failed", "text": ""}, status_code=500)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    client_id = uuid.uuid4().hex
    clients[client_id] = {"websocket": websocket, "room_code": None}

    try:
        await websocket.send_json({"type": "connected", "clientId": client_id})

        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "join-room":
                room_code = str(message.get("roomCode", "")).strip().upper()
                if not room_code:
                    await websocket.send_json({"type": "error", "message": "roomCode is required"})
                    continue

                async with rooms_lock:
                    room = rooms.setdefault(room_code, [])
                    if client_id in room:
                        continue

                    if len(room) >= 2:
                        await websocket.send_json({"type": "room-full"})
                        continue

                    room.append(client_id)
                    clients[client_id]["room_code"] = room_code

                    if len(room) == 2:
                        first, second = room
                        await send_message(first, {"type": "peer-joined", "initiator": True})
                        await send_message(second, {"type": "peer-joined", "initiator": False})
                    else:
                        await websocket.send_json({"type": "waiting-for-peer"})

            elif msg_type in {"signal", "subtitle"}:
                room_code = clients.get(client_id, {}).get("room_code")
                if not room_code:
                    continue

                recipients = [member_id for member_id in rooms.get(room_code, []) if member_id != client_id]
                outgoing = {key: value for key, value in message.items() if key != "roomCode"}

                for recipient_id in recipients:
                    await send_message(recipient_id, outgoing)
            else:
                await websocket.send_json({"type": "error", "message": f"Unsupported message type: {msg_type}"})

    except WebSocketDisconnect:
        pass
    finally:
        await remove_client(client_id)


def create_server_args(reload: bool) -> dict[str, Any]:
    server_args: dict[str, Any] = {
        "app": "app.main:app",
        "host": "0.0.0.0",
        "port": PORT,
        "reload": reload,
    }

    if HAS_TLS:
        server_args["ssl_keyfile"] = str(KEY_FILE)
        server_args["ssl_certfile"] = str(CERT_FILE)

    return server_args


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AnyTalk FastAPI server.")
    parser.add_argument("--reload", action="store_true", help="Run the server with auto-reload.")
    args = parser.parse_args()

    log(f"Starting {SERVER_PROTOCOL.upper()} server on {SERVER_PROTOCOL}://localhost:{PORT}")
    log(f"Translation backend: LibreTranslate ({LIBRETRANSLATE_URL})")

    # Load Whisper model on startup
    model = get_whisper_model()
    if model:
        log(f"STT backend: Whisper (faster-whisper, model={WHISPER_MODEL}, device={WHISPER_DEVICE})")
    else:
        log("STT backend: Whisper not available. Manual text and translation remain available.")

    uvicorn.run(**create_server_args(reload=args.reload))


if __name__ == "__main__":
    main()
