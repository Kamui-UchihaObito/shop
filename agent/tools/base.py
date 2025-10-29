"""Base classes for tool implementations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass
class ToolSpec:
    name: str
    description: str


class Tool(Protocol):
    spec: ToolSpec

    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        ...
