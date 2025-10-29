from pathlib import Path

from rag.ingest import ingest
from rag.retriever import VectorStore


def test_ingest_builds_index(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "guide.md").write_text("操作流程 A\n\n步骤1\n步骤2", encoding="utf-8")

    output = tmp_path / "index.jsonl"
    documents = ingest(docs_dir, chunk_size=10, chunk_overlap=2, output=output)

    assert output.exists()
    store = VectorStore(output)
    results = store.search("流程", k=1)
    assert results
    assert "流程" in results[0].document.content
