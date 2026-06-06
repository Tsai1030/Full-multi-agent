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


class _GeminiChromaEmbeddingFunction:
    """
    把 langchain GoogleGenerativeAIEmbeddings 包成 chromadb 相容的
    EmbeddingFunction。

    chromadb 不同版本會呼叫 __call__ / embed_documents / embed_query，
    這裡三者都實作，皆回傳 list[list[float]]（每筆輸入一個向量）。
    """

    def __init__(self, embeddings: Any, model_name: str) -> None:
        self._emb = embeddings
        self._model_name = model_name

    @staticmethod
    def _coerce(value: Any) -> list[str]:
        if isinstance(value, str):
            return [value]
        return [str(v) for v in value]

    def __call__(self, input: Any) -> list[list[float]]:  # noqa: A002
        return self._emb.embed_documents(self._coerce(input))

    def embed_documents(self, input: Any) -> list[list[float]]:  # noqa: A002
        return self._emb.embed_documents(self._coerce(input))

    def embed_query(self, input: Any) -> list[list[float]]:  # noqa: A002
        return self._emb.embed_documents(self._coerce(input))

    def name(self) -> str:
        # chromadb 用來識別 embedding function 的名稱
        return f"gemini:{self._model_name}"


class GeminiEmbeddingProvider(EmbeddingProvider):
    """
    使用 Google Gemini Embedding（透過 langchain-google-genai）。
    model 例：gemini-embedding-002 / gemini-embedding-001 / text-embedding-004
    """

    def __init__(self, api_key: str, model: str = "gemini-embedding-2") -> None:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        # langchain 要求 model 帶 "models/" 前綴
        self._model_name = model
        full_model = model if model.startswith("models/") else f"models/{model}"
        self._emb = GoogleGenerativeAIEmbeddings(
            model=full_model, google_api_key=api_key
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._emb.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._emb.embed_query(text)

    @property
    def dimension(self) -> int:
        # gemini-embedding-* 預設 3072；實際維度由向量決定，此值僅供參考
        return 3072

    def as_chromadb_fn(self) -> Any:
        return _GeminiChromaEmbeddingFunction(self._emb, self._model_name)
