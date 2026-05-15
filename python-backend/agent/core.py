"""
agent/core.py
-------------
Tiered LLM selection — accuracy + speed optimized:

  RAG HIT   → Qwen2.5-7B-Instruct  (fast, ~2-8s)
              LLM just formats pre-retrieved docs into steps.
              7B is as accurate as 72B here because the facts come from ChromaDB.

  NO_CONTEXT → Qwen2.5-72B-Instruct (slower, ~8-15s but worth it)
               LLM must recall knowledge from its own weights.
               72B knows significantly more than 7B for open-ended questions.

This gives the best of both worlds: speed when knowledge is available,
quality when the LLM is the sole source of truth.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, List, Optional
import requests
from langchain_core.language_models.llms import LLM
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

from tools.rag_tool import rag_retriever_tool
from tools.screen_tool import screen_analyzer_tool
from tools.fraud_tool import fraud_detection_tool
from tools.action_tool import action_planner_tool
from memory.buffer import get_memory
from config.settings import (
    HUGGINGFACEHUB_API_TOKEN,
    LLM_FAST_MODEL,
    LLM_QUALITY_MODEL,
    LLM_MAX_TOKENS_RAG,
    LLM_MAX_TOKENS_FALLBACK,
    LLM_TEMPERATURE,
)

HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"


# ---------------------------------------------------------------------------
# Custom LLM wrapper — HF OpenAI-compatible router
# ---------------------------------------------------------------------------
class HFChatLLM(LLM):
    repo_id: str
    api_token: str
    max_tokens: int = 300
    temperature: float = 0.1

    @property
    def _llm_type(self) -> str:
        return "hf_chat_router"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload: dict = {
            "model": self.repo_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if stop:
            payload["stop"] = stop

        response = requests.post(HF_CHAT_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Shared prompt — works for both models
# Context is pre-loaded by the router, so agent goes straight to Final Answer.
# ---------------------------------------------------------------------------
REACT_TEMPLATE = """You are a Context-Aware AI Guidance Agent helping a mobile user.

IMPORTANT: Screen analysis, fraud check, and knowledge retrieval are ALREADY DONE.
They are in the Question below. Go DIRECTLY to Final Answer.
Only call a tool if you genuinely need information not already provided.

RULES:
1. Plain simple language. No jargon.
2. Numbered steps only. Under 80 words.
3. If fraud risk is HIGH -> warn user to STOP immediately.
4. If [NO_CONTEXT] is shown -> use your own general knowledge to help.
5. If unsure -> start with "I'm not fully sure, but..."

Previous conversation:
{chat_history}

Available tools (use only if truly needed):
{tools}

Format (go direct):
Question: {input}
Thought: I have all the context. I will answer directly.
Final Answer: [plain numbered steps]

OR if a tool call is needed:
Thought: ...
Action: one of [{tool_names}]
Action Input: ...
Observation: ...
Thought: I now know the final answer
Final Answer: [plain numbered steps]

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


# ---------------------------------------------------------------------------
# Two pre-built AgentExecutors — swapped per query based on RAG result
# ---------------------------------------------------------------------------
def _build_executor(llm: HFChatLLM, memory) -> AgentExecutor:
    tools = [
        rag_retriever_tool,
        screen_analyzer_tool,
        fraud_detection_tool,
        action_planner_tool,
    ]
    prompt = PromptTemplate.from_template(REACT_TEMPLATE)
    agent  = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        return_intermediate_steps=False,
    )


class GuidanceAgent:
    """
    Wraps two AgentExecutors — one fast (7B), one quality (72B).
    The router's rag_used flag determines which is called per query.

    Both executors share the SAME memory object so conversation
    history is consistent regardless of which model answered.
    """

    def __init__(self):
        # PRE-WARM: load embedding model + ChromaDB once at startup
        from rag.pipeline import get_rag_pipeline
        print("[Agent] Pre-warming RAG pipeline...")
        get_rag_pipeline()

        # Shared memory across both executors
        self.memory = get_memory()

        # Fast executor — Qwen2.5-7B (RAG hit path)
        print(f"[Agent] Fast model  : {LLM_FAST_MODEL}")
        llm_fast = HFChatLLM(
            repo_id=LLM_FAST_MODEL,
            api_token=HUGGINGFACEHUB_API_TOKEN,
            max_tokens=LLM_MAX_TOKENS_RAG,
            temperature=LLM_TEMPERATURE,
        )
        self._fast_executor = _build_executor(llm_fast, self.memory)

        # Quality executor — Qwen2.5-72B (NO_CONTEXT fallback path)
        print(f"[Agent] Quality model: {LLM_QUALITY_MODEL}")
        llm_quality = HFChatLLM(
            repo_id=LLM_QUALITY_MODEL,
            api_token=HUGGINGFACEHUB_API_TOKEN,
            max_tokens=LLM_MAX_TOKENS_FALLBACK,
            temperature=LLM_TEMPERATURE,
        )
        self._quality_executor = _build_executor(llm_quality, self.memory)

        print("[Agent] Ready. (7B for RAG hits | 72B for LLM fallback)")

    def invoke(self, enriched_input: str, rag_used: bool) -> dict:
        """
        Route to the appropriate executor based on whether RAG returned docs.

        Args:
            enriched_input: Full context string from router.
            rag_used: True if ChromaDB returned relevant documents.

        Returns:
            AgentExecutor response dict (has 'output' key).
        """
        if rag_used:
            model_tag = f"7B [{LLM_FAST_MODEL.split('/')[-1]}]"
            executor  = self._fast_executor
        else:
            model_tag = f"72B [{LLM_QUALITY_MODEL.split('/')[-1]}]"
            executor  = self._quality_executor

        print(f"[Agent] Using {model_tag} (rag_used={rag_used})")
        return executor.invoke({"input": enriched_input})

    def clear_memory(self):
        """Reset conversation history."""
        self.memory.clear()


def create_guidance_agent() -> GuidanceAgent:
    """Build and return the fully configured GuidanceAgent."""
    return GuidanceAgent()
