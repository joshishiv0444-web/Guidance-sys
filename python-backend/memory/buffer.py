"""
memory/buffer.py
-----------------
Conversation memory for the guidance agent.

Uses ConversationBufferMemory which stores:
  - Human message : the user's original query (clean, not the enriched router input)
  - AI message    : the agent's final response

IMPORTANT: The agent.invoke() receives the full enriched_input from the router,
but we override the input_key so that only the clean user query is stored in memory.
This keeps chat_history readable and concise across turns.

memory_key="chat_history" must match the {chat_history} placeholder in REACT_TEMPLATE.
"""

from langchain_classic.memory import ConversationBufferMemory


def get_memory() -> ConversationBufferMemory:
    return ConversationBufferMemory(
        memory_key="chat_history",     # matches {chat_history} in prompt
        input_key="input",             # saves only agent input, not full enriched blob
        output_key="output",           # saves agent's final answer
        return_messages=True,          # returns BaseMessage list (required for chat models)
    )
