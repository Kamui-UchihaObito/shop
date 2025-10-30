"""Summariser that aggregates the other VOC outputs."""
from __future__ import annotations

from typing import Dict, Iterable, List

from .aspect_mining import extract_aspects
from .keywords import extract_keywords
from .sentiment import analyse_sentiment


def summarise_reviews(reviews: Iterable[str]) -> Dict[str, object]:
    reviews = list(reviews)
    sentiments = analyse_sentiment(reviews)
    aspects = extract_aspects(reviews)
    keywords = extract_keywords(reviews)
    positive = [result.text for result in sentiments if result.sentiment == "positive"]
    negative = [result.text for result in sentiments if result.sentiment == "negative"]

    return {
        "total": len(reviews),
        "positive_examples": positive[:3],
        "negative_examples": negative[:3],
        "aspects": aspects,
        "keywords": keywords,
        "summary": _build_summary(len(reviews), aspects, keywords),
    }


def _build_summary(total: int, aspects: Dict[str, List[str]], keywords: List[str]) -> str:
    parts: List[str] = [f"共分析{total}条评论。"]
    if aspects:
        leading_aspect, texts = max(aspects.items(), key=lambda item: len(item[1]))
        parts.append(f"重点关注维度：{leading_aspect}（相关评论{len(texts)}条）。")
    if keywords:
        parts.append("高频关键词：" + "、".join(keywords[:3]) + "。")
    return "".join(parts)
