"""Planner implementation for the ops assistant agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .router import RouteResult


@dataclass
class PlanStep:
    """Represents a single step in the execution plan."""

    action: str
    description: str


@dataclass
class Plan:
    """The planner output consumed by the orchestrator."""

    steps: List[PlanStep]
    expected_tools: List[str]


class Planner:
    """Convert router output into a deterministic execution plan."""

    _INTENT_TO_PLAN: Dict[str, List[PlanStep]] = {
        "SOP_ASK": [
            PlanStep(action="rag.search", description="召回与问题相关的SOP片段"),
            PlanStep(action="template.fill", description="若用户需要模板则填充骨架"),
        ],
        "DAILY_WORK": [
            PlanStep(action="kb.lookup", description="检索Owner、归口与历史记录"),
        ],
        "VOC_ANALYSIS": [
            PlanStep(action="voc.analyze", description="提取评论情感与方面"),
            PlanStep(action="voc.summarize", description="生成可执行洞察"),
        ],
        "DATA_QUERY": [
            PlanStep(action="sql.query", description="执行指标查询或返回口径说明"),
        ],
        "TEMPLATE_GENERATION": [
            PlanStep(action="template.fill", description="根据槽位填充内部模板"),
        ],
        "GENERAL_QA": [
            PlanStep(action="rag.search", description="执行兜底文档检索"),
        ],
    }

    def build_plan(self, route: RouteResult) -> Plan:
        """Return the execution plan based on router output."""

        steps = self._INTENT_TO_PLAN.get(route.intent, self._INTENT_TO_PLAN["GENERAL_QA"])
        tool_names = [step.action for step in steps]
        if route.slots.get("need_checklist"):
            steps = steps + [
                PlanStep(action="template.checklist", description="返回下一步操作清单"),
            ]
            tool_names.append("template.checklist")
        return Plan(steps=steps, expected_tools=tool_names)
