"""
server.py
---------
FastAPI server for the Context-Aware AI Guidance Agent.
Accepts JSON inputs (user query, screen context, risk level) and returns guidance.
Maintains session state via session_id.
"""

import os
import sys
from typing import Dict, Any, Optional, List
import socket

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import create_guidance_agent, GuidanceAgent
from agent.router import route
from utils.text_cleaner import clean_for_voice, add_hedging_if_needed
from langchain_core.documents import Document
from rag.pipeline import get_rag_pipeline

app = FastAPI(
    title="Guidance Agent API",
    description="API for the Context-Aware AI Guidance Agent",
    version="1.0.0"
)

# ---------------------------------------------------------------------------
# Global state for sessions
# ---------------------------------------------------------------------------
# In a real production app, this would be a database (e.g., Redis).
# For now, we store sessions in memory.
sessions: Dict[str, GuidanceAgent] = {}

# ---------------------------------------------------------------------------
# Pydantic Models for Input/Output
# ---------------------------------------------------------------------------
class GuidanceRequest(BaseModel):
    session_id: str = Field(..., description="Unique ID for the user session to maintain memory")
    user_query: str = Field(..., description="Text query from the user")
    screen_context: Any = Field(..., description="JSON object or string describing the current screen")
    risk_level: str = Field(default="LOW", description="LOW, MEDIUM, or HIGH risk from fraud system")

class GuidanceResponse(BaseModel):
    output: str = Field(..., description="Final text guidance to show to the user")
    voice_output: str = Field(..., description="Cleaned version of the output suitable for TTS")
    hard_stop: bool = Field(..., description="True if a critical fraud risk was detected")
    fraud_risk: str = Field(..., description="Fraud risk assessed by the screen model")
    rag_used: bool = Field(..., description="True if knowledge base context was used")


class KnowledgeItem(BaseModel):
    content: str = Field(..., description="Raw text/content to add to the knowledge base")
    metadata: Optional[dict] = Field(None, description="Optional metadata for the document")


class KnowledgeRequest(BaseModel):
    items: List[KnowledgeItem] = Field(..., description="List of knowledge documents to add")


class URLRequest(BaseModel):
    url: str = Field(..., description="URL string to check reputation for")


