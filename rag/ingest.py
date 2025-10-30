"""Utility script to build the lightweight JSON index described in the README."""
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Iterator, List, Tuple

from .retriever import tokenise
from .schemas import Document, normalise_counter

DEFAULT_INDEX_PATH = Path("rag/index.jsonl")


def chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    segments: List[str] = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        segments.append(text[start:end])
        if end == length:
            break
        start = end - chunk_overlap
    return [segment.strip() for segment in segments if segment.strip()]


def iter_documents(source: Path) -> Iterator[Tuple[Path, str]]:
    for path in source.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            yield path, path.read_text(encoding="utf-8")


def ingest(source: Path, *, chunk_size: int, chunk_overlap: int, output: Path) -> List[Document]:
    documents: List[Document] = []
    for path, content in iter_documents(source):
        for idx, chunk in enumerate(chunk_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)):
            tokens = tokenise(chunk)
            documents.append(
                Document(
                    content=chunk,
                    source=path.relative_to(source),
                    chunk_id=f"{path.stem}-{idx}-{uuid.uuid4().hex[:8]}",
                    metadata={"source_file": path.name},
                    token_freq=normalise_counter(tokens),
                )
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for doc in documents:
            handle.write(
                json.dumps(
                    {
                        "content": doc.content,
                        "source": str(doc.source),
                        "chunk_id": doc.chunk_id,
                        "metadata": doc.metadata,
                        "token_freq": doc.token_freq,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    return documents


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Path containing documents to ingest")
    parser.add_argument("--db", type=str, default="chromadb", help="Placeholder for CLI compatibility")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--chunk-overlap", type=int, default=120)
    parser.add_argument("--output", type=Path, default=DEFAULT_INDEX_PATH)
    return parser


def main(argv: List[str] | None = None) -> None:
    args = build_argument_parser().parse_args(argv)
    ingest(args.source, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap, output=args.output)
    print(f"Indexed documents written to {args.output}")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
