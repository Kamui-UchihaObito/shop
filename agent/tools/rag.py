"""Lightweight RAG tool built on top of the local vector store."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from rag.retriever import VectorStore
from rag.reranker import rerank
from rag.schemas import Document

from .base import ToolSpec


class RAGSearchTool:
    spec = ToolSpec(
        name="rag.search",
        description="从本地索引检索与问题相关的文本片段",
    )

    def __init__(self, index_path: Path | str | None = None) -> None:
        if index_path is None:
            self.index_path = Path("rag/index.jsonl")
        else:
            self.index_path = Path(index_path)

    def __call__(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        store = VectorStore(self.index_path)
        results = store.search(query, k=top_k)
        documents = rerank(query, [result.document for result in results])
        return {
            "documents": [self._format_doc(doc) for doc in documents],
        }

    def _format_doc(self, doc: Document) -> Dict[str, Any]:
        return {
            "content": doc.content,
            "source": str(doc.source),
            "chunk_id": doc.chunk_id,
            "metadata": doc.metadata,
        }
