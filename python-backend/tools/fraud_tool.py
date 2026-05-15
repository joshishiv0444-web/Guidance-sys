"""
tools/fraud_tool.py
--------------------
LangChain @tool wrapper around fraud_model_interface.py.

The router now calls assess_screen_risk() DIRECTLY from fraud_model_interface
with screen_context only. This tool is kept for use inside the AgentExecutor
if the agent decides to run an additional fraud check mid-conversation.

NOTE: The real fraud assessment flow is:
  router.py → fraud_model_interface.assess_screen_risk(screen_context)
This tool is the agent-callable version of the same function.
"""

from langchain_core.tools import tool
from tools.fraud_model_interface import assess_screen_risk


@tool
def fraud_detection_tool(screen_context: str) -> str:
    """
    Assess the fraud risk of the current screen.
    Input : The screen context (JSON or text description of the mobile UI).
    Output: "HIGH", "MEDIUM", or "LOW".
    HIGH  — warn the user immediately to stop.
    MEDIUM — advise caution.
    LOW    — no obvious fraud signals.
    """
    return assess_screen_risk(screen_context)
