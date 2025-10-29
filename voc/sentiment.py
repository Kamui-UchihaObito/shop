"""Naive sentiment analyser tailored for deterministic tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

POSITIVE = {"好", "赞", "满意", "喜欢", "推荐"}
NEGATIVE = {"差", "慢", "不满", "吐槽", "bug", "差劲"}


@dataclass
class SentimentResult:
    text: str
    sentiment: str


def analyse_sentiment(texts: Iterable[str]) -> List[SentimentResult]:
    results: List[SentimentResult] = []
    for text in texts:
        score = 0
        for token in POSITIVE:
            if token in text:
                score += 1
        for token in NEGATIVE:
            if token in text:
                score -= 1
        if score > 0:
            sentiment = "positive"
        elif score < 0:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        results.append(SentimentResult(text=text, sentiment=sentiment))
    return results
