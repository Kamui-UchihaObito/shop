"""FastAPI entrypoint that exposes the Ops Assistant agent."""
from __future__ import annotations

from fastapi import FastAPI

from agent import AgentConfig, OpsAssistantAgent

from .schemas import AgentRequest, AgentResponse

app = FastAPI(title="Ops Assistant Agent", version="0.1.0")
_agent = OpsAssistantAgent(AgentConfig())


@app.post("/v1/agent/ask", response_model=AgentResponse)
def ask_agent(payload: AgentRequest) -> AgentResponse:
    result = _agent.run(payload.query, reviews=payload.reviews, need_refs=payload.options.need_refs)
    return AgentResponse(**result)


@app.get("/healthz")
def healthcheck() -> dict:
    return {"status": "ok"}
