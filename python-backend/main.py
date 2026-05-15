"""
main.py — Context-Aware AI Guidance Agent
==========================================
Entry point for the guidance backend service.

This agent receives:
  - user_query    : Text from the user (voice-to-text done inside the mobile app)
  - screen_context: JSON or text description of the current mobile screen
  - risk_level    : "LOW" | "MEDIUM" | "HIGH" from the app's fraud detection system

It returns:
  - A plain-text, step-by-step guidance response
  - An MP3 audio file of that response (via gTTS)

Usage:
    python main.py              # interactive text loop
    python main.py --test       # run 4 built-in test cases
    python main.py --audio      # interactive loop + speak responses aloud

The mobile app sends text input only. Audio-to-text is handled by the app.
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import create_guidance_agent
from agent.router import route, HIGH_RISK_MESSAGE
from utils.text_cleaner import clean_for_voice, add_hedging_if_needed


# ---------------------------------------------------------------------------
# Core query runner
# ---------------------------------------------------------------------------
def run_query(
    agent,
    user_query: str,
    screen_context: str,
    risk_level: str,
) -> dict:
    """
    Run one query through the full pipeline.

    Pipeline:
      1. Router: pre-checks risk level and calls RAG (Python, no LLM)
      2. Hard-stop: if HIGH risk, return canned warning immediately
      3. AgentExecutor: ReAct loop with enriched context + memory
      4. Post-process: clean text for voice, inject hedging if LLM fallback

    Args:
        agent        : AgentExecutor instance (with memory).
        user_query   : Text from user (already converted from voice by the app).
        screen_context: Description of the current mobile screen (JSON or text).
        risk_level   : "LOW" | "MEDIUM" | "HIGH" from external fraud system.

    Returns:
        dict with keys:
          - output      : Full guidance text
          - voice_output: Markdown-cleaned version suitable for TTS
          - rag_used    : bool — True if ChromaDB returned documents
          - hard_stop   : bool — True if HIGH risk warning was triggered
    """
    # Step 1: Explicit routing (Python logic, no LLM)
    routing = route(user_query, screen_context, risk_level)

    # Step 2: Hard-stop for HIGH risk (no LLM call at all)
    if routing["hard_stop"]:
        return {
            "output": routing["hard_stop_msg"],
            "voice_output": routing["hard_stop_msg"],
            "rag_used": False,
            "hard_stop": True,
        }

    # Step 3: Agent call — tiered model selected automatically based on rag_used
    response = agent.invoke(
        enriched_input=routing["enriched_input"],
        rag_used=routing["rag_used"],
    )
    raw_output = response.get("output", str(response))

    # Step 4: Post-processing
    hedged_output = add_hedging_if_needed(raw_output, routing["rag_used"])
    voice_output  = clean_for_voice(hedged_output)

    return {
        "output": hedged_output,
        "voice_output": voice_output,
        "rag_used": routing["rag_used"],
        "hard_stop": False,
    }


# ---------------------------------------------------------------------------
# Interactive text loop (simulates receiving input from the mobile app)
# ---------------------------------------------------------------------------
def interactive_loop(audio_output: bool = False):
    """
    Multi-turn conversation loop.
    Input is TEXT only (voice-to-text is done by the mobile app before sending).
    Output is text + optional MP3 audio file.
    """
    print("\n" + "=" * 65)
    print("  Context-Aware AI Guidance Agent")
    print("  Input: text | Output: text" + (" + audio" if audio_output else ""))
    print("=" * 65)
    print("\nInitializing agent...")

    agent = create_guidance_agent()

    if audio_output:
        from audio.tts import speak
        print("[Audio] TTS output ENABLED — responses will be spoken aloud.")

    print("\nCOMMANDS:")
    print("  Type your query and press Enter")
    print("  'clear'  — reset conversation memory")
    print("  'quit'   — exit\n")

    # Session defaults (the mobile app would send these per request)
    current_screen = "home screen"
    current_risk   = "LOW"
    turn = 0

    while True:
        turn += 1
        print("\n" + "-" * 65)
        print(f"  Turn {turn}")
        print("-" * 65)

        # User query (text — voice conversion done in mobile app)
        user_query = input("  User query (text): ").strip()
        if not user_query:
            turn -= 1
            continue
        if user_query.lower() in ("quit", "exit", "bye"):
            print("\n  Session ended.")
            break
        if user_query.lower() == "clear":
            agent.memory.clear()
            turn = 0
            print("  [Memory cleared. Starting fresh session.]")
            continue

        # Screen context from mobile app
        sc = input(f"  Screen context [{current_screen}]: ").strip()
        if sc:
            current_screen = sc

        # Risk level from fraud system
        rl = input(f"  Risk level [{current_risk}]: ").strip().upper()
        if rl in ("LOW", "MEDIUM", "HIGH"):
            current_risk = rl

        print(f"\n  [Routing] risk={current_risk} | screen='{current_screen[:50]}'")

        try:
            result = run_query(agent, user_query, current_screen, current_risk)
        except Exception as e:
            print(f"  [ERROR]: {e}")
            continue

        # Print response
        tag    = "[HIGH RISK]" if result["hard_stop"] else "[RESPONSE]"
        source = "(RAG)" if result["rag_used"] else "(LLM fallback)"
        print(f"\n  {tag} {source}:")
        print("  " + "-" * 60)
        for line in result["output"].strip().split("\n"):
            print("    " + line)
        print("  " + "-" * 60)

        # Speak the response (optional)
        if audio_output:
            try:
                speak(result["voice_output"], play=True)
            except Exception as e:
                print(f"  [TTS error: {e}]")


# ---------------------------------------------------------------------------
# Built-in test cases
# ---------------------------------------------------------------------------
def run_tests(audio_output: bool = False):
    """
    Run 4 predefined test cases to verify the full pipeline end-to-end.
    Test 4 specifically verifies that memory carries context from Test 1.
    """
    print("\n" + "=" * 65)
    print("  Context-Aware AI Guidance Agent -- Test Suite")
    print("=" * 65)

    agent = create_guidance_agent()

    if audio_output:
        from audio.tts import speak

    test_cases = [
        {
            "label": "Test 1 -- IFSC payment screen (LOW risk)",
            "user_query": "what should I do here",
            "screen_context": "payment screen with IFSC field",
            "risk_level": "LOW",
        },
        {
            "label": "Test 2 -- UPI payment JSON screen (LOW risk)",
            "user_query": "how do I pay using UPI",
            "screen_context": '{"screen": "payment_page", "elements": ["UPI ID input", "Amount field", "Pay button"]}',
            "risk_level": "LOW",
        },
        {
            "label": "Test 3 -- OTP scam call (HIGH risk - hard stop)",
            "user_query": "someone called and asked me to share my OTP",
            "screen_context": "OTP sharing screen for remote support",
            "risk_level": "HIGH",
        },
        {
            "label": "Test 4 -- Follow-up question (MEMORY test)",
            "user_query": "where exactly do I find that code you mentioned",
            "screen_context": "payment screen with IFSC field",
            "risk_level": "LOW",
        },
    ]

    for tc in test_cases:
        print("\n" + "-" * 65)
        print("  " + tc["label"])
        print("-" * 65)
        print("  Query  : " + tc["user_query"])
        print("  Screen : " + tc["screen_context"][:60])
        print("  Risk   : " + tc["risk_level"] + "\n")

        try:
            result = run_query(
                agent, tc["user_query"], tc["screen_context"], tc["risk_level"]
            )
            tag    = "[HIGH RISK]" if result["hard_stop"] else "[OK]"
            source = "(RAG)" if result["rag_used"] else "(LLM fallback)"
            print(f"  {tag} {source} RESPONSE:")
            for line in result["output"].strip().split("\n"):
                print("    " + line)
            if audio_output:
                try:
                    speak(result["voice_output"], play=True)
                except Exception as e:
                    print(f"  [TTS error: {e}]")
        except Exception as e:
            print(f"  [ERROR]: {e}")

    print("\n" + "=" * 65)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Context-Aware AI Guidance Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Screen context format (sent by mobile app):
  Plain text : "payment screen with IFSC field"
  JSON       : {"screen": "payment_page", "elements": ["UPI ID input", "Pay button"]}

Risk level (from app fraud system):
  LOW    — safe, proceed normally
  MEDIUM — caution, warn user
  HIGH   — hard stop, immediate fraud warning
        """
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run 4 built-in test cases and exit"
    )
    parser.add_argument(
        "--audio", action="store_true",
        help="Speak responses aloud via gTTS (text-to-speech output)"
    )
    args = parser.parse_args()

    if args.test:
        run_tests(audio_output=args.audio)
    else:
        interactive_loop(audio_output=args.audio)
