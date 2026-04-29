"""
RAG Tool - 搜索紫微斗數知識庫
LangChain @tool 裝飾器，供 LangGraph ToolNode 使用
"""

from __future__ import annotations

from langchain_core.tools import tool
from loguru import logger


@tool
async def search_ziwei_knowledge(query: str) -> str:
    """
    搜索紫微斗數專業知識庫（RAG）。
    適合查詢星曜定義、宮位解釋、四化含義、命盤解讀規則等傳統命理知識。

    Args:
        query: 查詢關鍵字，例如「紫微星在命宮的意義」或「化祿的含義」

    Returns:
        相關紫微斗數知識段落
    """
    from ..config.settings import get_settings
    from ..rag.retriever import RAGRetriever
    from ..rag.vector_store import ZiweiVectorStore

    settings = get_settings()

    try:
        store = ZiweiVectorStore(
            persist_directory=settings.rag_vector_db_path,
            collection_name=settings.rag_collection_name,
            openai_api_key=settings.openai_api_key,
            embedding_model=settings.openai_embedding_model,
        )
        retriever = RAGRetriever(
            store,
            default_top_k=settings.rag_top_k,
            default_min_score=settings.rag_min_score,
        )
        context = retriever.search_and_format(query)
        logger.debug(f"RAG tool returned {len(context)} chars for query: {query[:40]}")
        return context

    except Exception as exc:
        logger.error(f"RAG tool error: {exc}")
        return f"知識庫查詢失敗：{exc}"
