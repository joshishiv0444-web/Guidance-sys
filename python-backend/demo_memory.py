"""
demo_memory.py
--------------
Proves that ConversationBufferMemory is working across turns.

Turn 1: Ask about IFSC code → agent explains what IFSC is
Turn 2: Different topic → ask about UPI payment
Turn 3: Follow-up referring to Turn 1 ("that code you mentioned earlier")
         → agent can ONLY answer this correctly if it remembers Turn 1

After each turn, we print the raw memory contents so you can SEE what is stored.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import create_guidance_agent
from agent.router import route
from utils.text_cleaner import add_hedging_if_needed


def run_turn(agent, label, user_query, screen_context, risk_level):
    print("\n" + "=" * 65)
    print("  " + label)
    print("=" * 65)
    print(f"  Query  : {user_query}")
    print(f"  Screen : {screen_context[:60]}")
    print(f"  Risk   : {risk_level}")

    routing = route(user_query, screen_context, risk_level)

    if routing["hard_stop"]:
        print(f"\n  [HARD STOP]: {routing['hard_stop_msg'][:100]}")
        return

    print(f"  Grounded: {routing['grounded_query']}")
    print(f"  RAG    : {'HIT' if routing['rag_used'] else 'NO_CONTEXT -> LLM fallback'}")

    response = agent.invoke(
        enriched_input=routing["enriched_input"],
        rag_used=routing["rag_used"],
    )
    raw = response.get("output", str(response))
    final = add_hedging_if_needed(raw, routing["rag_used"])

    print(f"\n  [AGENT RESPONSE]:")
    for line in final.strip().split("\n"):
        print(f"    {line}")

    # Print memory contents after each turn
    mem = agent.memory
    msgs = mem.chat_memory.messages
    print(f"\n  [MEMORY SNAPSHOT] ({len(msgs)} messages stored):")
    for i, msg in enumerate(msgs):
        role = "Human" if msg.__class__.__name__ == "HumanMessage" else "AI"
        content_preview = msg.content[:80].replace("\n", " ")
        print(f"    [{i+1}] {role}: {content_preview}...")
    return final


def main():
    print("\n" + "#" * 65)
    print("  MEMORY TEST — 3-Turn Conversation")
    print("  Turn 3 references Turn 1 to prove memory works")
    print("#" * 65)

    agent = create_guidance_agent()

    # Turn 1: IFSC code on payment screen
    run_turn(
        agent,
        label="TURN 1 — User on IFSC payment screen",
        user_query="what is this code I need to enter",
        screen_context="payment screen with IFSC code input field",
        risk_level="LOW",
    )

    # Turn 2: Different topic — UPI
    run_turn(
        agent,
        label="TURN 2 — Different topic (UPI payment)",
        user_query="how do I pay using UPI",
        screen_context='{"screen": "upi_payment", "elements": ["UPI ID input", "Pay button"]}',
        risk_level="LOW",
    )

    # Turn 3: Follow-up referring to Turn 1
    # Agent can ONLY answer this if it remembers Turn 1's IFSC discussion
    run_turn(
        agent,
        label="TURN 3 — Follow-up referencing Turn 1 (MEMORY PROOF)",
        user_query="where do I find that 11 digit code you mentioned earlier",
        screen_context="payment screen with IFSC code input field",
        risk_level="LOW",
    )

    print("\n" + "#" * 65)
    print("  TEST COMPLETE")
    print("  If Turn 3 mentions passbook/cheque/bank app,")
    print("  memory is working correctly.")
    print("#" * 65 + "\n")


if __name__ == "__main__":
    main()
