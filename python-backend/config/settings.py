"""
config/settings.py
------------------
All configuration loaded from .env (via python-dotenv).
Never hardcode secrets here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# HuggingFace (LLM + STT)
# ---------------------------------------------------------------------------
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HUGGINGFACEHUB_API_TOKEN:
	raise RuntimeError(
		"HUGGINGFACEHUB_API_TOKEN is not set.\n"
		"Please set the HUGGINGFACEHUB_API_TOKEN environment variable in your Render service settings "
		"or provide it via a .env file during local development."
	)

# ---------------------------------------------------------------------------
# LLM — Tiered model selection (accuracy + speed)
#
# FAST MODEL   : Used when RAG retrieves documents (7B just formats pre-fetched facts)
#                ~2-8s response time
# QUALITY MODEL: Used when NO_CONTEXT (LLM must recall from its own knowledge)
#                ~8-20s response time — worth the wait when accuracy matters
# ---------------------------------------------------------------------------
LLM_FAST_MODEL          = "Qwen/Qwen2.5-7B-Instruct"    # RAG hit path
LLM_QUALITY_MODEL       = "Qwen/Qwen2.5-72B-Instruct"   # NO_CONTEXT fallback path
LLM_MAX_TOKENS_RAG      = 300   # short enough for formatting retrieved docs
LLM_MAX_TOKENS_FALLBACK = 500   # more tokens for open-ended LLM answers
LLM_TEMPERATURE         = 0.1

# Keep this for any legacy references
LLM_REPO_ID    = LLM_FAST_MODEL
LLM_MAX_TOKENS = LLM_MAX_TOKENS_RAG


# ---------------------------------------------------------------------------
# TTS — gTTS by default (free, no key). Set ELEVENLABS_API_KEY to upgrade.
# ---------------------------------------------------------------------------
TTS_ENGINE          = "gtts"               # "gtts" | "elevenlabs"
TTS_LANGUAGE        = "en"
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Rachel")
TTS_OUTPUT_DIR      = str(_BASE_DIR / "audio_output")

# ---------------------------------------------------------------------------
# Embeddings — all-MiniLM-L6-v2 runs locally on CPU (free, no key)
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# RAG / ChromaDB
# ---------------------------------------------------------------------------
RAG_SIMILARITY_THRESHOLD = 0.30
CHROMA_PERSIST_DIRECTORY = str(_BASE_DIR / "chroma_db")

# Create audio output dir
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)
