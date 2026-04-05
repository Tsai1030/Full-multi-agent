"""
RAG向量資料庫實現
用於存儲和檢索紫微斗數相關文檔
"""

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

class ZiweiRAGSystem:
    """紫微斗數RAG系統"""
    
    def __init__(self, vector_store: ZiweiVectorStore, logger=None):
        self.vector_store = vector_store
        self.logger = logger or logging.getLogger(__name__)
    
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
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "vector_store_stats": self.vector_store.get_collection_stats(),
            "status": "active"
        }
