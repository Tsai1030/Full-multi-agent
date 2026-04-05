"""
BGE-M3 嵌入模型實現
使用 Hugging Face 的 BGE-M3 模型進行文本嵌入
"""

import os
import logging
import torch
from typing import List, Optional, Union
from transformers import AutoTokenizer, AutoModel
import numpy as np


class BGEM3Embeddings:
    """BGE-M3 嵌入模型類"""
    
    def __init__(self, 
                 model_name: str = "BAAI/bge-m3",
                 device: str = "cpu",
                 max_length: int = 8192,
                 batch_size: int = 32,
                 use_fp16: bool = False,
                 logger=None):
        """
        初始化 BGE-M3 嵌入模型
        
        Args:
            model_name: 模型名稱，默認為 BAAI/bge-m3
            device: 運行設備，cpu 或 cuda
            max_length: 最大序列長度
            batch_size: 批次大小
            use_fp16: 是否使用半精度浮點數
            logger: 日誌記錄器
        """
        self.model_name = model_name
        self.device = device
        self.max_length = max_length
        self.batch_size = batch_size
        self.use_fp16 = use_fp16
        self.logger = logger or logging.getLogger(__name__)
        
        # 檢查設備可用性
        if device == "cuda" and not torch.cuda.is_available():
            self.logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"
        
        # 初始化模型和分詞器
        self.tokenizer, self.model = self._load_model()

    def _load_model(self):
        """載入 BGE-M3 模型和分詞器"""
        try:
            self.logger.info(f"Loading BGE-M3 model from HuggingFace: {self.model_name}")

            # 載入分詞器
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # 載入模型
            model = AutoModel.from_pretrained(self.model_name)

            # 移動到指定設備
            model = model.to(self.device)

            # 設置為評估模式
            model.eval()

            # 如果使用 fp16
            if self.use_fp16 and self.device != "cpu":
                model = model.half()

            self.logger.info(f"BGE-M3 model loaded successfully on {self.device}")
            return tokenizer, model

        except Exception as e:
            self.logger.error(f"Error loading BGE-M3 model: {str(e)}")
            raise

    def _mean_pooling(self, model_output, attention_mask):
        """平均池化"""
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def _encode_texts(self, texts: List[str]) -> torch.Tensor:
        """編碼文本列表"""
        # 分詞
        encoded_input = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )

        # 移動到設備
        encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

        # 前向傳播
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # 平均池化
        sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])

        # 正規化
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        對文檔列表進行嵌入

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        if not texts:
            return []

        try:
            self.logger.debug(f"Embedding {len(texts)} documents")

            # 批次處理
            all_embeddings = []
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]

                # 使用 HuggingFace 模型進行嵌入
                batch_embeddings = self._encode_texts(batch_texts)
                all_embeddings.extend(batch_embeddings.cpu().numpy().tolist())

            self.logger.debug(f"Successfully embedded {len(texts)} documents")
            return all_embeddings

        except Exception as e:
            self.logger.error(f"Error embedding documents: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        對查詢文本進行嵌入

        Args:
            text: 查詢文本

        Returns:
            嵌入向量
        """
        try:
            self.logger.debug(f"Embedding query: {text[:100]}...")

            # 使用 HuggingFace 模型進行嵌入
            embedding = self._encode_texts([text])

            return embedding[0].cpu().numpy().tolist()

        except Exception as e:
            self.logger.error(f"Error embedding query: {str(e)}")
            raise
    
    def get_model_info(self) -> dict:
        """獲取模型信息"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "batch_size": self.batch_size,
            "use_fp16": self.use_fp16,
            "embedding_dimension": self.get_embedding_dimension()
        }
    
    def get_embedding_dimension(self) -> int:
        """獲取嵌入向量維度"""
        try:
            # 從模型配置獲取維度
            return self.model.config.hidden_size
        except:
            try:
                # 使用一個簡單的測試文本來獲取維度
                test_embedding = self.embed_query("test")
                return len(test_embedding)
            except:
                # BGE-M3 的默認維度
                return 1024


class HybridEmbeddings:
    """混合嵌入模型類，支持 BGE-M3 和 OpenAI 嵌入"""
    
    def __init__(self, 
                 primary_provider: str = "huggingface",
                 bge_config: dict = None,
                 openai_config: dict = None,
                 logger=None):
        """
        初始化混合嵌入模型
        
        Args:
            primary_provider: 主要提供商，huggingface 或 openai
            bge_config: BGE-M3 配置
            openai_config: OpenAI 配置
            logger: 日誌記錄器
        """
        self.primary_provider = primary_provider
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化 BGE-M3
        if bge_config:
            try:
                self.bge_embeddings = BGEM3Embeddings(**bge_config, logger=logger)
                self.logger.info("BGE-M3 embeddings initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize BGE-M3: {str(e)}")
                self.bge_embeddings = None
        else:
            self.bge_embeddings = None
        
        # 初始化 OpenAI（作為備用）
        if openai_config:
            try:
                try:
                    from langchain_openai import OpenAIEmbeddings
                except ImportError:
                    from langchain_community.embeddings import OpenAIEmbeddings

                self.openai_embeddings = OpenAIEmbeddings(**openai_config)
                self.logger.info("OpenAI embeddings initialized as backup")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI embeddings: {str(e)}")
                self.openai_embeddings = None
        else:
            self.openai_embeddings = None
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文檔列表"""
        if self.primary_provider == "huggingface" and self.bge_embeddings:
            try:
                return self.bge_embeddings.embed_documents(texts)
            except Exception as e:
                self.logger.warning(f"BGE-M3 failed, falling back to OpenAI: {str(e)}")
                if self.openai_embeddings:
                    return self.openai_embeddings.embed_documents(texts)
                raise
        
        elif self.primary_provider == "openai" and self.openai_embeddings:
            try:
                return self.openai_embeddings.embed_documents(texts)
            except Exception as e:
                self.logger.warning(f"OpenAI failed, falling back to BGE-M3: {str(e)}")
                if self.bge_embeddings:
                    return self.bge_embeddings.embed_documents(texts)
                raise
        
        else:
            raise ValueError("No valid embedding provider available")
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入查詢文本"""
        if self.primary_provider == "huggingface" and self.bge_embeddings:
            try:
                return self.bge_embeddings.embed_query(text)
            except Exception as e:
                self.logger.warning(f"BGE-M3 failed, falling back to OpenAI: {str(e)}")
                if self.openai_embeddings:
                    return self.openai_embeddings.embed_query(text)
                raise
        
        elif self.primary_provider == "openai" and self.openai_embeddings:
            try:
                return self.openai_embeddings.embed_query(text)
            except Exception as e:
                self.logger.warning(f"OpenAI failed, falling back to BGE-M3: {str(e)}")
                if self.bge_embeddings:
                    return self.bge_embeddings.embed_query(text)
                raise
        
        else:
            raise ValueError("No valid embedding provider available")
    
    def get_current_provider(self) -> str:
        """獲取當前使用的提供商"""
        return self.primary_provider
    
    def switch_provider(self, provider: str):
        """切換提供商"""
        if provider in ["huggingface", "openai"]:
            self.primary_provider = provider
            self.logger.info(f"Switched to {provider} embeddings")
        else:
            raise ValueError("Invalid provider. Use 'huggingface' or 'openai'")
