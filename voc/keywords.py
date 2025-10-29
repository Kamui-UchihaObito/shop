"""Keyword extraction using simple frequency analysis."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, List


def extract_keywords(texts: Iterable[str], top_k: int = 5) -> List[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        for token in text.split():
            if len(token) <= 1:
                continue
            counter[token] += 1
    return [token for token, _ in counter.most_common(top_k)]
