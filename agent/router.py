"""Intent routing logic for the ops assistant agent.

The router implements a light-weight keyword and rule based detector. In a
production system this would be replaced with a classifier or a model call, but
for the purposes of this repository we aim to keep dependencies light weight and
transparent so that unit tests can exercise the whole stack without access to
external services.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class RouteResult:
    """Represents the router output.

    Attributes
    ----------
    intent:
        The detected top level intent.
    confidence:
        A float in the ``[0, 1]`` range that expresses how confident the router
        is in the returned intent.
    slots:
        Additional structured hints extracted from the query.  Only a few
        coarse-grained slots are supported in this demo implementation, but the
        structure mirrors what the README describes so the downstream planner is
        able to consume richer data in the future.
    """

    intent: str
    confidence: float
    slots: Dict[str, str]


class IntentRouter:
    """Routes an incoming query to a coarse intent label.

    The implementation relies on a handful of curated keyword groups.  The
    groups emulate the behaviour of a multi label classifier by scoring each
    candidate and selecting the highest ranking one.
    """

    _INTENT_KEYWORDS: Dict[str, Tuple[List[str], float]] = {
        "SOP_ASK": (["sop", "流程", "制度", "模板", "案例"], 0.8),
        "DAILY_WORK": (["owner", "归口", "负责人", "历史记录", "日报", "周报"], 0.7),
        "VOC_ANALYSIS": (["评论", "情感", "差评", "好评", "亮点", "痛点", "口碑"], 0.75),
        "DATA_QUERY": (["数据", "指标", "sql", "报表", "转化率"], 0.6),
        "TEMPLATE_GENERATION": (["模板", "填充", "生成", "通知", "复盘"], 0.65),
    }

    def route(self, query: str) -> RouteResult:
        """Return the most likely intent for ``query``.

        Parameters
        ----------
        query:
            Free form user question.
        """

        lowered = query.lower()
        best_intent = "GENERAL_QA"
        best_score = 0.3
        for intent, (keywords, base_confidence) in self._INTENT_KEYWORDS.items():
            match_count = sum(1 for kw in keywords if kw in lowered)
            if match_count == 0:
                continue
            score = base_confidence + 0.05 * match_count
            if score > best_score:
                best_intent = intent
                best_score = min(score, 0.99)

        slots: Dict[str, str] = {}
        if "模板" in query:
            slots["need_template"] = "true"
        if "下一步" in query or "怎么做" in query:
            slots["need_checklist"] = "true"

        return RouteResult(intent=best_intent, confidence=best_score, slots=slots)
