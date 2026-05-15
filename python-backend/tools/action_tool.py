"""
tools/action_tool.py
---------------------
Suggests the next best user action based on the screen description.
Uses rule-based logic — no LLM call needed.
"""

from langchain_core.tools import tool

# Map of keyword → action suggestion
_ACTION_MAP = [
    (
        ["ifsc"],
        "1. Find your IFSC code in your bank passbook or app.\n"
        "2. Tap the IFSC field on screen.\n"
        "3. Type the 11-character code carefully.\n"
        "4. Tap Next or Confirm to proceed.",
    ),
    (
        ["upi id", "upi"],
        "1. Tap the UPI ID input field.\n"
        "2. Type the recipient's UPI ID (e.g., name@bank).\n"
        "3. Verify the payee name that appears.\n"
        "4. Enter the amount.\n"
        "5. Tap the Pay button and enter your UPI PIN.",
    ),
    (
        ["otp"],
        "1. Check your registered mobile number for the OTP SMS.\n"
        "2. Tap the OTP input field on screen.\n"
        "3. Enter the OTP digits quickly — it expires in a few minutes.\n"
        "4. Do NOT share the OTP with anyone.",
    ),
    (
        ["collect request"],
        "WARNING: Approving a UPI collect request SENDS money — it does NOT receive money.\n"
        "1. Check who sent this request.\n"
        "2. If you do not recognise the sender, tap DECLINE immediately.\n"
        "3. Never approve collect requests from unknown people.",
    ),
    (
        ["anydesk", "teamviewer", "remote"],
        "WARNING: Do NOT install this app.\n"
        "1. Close this screen immediately.\n"
        "2. No legitimate bank or company will ask you to install remote access software.\n"
        "3. End the call with the person who asked you to do this.",
    ),
    (
        ["account number"],
        "1. Enter your bank account number carefully — double-check each digit.\n"
        "2. Re-enter the account number in the confirmation field.\n"
        "3. Tap Next to continue.",
    ),
    (
        ["amount", "pay button", "payment"],
        "1. Check the payment amount is correct.\n"
        "2. Verify the recipient name or UPI ID shown on screen.\n"
        "3. Tap the Pay button to confirm.\n"
        "4. Enter your UPI PIN when prompted.",
    ),
    (
        ["login", "sign in"],
        "1. Enter your registered mobile number or username.\n"
        "2. Enter your password.\n"
        "3. Tap the Login or Sign In button.\n"
        "4. Enter the OTP sent to your phone if prompted.",
    ),
]


@tool
def action_planner_tool(screen_description: str) -> str:
    """
    Suggest clear, step-by-step next actions for the user based on the
    current screen description.
    Input: Human-readable screen description (from screen_analyzer_tool).
    Output: Numbered step-by-step action guide for that screen.
    """
    desc = screen_description.lower()

    for keywords, action in _ACTION_MAP:
        if any(kw in desc for kw in keywords):
            return action

    return (
        "1. Read the text on your screen carefully.\n"
        "2. Fill in the required fields one by one.\n"
        "3. Double-check your entries before tapping any button.\n"
        "4. If unsure, contact your bank's customer care for help."
    )
