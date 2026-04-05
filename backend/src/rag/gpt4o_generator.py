"""
GPT-4o 輸出生成器
用於基於檢索到的知識生成回答
"""

import os
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI
import json


class GPT4oGenerator:
    """GPT-4o 輸出生成器類"""
    
    def __init__(self, 
                 api_key: str = None,
                 base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-4o-mini",
                 temperature: float = 0.7,
                 max_tokens: int = 2000,
                 logger=None):
        """
        初始化 GPT-4o 生成器
        
        Args:
            api_key: OpenAI API 密鑰
            base_url: API 基礎 URL
            model: 模型名稱
            temperature: 溫度參數
            max_tokens: 最大 token 數
            logger: 日誌記錄器
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化 OpenAI 客戶端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        self.logger.info(f"GPT-4o generator initialized with model: {self.model}")
    
    def generate_response(self, 
                         query: str, 
                         context_documents: List[str],
                         system_prompt: str = None,
                         **kwargs) -> Dict[str, Any]:
        """
        基於查詢和上下文文檔生成回答
        
        Args:
            query: 用戶查詢
            context_documents: 檢索到的相關文檔
            system_prompt: 系統提示詞
            **kwargs: 其他參數
            
        Returns:
            生成的回答和元數據
        """
        try:
            # 構建上下文
            context = self._build_context(context_documents)
            
            # 構建消息
            messages = self._build_messages(query, context, system_prompt)
            
            # 調用 GPT-4o
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0)
            )
            
            # 提取回答
            answer = response.choices[0].message.content
            
            # 構建結果
            result = {
                "answer": answer,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "context_used": len(context_documents),
                "query": query
            }
            
            self.logger.info(f"Generated response for query: {query[:100]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": f"抱歉，生成回答時發生錯誤：{str(e)}",
                "error": str(e),
                "model": self.model,
                "query": query
            }
    
    def _build_context(self, documents: List[str]) -> str:
        """構建上下文字符串"""
        if not documents:
            return "沒有找到相關的背景資料。"
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"參考資料 {i}:\n{doc}")
        
        return "\n\n".join(context_parts)
    
    def _build_messages(self, 
                       query: str, 
                       context: str, 
                       system_prompt: str = None) -> List[Dict[str, str]]:
        """構建對話消息"""
        
        # 默認系統提示詞
        default_system_prompt = """你是一位專業的紫微斗數命理師，具有深厚的紫微斗數知識和豐富的解盤經驗。

請根據提供的參考資料回答用戶的問題。回答時請：

1. 基於提供的參考資料進行回答
2. 如果參考資料不足，請明確說明
3. 使用專業但易懂的語言
4. 提供具體、實用的建議
5. 保持客觀和準確性

請用繁體中文回答。"""
        
        messages = [
            {
                "role": "system",
                "content": system_prompt or default_system_prompt
            },
            {
                "role": "user",
                "content": f"""參考資料：
{context}

用戶問題：{query}

請基於上述參考資料回答用戶的問題。"""
            }
        ]
        
        return messages
    
    def generate_ziwei_analysis(self, 
                               chart_data: Dict[str, Any],
                               context_documents: List[str],
                               analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        生成紫微斗數分析
        
        Args:
            chart_data: 命盤數據
            context_documents: 相關文檔
            analysis_type: 分析類型
            
        Returns:
            分析結果
        """
        
        # 構建專門的紫微斗數分析提示詞
        system_prompt = """你是一位資深的紫微斗數命理師，請根據提供的命盤資料和參考文獻進行專業分析。

分析時請包含以下方面：
1. 命宮主星特質分析
2. 十二宮位重點解析
3. 星曜組合的影響
4. 大運流年趨勢
5. 性格特質總結
6. 事業財運建議
7. 感情婚姻分析
8. 健康注意事項

請提供詳細、準確且實用的分析結果。"""
        
        # 構建查詢
        query = f"""請分析以下紫微斗數命盤：

命盤資料：
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

分析類型：{analysis_type}

請提供完整的命理分析。"""
        
        return self.generate_response(
            query=query,
            context_documents=context_documents,
            system_prompt=system_prompt
        )
    
    def generate_qa_response(self, 
                            question: str,
                            context_documents: List[str],
                            question_type: str = "general") -> Dict[str, Any]:
        """
        生成問答回應
        
        Args:
            question: 用戶問題
            context_documents: 相關文檔
            question_type: 問題類型
            
        Returns:
            回答結果
        """
        
        # 根據問題類型調整提示詞
        type_prompts = {
            "general": "請回答關於紫微斗數的一般性問題。",
            "interpretation": "請解釋紫微斗數的概念或術語。",
            "prediction": "請基於紫微斗數理論提供預測性分析。",
            "advice": "請提供基於紫微斗數的建議和指導。"
        }
        
        system_prompt = f"""你是紫微斗數專家。{type_prompts.get(question_type, type_prompts['general'])}

請基於提供的參考資料準確回答，如果資料不足請說明。保持專業性和準確性。"""
        
        return self.generate_response(
            query=question,
            context_documents=context_documents,
            system_prompt=system_prompt
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "provider": "OpenAI"
        }


class RAGResponseGenerator:
    """RAG 回應生成器，整合檢索和生成"""
    
    def __init__(self, 
                 vector_store,
                 generator: GPT4oGenerator,
                 logger=None):
        """
        初始化 RAG 回應生成器
        
        Args:
            vector_store: 向量存儲
            generator: GPT-4o 生成器
            logger: 日誌記錄器
        """
        self.vector_store = vector_store
        self.generator = generator
        self.logger = logger or logging.getLogger(__name__)
    
    def generate_rag_response(self, 
                             query: str,
                             top_k: int = 5,
                             min_score: float = 0.7,
                             **kwargs) -> Dict[str, Any]:
        """
        生成 RAG 回應
        
        Args:
            query: 用戶查詢
            top_k: 檢索文檔數量
            min_score: 最小相似度分數
            **kwargs: 其他參數
            
        Returns:
            完整的 RAG 回應
        """
        try:
            # 檢索相關文檔
            search_results = self.vector_store.search(query, top_k)
            
            # 過濾低分文檔
            relevant_docs = [
                result["content"] 
                for result in search_results 
                if result["score"] >= min_score
            ]
            
            # 生成回答
            response = self.generator.generate_response(
                query=query,
                context_documents=relevant_docs,
                **kwargs
            )
            
            # 添加檢索信息
            response["retrieval_info"] = {
                "total_retrieved": len(search_results),
                "relevant_docs": len(relevant_docs),
                "min_score": min_score,
                "search_results": search_results
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in RAG response generation: {str(e)}")
            return {
                "answer": f"抱歉，處理您的問題時發生錯誤：{str(e)}",
                "error": str(e),
                "query": query
            }
