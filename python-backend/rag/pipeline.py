"""
rag/pipeline.py
---------------
RAG pipeline — OPTIMIZED:
  - Singleton embedding model (loaded ONCE, reused forever)
  - Singleton ChromaDB client (no repeated disk reads)
  - Startup pre-warm supported via get_rag_pipeline()
"""

import os
import json
from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import (
    CHROMA_PERSIST_DIRECTORY,
    RAG_SIMILARITY_THRESHOLD,
    EMBEDDING_MODEL,
)


class RAGPipeline:
    """
    Singleton-safe RAG pipeline.
    Both the embedding model and the ChromaDB vectorstore are created
    once and reused for all subsequent queries in the same process.
    """
    def __init__(self):
        print(f"[RAG] Loading embedding model: {EMBEDDING_MODEL} (one-time)")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        # Pre-load the vectorstore immediately so first query doesn't pay the cost
        print(f"[RAG] Pre-loading ChromaDB from: {CHROMA_PERSIST_DIRECTORY}")
        self.vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=self.embeddings,
        )
        print("[RAG] Ready.")

    def get_retriever(self):
        return self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": RAG_SIMILARITY_THRESHOLD,
                "k": 3,
            },
        )

    # ── Seeding (called from rag/seed_db.py, run once) ─────────────────────

    def _load_txt_files(self, dir_path: str) -> list:
        loader = DirectoryLoader(
            dir_path, glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        return loader.load()

    def _load_pdf_files(self, dir_path: str) -> list:
        docs = []
        for pdf_path in Path(dir_path).rglob("*.pdf"):
            try:
                docs.extend(PyPDFLoader(str(pdf_path)).load())
                print(f"[RAG] Loaded PDF: {pdf_path.name}")
            except Exception as e:
                print(f"[RAG] WARNING: {pdf_path.name}: {e}")
        return docs

    def _load_json_files(self, dir_path: str) -> list:
        docs = []
        for json_path in Path(dir_path).rglob("*.json"):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                items = data if isinstance(data, list) else [data]
                for i, item in enumerate(items):
                    docs.append(Document(
                        page_content=json.dumps(item, ensure_ascii=False, indent=2),
                        metadata={"source": str(json_path), "index": i}
                    ))
                print(f"[RAG] Loaded JSON: {json_path.name}")
            except Exception as e:
                print(f"[RAG] WARNING: {json_path.name}: {e}")
        return docs

    def seed_from_directory(self, dir_path: str) -> int:
        all_docs = (
            self._load_txt_files(dir_path)
            + self._load_pdf_files(dir_path)
            + self._load_json_files(dir_path)
        )
        if not all_docs:
            raise ValueError(f"No documents found in {dir_path}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400, chunk_overlap=60,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(all_docs)

        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIRECTORY,
        )
        print(f"[RAG] Seeded {len(chunks)} chunks → {CHROMA_PERSIST_DIRECTORY}")
        return len(chunks)


# ── Module-level singleton ────────────────────────────────────────────────────
_INSTANCE: RAGPipeline | None = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Return the module-level singleton RAGPipeline.
    First call loads the embedding model + ChromaDB (takes ~5s).
    Every subsequent call returns the cached instance instantly.
    """
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = RAGPipeline()
    return _INSTANCE
