"""High level orchestrator tying router, planner and tools together."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .planner import Planner
from .router import IntentRouter
from .tools import (
    ChecklistTool,
    KnowledgeBaseLookupTool,
    RAGSearchTool,
    SQLQueryTool,
    TemplateFillTool,
    VOCAnalysisTool,
    VOCSummaryTool,
)


@dataclass
class AgentConfig:
    index_path: Path = Path("rag/index.jsonl")


@dataclass
class AgentTrace:
    intent: str
    confidence: float
    tools: List[str] = field(default_factory=list)


class OpsAssistantAgent:
    """Minimal agent orchestrator used by the FastAPI layer."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.router = IntentRouter()
        self.planner = Planner()
        self.rag_tool = RAGSearchTool(index_path=self.config.index_path)
        self.kb_tool = KnowledgeBaseLookupTool(index_path=self.config.index_path)
        self.voc_analyse = VOCAnalysisTool()
        self.voc_summary = VOCSummaryTool()
        self.template_tool = TemplateFillTool()
        self.checklist_tool = ChecklistTool()
        self.sql_tool = SQLQueryTool()

    def run(self, query: str, *, reviews: List[str] | None = None, need_refs: bool = True) -> Dict[str, Any]:
        route = self.router.route(query)
        plan = self.planner.build_plan(route)
        trace = AgentTrace(intent=route.intent, confidence=route.confidence)
        response: Dict[str, Any] = {
            "answer": self._synthesise_answer(query, plan.expected_tools, reviews=reviews or []),
            "trace": {
                "intent": trace.intent,
                "confidence": trace.confidence,
                "tools": plan.expected_tools,
            },
        }
        if need_refs and "rag.search" in plan.expected_tools:
            rag_output = self.rag_tool(query=query)
            response["refs"] = rag_output["documents"]
        return response

    def _synthesise_answer(self, query: str, tools: Iterable[str], *, reviews: List[str]) -> str:
        parts: List[str] = [f"问题：{query}"]
        for tool_name in tools:
            if tool_name == "rag.search":
                docs = self.rag_tool(query=query)["documents"]
                if docs:
                    parts.append("相关资料：")
                    for doc in docs[:2]:
                        parts.append(f"- {doc['source']}：{doc['content'][:80]}...")
            elif tool_name == "kb.lookup":
                entries = self.kb_tool(query=query)["entries"]
                if entries:
                    parts.append("知识库匹配：")
                    for entry in entries[:2]:
                        parts.append(f"- {entry['title']}：{entry['content'][:80]}...")
            elif tool_name == "voc.analyze":
                sentiments = self.voc_analyse(reviews=reviews)["sentiments"]
                counts = {
                    "positive": sum(1 for item in sentiments if item["sentiment"] == "positive"),
                    "negative": sum(1 for item in sentiments if item["sentiment"] == "negative"),
                }
                parts.append(f"情感分布：正向{counts['positive']}条，负向{counts['negative']}条。")
            elif tool_name == "voc.summarize":
                summary = self.voc_summary(reviews=reviews)
                parts.append(summary["summary"])
            elif tool_name == "template.fill":
                rendered = self.template_tool()["rendered"]
                parts.append("推荐模板：\n" + rendered)
            elif tool_name == "template.checklist":
                checklist = self.checklist_tool()["checklist"]
                parts.append("下一步行动：")
                parts.extend(f"- {item}" for item in checklist)
            elif tool_name == "sql.query":
                sql_result = self.sql_tool()
                rows = ", ".join(f"{row['metric']}={row['value']}" for row in sql_result["rows"])
                parts.append(f"示例查询：{sql_result['statement']} => {rows}")
        return "\n".join(parts)
