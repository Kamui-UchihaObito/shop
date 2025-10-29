"""SQL query tool stub."""
from __future__ import annotations

from typing import Any, Dict, Iterable

from .base import ToolSpec


class SQLQueryTool:
    spec = ToolSpec(
        name="sql.query",
        description="执行模拟的SQL查询并返回示例数据",
    )

    def __call__(self, statement: str | None = None, **_: Any) -> Dict[str, Any]:
        if not statement:
            statement = "SELECT metric, value FROM ops_metrics LIMIT 5"
        rows = [
            {"metric": "pv", "value": 12345},
            {"metric": "uv", "value": 6789},
            {"metric": "conversion_rate", "value": 0.032},
        ]
        return {
            "statement": statement,
            "rows": rows,
            "explain": "此处仅返回示例数据，真实环境应连接数据仓库。",
        }
