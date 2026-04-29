"""
系統設定 - 單一 flat Settings 使用 pydantic-settings
所有環境變數直接對應，無巢狀 BaseSettings 問題
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Anthropic ──────────────────────────────────────────────
    anthropic_api_key: str = Field("", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-haiku-4-5-20251001", alias="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(4096, alias="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(0.7, alias="ANTHROPIC_TEMPERATURE")

    # ── OpenAI (embeddings) ────────────────────────────────────
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        "text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    # ── Tavily web search ──────────────────────────────────────
    tavily_api_key: str = Field("", alias="TAVILY_API_KEY")
    tavily_max_results: int = Field(5, alias="TAVILY_MAX_RESULTS")

    # ── RAG ────────────────────────────────────────────────────
    rag_data_path: str = Field(
        "C:/Users/226376/Desktop/Full-multi-agent/zi_wei_dou_shu_rag_chunks.json",
        alias="RAG_DATA_PATH",
    )
    rag_vector_db_path: str = Field(
        "./data/vector_db", alias="RAG_VECTOR_DB_PATH"
    )
    rag_collection_name: str = Field(
        "ziwei_knowledge", alias="RAG_COLLECTION_NAME"
    )
    rag_top_k: int = Field(5, alias="RAG_TOP_K")
    rag_min_score: float = Field(0.3, alias="RAG_MIN_SCORE")

    # ── MCP server ─────────────────────────────────────────────
    mcp_host: str = Field("localhost", alias="MCP_HOST")
    mcp_port: int = Field(8001, alias="MCP_PORT")
    ziwei_website_url: str = Field(
        "https://fate.windada.com/cgi-bin/fate", alias="ZIWEI_WEBSITE_URL"
    )
    mcp_request_timeout: int = Field(30, alias="MCP_REQUEST_TIMEOUT")

    # ── LangGraph ──────────────────────────────────────────────
    graph_max_iterations: int = Field(6, alias="GRAPH_MAX_ITERATIONS")
    graph_recursion_limit: int = Field(25, alias="GRAPH_RECURSION_LIMIT")

    # ── App ────────────────────────────────────────────────────
    app_host: str = Field("0.0.0.0", alias="APP_HOST")
    app_port: int = Field(8000, alias="APP_PORT")
    app_debug: bool = Field(False, alias="APP_DEBUG")
    app_log_level: str = Field("INFO", alias="APP_LOG_LEVEL")
    app_cors_origins: str = Field("*", alias="APP_CORS_ORIGINS")

    # ── helpers ────────────────────────────────────────────────
    @property
    def mcp_base_url(self) -> str:
        # MCP is mounted at /mcp under the main app (not a separate process)
        host = "localhost" if self.app_host == "0.0.0.0" else self.app_host
        return f"http://{host}:{self.app_port}/mcp"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.app_cors_origins.split(",")]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
