"""
tools/fraud_model_interface.py
-------------------------------
FRAUD DETECTION INTERFACE — Screen Context Only

This is the single point you will replace with your actual ML fraud
detection model. The rest of the system calls ONLY this function.

CONTRACT:
  Input  : screen_context (str) — the raw JSON or text from the mobile app
  Output : "HIGH" | "MEDIUM" | "LOW"

CURRENT IMPLEMENTATION: Rule-based heuristic matcher (20+ patterns).
FUTURE REPLACEMENT     : Load your trained model here and call model.predict(screen_context).

To swap in your model:
  1. Delete the rule-based block below.
  2. Load your model (e.g., joblib.load, torch.load, etc.)
  3. Implement assess_screen_risk() to call your model and return the label.
  4. Nothing else in the codebase needs to change.
"""

import os
import re
from typing import Optional, Dict, Any, List

# Heuristics-only fraud detector (no HF model). This file intentionally
# keeps a small compatible API so the rest of the system can call the same
# helper functions (`_model_predict_prob`, `analyze_screen_text`,
# `assess_screen_risk`) but they operate using rule-based patterns only.


# ---------------------------------------------------------------------------
# Minimal compatibility stubs
# ---------------------------------------------------------------------------
def _model_predict_prob(screen_text: str) -> Optional[float]:
    """Model not present in heuristics-only mode — always return None."""
    return None


def _get_url_reputation(url: str) -> str:
    """URL reputation unavailable in heuristics-only mode.

    The endpoint that checks VirusTotal will still call this function, but
    without a configured API key the app will return "No API Key".
    """
    vt_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not vt_key:
        return "No API Key"
    return "Unrated"


def analyze_screen_text(screen_text: str) -> Dict[str, Any]:
    """Return a simple analysis dict derived from heuristics only.

    This preserves the contract used elsewhere in the codebase but does not
    perform any ML inference.
    """
    risk = assess_screen_risk(screen_text)
    return {
        "risk_level": risk,
        "label": None,
        "confidence": None,
        "url_reputation": "No API Key",
        "detected_urls": [],
    }


# ---------------------------------------------------------------------------
# Fallback rule-based heuristics (kept for compatibility and debugging)
# ---------------------------------------------------------------------------
_HIGH_PATTERNS = [
    r"share.{0,15}otp",
    r"send.{0,15}otp",
    r"enter.{0,15}otp.{0,20}(agent|support|rep|officer|executive)",
    r"remote.{0,15}(access|control|support|desktop)",
    r"screen.{0,10}share",
    r"anydesk",
    r"teamviewer",
    r"quicksupport",
    r"install.{0,20}(app|apk|software).{0,20}(said|asked|told|requested)",
    r"refund.{0,15}process",
    r"kyc.{0,15}(expire|block|suspend|freeze)",
    r"account.{0,15}(block|suspend|freeze|close)",
    r"prize.{0,10}(won|win|claim)",
    r"lottery.{0,10}(won|win|claim)",
    r"lucky.{0,10}(draw|winner)",
    r"customs.{0,10}(duty|clearance|package)",
    r"electricity.{0,10}(cut|disconnect|bill)",
    r"police.{0,10}(case|notice|arrest)",
    r"aadhaar.{0,10}(link|deactivate|block)",
]

_MEDIUM_PATTERNS = [
    r"unknown.{0,10}(upi|account|payment)",
    r"pay.{0,10}(urgent|immediately|now)",
    r"verify.{0,10}(account|identity|card)",
    r"confirm.{0,10}(payment|transfer).{0,15}(phone|call|message)",
    r"(new|unknown).{0,10}(beneficiary|contact)",
    r"gift.{0,10}card.{0,10}(payment|pay)",
    r"wallet.{0,10}(recharge|add money).{0,10}(urgent|immediately)",
]


def assess_screen_risk(screen_context: str) -> str:
    """
    Analyse the screen_context and return a fraud risk level.

    This function will use a trained Hugging Face sequence-classification model
    if one is present at `FRAUD_MODEL_DIR` (default: `./fraud_detection_model`).

    Model contract (if present):
      - Binary classification with labels {0: legitimate, 1: scam}
      - We map predicted probability to risk levels:
          prob >= 0.75 -> "HIGH"
          0.40 <= prob < 0.75 -> "MEDIUM"
          prob < 0.40 -> "LOW"

    If no model is available or model inference fails, this function falls back
    to the original rule-based heuristics (pattern matching).

    Args:
        screen_context: Raw string or JSON from the mobile app describing
                        the current UI state.

    Returns:
        "HIGH"   — strong fraud indicators present, hard-stop the user
        "MEDIUM" — suspicious signals, caution warning to user
        "LOW"    — no obvious fraud signals detected
    """
    # Heuristics-only path: use rule-based patterns
    text = screen_context.lower()

    for pattern in _HIGH_PATTERNS:
        if re.search(pattern, text):
            return "HIGH"

    for pattern in _MEDIUM_PATTERNS:
        if re.search(pattern, text):
            return "MEDIUM"

    return "LOW"
