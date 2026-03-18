#!/usr/bin/env python3
"""
Pre-build FAISS index for Insurance RAG at startup.
Runs after load_insurance_qa. Requires OPENAI_API_KEY.
"""

import os
import sys
from pathlib import Path

# Ensure app is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Optional: override data paths for Docker
DATA_DIR = Path(os.environ.get("INSURANCE_DATA_DIR", Path(__file__).parent.parent / "app" / "data" / "insurance"))
FAISS_DIR = Path(os.environ.get("FAISS_INDEX_DIR", Path(__file__).parent.parent / "app" / "data" / "faiss_insurance"))


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set — skipping FAISS pre-build")
        return 0

    if not list(DATA_DIR.glob("*.md")):
        print("No .md files in insurance data dir — skipping FAISS pre-build")
        return 0

    if (FAISS_DIR / "index" / "index.faiss").exists():
        print("FAISS index already exists — skipping pre-build")
        return 0

    print("Pre-building FAISS index for Insurance RAG...")
    try:
        from app.rag.retriever import InsuranceRetriever

        retriever = InsuranceRetriever(data_dir=DATA_DIR, faiss_index_dir=FAISS_DIR)
        retriever.retrieve("prebuild")  # Triggers _init(), builds and saves index
        print("FAISS index built successfully")
    except Exception as e:
        print(f"FAISS pre-build failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
