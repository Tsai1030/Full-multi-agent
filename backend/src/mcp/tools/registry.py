"""
MCP Tool Registry
統一管理所有 MCP 工具的註冊、查找與呼叫
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from .base import BaseMCPTool, ToolResult, ToolSchema


class ToolRegistry:
    """工具註冊表 - 單例模式"""

    def __init__(self) -> None:
        self._tools: dict[str, BaseMCPTool] = {}

    def register(self, tool: BaseMCPTool) -> None:
        self._tools[tool.name] = tool
        logger.debug(f"MCP tool registered: {tool.name}")

    def get(self, name: str) -> BaseMCPTool | None:
        return self._tools.get(name)

    def list_schemas(self) -> list[ToolSchema]:
        return [t.schema() for t in self._tools.values()]

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    async def call(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult.fail(name, f"Tool '{name}' not found")
        return await tool(**arguments)

    def __len__(self) -> int:
        return len(self._tools)
