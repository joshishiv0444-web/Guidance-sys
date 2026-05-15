"""
agent/router.py
---------------
EXPLICIT routing logic — runs BEFORE the AgentExecutor.

Two key design decisions:
  1. QUERY-SCREEN FUSION: The user query and screen context are fused into
     one grounded query before RAG retrieval. Vague queries like "what do I
     do?" become specific when combined with the screen ("...on a UPI payment
     screen with IFSC input field"). This makes RAG retrieval much more accurate.

  2. FRAUD DETECTION — SCREEN CONTEXT ONLY: The fraud model receives ONLY the
     screen_context, not the user's query. This matches the future ML model's
     expected input (screen metadata/description). The user replaces
     tools/fraud_model_interface.py to plug in their trained model.

Routing order:
  Step 1 → Analyze screen context (rule-based parser)
  Step 2 → Assess fraud risk from SCREEN ONLY (fraud_model_interface.py)
  Step 3 → Hard-stop if HIGH risk (no LLM call)
  Step 4 → Fuse query + screen into grounded query
  Step 5 → RAG retrieval on grounded query
  Step 6 → Build enriched input for AgentExecutor
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.rag_tool import rag_retriever_tool
from tools.screen_tool import screen_analyzer_tool
from tools.fraud_model_interface import assess_screen_risk


# Hard-stop canned warning — no LLM involvement
HIGH_RISK_MESSAGE = (
    "WARNING! This looks like a FRAUD attempt. "
    "STOP what you are doing immediately. "
    "Do NOT share your OTP, PIN, password, or any personal information. "
    "Do NOT install any app someone asked you to install. "
    "End the call now. "
    "Call your bank's official helpline number on the back of your debit card if needed. "
    "You can also report fraud at the National Cyber Crime helpline: 1930."
)

# Phrases that indicate the user's query is too vague on its own
_VAGUE_QUERY_PHRASES = [
    "what should i do", "what do i do", "what now", "help me",
    "i don't understand", "i dont understand", "what is this",
    "what does this mean", "how to proceed", "help", "confused",
    "what do i click", "what do i tap", "what next", "next step",
]


def fuse_query_with_screen(user_query: str, screen_desc: str) -> str:
    """
    Combine the user's query with the screen description into a single
    grounded query for RAG retrieval.

    Why this matters:
      - "what should I do?" → useless for RAG
      - "what should I do on a UPI payment screen with IFSC code input?" → great for RAG

    Logic:
      - If query is vague → use screen as the primary search term
      - If query is specific → prefix screen context for more precision
    """
    query_lower = user_query.lower().strip()
    is_vague = any(phrase in query_lower for phrase in _VAGUE_QUERY_PHRASES)

    if is_vague:
        # The screen tells us more than the query — make screen the anchor
        grounded = f"how to use {screen_desc}"
    else:
        # Query is specific — fuse both for maximum RAG precision
        grounded = f"{user_query} on {screen_desc}"

    return grounded


def route(
    user_query: str,
    screen_context: str,
    external_risk_level: str,
) -> dict:
    """
    Run full routing logic before the AgentExecutor.

    Args:
        user_query         : Text from the user (voice-to-text done by mobile app).
        screen_context     : Raw JSON or text from the mobile app's screen capture.
        external_risk_level: "LOW" | "MEDIUM" | "HIGH" from the app's system.

    Returns dict with:
        hard_stop       : bool — skip agent, return canned warning immediately
        hard_stop_msg   : str  — the canned warning message
        grounded_query  : str  — query fused with screen context
        rag_result      : str  — retrieved docs or "NO_CONTEXT"
        rag_used        : bool — True if RAG returned documents
        screen_desc     : str  — human-readable screen description
        fraud_risk      : str  — risk from fraud_model_interface (screen only)
        external_risk   : str  — risk passed in from mobile app
        enriched_input  : str  — full context string for AgentExecutor
    """
    result = {
        "hard_stop": False,
        "hard_stop_msg": "",
        "grounded_query": "",
        "rag_result": "NO_CONTEXT",
        "rag_used": False,
        "screen_desc": "",
        "fraud_risk": "LOW",
        "external_risk": external_risk_level.upper(),
        "enriched_input": "",
    }

    # ─── Step 1: Parse screen context ────────────────────────────────────────
    screen_desc = screen_analyzer_tool.invoke(screen_context)
    result["screen_desc"] = screen_desc

    # ─── Step 2: Fraud assessment — SCREEN CONTEXT ONLY ─────────────────────
    # NOTE: Only screen_context is passed here. User query is NOT sent.
    # This matches the future ML model's expected input (screen metadata only).
    fraud_risk = assess_screen_risk(screen_context)
    result["fraud_risk"] = fraud_risk

    # ─── Step 3: Hard-stop on HIGH risk ──────────────────────────────────────
    # Either source triggers a hard stop — external app signal OR our model
    if external_risk_level.upper() == "HIGH" or fraud_risk == "HIGH":
        result["hard_stop"] = True
        result["hard_stop_msg"] = HIGH_RISK_MESSAGE
        return result

    # ─── Step 4: Query-screen fusion ─────────────────────────────────────────
    grounded_query = fuse_query_with_screen(user_query, screen_desc)
    result["grounded_query"] = grounded_query
    print(f"[Router] Grounded query: '{grounded_query}'")

    # ─── Step 5: RAG retrieval on grounded query ──────────────────────────────
    rag_result = rag_retriever_tool.invoke(grounded_query)
    result["rag_result"] = rag_result
    result["rag_used"] = not rag_result.startswith("NO_CONTEXT")

    rag_status = "RAG hit" if result["rag_used"] else "NO_CONTEXT -> LLM fallback"
    print(f"[Router] RAG: {rag_status}")

    # ─── Step 6: Build enriched input for AgentExecutor ──────────────────────
    caution_flag = ""
    if external_risk_level.upper() == "MEDIUM" or fraud_risk == "MEDIUM":
        caution_flag = "\n[CAUTION: Medium fraud risk detected. Advise the user to be careful.]\n"

    if result["rag_used"]:
        knowledge_block = (
            "\n[KNOWLEDGE BASE — use this to answer]:\n"
            + rag_result + "\n"
        )
    else:
        knowledge_block = (
            "\n[NO_CONTEXT: knowledge base had nothing relevant. "
            "Use your general knowledge to help the user.]\n"
        )

    result["enriched_input"] = (
        f"User Query: {user_query}\n"
        f"Grounded Query (query + screen): {grounded_query}\n"
        f"Screen Description: {screen_desc}\n"
        f"Fraud Risk (screen model): {fraud_risk}\n"
        f"External Risk Level: {external_risk_level}\n"
        f"{caution_flag}"
        f"{knowledge_block}\n"
        f"Give the user simple, step-by-step guidance. "
        f"If unsure, say 'I'm not fully sure, but...' before answering. "
        f"Plain language only. Under 120 words."
    )

    return result
