"""
tools/rag_tool.py
-----------------
RAG retriever tool — uses the module-level singleton from pipeline.py.
The embedding model and ChromaDB are loaded ONCE when the tool is first
called and cached for the entire process lifetime.
"""

from langchain_core.tools import tool
from rag.pipeline import get_rag_pipeline


@tool
def rag_retriever_tool(query: str) -> str:
    """
    Retrieve relevant knowledge from the local ChromaDB vector database.
    Input : A search query derived from the user's question and screen context.
    Output: Relevant knowledge chunks joined as text, OR "NO_CONTEXT" if
            no documents score above the similarity threshold.
    """
    try:
        retriever = get_rag_pipeline().get_retriever()
        docs = retriever.invoke(query)
        if not docs:
            return "NO_CONTEXT"
        return "\n\n---\n\n".join(doc.page_content for doc in docs)
    except Exception as exc:
        return f"NO_CONTEXT (retrieval error: {exc})"
