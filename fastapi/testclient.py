"""Simple synchronous test client for the FastAPI stub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from . import FastAPI


@dataclass
class Response:
    status_code: int
    _json: Dict[str, Any]

    def json(self) -> Dict[str, Any]:
        return self._json


class TestClient:
    __test__ = False

    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def get(self, path: str) -> Response:
        data = self.app._call_route("GET", path)
        return Response(status_code=200, _json=data)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Response:
        data = self.app._call_route("POST", path, json=json or {})
        if isinstance(data, dict):
            body = data
        elif hasattr(data, "model_dump"):
            body = data.model_dump()
        else:
            body = data.__dict__
        return Response(status_code=200, _json=body)
