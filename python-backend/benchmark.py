"""
benchmark.py — before vs after timing with warm/cold breakdown
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import create_guidance_agent
from agent.router import route
from utils.text_cleaner import add_hedging_if_needed

QUERY  = "what should I do here"
SCREEN = "payment screen with IFSC field"
RISK   = "LOW"

print("\n" + "=" * 60)
print("  OPTIMIZED BENCHMARK")
print("=" * 60)

# ── Startup (one-time cost) ───────────────────────────────────────────────────
t0 = time.time()
agent = create_guidance_agent()
startup_time = time.time() - t0
print(f"\n  [Startup]  {startup_time:.2f}s  (embedding model + ChromaDB + LLM init)")

# ── Query 1 — cold (first query after startup) ────────────────────────────────
t0 = time.time()
routing1 = route(QUERY, SCREEN, RISK)
router1_t = time.time() - t0

t0 = time.time()
resp1 = agent.invoke({"input": routing1["enriched_input"]})
llm1_t = time.time() - t0

query1_total = router1_t + llm1_t
print(f"\n  [Query 1 — first call]")
print(f"    Router (screen+fraud+RAG) : {router1_t:.2f}s")
print(f"    LLM call (Qwen2.5)        : {llm1_t:.2f}s")
print(f"    Query total               : {query1_total:.2f}s")
print(f"    Response: {resp1.get('output','')[:70]}...")

# ── Query 2 — warm (everything cached) ───────────────────────────────────────
QUERY2  = "how do I pay using UPI"
SCREEN2 = '{"screen": "payment_page", "elements": ["UPI ID input", "Pay button"]}'

t0 = time.time()
routing2 = route(QUERY2, SCREEN2, RISK)
router2_t = time.time() - t0

t0 = time.time()
resp2 = agent.invoke({"input": routing2["enriched_input"]})
llm2_t = time.time() - t0

query2_total = router2_t + llm2_t
print(f"\n  [Query 2 — warm call (all caches hot)]")
print(f"    Router (screen+fraud+RAG) : {router2_t:.2f}s")
print(f"    LLM call (Qwen2.5)        : {llm2_t:.2f}s")
print(f"    Query total               : {query2_total:.2f}s")
print(f"    Response: {resp2.get('output','')[:70]}...")

print(f"\n  {'-'*55}")
print(f"  Startup cost  : {startup_time:.2f}s  (paid once per session)")
print(f"  Per-query avg : {(query1_total + query2_total) / 2:.2f}s")
print("=" * 60 + "\n")
