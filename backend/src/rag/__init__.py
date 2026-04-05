"""
RAG (Retrieval-Augmented Generation) 系統
使用 BGE-M3 嵌入模型和 GPT-4o 輸出模型
"""

from .rag_system import ZiweiRAGSystem, create_rag_system, quick_setup
from .vector_store import ZiweiVectorStore
from .bge_embeddings import BGEM3Embeddings, HybridEmbeddings
from .gpt4o_generator import GPT4oGenerator, RAGResponseGenerator

__all__ = [
    "ZiweiRAGSystem",
    "create_rag_system",
    "quick_setup",
    "ZiweiVectorStore",
    "BGEM3Embeddings",
    "HybridEmbeddings",
    "GPT4oGenerator",
    "RAGResponseGenerator"
]

__version__ = "1.0.0"
