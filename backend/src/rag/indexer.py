"""
RAG 資料索引器
將 zi_wei_dou_shu_rag_chunks.json 載入並寫入向量庫
"""

from __future__ import annotations

import json
from pathlib import Path

from loguru import logger

from .vector_store import ZiweiVectorStore


class RAGIndexer:
    """
    一次性將 JSON chunk 資料寫入 ChromaDB。
    若向量庫已有資料則跳過（冪等操作）。
    """

    def __init__(self, vector_store: ZiweiVectorStore) -> None:
        self._store = vector_store

    def index_from_json(self, json_path: str, force: bool = False) -> int:
        """
        載入 JSON 並索引所有 chunk。

        Args:
            json_path: zi_wei_dou_shu_rag_chunks.json 路徑
            force    : True 則強制重新索引（即使向量庫非空）

        Returns:
            實際新增的 chunk 數量
        """
        if not force and not self._store.is_empty():
            count = self._store.count()
            logger.info(f"Vector store already has {count} docs, skipping index.")
            return 0

        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"RAG data not found: {json_path}")

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        chunks: list[dict] = data.get("chunks", [])
        if not chunks:
            logger.warning("No chunks found in JSON file")
            return 0

        logger.info(f"Indexing {len(chunks)} chunks from {path.name} …")
        added = self._store.add_chunks(chunks)
        logger.info(f"Indexing complete: {added} docs added. Total: {self._store.count()}")
        return added
