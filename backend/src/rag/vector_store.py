"""
向量儲存層 - ChromaDB 實作
提供 add / search 介面，封裝底層 ChromaDB 細節
"""

from __future__ import annotations

import uuid
from typing import Any

import chromadb
from loguru import logger


class ZiweiVectorStore:
    """
    ChromaDB 向量儲存

    chunk document 結構：
        content  : str           - 原始文字（embedding_text 欄位）
        metadata : dict          - chunk_id, level, topic, keywords…

    embedding provider 由設定決定（預設 gemini），可切換 openai。
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        api_key: str | None = None,
        embedding_model: str | None = None,
        provider: str = "gemini",
        # 向後相容舊呼叫（openai_api_key=...）
        openai_api_key: str | None = None,
    ) -> None:
        self._collection_name = collection_name
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._ef = self._build_embedding_fn(
            provider=provider,
            api_key=api_key or openai_api_key or "",
            embedding_model=embedding_model,
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"VectorStore ready: '{collection_name}' "
            f"({self._collection.count()} docs)"
        )

    # ── embedding function ─────────────────────────────────────

    @staticmethod
    def _build_embedding_fn(
        provider: str, api_key: str, embedding_model: str | None
    ) -> Any:
        """依 provider 建立 chromadb 相容的 embedding function"""
        provider = (provider or "gemini").lower()

        if provider == "openai":
            from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

            return OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name=embedding_model or "text-embedding-3-small",
            )

        # 預設：Gemini embedding
        from .embeddings import GeminiEmbeddingProvider

        provider_obj = GeminiEmbeddingProvider(
            api_key=api_key,
            model=embedding_model or "gemini-embedding-2",
        )
        return provider_obj.as_chromadb_fn()

    # ── write ──────────────────────────────────────────────────

    def add_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """
        批量新增 chunk。
        chunk 需含 'embedding_text' 欄位作為內容，
        其餘欄位存入 metadata。
        """
        if not chunks:
            return 0

        ids, documents, metadatas = [], [], []
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id") or str(uuid.uuid4())
            text = chunk.get("embedding_text") or chunk.get("text", "")
            if not text:
                continue

            meta = {
                k: (", ".join(v) if isinstance(v, list) else str(v))
                for k, v in chunk.items()
                if k not in ("embedding_text", "text")
                and isinstance(v, (str, int, float, bool, list))
            }
            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(meta)

        if ids:
            # upsert 避免重複
            self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            logger.debug(f"Upserted {len(ids)} chunks into '{self._collection_name}'")

        return len(ids)

    # ── read ───────────────────────────────────────────────────

    def search(
        self, query: str, top_k: int = 5, min_score: float = 0.3
    ) -> list[dict[str, Any]]:
        """
        語意搜索，回傳最多 top_k 筆結果（cosine 距離 < 1-min_score）
        """
        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, max(self._collection.count(), 1)),
            include=["documents", "metadatas", "distances"],
        )

        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        dists = results["distances"][0] if results["distances"] else []

        output = []
        for doc, meta, dist in zip(docs, metas, dists):
            score = 1.0 - dist  # cosine similarity
            if score >= min_score:
                output.append(
                    {
                        "content": doc,
                        "metadata": meta,
                        "score": round(score, 4),
                    }
                )
        return output

    def count(self) -> int:
        return self._collection.count()

    def is_empty(self) -> bool:
        return self._collection.count() == 0
