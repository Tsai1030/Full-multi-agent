"""
完整的 RAG 系統實現
整合 BGE-M3 嵌入模型和 GPT-4o 輸出模型
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from .vector_store import ZiweiVectorStore
from .gpt4o_generator import GPT4oGenerator, RAGResponseGenerator
from .bge_embeddings import BGEM3Embeddings, HybridEmbeddings

# 載入環境變數
load_dotenv()


class ZiweiRAGSystem:
    """紫微斗數 RAG 系統"""
    
    def __init__(self, config: Dict[str, Any] = None, logger=None):
        """
        初始化 RAG 系統
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.config = config or self._load_default_config()
        self.logger = logger or self._setup_logger()
        
        # 初始化組件
        self.vector_store = None
        self.generator = None
        self.rag_generator = None
        
        # 初始化系統
        self._initialize_system()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """載入默認配置"""
        return {
            # 向量存儲配置
            "vector_store": {
                "persist_directory": os.getenv("VECTOR_DB_PATH", "./data/vector_db"),
                "collection_name": os.getenv("VECTOR_DB_COLLECTION", "ziwei_knowledge"),
                "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "huggingface"),
                "embedding_model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
                "embedding_config": {
                    "device": os.getenv("EMBEDDING_DEVICE", "cpu"),
                    "max_length": int(os.getenv("EMBEDDING_MAX_LENGTH", "8192")),
                    "batch_size": int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
                    "use_fp16": os.getenv("EMBEDDING_USE_FP16", "false").lower() == "true",
                    "openai_fallback": True,
                    "openai_model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
                }
            },
            
            # GPT-4o 生成器配置
            "generator": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "model": os.getenv("OPENAI_MODEL_GPT4O", "gpt-4o-mini"),
                "temperature": float(os.getenv("GPT4O_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("GPT4O_MAX_TOKENS", "2000"))
            },
            
            # RAG 配置
            "rag": {
                "top_k": int(os.getenv("RAG_TOP_K", "5")),
                "min_score": float(os.getenv("RAG_MIN_SCORE", "0.7")),
                "enable_reranking": os.getenv("RAG_ENABLE_RERANKING", "false").lower() == "true"
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger("ZiweiRAG")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_system(self):
        """初始化系統組件"""
        try:
            # 初始化向量存儲
            self.logger.info("Initializing vector store...")
            self.vector_store = ZiweiVectorStore(
                **self.config["vector_store"],
                logger=self.logger
            )
            
            # 初始化 GPT-4o 生成器
            self.logger.info("Initializing GPT-4o generator...")
            self.generator = GPT4oGenerator(
                **self.config["generator"],
                logger=self.logger
            )
            
            # 初始化 RAG 生成器
            self.logger.info("Initializing RAG generator...")
            self.rag_generator = RAGResponseGenerator(
                vector_store=self.vector_store,
                generator=self.generator,
                logger=self.logger
            )
            
            self.logger.info("RAG system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing RAG system: {str(e)}")
            raise
    
    def add_knowledge(self, documents: List[Dict[str, Any]]) -> bool:
        """
        添加知識到向量庫
        
        Args:
            documents: 文檔列表，每個文檔包含 content 和 metadata
            
        Returns:
            是否成功添加
        """
        try:
            from langchain.schema import Document
            
            # 轉換為 Document 對象
            doc_objects = []
            for doc in documents:
                doc_obj = Document(
                    page_content=doc["content"],
                    metadata=doc.get("metadata", {})
                )
                doc_objects.append(doc_obj)
            
            # 添加到向量存儲
            doc_ids = self.vector_store.add_documents(doc_objects)
            
            self.logger.info(f"Added {len(doc_ids)} documents to knowledge base")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding knowledge: {str(e)}")
            return False
    
    def load_knowledge_from_directory(self, directory_path: str) -> int:
        """
        從目錄載入知識
        
        Args:
            directory_path: 目錄路徑
            
        Returns:
            載入的文檔數量
        """
        try:
            from .vector_store import ZiweiRAGSystem as LegacyRAG
            legacy_rag = LegacyRAG(self.vector_store, self.logger)
            return legacy_rag.load_documents_from_directory(directory_path)
            
        except Exception as e:
            self.logger.error(f"Error loading knowledge from directory: {str(e)}")
            return 0
    
    def search_knowledge(self, 
                        query: str, 
                        top_k: int = None,
                        min_score: float = None) -> List[Dict[str, Any]]:
        """
        搜索知識庫
        
        Args:
            query: 查詢字符串
            top_k: 返回結果數量
            min_score: 最小相似度分數
            
        Returns:
            搜索結果列表
        """
        top_k = top_k or self.config["rag"]["top_k"]
        min_score = min_score or self.config["rag"]["min_score"]
        
        results = self.vector_store.search(query, top_k)
        
        # 過濾低分結果
        filtered_results = [
            result for result in results 
            if result["score"] >= min_score
        ]
        
        return filtered_results
    
    def generate_answer(self, 
                       query: str,
                       context_type: str = "auto",
                       **kwargs) -> Dict[str, Any]:
        """
        生成回答
        
        Args:
            query: 用戶查詢
            context_type: 上下文類型 (auto, manual, none)
            **kwargs: 其他參數
            
        Returns:
            生成的回答
        """
        try:
            if context_type == "auto":
                # 自動檢索上下文
                return self.rag_generator.generate_rag_response(
                    query=query,
                    top_k=kwargs.get("top_k", self.config["rag"]["top_k"]),
                    min_score=kwargs.get("min_score", self.config["rag"]["min_score"]),
                    **kwargs
                )
            
            elif context_type == "manual":
                # 手動提供上下文
                context_docs = kwargs.get("context_documents", [])
                return self.generator.generate_response(
                    query=query,
                    context_documents=context_docs,
                    **kwargs
                )
            
            elif context_type == "none":
                # 不使用上下文
                return self.generator.generate_response(
                    query=query,
                    context_documents=[],
                    **kwargs
                )
            
            else:
                raise ValueError(f"Invalid context_type: {context_type}")
                
        except Exception as e:
            self.logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": f"抱歉，生成回答時發生錯誤：{str(e)}",
                "error": str(e),
                "query": query
            }
    
    def analyze_ziwei_chart(self, 
                           chart_data: Dict[str, Any],
                           analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        分析紫微斗數命盤
        
        Args:
            chart_data: 命盤數據
            analysis_type: 分析類型
            
        Returns:
            分析結果
        """
        try:
            # 根據命盤數據檢索相關知識
            query_parts = []
            
            # 提取主要信息構建查詢
            if "main_stars" in chart_data:
                query_parts.extend(chart_data["main_stars"])
            
            if "palaces" in chart_data:
                query_parts.extend([f"{palace}宮" for palace in chart_data["palaces"]])
            
            query = " ".join(query_parts) if query_parts else "紫微斗數 命盤分析"
            
            # 檢索相關文檔
            context_docs = self.search_knowledge(query, top_k=10, min_score=0.6)
            context_texts = [doc["content"] for doc in context_docs]
            
            # 生成分析
            return self.generator.generate_ziwei_analysis(
                chart_data=chart_data,
                context_documents=context_texts,
                analysis_type=analysis_type
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing ziwei chart: {str(e)}")
            return {
                "answer": f"抱歉，分析命盤時發生錯誤：{str(e)}",
                "error": str(e),
                "chart_data": chart_data
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            status = {
                "system": "active",
                "config": self.config,
                "components": {
                    "vector_store": "active" if self.vector_store else "inactive",
                    "generator": "active" if self.generator else "inactive",
                    "rag_generator": "active" if self.rag_generator else "inactive"
                }
            }
            
            # 添加向量存儲統計
            if self.vector_store:
                status["vector_store_stats"] = self.vector_store.get_collection_stats()
            
            # 添加生成器信息
            if self.generator:
                status["generator_info"] = self.generator.get_model_info()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {"system": "error", "error": str(e)}


# 便捷函數
def create_rag_system(config: Dict[str, Any] = None) -> ZiweiRAGSystem:
    """創建 RAG 系統實例"""
    return ZiweiRAGSystem(config)


def quick_setup() -> ZiweiRAGSystem:
    """快速設置 RAG 系統"""
    system = create_rag_system()
    return system
