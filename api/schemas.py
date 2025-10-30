"""Pydantic schemas for the FastAPI service."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AgentOptions(BaseModel):
    need_refs: bool = Field(default=True, description="是否返回引用信息")


class AgentContext(BaseModel):
    user_role: Optional[str] = Field(default=None, description="调用者角色")
    language: str = Field(default="zh", description="目标语言")


class AgentRequest(BaseModel):
    query: str = Field(..., description="用户问题")
    context: AgentContext = Field(default_factory=AgentContext)
    options: AgentOptions = Field(default_factory=AgentOptions)
    reviews: List[str] = Field(default_factory=list, description="用于VOC分析的评论文本")


class AgentResponse(BaseModel):
    answer: str
    refs: Optional[List[dict]] = None
    trace: dict
