"""Knowledge base lookup tool.

The tool is intentionally simple: it reuses the RAG store but exposes a
knowledge centric description so the planner can target it for operational
queries that expect structured metadata.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from rag.retriever import VectorStore

from .base import ToolSpec


class KnowledgeBaseLookupTool:
    spec = ToolSpec(
        name="kb.lookup",
        description="查询Owner/归口/历史记录等知识条目",
    )

    def __init__(self, index_path: Path | str | None = None) -> None:
        if index_path is None:
            self.index_path = Path("rag/index.jsonl")
        else:
            self.index_path = Path(index_path)

    def __call__(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        store = VectorStore(self.index_path)
        results = store.search(query, k=top_k)
        return {
            "entries": [
                {
                    "title": result.document.metadata.get("source_file", result.document.source.name),
                    "content": result.document.content,
                    "source": str(result.document.source),
                }
                for result in results
            ]
        }
