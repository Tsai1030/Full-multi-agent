"""
RAG Retriever
封裝搜索邏輯，提供格式化結果給 agent tools 使用
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from .vector_store import ZiweiVectorStore


class RAGRetriever:
    """
    RAG 檢索器

    負責：
    1. 接受自然語言查詢
    2. 搜索向量庫
    3. 格式化並回傳結果
    """

    def __init__(
        self,
        vector_store: ZiweiVectorStore,
        default_top_k: int = 5,
        default_min_score: float = 0.3,
    ) -> None:
        self._store = vector_store
        self._default_top_k = default_top_k
        self._default_min_score = default_min_score

    def search(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        搜索紫微斗數知識庫

        Returns:
            list of { content, metadata, score }
        """
        top_k = top_k or self._default_top_k
        min_score = min_score or self._default_min_score

        results = self._store.search(query, top_k=top_k, min_score=min_score)
        logger.debug(f"RAG query='{query[:50]}…' → {len(results)} results")
        return results

    def format_context(self, results: list[dict[str, Any]]) -> str:
        """將搜索結果格式化為 LLM 可讀的上下文字串"""
        if not results:
            return "（找不到相關紫微斗數知識）"

        parts = ["## 紫微斗數相關知識\n"]
        for i, r in enumerate(results, 1):
            meta = r.get("metadata", {})
            title = meta.get("title", "")
            breadcrumb = meta.get("breadcrumb", "")
            score = r.get("score", 0)
            parts.append(
                f"### {i}. {title} （相關度 {score:.2f}）\n"
                f"路徑：{breadcrumb}\n\n"
                f"{r['content']}\n"
            )
        return "\n".join(parts)

    def search_and_format(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> str:
        results = self.search(query, top_k=top_k, min_score=min_score)
        return self.format_context(results)
