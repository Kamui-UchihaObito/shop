from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agent_endpoint_returns_answer(monkeypatch):
    # Ensure the index file exists with at least one document
    from rag.ingest import ingest
    from pathlib import Path

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    sample_file = docs_dir / "sample.md"
    if not sample_file.exists():
        sample_file.write_text("新人入职SOP：第一天完成账号申请。", encoding="utf-8")

    ingest(docs_dir, chunk_size=50, chunk_overlap=10, output=Path("rag/index.jsonl"))

    payload = {
        "query": "新人入职第一周需要完成哪些任务？",
        "reviews": ["客服服务很好", "物流有点慢"],
    }
    response = client.post("/v1/agent/ask", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "新人" in body["answer"]
    assert body["trace"]["intent"]
