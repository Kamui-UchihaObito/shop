"""Simple reranker that boosts documents containing the query keywords."""
from __future__ import annotations

from typing import Iterable, List

from .retriever import tokenise
from .schemas import Document


def rerank(query: str, documents: Iterable[Document]) -> List[Document]:
    query_tokens = set(tokenise(query).keys())
    scored = []
    for doc in documents:
        doc_tokens = set(tokenise(doc.content).keys())
        overlap = len(query_tokens & doc_tokens)
        scored.append((overlap, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored]
