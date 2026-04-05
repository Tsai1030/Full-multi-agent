# vector_store.py 逐行解析文檔

## 檔案概述
這是RAG向量資料庫的實現檔案，用於存儲和檢索紫微斗數相關文檔。該檔案整合了ChromaDB向量資料庫、BGE-M3嵌入模型和LangChain文檔處理，提供完整的向量存儲和檢索功能。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-19行)

```python
"""
RAG向量資料庫實現
用於存儲和檢索紫微斗數相關文檔
"""
```
**用意**: 檔案說明文檔，明確這是向量資料庫的實現

```python
import os
import json
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import hashlib
from .bge_embeddings import BGEM3Embeddings, HybridEmbeddings
```
**用意**: 導入必要的模組
- `chromadb`: 向量資料庫
- `langchain`: 文檔處理和分割
- `hashlib`: 生成文檔ID
- 本地嵌入模組

### ZiweiVectorStore 類定義與初始化 (第21-59行)

```python
class ZiweiVectorStore:
    """紫微斗數向量資料庫"""
    
    def __init__(self,
                 persist_directory: str = "./data/vector_db",
                 collection_name: str = "ziwei_knowledge",
                 embedding_provider: str = "huggingface",
                 embedding_model: str = "BAAI/bge-m3",
                 embedding_config: Dict[str, Any] = None,
                 logger=None):

        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider
        self.logger = logger or logging.getLogger(__name__)

        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # 初始化嵌入模型
        self.embeddings = self._initialize_embeddings(
            embedding_provider,
            embedding_model,
            embedding_config or {}
        )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
        
        # 獲取或創建集合
        self.collection = self._get_or_create_collection()
```
**用意**: 
- 定義向量資料庫類
- 初始化ChromaDB持久化客戶端
- 設置中文友好的文本分割器
- 使用中文標點符號作為分割標準
- 自動創建或載入集合

### 嵌入模型初始化方法 (第61-99行)

```python
    def _initialize_embeddings(self, provider: str, model: str, config: Dict[str, Any]):
        """初始化嵌入模型"""
        try:
            if provider == "huggingface":
                # 使用 BGE-M3
                bge_config = {
                    "model_name": model,
                    "device": config.get("device", "cpu"),
                    "max_length": config.get("max_length", 8192),
                    "batch_size": config.get("batch_size", 32),
                    "use_fp16": config.get("use_fp16", False)
                }

                # 如果有 OpenAI 配置，創建混合嵌入
                if config.get("openai_fallback", True):
                    openai_config = {
                        "model": config.get("openai_model", "text-embedding-ada-002")
                    }
                    return HybridEmbeddings(
                        primary_provider="huggingface",
                        bge_config=bge_config,
                        openai_config=openai_config,
                        logger=self.logger
                    )
                else:
                    return BGEM3Embeddings(**bge_config)

            elif provider == "openai":
                # 使用 OpenAI
                return OpenAIEmbeddings(model=model)

            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")

        except Exception as e:
            self.logger.error(f"Error initializing embeddings: {str(e)}")
            # 回退到 OpenAI
            self.logger.info("Falling back to OpenAI embeddings")
            return OpenAIEmbeddings(model="text-embedding-ada-002")
```
**用意**: 
- 支援多種嵌入提供商
- 優先使用BGE-M3，支援OpenAI備用
- 自動創建混合嵌入模型
- 完整的錯誤處理和回退機制

### 集合管理方法 (第101-113行)

```python
    def _get_or_create_collection(self):
        """獲取或創建向量集合"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            self.logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "紫微斗數知識庫"}
            )
            self.logger.info(f"Created new collection: {self.collection_name}")
        
        return collection
```
**用意**: 
- 嘗試載入現有集合
- 不存在時自動創建新集合
- 添加描述性元數據
- 記錄操作日誌

### 文檔添加方法 (第115-171行)

```python
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        添加文檔到向量資料庫
        
        Args:
            documents: 文檔列表
            
        Returns:
            添加的文檔ID列表
        """
        if not documents:
            return []
        
        # 分割文檔
        split_docs = []
        for doc in documents:
            chunks = self.text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                split_doc = Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                split_docs.append(split_doc)
        
        # 生成嵌入向量
        texts = [doc.page_content for doc in split_docs]
        embeddings = self.embeddings.embed_documents(texts)
        
        # 生成文檔ID
        doc_ids = []
        metadatas = []
        
        for i, doc in enumerate(split_docs):
            # 使用內容哈希作為ID的一部分
            content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()[:8]
            doc_id = f"doc_{i}_{content_hash}"
            doc_ids.append(doc_id)
            
            # 準備元數據
            metadata = doc.metadata.copy()
            metadata["doc_id"] = doc_id
            metadatas.append(metadata)
        
        # 添加到ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=doc_ids
        )
        
        self.logger.info(f"Added {len(split_docs)} document chunks to vector store")
        return doc_ids
```
**用意**: 
- 自動分割長文檔為小塊
- 保留原始元數據並添加分塊信息
- 生成唯一的文檔ID（包含內容哈希）
- 批次生成嵌入向量
- 一次性添加到ChromaDB

