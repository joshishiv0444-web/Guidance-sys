"""
rag/seed_db.py
--------------
Run this ONCE to build the local ChromaDB vector database from the
knowledge-base documents in  rag/knowledge_base/.

Usage:
    cd "c:\\Users\\User\\Downloads\\Guidance sys"
    python rag/seed_db.py

The script will:
  1. Read every .txt file inside rag/knowledge_base/
  2. Split them into chunks
  3. Embed them with OpenAI Embeddings
  4. Persist the vectors to chroma_db/ (project root)
"""

import os
import sys

# Make sure the project root is on sys.path so config can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import CHROMA_PERSIST_DIRECTORY
from rag.pipeline import RAGPipeline


KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")


def main():
    if not os.path.isdir(KB_DIR):
        print(f"[ERROR] Knowledge-base directory not found: {KB_DIR}")
        print("Create 'rag/knowledge_base/' and add .txt files, then re-run.")
        sys.exit(1)

    txt_files = [f for f in os.listdir(KB_DIR) if f.endswith(".txt")]
    if not txt_files:
        print(f"[ERROR] No .txt files found in {KB_DIR}")
        sys.exit(1)

    print(f"[INFO] ChromaDB will be stored at: {CHROMA_PERSIST_DIRECTORY}")
    print(f"[INFO] Found {len(txt_files)} knowledge-base file(s): {txt_files}\n")

    pipeline = RAGPipeline()
    total_chunks = pipeline.seed_from_directory(KB_DIR, glob="**/*.txt")

    print(f"\n[SUCCESS] Seeded {total_chunks} chunks into ChromaDB.")
    print(f"          DB location: {CHROMA_PERSIST_DIRECTORY}")


if __name__ == "__main__":
    main()
