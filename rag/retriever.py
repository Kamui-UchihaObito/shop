"""A tiny self contained vector index used for tests and demos."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .schemas import Document, cosine_similarity, normalise_counter


@dataclass
class RetrievalResult:
    document: Document
    score: float


class VectorStore:
    """Loads a JSONL based store produced by :mod:`rag.ingest`."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._documents: List[Document] = []
        if path.exists():
            self._documents = [self._decode_line(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._documents)

    def _decode_line(self, line: str) -> Document:
        payload = json.loads(line)
        return Document(
            content=payload["content"],
            source=Path(payload["source"]),
            chunk_id=payload["chunk_id"],
            metadata=payload.get("metadata", {}),
            token_freq=payload.get("token_freq", {}),
        )

    def search(self, query: str, *, k: int = 4) -> List[RetrievalResult]:
        query_tokens = tokenise(query)
        normalised_query = normalise_counter(query_tokens)
        scored = [
            RetrievalResult(document=doc, score=cosine_similarity(normalised_query, doc.token_freq))
            for doc in self._documents
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:k]


def tokenise(text: str) -> Dict[str, int]:
    tokens = [token for token in text.lower().split() if token]
    return dict(Counter(tokens))