### 搜索方法 (第173-216行)

```python
    def search(self, 
               query: str, 
               top_k: int = 5,
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        搜索相關文檔
        
        Args:
            query: 查詢字符串
            top_k: 返回結果數量
            filter_metadata: 元數據過濾條件
            
        Returns:
            搜索結果列表
        """
        try:
            # 生成查詢嵌入
            query_embedding = self.embeddings.embed_query(query)
            
            # 執行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # 格式化結果
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "score": 1 - results['distances'][0][i] if results['distances'] else 0,  # 轉換為相似度分數
                        "id": results['ids'][0][i] if results['ids'] else None
                    }
                    formatted_results.append(result)
            
            self.logger.info(f"Search query: '{query}' returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            return []
```
**用意**: 
- 將查詢文本轉換為嵌入向量
- 支援元數據過濾
- 將距離轉換為相似度分數
- 格式化返回結果
- 完整的錯誤處理

### 關鍵詞搜索方法 (第218-233行)

```python
    def search_by_keywords(self, 
                          keywords: List[str], 
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """
        根據關鍵詞搜索
        
        Args:
            keywords: 關鍵詞列表
            top_k: 返回結果數量
            
        Returns:
            搜索結果列表
        """
        # 組合關鍵詞為查詢字符串
        query = " ".join(keywords)
        return self.search(query, top_k)
```
**用意**: 
- 提供關鍵詞搜索的便利接口
- 自動組合關鍵詞為查詢字符串
- 復用標準搜索方法

## 程式碼架構總結

### 設計模式
1. **適配器模式**: 統一不同嵌入提供商的接口
2. **工廠模式**: 根據配置創建不同的嵌入模型
3. **策略模式**: 支援多種搜索和過濾策略
4. **組合模式**: 整合多個組件協同工作

### 主要特點
- **持久化存儲**: 使用ChromaDB實現數據持久化
- **智能分割**: 中文友好的文本分割策略
- **混合嵌入**: 支援本地和雲端嵌入模型
- **元數據支援**: 完整的元數據管理和過濾

### 統計信息方法 (第235-246行)

```python
    def get_collection_stats(self) -> Dict[str, Any]:
        """獲取集合統計信息"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            return {}
```
**用意**:
- 提供集合的統計信息
- 包含文檔總數和存儲位置
- 錯誤處理確保穩定性

### 文檔刪除方法 (第248-264行)

```python
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """
        刪除文檔

        Args:
            doc_ids: 要刪除的文檔ID列表

        Returns:
            是否成功刪除
        """
        try:
            self.collection.delete(ids=doc_ids)
            self.logger.info(f"Deleted {len(doc_ids)} documents")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting documents: {str(e)}")
            return False
```
**用意**:
- 支援批量刪除文檔
- 記錄刪除操作日誌
- 返回操作成功狀態

### 文檔更新方法 (第266-293行)

```python
    def update_document(self, doc_id: str, document: Document) -> bool:
        """
        更新文檔

        Args:
            doc_id: 文檔ID
            document: 新文檔內容

        Returns:
            是否成功更新
        """
        try:
            # 生成新的嵌入
            embedding = self.embeddings.embed_documents([document.page_content])[0]

            # 更新文檔
            self.collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document.page_content],
                metadatas=[document.metadata]
            )

            self.logger.info(f"Updated document: {doc_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating document: {str(e)}")
            return False
```
**用意**:
- 支援單個文檔的更新
- 重新生成嵌入向量
- 同時更新內容和元數據

## ZiweiRAGSystem 舊版系統 (第295-400行)

### 舊版RAG系統類定義 (第295-300行)

```python
class ZiweiRAGSystem:
    """紫微斗數RAG系統"""

    def __init__(self, vector_store: ZiweiVectorStore, logger=None):
        self.vector_store = vector_store
        self.logger = logger or logging.getLogger(__name__)
```
**用意**:
- 提供向後兼容的RAG系統接口
- 依賴注入向量存儲實例
- 保持與舊版代碼的兼容性

