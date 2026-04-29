"""
主程式入口
- 掛載 MCP Server（/mcp）
- 掛載 API Router（/api）
- 啟動時自動建立 RAG 向量庫（若尚未建立）
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.config.settings import get_settings
from src.api.router import api_router
from src.mcp.server import create_mcp_app


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ── startup ───────────────────────────────────────────
        await _init_rag(settings)
        yield
        # ── shutdown（可在此清理資源）─────────────────────────

    app = FastAPI(
        title="紫微斗數 Multi-Agent AI 系統",
        description="Graph-based multi-agent 命盤分析，含自訂 MCP + RAG + Web Search",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── 掛載子應用 ────────────────────────────────────────────
    mcp_app = create_mcp_app()
    app.mount("/mcp", mcp_app)

    app.include_router(api_router)

    # ── 基本路由 ──────────────────────────────────────────────
    @app.get("/")
    async def root():
        return {
            "system": "紫微斗數 Multi-Agent AI",
            "version": "2.0.0",
            "endpoints": {
                "api_docs": "/docs",
                "analyze": "/api/analyze",
                "status": "/api/status",
                "mcp_tools": "/mcp/tools",
            },
        }

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


async def _init_rag(settings) -> None:
    """啟動時確保 RAG 向量庫已建立"""
    import asyncio

    try:
        from src.rag.vector_store import ZiweiVectorStore
        from src.rag.indexer import RAGIndexer

        store = ZiweiVectorStore(
            persist_directory=settings.rag_vector_db_path,
            collection_name=settings.rag_collection_name,
            openai_api_key=settings.openai_api_key,
            embedding_model=settings.openai_embedding_model,
        )

        if store.is_empty():
            logger.info("Vector store is empty, starting indexing …")
            indexer = RAGIndexer(store)
            # 在 executor 中執行（indexer 是同步操作）
            loop = asyncio.get_event_loop()
            count = await loop.run_in_executor(
                None, indexer.index_from_json, settings.rag_data_path
            )
            logger.success(f"RAG indexing complete: {count} docs")
        else:
            logger.info(f"RAG ready: {store.count()} docs in vector store")

    except Exception as exc:
        logger.warning(f"RAG init failed (non-fatal): {exc}")


# ── 主程式 ────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    s = get_settings()
    logger.info(f"Starting server on {s.app_host}:{s.app_port}")
    uvicorn.run(
        "api_server:app",
        host=s.app_host,
        port=s.app_port,
        reload=s.app_debug,
        log_level=s.app_log_level.lower(),
    )
