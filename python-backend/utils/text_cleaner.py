"""
utils/text_cleaner.py
----------------------
Post-processing utilities for voice-friendly output.

Strips markdown formatting, removes special symbols, truncates to a
comfortable listening length, and ensures numbered steps are spoken naturally.
"""

import re


# Max characters to speak in one TTS call (~250 words ≈ 90 seconds)
MAX_VOICE_CHARS = 1800


def clean_for_voice(text: str) -> str:
    """
    Transform agent output text into clean, natural-sounding spoken language.

    Steps:
      1. Strip markdown (headers, bold, italic, bullets, links)
      2. Remove code fences
      3. Normalize punctuation for natural pauses
      4. Collapse whitespace
      5. Truncate to MAX_VOICE_CHARS

    Args:
        text: Raw agent response text (may contain markdown).

    Returns:
        Clean string suitable for TTS.
    """
    # Remove markdown headers (### Heading → Heading)
    text = re.sub(r"#{1,6}\s+", "", text)

    # Remove bold/italic markers (**text** → text, *text* → text)
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)

    # Remove inline code (`code` → code)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove fenced code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Remove markdown links [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Remove horizontal rules ---
    text = re.sub(r"-{3,}", ".", text)

    # Remove bullet dashes at start of line (- item → item)
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)

    # Convert em-dash to comma pause
    text = text.replace("—", ", ").replace("–", ", ")

    # Normalize numbered list dots: "1." → "Step 1."
    text = re.sub(r"(?m)^\s*(\d+)\.\s+", r"Step \1. ", text)

    # Remove parenthetical URL-like content
    text = re.sub(r"\(https?://[^\)]+\)", "", text)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.splitlines())

    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Truncate to max length (keep complete sentences)
    if len(text) > MAX_VOICE_CHARS:
        truncated = text[:MAX_VOICE_CHARS]
        # Try to end at a sentence boundary
        last_period = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
        if last_period > MAX_VOICE_CHARS * 0.5:
            text = truncated[:last_period + 1]
        else:
            text = truncated + "..."

    return text


def is_high_risk_response(text: str) -> bool:
    """Return True if the agent response contains a HIGH risk warning."""
    keywords = ["stop immediately", "do not proceed", "warn", "fraud", "scam", "stop!"]
    lower = text.lower()
    return any(kw in lower for kw in keywords)


def add_hedging_if_needed(text: str, rag_used: bool) -> str:
    """
    Prepend 'I'm not fully sure, but...' if the agent fell back to LLM
    (i.e., RAG was not used) and no confident answer markers are present.
    """
    if not rag_used:
        confident_markers = [
            "according to", "based on", "the ifsc", "the upi", "you should",
            "step 1", "step one", "first,", "here is"
        ]
        lower = text.lower()
        has_confident = any(m in lower for m in confident_markers)
        if not has_confident:
            text = "I'm not fully sure, but... " + text
    return text