class ScamRequest(BaseModel):
    screen_context: Any = Field(..., description="Screen context string or JSON to run scam model on")

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/v1/guidance", response_model=GuidanceResponse)
async def get_guidance(req: GuidanceRequest = Body(...)):
    """
    Process a user query along with screen context to provide guidance.
    Maintains conversation history based on session_id.
    """
    try:
        # 1. Get or create session agent
        if req.session_id not in sessions:
            print(f"[Server] Creating new session: {req.session_id}")
            sessions[req.session_id] = create_guidance_agent()
        
        agent = sessions[req.session_id]

        # 2. Convert screen context to string if it's a dict/json
        screen_ctx_str = req.screen_context
        if isinstance(screen_ctx_str, dict):
            import json
            screen_ctx_str = json.dumps(screen_ctx_str)

        # 3. Explicit routing (Python logic, no LLM)
        print(f"[Server] Processing query for session {req.session_id}")
        routing = route(req.user_query, screen_ctx_str, req.risk_level)

        # 4. Hard-stop for HIGH risk (no LLM call)
        if routing["hard_stop"]:
            return GuidanceResponse(
                output=routing["hard_stop_msg"],
                voice_output=routing["hard_stop_msg"],
                hard_stop=True,
                fraud_risk=routing["fraud_risk"],
                rag_used=False
            )

        # 5. Agent call — tiered model selected automatically based on rag_used
        response = agent.invoke(
            enriched_input=routing["enriched_input"],
            rag_used=routing["rag_used"],
        )
        raw_output = response.get("output", str(response))

        # 6. Post-processing
        hedged_output = add_hedging_if_needed(raw_output, routing["rag_used"])
        voice_output  = clean_for_voice(hedged_output)

        return GuidanceResponse(
            output=hedged_output,
            voice_output=voice_output,
            hard_stop=False,
            fraud_risk=routing["fraud_risk"],
            rag_used=routing["rag_used"]
        )

    except Exception as e:
        print(f"[Server Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    Clear the memory for a specific session.
    """
    if session_id in sessions:
        sessions[session_id].clear_memory()
        return {"status": "success", "message": f"Memory cleared for session {session_id}"}
    return {"status": "not_found", "message": "Session not found"}


@app.post("/api/v1/fraud/url")
async def check_url(req: URLRequest = Body(...)):
    """Run URL-only reputation lookup (VirusTotal if API key configured).

    Returns simple JSON: `{url, url_reputation}`.
    """
    try:
        from tools.fraud_model_interface import _get_url_reputation

        rep = _get_url_reputation(req.url)
        return {"url": req.url, "url_reputation": rep}
    except Exception as e:
        print(f"[Server Error] check_url: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/fraud/scam")
async def check_scam(req: ScamRequest = Body(...)):
    """Run the scam detection model alone and return probability/label.

    If a HF model is present this returns `model_prob`, `label`, and `risk_level`.
    Otherwise falls back to heuristics via `assess_screen_risk`.
    """
    try:
        from tools.fraud_model_interface import _model_predict_prob, analyze_screen_text, assess_screen_risk

        screen_ctx = req.screen_context
        if isinstance(screen_ctx, dict):
            import json
            screen_ctx = json.dumps(screen_ctx)

        prob = _model_predict_prob(screen_ctx)
        if prob is None:
            # No model: use existing analysis/fallback
            analysis = analyze_screen_text(screen_ctx)
            # analyze_screen_text may return Nones if model missing; also derive risk via heuristics
            risk = analysis.get("risk_level") or assess_screen_risk(screen_ctx)
            return {"model_prob": analysis.get("confidence"), "label": analysis.get("label"), "risk_level": risk}

        label = "scam" if prob >= 0.5 else "legit"
        if prob >= 0.75:
            risk = "HIGH"
        elif prob >= 0.40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {"model_prob": prob, "label": label, "risk_level": risk}
    except Exception as e:
        print(f"[Server Error] check_scam: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/knowledge")
async def add_knowledge(req: KnowledgeRequest = Body(...)):
    """
    Add new documents to the RAG vector database (Chroma).

    Accepts a JSON body with `items: [{content, metadata}]` and adds them
    into the existing Chroma vectorstore used by the RAG pipeline.
    """
    try:
        pipeline = get_rag_pipeline()
        docs = [Document(page_content=item.content, metadata=item.metadata or {}) for item in req.items]

        # Add documents to vectorstore using supported API
        vs = pipeline.vectorstore
        if hasattr(vs, "add_documents"):
            vs.add_documents(docs)
        elif hasattr(vs, "add_texts"):
            texts = [d.page_content for d in docs]
            metadatas = [d.metadata for d in docs]
            vs.add_texts(texts=texts, metadatas=metadatas)
        else:
            raise RuntimeError("Vectorstore does not support programmatic ingestion in this runtime")

        # Persist to disk if supported
        if hasattr(vs, "persist"):
            try:
                vs.persist()
            except Exception:
                # Not fatal — ingestion may still be in-memory
                print("[Server] Warning: vectorstore.persist() failed or is unsupported")

        return {"status": "success", "added": len(docs)}

    except Exception as e:
        print(f"[Server Error] add_knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "active_sessions": len(sessions)}


if __name__ == "__main__":
    # Pre-warm the RAG pipeline before starting the server so the first request is fast
    print("Pre-warming RAG pipeline before server start...")
    try:
        from rag.pipeline import get_rag_pipeline
        # Only attempt to pre-warm if chroma/embeddings are available
        get_rag_pipeline()
    except Exception as e:
        print(f"[Server] RAG pre-warm skipped: {e}")

    # Render (and many PaaS) expect the process to bind to the PORT env var.
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"\nStarting FastAPI server on http://{host}:{port}")
    # Do not enable auto-reload in production containers
    # Check whether the port is available to fail fast with a clear message
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except OSError as e:
            print(f"[Server Error] Port {port} is already in use: {e}")
            sys.exit(1)

    uvicorn.run("server:app", host=host, port=port)
