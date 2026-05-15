"""
demo_no_context.py
-------------------
Demonstrates the NO_CONTEXT (LLM fallback) path.

The agent is given a query about something completely outside the knowledge base
(stock trading, app store, etc.) so ChromaDB finds nothing relevant and the
router routes to LLM general knowledge instead.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import create_guidance_agent
from agent.router import route, fuse_query_with_screen
from utils.text_cleaner import add_hedging_if_needed, clean_for_voice

agent = create_guidance_agent()

# --- Cases that will hit NO_CONTEXT ---
no_context_cases = [
    {
        "label": "CASE A -- Stock trading (not in KB)",
        "user_query": "how do I buy shares here",
        "screen_context": '{"screen": "stock_trading_app", "elements": ["Stock search", "Buy button", "Portfolio tab"]}',
        "risk_level": "LOW",
    },
    {
        "label": "CASE B -- Vague query on unknown screen",
        "user_query": "I am confused",
        "screen_context": "mobile data recharge plan selection screen",
        "risk_level": "LOW",
    },
]

print("\n" + "=" * 65)
print("  NO_CONTEXT DEMO — LLM Fallback Path")
print("=" * 65)

for tc in no_context_cases:
    print("\n" + "-" * 65)
    print("  " + tc["label"])
    print("-" * 65)
    print("  User query    : " + tc["user_query"])
    print("  Screen context: " + tc["screen_context"][:65])
    print("  Risk level    : " + tc["risk_level"])
    print()

    # Run router
    routing = route(tc["user_query"], tc["screen_context"], tc["risk_level"])

    print("  [ROUTER DECISIONS]")
    print("  Grounded query : " + routing["grounded_query"])
    print("  Fraud risk     : " + routing["fraud_risk"] + "  (screen-only assessment)")
    print("  RAG result     : " + routing["rag_result"][:50])
    print("  RAG used?      : " + str(routing["rag_used"]) + "  --> LLM FALLBACK ACTIVATED")

    if routing["hard_stop"]:
        print("\n  [HIGH RISK HARD STOP]")
        print("  " + routing["hard_stop_msg"])
        continue

    # Call agent
    response = agent.invoke({"input": routing["enriched_input"]})
    raw_output = response.get("output", str(response))
    hedged = add_hedging_if_needed(raw_output, rag_used=False)

    print("\n  [AGENT RESPONSE] (LLM fallback - no RAG docs used):")
    print("  " + "-" * 58)
    for line in hedged.strip().split("\n"):
        print("    " + line)
    print("  " + "-" * 58)

print("\n" + "=" * 65)
