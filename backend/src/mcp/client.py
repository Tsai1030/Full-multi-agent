"""
MCP Client - 非同步 HTTP 客戶端
Agent graph 透過此 client 呼叫 MCP Server 上的工具
"""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from .tools.base import ToolResult, ToolSchema


class MCPClient:
    """
    輕量非同步 MCP HTTP 客戶端

    使用方式（需搭配 async context manager）：
        async with MCPClient(base_url) as client:
            result = await client.call("ziwei_chart", {...})
    """

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "MCPClient":
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── public API ────────────────────────────────────────────

    async def list_tools(self) -> list[ToolSchema]:
        data = await self._get("/tools")
        schemas = []
        for item in data.get("tools", []):
            schemas.append(ToolSchema(**item))
        return schemas

    async def call(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        payload = {"name": tool_name, "arguments": arguments}
        try:
            data = await self._post("/tools/call", payload)
            return ToolResult(
                tool_name=data["tool_name"],
                success=data["success"],
                data=data.get("data"),
                error=data.get("error"),
                elapsed_ms=data.get("elapsed_ms", 0.0),
            )
        except Exception as exc:
            logger.error(f"MCPClient.call({tool_name}) failed: {exc}")
            return ToolResult.fail(tool_name, str(exc))

    async def health(self) -> dict[str, Any]:
        return await self._get("/health")

    # ── private helpers ───────────────────────────────────────

    async def _get(self, path: str) -> dict[str, Any]:
        assert self._client, "Must be used inside async context manager"
        resp = await self._client.get(f"{self._base_url}{path}")
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        assert self._client, "Must be used inside async context manager"
        resp = await self._client.post(f"{self._base_url}{path}", json=body)
        resp.raise_for_status()
        return resp.json()
