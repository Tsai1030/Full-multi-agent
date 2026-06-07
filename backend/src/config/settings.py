"""
系統設定 - 單一 flat Settings 使用 pydantic-settings
所有環境變數直接對應，無巢狀 BaseSettings 問題
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# repo 根目錄的 .env（無論從哪個 cwd 啟動都讀得到）。
# settings.py 位於 backend/src/config/settings.py → parents[3] = repo 根目錄。
_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # 先讀 repo 根目錄 .env，再讀 cwd 的 .env（若存在則覆寫，方便本地覆蓋）
        env_file=(str(_ROOT_ENV), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Google Gemini (LLM) ────────────────────────────────────
    google_api_key: str = Field("", alias="GOOGLE_API_KEY")
    gemini_model: str = Field("gemini-3.5-flash", alias="GEMINI_MODEL")
    gemini_max_tokens: int = Field(4096, alias="GEMINI_MAX_TOKENS")
    gemini_temperature: float = Field(0.7, alias="GEMINI_TEMPERATURE")

    # ── Embeddings ─────────────────────────────────────────────
    # provider: "gemini" (預設) | "openai"
    embedding_provider: str = Field("gemini", alias="EMBEDDING_PROVIDER")
    gemini_embedding_model: str = Field(
        "gemini-embedding-2", alias="GEMINI_EMBEDDING_MODEL"
    )

    # ── Anthropic (legacy, 已停用，保留向後相容) ───────────────
    anthropic_api_key: str = Field("", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-haiku-4-5-20251001", alias="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(4096, alias="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(0.7, alias="ANTHROPIC_TEMPERATURE")

    # ── OpenAI (embeddings, 備用) ──────────────────────────────
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        "text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    # ── Tavily web search ──────────────────────────────────────
    tavily_api_key: str = Field("", alias="TAVILY_API_KEY")
    tavily_max_results: int = Field(5, alias="TAVILY_MAX_RESULTS")

    # ── RAG ────────────────────────────────────────────────────
    rag_data_path: str = Field(
        "../zi_wei_dou_shu_rag_chunks.json",
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

    # ── Database (PostgreSQL) ──────────────────────────────────
    database_url: str = Field(
        "postgresql+asyncpg://ziwei:ziwei_dev_pw@localhost:5432/ziwei",
        alias="DATABASE_URL",
    )

    # ── Auth / JWT ─────────────────────────────────────────────
    jwt_secret_key: str = Field("change-me-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    cookie_secure: bool = Field(False, alias="COOKIE_SECURE")
    cookie_samesite: str = Field("lax", alias="COOKIE_SAMESITE")
    refresh_cookie_name: str = Field("ziwei_refresh", alias="REFRESH_COOKIE_NAME")

    # ── App ────────────────────────────────────────────────────
    app_host: str = Field("0.0.0.0", alias="APP_HOST")
    app_port: int = Field(8000, alias="APP_PORT")
    app_debug: bool = Field(False, alias="APP_DEBUG")
    app_log_level: str = Field("INFO", alias="APP_LOG_LEVEL")
    # cookie 認證需明確來源（不能用 "*"，瀏覽器會拒絕帶 credentials）
    app_cors_origins: str = Field("http://localhost:3000", alias="APP_CORS_ORIGINS")

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
