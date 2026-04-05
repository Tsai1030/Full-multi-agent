# gpt4o_generator.py 逐行解析文檔

## 檔案概述
這是GPT-4o生成器的實現檔案，負責使用OpenAI的GPT-4o模型生成紫微斗數分析回應。該檔案提供了完整的文本生成功能，包括基礎生成器和RAG增強生成器。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-14行)

```python
"""
GPT-4o 生成器實現
使用 OpenAI GPT-4o 模型生成紫微斗數分析回應
"""
```
**用意**: 檔案說明文檔，明確這是GPT-4o生成器的實現

```python
import os
import logging
import json
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI
from dataclasses import dataclass
```
**用意**: 導入必要的模組
- `openai`: OpenAI API客戶端
- `AsyncOpenAI`: 異步API客戶端
- `dataclasses`: 數據類裝飾器

### 數據類定義 (第16-31行)

```python
@dataclass
class GenerationConfig:
    """生成配置"""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
```
**用意**: 
- 定義生成參數的數據結構
- 提供默認的GPT-4o配置
- 包含溫度、token數量、懲罰參數等

```python
@dataclass
class GenerationResult:
    """生成結果"""
    content: str
    usage: Dict[str, Any]
    model: str
    finish_reason: str
    error: Optional[str] = None
```
**用意**: 
- 定義生成結果的數據結構
- 包含內容、使用統計、模型信息
- 支援錯誤信息記錄

### GPT4oGenerator 類定義與初始化 (第33-58行)

```python
class GPT4oGenerator:
    """GPT-4o 生成器"""
    
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
            model: 使用的模型名稱
            temperature: 生成溫度
            max_tokens: 最大 token 數
            logger: 日誌記錄器
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化配置
        self.config = GenerationConfig(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 初始化客戶端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
```
**用意**: 
- 定義GPT-4o生成器類
- 支援自定義API配置
- 使用異步客戶端提高性能
- 從環境變數載入API密鑰

### 基礎生成方法 (第60-108行)

```python
    async def generate_response(self,
                              query: str,
                              context_documents: List[str] = None,
                              system_prompt: str = None,
                              **kwargs) -> GenerationResult:
        """
        生成回應
        
        Args:
            query: 用戶查詢
            context_documents: 上下文文檔列表
            system_prompt: 系統提示詞
            **kwargs: 其他生成參數
            
        Returns:
            生成結果
        """
        try:
            # 構建消息
            messages = []
            
            # 添加系統提示詞
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 構建用戶消息
            user_content = query
            if context_documents:
                context_text = "\n\n".join(context_documents)
                user_content = f"參考資料：\n{context_text}\n\n問題：{query}"
            
            messages.append({
                "role": "user", 
                "content": user_content
            })
            
            # 更新配置
            config = self._update_config(**kwargs)
            
            # 調用 OpenAI API
            response = await self.client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty
            )
            
            return GenerationResult(
                content=response.choices[0].message.content,
                usage=response.usage.model_dump() if response.usage else {},
                model=response.model,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return GenerationResult(
                content=f"抱歉，生成回應時發生錯誤：{str(e)}",
                usage={},
                model=self.config.model,
                finish_reason="error",
                error=str(e)
            )
```
**用意**: 
- 核心的文本生成方法
- 支援上下文文檔和系統提示詞
- 自動構建對話消息格式
- 完整的錯誤處理和結果封裝

### 紫微斗數分析生成方法 (第110-158行)

```python
    async def generate_ziwei_analysis(self,
                                    chart_data: Dict[str, Any],
                                    context_documents: List[str] = None,
                                    analysis_type: str = "comprehensive") -> GenerationResult:
        """
        生成紫微斗數分析
        
        Args:
            chart_data: 命盤數據
            context_documents: 參考文檔
            analysis_type: 分析類型
            
        Returns:
            分析結果
        """
        # 構建專業的系統提示詞
        system_prompt = """你是一位專業的紫微斗數命理師，擁有深厚的理論基礎和豐富的實戰經驗。
        
請根據提供的命盤數據和參考資料，進行專業的紫微斗數分析。

分析要求：
1. 基於傳統紫微斗數理論
2. 結合現代生活實際情況
3. 語言溫和專業，避免過於絕對的預測
4. 提供實用的人生建議
5. 保持客觀理性的分析態度

請以JSON格式回應，包含以下結構：
{
    "analysis_type": "分析類型",
    "main_stars": "主要影響星曜",
    "detailed_analysis": "詳細分析內容",
    "suggestions": ["建議1", "建議2", "建議3"],
    "precautions": ["注意事項1", "注意事項2"]
}"""
        
        # 構建查詢
        chart_summary = self._format_chart_data(chart_data)
        query = f"請分析以下紫微斗數命盤（{analysis_type}分析）：\n\n{chart_summary}"
        
        return await self.generate_response(
            query=query,
            context_documents=context_documents,
            system_prompt=system_prompt,
            temperature=0.3  # 較低溫度確保專業性
        )
```
**用意**: 
- 專門用於紫微斗數分析的生成方法
- 使用專業的系統提示詞
- 要求JSON格式輸出
- 較低的溫度確保專業性和一致性

