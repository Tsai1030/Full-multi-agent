"""
Embedding Provider 抽象層
支援 OpenAI / HuggingFace，可透過設定切換
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):
    """Embedding 抽象介面"""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量對文件做 embedding"""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """對查詢做 embedding"""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """向量維度"""


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    使用 OpenAI text-embedding-3-small（預設）
    chromadb 的 OpenAIEmbeddingFunction 包裝
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

        self._fn = OpenAIEmbeddingFunction(api_key=api_key, model_name=model)
        self._model = model
        # 3-small = 1536, 3-large = 3072, ada-002 = 1536
        self._dim = 1536 if "small" in model or "ada" in model else 3072

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._fn(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._fn([text])[0]

    @property
    def dimension(self) -> int:
        return self._dim

    def as_chromadb_fn(self) -> Any:
        """回傳 chromadb 相容的 embedding function"""
        return self._fn