### 目錄文檔載入方法 (第302-339行)

```python
    def load_documents_from_directory(self, directory_path: str) -> int:
        """
        從目錄載入文檔

        Args:
            directory_path: 文檔目錄路徑

        Returns:
            載入的文檔數量
        """
        documents = []

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.txt', '.md', '.json')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        doc = Document(
                            page_content=content,
                            metadata={
                                "source": file_path,
                                "filename": file,
                                "file_type": file.split('.')[-1]
                            }
                        )
                        documents.append(doc)

                    except Exception as e:
                        self.logger.warning(f"Error loading file {file_path}: {str(e)}")

        if documents:
            self.vector_store.add_documents(documents)
            self.logger.info(f"Loaded {len(documents)} documents from {directory_path}")

        return len(documents)
```
**用意**:
- 遞歸掃描目錄中的文檔
- 支援txt、md、json格式
- 自動生成文檔元數據
- 批次添加到向量存儲

### 知識搜索方法 (第341-365行)

```python
    def search_knowledge(self,
                        query: str,
                        top_k: int = 5,
                        min_score: float = 0.7) -> List[str]:
        """
        搜索知識庫

        Args:
            query: 查詢字符串
            top_k: 返回結果數量
            min_score: 最小相似度分數

        Returns:
            相關知識片段列表
        """
        results = self.vector_store.search(query, top_k)

        # 過濾低分結果
        filtered_results = [
            result["content"]
            for result in results
            if result["score"] >= min_score
        ]

        return filtered_results
```
**用意**:
- 提供簡化的搜索接口
- 自動過濾低相似度結果
- 只返回文本內容，不包含元數據

### 紫微斗數元素搜索方法 (第367-392行)

```python
    def search_by_ziwei_elements(self,
                                main_stars: List[str],
                                palaces: List[str] = None,
                                top_k: int = 5) -> List[str]:
        """
        根據紫微斗數元素搜索

        Args:
            main_stars: 主星列表
            palaces: 宮位列表
            top_k: 返回結果數量

        Returns:
            相關知識片段列表
        """
        # 構建查詢
        query_parts = []

        if main_stars:
            query_parts.extend(main_stars)

        if palaces:
            query_parts.extend(palaces)

        query = " ".join(query_parts)
        return self.search_knowledge(query, top_k)
```
**用意**:
- 專門針對紫微斗數的搜索方法
- 組合主星和宮位信息
- 構建專業的查詢字符串

### 系統狀態方法 (第394-400行)

```python
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "vector_store_stats": self.vector_store.get_collection_stats(),
            "status": "active"
        }
```
**用意**:
- 提供系統狀態檢查
- 包含向量存儲統計信息
- 簡化的狀態報告

## 深度技術分析

### ChromaDB集成特點

#### 1. 持久化存儲
- 使用PersistentClient確保數據持久化
- 支援服務重啟後數據恢復
- 本地文件系統存儲

#### 2. 高效檢索
- 基於向量相似度的快速搜索
- 支援元數據過濾
- 可擴展的索引結構

#### 3. 批次操作
- 支援批次添加、更新、刪除
- 優化的內存使用
- 高效的I/O操作

### 文本處理策略

#### 1. 智能分割
```python
separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
```
- 優先使用段落分割
- 支援中文標點符號
- 保持語義完整性

#### 2. 元數據管理
- 保留原始文檔信息
- 添加分塊索引
- 支援自定義元數據

#### 3. ID生成策略
```python
content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()[:8]
doc_id = f"doc_{i}_{content_hash}"
```
- 基於內容哈希的唯一ID
- 避免重複內容
- 便於調試和追蹤

### 搜索優化

#### 1. 相似度計算
```python
"score": 1 - results['distances'][0][i]
```
- 將距離轉換為相似度
- 直觀的分數表示
- 便於閾值過濾

#### 2. 結果格式化
- 統一的返回格式
- 包含內容、元數據、分數
- 便於後續處理

## 使用場景

### 1. 知識庫建設
- 批量導入文檔
- 自動分割和索引
- 持久化存儲

### 2. 語義搜索
- 基於語義的文檔檢索
- 支援複雜查詢
- 高精度匹配

### 3. 專業領域應用
- 紫微斗數知識檢索
- 專業術語搜索
- 領域特化優化

## 總結

向量存儲系統通過整合ChromaDB、BGE-M3嵌入和LangChain文檔處理，提供了完整的向量存儲和檢索解決方案。其智能的文本分割、高效的批次處理和靈活的搜索功能，為RAG系統提供了堅實的數據基礎。
