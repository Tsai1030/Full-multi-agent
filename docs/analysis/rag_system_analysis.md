# rag_system.py 逐行解析文檔

## 檔案概述
這是RAG系統的主要控制器，整合BGE-M3嵌入模型和GPT-4o輸出模型，提供完整的檢索增強生成功能。該檔案是整個RAG系統的核心，負責協調各個組件的工作。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-16行)

```python
"""
完整的 RAG 系統實現
整合 BGE-M3 嵌入模型和 GPT-4o 輸出模型
"""
```
**用意**: 檔案說明文檔，明確這是完整的RAG系統實現

```python
import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from .vector_store import ZiweiVectorStore
from .gpt4o_generator import GPT4oGenerator, RAGResponseGenerator
from .bge_embeddings import BGEM3Embeddings, HybridEmbeddings
```
**用意**: 導入必要的模組
- `os`, `logging`: 系統和日誌功能
- `typing`: 類型提示
- `dotenv`: 環境變數載入
- 本地模組：向量存儲、生成器、嵌入模型

```python
# 載入環境變數
load_dotenv()
```
**用意**: 載入.env檔案中的環境變數配置

### ZiweiRAGSystem 類定義與初始化 (第19-39行)

```python
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
```
**用意**: 
- 定義RAG系統的主類
- 接受可選的配置和日誌記錄器
- 初始化三個核心組件：向量存儲、生成器、RAG生成器
- 調用系統初始化方法

### 默認配置載入方法 (第41-75行)

```python
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
                    "batch_size": int(os.getenv("EMBEDDING_BATCH_SIZE", "32")), # 如果要提升執行速度可以增加做嘗試
                    "use_fp16": os.getenv("EMBEDDING_USE_FP16", "false").lower() == "true",
                    "openai_fallback": True,
                    "openai_model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
                }
            },
```
**用意**: 
- 從環境變數載入向量存儲配置
- 支援BGE-M3和OpenAI嵌入模型
- 提供合理的默認值
- 包含性能調優參數（batch_size註解）

```python
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
```
**用意**: 
- 配置GPT-4o生成器參數
- 設置RAG檢索參數
- 支援重排序功能（可選）
- 所有參數都可通過環境變數覆蓋

### 日誌設置方法 (第77-90行)

```python
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
```
**用意**: 
- 創建專用的RAG系統日誌記錄器
- 設置INFO級別的日誌
- 避免重複添加處理器
- 使用標準的日誌格式

### 系統初始化方法 (第92-121行)

```python
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
```
**用意**: 
- 按順序初始化三個核心組件
- 使用配置字典傳遞參數
- 記錄初始化過程
- 完整的錯誤處理和日誌記錄

### 知識添加方法 (第123-153行)

```python
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
```
**用意**: 
- 提供添加知識的公共接口
- 將字典格式轉換為LangChain Document對象
- 支援元數據的傳遞
- 返回操作成功狀態

### 目錄載入方法 (第155-172行)

```python
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
```
**用意**: 
- 支援從目錄批量載入文檔
- 使用舊版RAG系統的載入功能
- 返回載入的文檔數量
- 錯誤處理返回0

### 知識搜索方法 (第174-200行)

```python
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
```
**用意**: 
- 提供知識庫搜索接口
- 支援參數覆蓋，使用配置默認值
- 自動過濾低相似度結果
- 返回結構化的搜索結果

### 回答生成方法 (第202-253行)

```python
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
```
**用意**: 
- 提供靈活的回答生成接口
- 支援三種上下文模式：自動檢索、手動提供、無上下文
- 使用配置默認值
- 完整的錯誤處理和用戶友好的錯誤訊息

## 程式碼架構總結

### 設計模式
1. **外觀模式**: ZiweiRAGSystem作為統一接口
2. **配置模式**: 集中化的配置管理
3. **組合模式**: 整合多個組件協同工作
4. **策略模式**: 支援多種上下文生成策略

