"""
自訂 Python MCP Server
使用 FastAPI 實作 MCP HTTP 協定，完全取代舊版 Node.js ziwei-server.js

端點：
  GET  /mcp/tools          - 列出所有工具及其 schema
  POST /mcp/tools/call     - 呼叫指定工具
  GET  /mcp/health         - 健康檢查
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from .tools import ToolRegistry, ZiweiChartTool
from ..config.settings import get_settings


# ── Request / Response models ──────────────────────────────────


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


class ToolCallResponse(BaseModel):
    tool_name: str
    success: bool
    data: Any = None
    error: str | None = None
    elapsed_ms: float = 0.0


# ── MCP Server factory ────────────────────────────────────────


def create_mcp_app() -> FastAPI:
    """建立並回傳 MCP FastAPI 應用（可獨立啟動或掛載到主 app）"""

    settings = get_settings()
    registry = ToolRegistry()

    # ── 註冊所有工具 ──────────────────────────────────────────
    registry.register(
        ZiweiChartTool(
            base_url=settings.ziwei_website_url,
            timeout=settings.mcp_request_timeout,
        )
    )
    logger.info(f"MCP Server: {len(registry)} tools registered → {registry.list_names()}")

    # ── FastAPI app ──────────────────────────────────────────
    app = FastAPI(
        title="Ziwei MCP Server",
        description="自訂 Python MCP 工具伺服器",
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ───────────────────────────────────────────────

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "tools": registry.list_names()}

    @app.get("/tools")
    async def list_tools() -> dict[str, Any]:
        schemas = [s.model_dump() for s in registry.list_schemas()]
        return {"tools": schemas}

    @app.post("/tools/call", response_model=ToolCallResponse)
    async def call_tool(req: ToolCallRequest) -> ToolCallResponse:
        if req.name not in registry.list_names():
            raise HTTPException(
                status_code=404, detail=f"Tool '{req.name}' not found"
            )
        result = await registry.call(req.name, req.arguments)
        return ToolCallResponse(
            tool_name=result.tool_name,
            success=result.success,
            data=result.data,
            error=result.error,
            elapsed_ms=result.elapsed_ms,
        )

    return app


# ── 獨立啟動入口 ─────────────────────────────────────────────

mcp_app = create_mcp_app()

if __name__ == "__main__":
    import uvicorn
    from ..config.settings import get_settings

    s = get_settings()
    uvicorn.run(mcp_app, host=s.mcp_host, port=s.mcp_port)
