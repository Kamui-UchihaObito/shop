"""A tiny subset of the FastAPI interface used for tests.

This stub is **not** feature complete; it merely offers enough functionality to
exercise the agent pipeline within unit tests without depending on external
packages.  Only the symbols that are imported within this repository are
implemented.
"""
from __future__ import annotations

from dataclasses import dataclass
from inspect import Signature, signature
from typing import Any, Callable, Dict, Optional, Tuple, get_type_hints

RouteKey = Tuple[str, str]


@dataclass
class Route:
    method: str
    path: str
    endpoint: Callable[..., Any]


class FastAPI:
    def __init__(self, title: str, version: str) -> None:
        self.title = title
        self.version = version
        self._routes: Dict[RouteKey, Route] = {}

    def add_api_route(self, path: str, endpoint: Callable[..., Any], method: str) -> None:
        key = (method.upper(), path)
        self._routes[key] = Route(method=method.upper(), path=path, endpoint=endpoint)

    def post(self, path: str, response_model: Optional[type] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, "POST")
            return func

        return decorator

    def get(self, path: str, response_model: Optional[type] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, "GET")
            return func

        return decorator

    def _call_route(self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None) -> Any:
        key = (method.upper(), path)
        if key not in self._routes:
            raise KeyError(f"Route {method} {path} not registered")
        route = self._routes[key]
        endpoint = route.endpoint
        sig = signature(endpoint)
        call_kwargs: Dict[str, Any] = {}
        if json is not None:
            params = list(sig.parameters.values())
            if params:
                param = params[0]
                hints = get_type_hints(endpoint)
                annotation = hints.get(param.name, param.annotation)
                if annotation is not Signature.empty and isinstance(annotation, type):
                    payload = annotation(**json)
                else:
                    payload = json
                call_kwargs[param.name] = payload
        return endpoint(**call_kwargs)