### 主要特點
- **模組化設計**: 清晰的組件分離
- **配置驅動**: 靈活的環境變數配置
- **錯誤處理**: 完整的異常處理機制
- **日誌記錄**: 詳細的操作日誌

### 紫微斗數命盤分析方法 (第255-298行)

```python
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
```
**用意**:
- 專門用於紫微斗數命盤分析
- 智能提取命盤關鍵信息構建查詢
- 使用較低的相似度閾值(0.6)獲取更多相關資料
- 調用專門的命盤分析生成器

### 系統狀態獲取方法 (第300-325行)

```python
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
```
**用意**:
- 提供系統健康狀態檢查
- 包含配置信息和組件狀態
- 添加向量存儲統計和生成器信息
- 錯誤處理確保狀態查詢的穩定性

### 便捷函數 (第328-337行)

```python
# 便捷函數
def create_rag_system(config: Dict[str, Any] = None) -> ZiweiRAGSystem:
    """創建 RAG 系統實例"""
    return ZiweiRAGSystem(config)


def quick_setup() -> ZiweiRAGSystem:
    """快速設置 RAG 系統"""
    system = create_rag_system()
    return system
```
**用意**:
- 提供模組級別的便捷函數
- 簡化RAG系統的創建過程
- 支援快速設置和自定義配置

## 深度架構分析

### 系統設計理念

#### 1. 統一接口設計
- ZiweiRAGSystem作為統一的系統入口
- 隱藏內部組件的複雜性
- 提供一致的API接口

#### 2. 配置驅動架構
- 所有參數都可通過環境變數配置
- 支援運行時配置覆蓋
- 提供合理的默認值

#### 3. 組件化設計
- 向量存儲、生成器、RAG生成器獨立
- 組件間通過接口通信
- 易於測試和維護

### 核心工作流程

#### 1. 系統初始化流程
```
載入配置 → 設置日誌 → 初始化向量存儲 → 初始化生成器 → 創建RAG生成器
```

#### 2. 知識檢索流程
```
用戶查詢 → 向量化查詢 → 搜索向量庫 → 過濾結果 → 返回相關文檔
```

#### 3. 回答生成流程
```
檢索相關文檔 → 構建上下文 → 調用GPT-4o → 生成回答 → 返回結果
```

### 技術特點

#### 1. 靈活的上下文管理
- 自動檢索：系統自動搜索相關文檔
- 手動提供：用戶指定上下文文檔
- 無上下文：直接使用GPT-4o生成

#### 2. 智能查詢構建
- 從命盤數據提取關鍵信息
- 自動組合主星和宮位信息
- 構建有效的搜索查詢

#### 3. 多層次錯誤處理
- 組件初始化錯誤處理
- 運行時異常捕獲
- 用戶友好的錯誤訊息

### 擴展性設計

#### 1. 新組件集成
- 標準化的組件接口
- 依賴注入模式
- 易於添加新功能

#### 2. 配置擴展
- 環境變數驅動
- 配置字典覆蓋
- 運行時參數調整

#### 3. 功能擴展
- 新的分析類型
- 不同的生成策略
- 自定義檢索邏輯

## 使用場景

### 1. 命盤分析系統
- 自動檢索相關紫微斗數知識
- 生成專業的命盤分析報告
- 支援不同類型的分析需求

### 2. 知識問答系統
- 基於紫微斗數知識庫回答問題
- 提供準確的專業解答
- 支援複雜的查詢需求

### 3. 教學輔助系統
- 為學習者提供相關知識
- 解釋紫微斗數概念和術語
- 提供實例和案例分析

## 總結

ZiweiRAGSystem是一個設計精良的RAG系統實現，通過統一接口整合了向量檢索和文本生成功能。其配置驅動的架構、完整的錯誤處理和靈活的擴展性，使其成為紫微斗數AI應用的理想基礎平台。
