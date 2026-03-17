"""Hybrid + RRF + Rerank retriever for Insurance Specialist."""

import re
from pathlib import Path
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.core.config import OPENAI_API_KEY
from app.rag.rrf import rrf_merge

# Lazy imports for heavy deps
_faiss_store = None
_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder

            _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception:
            _reranker = None
    return _reranker


class InsuranceRetriever:
    """
    Three-stage retrieval: Hybrid (FAISS + BM25) → RRF → Rerank.
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        faiss_index_dir: Optional[Path] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k_dense: int = 100,
        top_k_bm25: int = 100,
        top_k_final: int = 10,
        rrf_k: int = 60,
    ):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data" / "insurance"
        self.faiss_index_dir = faiss_index_dir or Path(__file__).parent.parent / "data" / "faiss_insurance"
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k_dense = top_k_dense
        self.top_k_bm25 = top_k_bm25
        self.top_k_final = top_k_final
        self.rrf_k = rrf_k

        self._chunks: list[dict] = []
        self._bm25: Optional[BM25Okapi] = None
        self._faiss_store = None
        self._embeddings = None
        self._initialized = False

    def _simple_chunk(self, text: str, size: int, overlap: int) -> list[str]:
        """Simple chunking by size with overlap."""
        if len(text) <= size:
            return [text] if text.strip() else []
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            if end < len(text):
                last_space = chunk.rfind(" ")
                if last_space > size // 2:
                    end = start + last_space + 1
                    chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
        return chunks

    def _load_and_chunk(self) -> list[dict]:
        """Load markdown files and chunk."""
        chunks = []
        for path in sorted(self.data_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            parts = self._simple_chunk(text, self.chunk_size, self.chunk_overlap)
            for i, part in enumerate(parts):
                chunks.append({
                    "id": f"{path.stem}_{i}",
                    "text": part,
                    "source": path.name,
                })
        return chunks

    def _init(self):
        global _faiss_store
        if self._initialized:
            return
        self._chunks = self._load_and_chunk()
        if not self._chunks:
            self._initialized = True
            return

        # BM25
        tokenized = [c["text"].lower().split() for c in self._chunks]
        self._bm25 = BM25Okapi(tokenized)

        # FAISS (dense)
        try:
            if OPENAI_API_KEY:
                self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
                self.faiss_index_dir.mkdir(parents=True, exist_ok=True)
                index_path = self.faiss_index_dir / "index"
                if (index_path / "index.faiss").exists():
                    self._faiss_store = FAISS.load_local(
                        str(index_path),
                        self._embeddings,
                        allow_dangerous_deserialization=True,
                    )
                else:
                    docs = [
                        Document(page_content=c["text"], metadata={"id": c["id"], "source": c["source"]})
                        for c in self._chunks
                    ]
                    self._faiss_store = FAISS.from_documents(docs, self._embeddings)
                    self._faiss_store.save_local(str(index_path))
        except Exception:
            self._faiss_store = None
            self._embeddings = None

        self._initialized = True

    def retrieve(self, query: str) -> list[str]:
        """
        Retrieve top-k chunks for query using Hybrid + RRF + Rerank.
        Returns list of chunk texts (best first).
        """
        self._init()
        if not self._chunks:
            return []

        # Stage 1a: Dense search (FAISS)
        dense_ids: list[str] = []
        if self._faiss_store and self._embeddings:
            dense_docs = self._faiss_store.similarity_search(
                query,
                k=min(self.top_k_dense, len(self._chunks)),
            )
            dense_ids = [d.metadata.get("id", "") for d in dense_docs if d.metadata.get("id")]

        # Stage 1b: BM25 search
        tokenized_query = query.lower().split()
        bm25_scores = self._bm25.get_scores(tokenized_query)
        top_indices = sorted(
            range(len(bm25_scores)),
            key=lambda i: bm25_scores[i],
            reverse=True,
        )[: self.top_k_bm25]
        bm25_ids = [self._chunks[i]["id"] for i in top_indices]

        # Stage 2: RRF merge
        lists_to_merge = [lst for lst in [dense_ids, bm25_ids] if lst]
        if not lists_to_merge:
            return []
        merged_ids = rrf_merge(lists_to_merge, k=self.rrf_k)

        # Map ids back to texts
        id_to_text = {c["id"]: c["text"] for c in self._chunks}
        candidates = [(id_to_text.get(rid, ""), rid) for rid in merged_ids]
        candidates = [(t, rid) for t, rid in candidates if t]

        # Stage 3: Rerank
        reranker = _get_reranker()
        if reranker and len(candidates) > 1:
            pairs = [(query, t) for t, _ in candidates[: min(50, len(candidates))]]
            scores = reranker.predict(pairs)
            scored = list(zip(scores, candidates))
            scored.sort(key=lambda x: x[0], reverse=True)
            top = scored[: self.top_k_final]
            return [t for (_, (t, _)) in top]
        else:
            return [t for t, _ in candidates[: self.top_k_final]]

    def format_context(self, chunks: List[str], max_chars: int = 3000) -> str:
        """
        Clean and format retrieved chunks for LLM input.
        - Deduplicates exact duplicates
        - Skips very short fragments
        - Normalizes formatting, limits total length
        """
        if not chunks:
            return ""

        seen_norm: set[str] = set()
        unique: list[str] = []
        for c in chunks:
            t = c.strip()
            if len(t) < 25:
                continue
            norm = re.sub(r"\s+", " ", t.lower())
            if norm in seen_norm:
                continue
            seen_norm.add(norm)
            unique.append(t)

        cleaned = [
            re.sub(r"\n{3,}", "\n\n", re.sub(r"\s*---\s*", "\n\n", t).strip())
            for t in unique
            if t.strip()
        ]

        result: list[str] = []
        total = 0
        for c in cleaned:
            if total + len(c) > max_chars:
                break
            result.append(c)
            total += len(c)

        return "\n\n---\n\n".join(result) if result else ""