### 命盤數據格式化方法 (第160-185行)

```python
    def _format_chart_data(self, chart_data: Dict[str, Any]) -> str:
        """格式化命盤數據"""
        formatted_parts = []
        
        # 基本信息
        if "basic_info" in chart_data:
            basic_info = chart_data["basic_info"]
            formatted_parts.append("基本信息：")
            for key, value in basic_info.items():
                formatted_parts.append(f"  {key}: {value}")
        
        # 主要星曜
        if "main_stars" in chart_data:
            formatted_parts.append(f"\n主要星曜：{', '.join(chart_data['main_stars'])}")
        
        # 宮位信息
        if "palaces" in chart_data:
            formatted_parts.append("\n宮位信息：")
            for palace, info in chart_data["palaces"].items():
                if isinstance(info, dict):
                    stars = info.get("stars", [])
                    formatted_parts.append(f"  {palace}: {', '.join(stars)}")
                else:
                    formatted_parts.append(f"  {palace}: {info}")
        
        return "\n".join(formatted_parts)
```
**用意**: 
- 將結構化的命盤數據轉換為可讀文本
- 分別處理基本信息、主星、宮位
- 生成格式化的命盤描述

### 配置更新方法 (第187-200行)

```python
    def _update_config(self, **kwargs) -> GenerationConfig:
        """更新生成配置"""
        config = GenerationConfig(
            model=kwargs.get("model", self.config.model),
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            top_p=kwargs.get("top_p", self.config.top_p),
            frequency_penalty=kwargs.get("frequency_penalty", self.config.frequency_penalty),
            presence_penalty=kwargs.get("presence_penalty", self.config.presence_penalty)
        )
        return config
```
**用意**: 
- 支援運行時配置覆蓋
- 保持默認配置不變
- 靈活的參數調整

### 模型信息方法 (第202-212行)

```python
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        return {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "base_url": self.base_url,
            "api_configured": bool(self.api_key)
        }
```
**用意**: 
- 提供模型配置信息
- 包含API配置狀態
- 用於系統狀態檢查

## 程式碼架構總結

### 設計模式
1. **配置模式**: 使用數據類管理生成參數
2. **模板方法**: 專業的系統提示詞模板
3. **異步模式**: 使用異步API提高性能
4. **錯誤處理**: 完整的異常捕獲和處理

### 主要特點
- **異步支援**: 使用AsyncOpenAI提高並發性能
- **專業化**: 針對紫微斗數的專門方法
- **靈活配置**: 支援運行時參數調整
- **錯誤恢復**: 優雅的錯誤處理和用戶反饋

## RAGResponseGenerator RAG增強生成器 (第214-350行)

### RAG生成器類定義與初始化 (第214-235行)

```python
class RAGResponseGenerator:
    """RAG 增強回應生成器"""

    def __init__(self,
                 vector_store,
                 generator: GPT4oGenerator,
                 logger=None):
        """
        初始化 RAG 生成器

        Args:
            vector_store: 向量存儲實例
            generator: GPT-4o 生成器實例
            logger: 日誌記錄器
        """
        self.vector_store = vector_store
        self.generator = generator
        self.logger = logger or logging.getLogger(__name__)

        # RAG 配置
        self.default_top_k = 5
        self.default_min_score = 0.7
```
**用意**:
- 定義RAG增強生成器類
- 整合向量存儲和GPT-4o生成器
- 設置默認的檢索參數

### RAG回應生成方法 (第237-295行)

```python
    async def generate_rag_response(self,
                                  query: str,
                                  top_k: int = None,
                                  min_score: float = None,
                                  system_prompt: str = None,
                                  **kwargs) -> Dict[str, Any]:
        """
        生成 RAG 增強回應

        Args:
            query: 用戶查詢
            top_k: 檢索文檔數量
            min_score: 最小相似度分數
            system_prompt: 系統提示詞
            **kwargs: 其他生成參數

        Returns:
            包含回應和檢索信息的字典
        """
        try:
            # 使用默認值
            top_k = top_k or self.default_top_k
            min_score = min_score or self.default_min_score

            # 檢索相關文檔
            self.logger.info(f"Retrieving documents for query: {query[:100]}...")
            search_results = self.vector_store.search(query, top_k)

            # 過濾低分結果
            filtered_results = [
                result for result in search_results
                if result["score"] >= min_score
            ]

            self.logger.info(f"Found {len(filtered_results)} relevant documents (score >= {min_score})")

            # 提取文檔內容
            context_documents = [result["content"] for result in filtered_results]

            # 如果沒有找到相關文檔，使用無上下文生成
            if not context_documents:
                self.logger.warning("No relevant documents found, generating without context")
                generation_result = await self.generator.generate_response(
                    query=query,
                    system_prompt=system_prompt,
                    **kwargs
                )
            else:
                # 使用檢索到的文檔作為上下文
                generation_result = await self.generator.generate_response(
                    query=query,
                    context_documents=context_documents,
                    system_prompt=system_prompt,
                    **kwargs
                )

            return {
                "answer": generation_result.content,
                "retrieved_documents": filtered_results,
                "retrieval_stats": {
                    "total_retrieved": len(search_results),
                    "filtered_count": len(filtered_results),
                    "top_k": top_k,
                    "min_score": min_score
                },
                "generation_info": {
                    "model": generation_result.model,
                    "usage": generation_result.usage,
                    "finish_reason": generation_result.finish_reason
                },
                "error": generation_result.error
            }

        except Exception as e:
            self.logger.error(f"Error in RAG response generation: {str(e)}")
            return {
                "answer": f"抱歉，生成回應時發生錯誤：{str(e)}",
                "error": str(e),
                "retrieved_documents": [],
                "retrieval_stats": {},
                "generation_info": {}
            }
```
**用意**:
- 實現完整的RAG流程：檢索→過濾→生成
- 自動處理無相關文檔的情況
- 提供詳細的檢索和生成統計信息
- 完整的錯誤處理和日誌記錄

