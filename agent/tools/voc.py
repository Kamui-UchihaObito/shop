"""VOC analysis tools wrapping the modules in :mod:`voc`."""
from __future__ import annotations

from typing import Any, Dict, Iterable

from voc.sentiment import analyse_sentiment
from voc.summarizer import summarise_reviews

from .base import ToolSpec


class VOCAnalysisTool:
    spec = ToolSpec(
        name="voc.analyze",
        description="对评论进行情感与方面分析",
    )

    def __call__(self, reviews: Iterable[str]) -> Dict[str, Any]:
        results = analyse_sentiment(reviews)
        return {
            "sentiments": [
                {
                    "text": result.text,
                    "sentiment": result.sentiment,
                }
                for result in results
            ]
        }


class VOCSummaryTool:
    spec = ToolSpec(
        name="voc.summarize",
        description="汇总VOC结果并输出洞察",
    )

    def __call__(self, reviews: Iterable[str]) -> Dict[str, Any]:
        return summarise_reviews(reviews)
