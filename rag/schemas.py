"""Data structures used across the RAG components."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass
class Document:
    """Represents a chunk of text stored in the lightweight index."""

    content: str
    source: Path
    chunk_id: str
    metadata: Dict[str, str]
    token_freq: Dict[str, float]


def normalise_counter(counter: Dict[str, int]) -> Dict[str, float]:
    total = sum(counter.values())
    if total == 0:
        return {k: 0.0 for k in counter}
    return {k: v / total for k, v in counter.items()}


def cosine_similarity(query: Dict[str, float], document: Dict[str, float]) -> float:
    score = 0.0
    for token, weight in query.items():
        score += weight * document.get(token, 0.0)
    return score


def merge_metadata(rows: Iterable[Dict[str, str]]) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    for row in rows:
        merged.update(row)
    return merged
