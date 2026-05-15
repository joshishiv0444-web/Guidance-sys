# Context-Aware AI Guidance Agent

This is a complete LangChain-based agent system for a mobile assistant. It understands screen context, processes user queries, retrieves relevant knowledge via RAG, detects fraud risks, and provides step-by-step guidance.

## Architecture
- **AgentExecutor**: Orchestrates the multi-tool workflow.
- **RAG Pipeline**: Retrieves context using ChromaDB and OpenAI Embeddings.
- **Tools**:
  - `rag_retriever_tool`: Performs similarity search on company docs.
  - `screen_analyzer_tool`: Parses raw UI into human-readable descriptions.
  - `fraud_detection_tool`: Simulates an external API for risk assessment.
  - `action_planner_tool`: Suggests next steps.

## Requirements
```bash
pip install -r requirements.txt
```

## Setup
Set your OpenAI API key in the environment before running:
```bash
export OPENAI_API_KEY="your-api-key"
```

## Usage
Run the sample application:
```bash
python main.py
```