### 紫微斗數RAG分析方法 (第297-350行)

```python
    async def generate_ziwei_rag_analysis(self,
                                        chart_data: Dict[str, Any],
                                        analysis_type: str = "comprehensive",
                                        top_k: int = 10,
                                        min_score: float = 0.6) -> Dict[str, Any]:
        """
        生成紫微斗數 RAG 分析

        Args:
            chart_data: 命盤數據
            analysis_type: 分析類型
            top_k: 檢索文檔數量
            min_score: 最小相似度分數

        Returns:
            分析結果
        """
        try:
            # 從命盤數據構建查詢
            query_parts = []

            # 添加主要星曜
            if "main_stars" in chart_data:
                query_parts.extend(chart_data["main_stars"])

            # 添加宮位信息
            if "palaces" in chart_data:
                for palace_name in chart_data["palaces"].keys():
                    query_parts.append(palace_name)

            # 添加分析類型
            query_parts.append(analysis_type)

            # 構建查詢字符串
            query = " ".join(query_parts)

            self.logger.info(f"Generated query for ziwei analysis: {query}")

            # 使用 RAG 生成分析
            result = await self.generate_rag_response(
                query=query,
                top_k=top_k,
                min_score=min_score,
                temperature=0.3  # 較低溫度確保專業性
            )

            # 添加命盤數據到結果中
            result["chart_data"] = chart_data
            result["analysis_type"] = analysis_type

            return result

        except Exception as e:
            self.logger.error(f"Error in ziwei RAG analysis: {str(e)}")
            return {
                "answer": f"抱歉，分析命盤時發生錯誤：{str(e)}",
                "error": str(e),
                "chart_data": chart_data,
                "analysis_type": analysis_type
            }
```
**用意**:
- 專門用於紫微斗數的RAG分析
- 智能提取命盤關鍵信息構建查詢
- 使用較低的相似度閾值獲取更多相關資料
- 較低的溫度確保專業性

## 深度技術分析

### 異步編程優勢

#### 1. 性能提升
```python
async def generate_response(self, ...):
    response = await self.client.chat.completions.create(...)
```
- 非阻塞I/O操作
- 支援高並發請求
- 提高系統吞吐量

#### 2. 資源效率
- 減少線程開銷
- 更好的內存使用
- 適合I/O密集型任務

### RAG增強策略

#### 1. 智能檢索
- 基於語義相似度的文檔檢索
- 可配置的檢索參數
- 自動過濾低質量結果

#### 2. 上下文管理
```python
if not context_documents:
    # 無上下文生成
else:
    # 使用檢索文檔作為上下文
```
- 優雅處理無相關文檔情況
- 動態上下文構建
- 確保生成質量

#### 3. 專業化查詢
```python
query_parts.extend(chart_data["main_stars"])
query_parts.append(palace_name)
```
- 從結構化數據提取關鍵信息
- 構建專業領域查詢
- 提高檢索精度

### 錯誤處理機制

#### 1. 多層次錯誤處理
- API調用錯誤
- 檢索失敗處理
- 生成錯誤恢復

#### 2. 用戶友好錯誤信息
```python
return GenerationResult(
    content=f"抱歉，生成回應時發生錯誤：{str(e)}",
    error=str(e)
)
```
- 中文錯誤提示
- 保留技術錯誤信息
- 優雅的錯誤恢復

### 配置管理

#### 1. 靈活的參數配置
- 運行時參數覆蓋
- 默認值管理
- 專業化配置

#### 2. 數據類優勢
```python
@dataclass
class GenerationConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
```
- 類型安全
- 默認值管理
- IDE友好

## 使用場景

### 1. 智能問答系統
- 基於知識庫的問答
- 上下文增強回應
- 專業領域諮詢

### 2. 命盤分析服務
- 自動化命盤解讀
- 專業分析報告
- 個性化建議生成

### 3. 知識檢索系統
- 語義搜索
- 相關文檔推薦
- 智能摘要生成

## 總結

GPT-4o生成器通過整合OpenAI的先進語言模型和RAG技術，提供了高質量的文本生成服務。其異步架構、專業化配置和完整的錯誤處理，使其成為構建智能對話系統和專業分析工具的理想選擇。
