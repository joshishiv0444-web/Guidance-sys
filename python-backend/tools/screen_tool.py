"""
tools/screen_tool.py
---------------------
Converts raw UI JSON (or a plain-text description) into a human-readable
screen description without calling an LLM.
"""

import json
from langchain_core.tools import tool


# Keyword → description mapping for rule-based parsing
_SCREEN_RULES = [
    (["ifsc"], "payment screen with an IFSC code input field"),
    (["upi id", "upi"], "payment screen with a UPI ID input field and a Pay button"),
    (["otp", "one-time password"], "verification screen asking for an OTP code"),
    (["anydesk", "teamviewer", "remote"], "screen requesting remote access app installation"),
    (["login", "sign in", "username", "password"], "login screen with username and password fields"),
    (["account number", "account no"], "payment screen with a bank account number input field"),
    (["beneficiary"], "fund transfer screen for adding a new beneficiary"),
    (["amount", "pay button", "payment"], "payment screen with an amount field and Pay button"),
    (["collect request", "collect"], "UPI collect request screen"),
]


@tool
def screen_analyzer_tool(screen_context: str) -> str:
    """
    Convert raw UI JSON or a plain-text screen description into a human-readable
    summary of what is displayed on the user's screen.
    Input: A JSON string (with 'screen' and 'elements' keys) or free-text
           description of the current mobile screen.
    Output: A simple English sentence describing the screen.
    """
    # ── Try JSON parsing first ──────────────────────────────────────────────
    try:
        data = json.loads(screen_context)
        screen_name = data.get("screen", "unknown screen").replace("_", " ")
        elements = data.get("elements", [])

        if elements:
            elem_str = ", ".join(str(e) for e in elements)
            return f"User is on a {screen_name} with the following elements: {elem_str}."
        elif "description" in data:
            return f"User is on a screen described as: {data['description']}."
        else:
            return f"User is on a {screen_name}."

    except (json.JSONDecodeError, TypeError):
        pass

    # ── Rule-based string matching ──────────────────────────────────────────
    text_lower = screen_context.lower()
    for keywords, description in _SCREEN_RULES:
        if any(kw in text_lower for kw in keywords):
            return f"User is on a {description}."

    # ── Generic fallback ────────────────────────────────────────────────────
    return f"User is on a screen described as: {screen_context}."
