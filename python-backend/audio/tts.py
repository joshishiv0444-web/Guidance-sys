"""
audio/tts.py — Text-to-Speech
-------------------------------
Converts agent text responses into spoken audio.

Engines:
  1. gTTS  (default) — Google TTS, FREE, no API key needed.
  2. ElevenLabs      — Premium quality, requires ELEVENLABS_API_KEY in .env.

Playback: Uses Windows os.startfile() — opens the MP3 with the default player.
          For silent/headless operation, set play=False.
"""

import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text_cleaner import clean_for_voice
from config.settings import (
    TTS_ENGINE,
    TTS_LANGUAGE,
    TTS_OUTPUT_DIR,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)


def _play_audio_windows(file_path: str) -> None:
    """
    Play audio on Windows using the default media player.
    Uses os.startfile which opens the system's default MP3 player.
    """
    abs_path = os.path.abspath(file_path)
    print(f"[TTS] Playing: {abs_path}")
    os.startfile(abs_path)
    # Small delay so the file opens before next operation
    time.sleep(1.5)


def _speak_gtts(text: str, output_path: str) -> str:
    """Generate MP3 using Google TTS (free, no key needed)."""
    from gtts import gTTS
    tts = gTTS(text=text, lang=TTS_LANGUAGE, slow=False)
    tts.save(output_path)
    return output_path


def _speak_elevenlabs(text: str, output_path: str) -> str:
    """Generate MP3 using ElevenLabs API (premium quality)."""
    import requests as req
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    response = req.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def speak(
    text: str,
    play: bool = True,
    filename: str | None = None,
) -> str:
    """
    Convert text to speech and optionally play it.

    Args:
        text    : Agent response (auto-cleaned of markdown).
        play    : Whether to play immediately (default True).
        filename: Output filename; auto-generated if not given.

    Returns:
        Absolute path to the saved MP3 file.
    """
    clean_text = clean_for_voice(text)
    if not clean_text.strip():
        print("[TTS] Empty text — skipping.")
        return ""

    if not filename:
        filename = f"response_{int(time.time())}.mp3"
    output_path = os.path.join(TTS_OUTPUT_DIR, filename)

    # Auto-upgrade to ElevenLabs if key is present
    engine = "elevenlabs" if ELEVENLABS_API_KEY else TTS_ENGINE

    print(f"[TTS] Generating audio ({engine})...")
    try:
        if engine == "elevenlabs":
            _speak_elevenlabs(clean_text, output_path)
        else:
            _speak_gtts(clean_text, output_path)
    except Exception as e:
        print(f"[TTS] {engine} failed ({e}). Falling back to gTTS...")
        try:
            _speak_gtts(clean_text, output_path)
        except Exception as e2:
            print(f"[TTS] gTTS also failed: {e2}")
            return ""

    print(f"[TTS] Saved: {output_path}")
    if play:
        _play_audio_windows(output_path)

    return output_path
