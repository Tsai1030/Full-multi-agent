"""
MCP Tool 抽象基類
所有自訂 MCP 工具都繼承此類別
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel


class ToolSchema(BaseModel):
    """工具的 JSON Schema 描述"""
    name: str
    description: str
    input_schema: dict[str, Any]


class ToolResult(BaseModel):
    """工具執行結果"""
    tool_name: str
    success: bool
    data: Any = None
    error: str | None = None
    elapsed_ms: float = 0.0

    @classmethod
    def ok(cls, tool_name: str, data: Any, elapsed_ms: float = 0.0) -> "ToolResult":
        return cls(tool_name=tool_name, success=True, data=data, elapsed_ms=elapsed_ms)

    @classmethod
    def fail(cls, tool_name: str, error: str, elapsed_ms: float = 0.0) -> "ToolResult":
        return cls(
            tool_name=tool_name, success=False, error=error, elapsed_ms=elapsed_ms
        )


class BaseMCPTool(ABC):
    """
    MCP Tool 抽象基類

    子類只需實作：
    - name: ClassVar[str]
    - description: ClassVar[str]
    - input_schema: ClassVar[dict]
    - _execute(self, **kwargs) -> Any
    """

    name: ClassVar[str]
    description: ClassVar[str]
    input_schema: ClassVar[dict[str, Any]]

    async def __call__(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()
        try:
            data = await self._execute(**kwargs)
            elapsed = (time.perf_counter() - t0) * 1000
            return ToolResult.ok(self.name, data, elapsed)
        except Exception as exc:  # noqa: BLE001
            elapsed = (time.perf_counter() - t0) * 1000
            return ToolResult.fail(self.name, str(exc), elapsed)

    @abstractmethod
    async def _execute(self, **kwargs: Any) -> Any:
        """實際執行邏輯，子類覆寫"""

    def schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
        )
