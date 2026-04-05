# gpt4o_formatter.py 逐行解析文檔

## 檔案概述
這是一個GPT-4o輸出格式化器，負責將Multi-Agent的分析結果格式化為最終的JSON或論述格式輸出。該檔案實現了完整的格式化流程，包括JSON結構化、論述生成和格式驗證。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-16行)

```python
"""
GPT-4o 輸出格式化器
負責將Multi-Agent的分析結果格式化為最終的JSON輸出
"""
```
**用意**: 檔案說明文檔，描述格式化器的主要功能

```python
import json
import asyncio
import time
from typing import Dict, Any, List, Optional
import openai
from dataclasses import dataclass

from ..config.settings import get_settings
from ..agents.coordinator import CoordinationResult
```
**用意**: 導入必要的模組
- `json`: JSON數據處理
- `asyncio`: 異步編程支援
- `time`: 時間測量
- `typing`: 類型提示
- `openai`: OpenAI API客戶端
- `dataclasses`: 數據類裝飾器
- `settings`: 項目配置
- `CoordinationResult`: 協調結果數據結構

```python
settings = get_settings()
```
**用意**: 獲取全域配置設定，用於OpenAI API配置

### 數據類定義 (第18-33行)

```python
@dataclass
class FormattingTask:
    """格式化任務"""
    content: str
    domain_type: str
    output_format: str = "json"
    user_profile: Optional[Dict[str, Any]] = None
```
**用意**: 
- 定義格式化任務的數據結構
- `content`: 待格式化的內容
- `domain_type`: 領域類型（love/wealth/future等）
- `output_format`: 輸出格式（json/narrative）
- `user_profile`: 可選的用戶背景信息

```python
@dataclass
class FormattedOutput:
    """格式化輸出"""
    success: bool
    formatted_content: str
    metadata: Dict[str, Any]
    processing_time: float
    validation_passed: bool = False
```
**用意**: 
- 定義格式化結果的數據結構
- `success`: 格式化是否成功
- `formatted_content`: 格式化後的內容
- `metadata`: 元數據信息
- `processing_time`: 處理時間
- `validation_passed`: 是否通過驗證

### GPT4oFormatter 類定義與初始化 (第35-49行)

```python
class GPT4oFormatter:
    """GPT-4o 輸出格式化器"""
    
    def __init__(self, logger=None):
        self.logger = logger or __import__('logging').getLogger(__name__)
        
        # 初始化GPT-4o客戶端
        self.client = openai.AsyncOpenAI(
            api_key=settings.openai.api_key,
            base_url=settings.openai.base_url
        )
        
        self.model = settings.openai.model_gpt4o
        self.temperature = 0.1  # 低溫度確保格式一致性
        self.max_tokens = 4000
```
**用意**: 
- 定義主要的格式化器類
- 設置日誌記錄器
- 初始化OpenAI異步客戶端
- 配置模型參數：低溫度確保輸出一致性
- 設置最大token數量限制

### 主要格式化方法 (第51-111行)

```python
    async def format_coordination_result(self,
                                       coordination_result: CoordinationResult,
                                       domain_type: str,
                                       user_profile: Optional[Dict[str, Any]] = None,
                                       output_format: str = "json") -> FormattedOutput:
        """格式化協調結果"""
        
        start_time = time.time()
```
**用意**: 
- 主要的格式化入口方法
- 接收協調結果和格式化參數
- 開始計時以追蹤處理時間

```python
        try:
            # 準備格式化任務
            task = FormattingTask(
                content=coordination_result.integrated_result or "",
                domain_type=domain_type,
                output_format=output_format,
                user_profile=user_profile
            )

            # 根據輸出格式執行格式化
            if output_format == "narrative":
                formatted_content = await self._format_to_narrative(task)
            elif output_format == "json_to_narrative":
                # 先生成 JSON，再轉換為論述
                json_content = await self._format_to_json(task)
                task.content = json_content  # 更新內容為 JSON 結果
                formatted_content = await self._format_to_narrative(task)
            else:
                formatted_content = await self._format_to_json(task)
```
**用意**: 
- 創建格式化任務對象
- 根據輸出格式選擇不同的處理路徑
- 支援三種格式：JSON、論述、JSON轉論述
- JSON轉論述模式：先生成結構化JSON，再轉為自然語言

```python
            # 驗證JSON格式
            validation_passed = await self._validate_json_format(formatted_content)
            
            processing_time = time.time() - start_time
            
            return FormattedOutput(
                success=True,
                formatted_content=formatted_content,
                metadata={
                    "model": self.model,
                    "domain_type": domain_type,
                    "agents_used": coordination_result.metadata.get("agents_used", []),
                    "coordination_strategy": coordination_result.metadata.get("strategy", ""),
                    "original_processing_time": coordination_result.total_time,
                    "formatting_time": processing_time
                },
                processing_time=processing_time,
                validation_passed=validation_passed
            )
```
**用意**: 
- 驗證生成內容的JSON格式
- 計算總處理時間
- 構建詳細的元數據信息
- 包含原始處理時間和格式化時間
- 記錄使用的代理和協調策略

```python
        except Exception as e:
            self.logger.error(f"Formatting failed: {str(e)}")
            
            return FormattedOutput(
                success=False,
                formatted_content=json.dumps({
                    "error": "格式化失敗",
                    "message": str(e)
                }, ensure_ascii=False, indent=2),
                metadata={"error": str(e)},
                processing_time=time.time() - start_time
            )
```
**用意**: 
- 完整的異常處理
- 記錄錯誤日誌
- 返回標準化的錯誤格式
- 確保方法總是返回有效的FormattedOutput

### JSON格式化方法 (第113-142行)

```python
    async def _format_to_json(self, task: FormattingTask) -> str:
        """格式化為JSON"""
        
        # 根據領域類型獲取對應的JSON模板
        json_template = self._get_json_template(task.domain_type)
        
        # 構建格式化提示詞
        format_prompt = self._build_format_prompt(task, json_template)
        
        # 調用GPT-4o進行格式化
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user",
                "content": format_prompt
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"}  # 確保JSON格式
        )
        
        return response.choices[0].message.content
```
**用意**: 
- 專門處理JSON格式化的方法
- 根據領域類型獲取對應模板
- 構建專業的格式化提示詞
- 使用OpenAI的JSON模式確保輸出格式
- 低溫度設置確保格式一致性

### 論述格式化方法 (第144-169行)

```python
    async def _format_to_narrative(self, task: FormattingTask) -> str:
        """格式化為論述格式"""

        # 構建論述格式提示詞
        narrative_prompt = self._build_narrative_prompt(task)

        # 調用GPT-4o進行格式化
        messages = [
            {
                "role": "system",
                "content": self._get_narrative_system_prompt()
            },
            {
                "role": "user",
                "content": narrative_prompt
            }
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=0.3,  # 稍高的溫度讓論述更自然
        )

        return response.choices[0].message.content
```
**用意**: 
- 專門處理論述格式化的方法
- 使用專門的論述系統提示詞
- 稍高的溫度（0.3）讓文字更自然流暢
- 不使用JSON模式，允許自由文本生成

### JSON模板生成方法 (第171-241行)

```python
    def _get_json_template(self, domain_type: str) -> Dict[str, Any]:
        """獲取JSON模板"""
        
        base_template = {
            "analysis_type": domain_type,
            "timestamp": "2025-07-11T00:00:00Z",
            "success": True,
            "data": {}
        }
```
**用意**: 
- 定義基礎JSON模板結構
- 包含分析類型、時間戳、成功狀態
- 為不同領域提供統一的基礎結構

```python
        if domain_type == "love":
            base_template["data"] = {
                "overall_rating": 0,
                "love_fortune": {
                    "strengths": [],
                    "challenges": [],
                    "ideal_partner": "",
                    "best_timing": "",
                    "compatibility_factors": []
                },
                "detailed_analysis": "",
                "suggestions": [],
                "precautions": []
            }
```
**用意**: 
- 愛情運勢專用的JSON結構
- 包含優勢、挑戰、理想伴侶等專業欄位
- 提供完整的感情分析框架

```python
        elif domain_type == "wealth":
            base_template["data"] = {
                "overall_rating": 0,
                "wealth_fortune": {
                    "wealth_source": "",
                    "career_direction": [],
                    "investment_style": "",
                    "peak_periods": [],
                    "financial_strengths": []
                },
                "detailed_analysis": "",
                "suggestions": [],
                "precautions": []
            }
```
**用意**: 
- 財運事業專用的JSON結構
- 包含財源、職業方向、投資風格等專業欄位
- 提供完整的財運分析框架

```python
        elif domain_type == "future":
            base_template["data"] = {
                "overall_rating": 0,
                "future_fortune": {
                    "current_phase": "",
                    "next_5_years": "",
                    "turning_points": [],
                    "health_fortune": "",
                    "family_fortune": "",
                    "career_development": ""
                },
                "detailed_analysis": "",
                "suggestions": [],
                "precautions": []
            }
```
**用意**: 
- 未來運勢專用的JSON結構
- 包含當前階段、未來五年、轉折點等時間性分析
- 涵蓋健康、家庭、事業等全面運勢

```python
        else:  # general
            base_template["data"] = {
                "overall_rating": 0,
                "comprehensive_analysis": {
                    "personality_traits": [],
                    "life_pattern": "",
                    "major_influences": [],
                    "development_potential": ""
                },
                "detailed_analysis": "",
                "suggestions": [],
                "precautions": []
            }
        
        return base_template
```
**用意**: 
- 綜合分析的默認JSON結構
- 包含性格特質、人生格局、主要影響等
- 提供全面的命盤分析框架

## 程式碼架構總結

### 設計模式
1. **策略模式**: 根據輸出格式選擇不同的處理策略
2. **模板方法**: 使用JSON模板確保輸出結構一致
3. **異步編程**: 全面使用async/await模式
4. **數據類**: 使用dataclass簡化數據結構

### 主要特點
- 支援多種輸出格式（JSON、論述、混合）
- 領域特化的JSON模板
- 完整的格式驗證機制
- 詳細的元數據追蹤

## 詳細方法解析（續）

### 格式化提示詞構建方法 (第243-276行)

```python
    def _build_format_prompt(self, task: FormattingTask, template: Dict[str, Any]) -> str:
        """構建格式化提示詞"""

        prompt = f"""請將以下紫微斗數分析內容格式化為標準JSON格式：

原始分析內容：
{task.content}

領域類型：{task.domain_type}

JSON模板結構：
{json.dumps(template, ensure_ascii=False, indent=2)}

格式化要求：
1. 嚴格按照模板結構組織內容
2. 從原始分析中提取關鍵信息填入對應欄位
3. overall_rating 使用1-10的評分
4. 陣列欄位要包含具體的項目
5. 確保所有字符串欄位都有內容
6. 保持專業性和準確性
7. 使用繁體中文

特別注意：
- suggestions 應包含3-5個實用建議
- precautions 應包含2-3個注意事項
- detailed_analysis 應該是完整的分析總結
- 所有評分和時間預測要合理

請直接返回格式化後的JSON，不要包含其他說明文字。"""

        if task.user_profile:
            prompt += f"\n\n用戶背景：{task.user_profile}\n請根據用戶特點調整建議內容。"

        return prompt
```
**用意**:
- 構建詳細的JSON格式化指令
- 包含原始內容、領域類型和模板結構
- 提供明確的格式化要求和評分標準
- 支援用戶背景信息的個性化調整
- 確保輸出的專業性和實用性

### 論述提示詞構建方法 (第278-364行)

```python
    def _build_narrative_prompt(self, task: FormattingTask) -> str:
        """構建論述格式提示詞"""

        domain_descriptions = {
            "love": "感情運勢",
            "wealth": "財運事業",
            "future": "未來運勢",
            "comprehensive": "綜合命盤"
        }

        domain_desc = domain_descriptions.get(task.domain_type, "命理")

        # 檢查原始內容是否包含結構化的 JSON 分析
        content_analysis = self._analyze_content_structure(task.content)
```
**用意**:
- 定義不同領域的中文描述
- 分析內容結構以選擇適當的處理方式
- 為不同類型的內容提供專門的處理邏輯

```python
        if content_analysis["has_json_structure"]:
            # 如果有結構化分析，使用專門的 JSON 轉論述 prompt
            prompt = f"""請將以下結構化的紫微斗數分析結果轉換成一篇完整、流暢的{domain_desc}分析論述：

結構化分析內容：
{task.content}

領域類型：{task.domain_type}

轉換要求：
1. 將 JSON 結構化數據轉換為自然流暢的中文論述
2. 保留所有重要的分析要點和建議
3. 按照以下結構組織內容：
   - 開頭：命盤整體印象和評分說明
   - 主體：詳細分析（根據領域特色展開）
   - 建議：實用的人生指導
   - 結尾：注意事項和鼓勵話語

4. 語調溫和專業，富有人文關懷
5. 字數控制在800-1200字之間
6. 使用繁體中文
7. **使用 Markdown 格式撰寫**

格式要求：
- 使用 ## 作為主要章節標題（如：## 命盤整體印象）
- 使用 ### 作為次級標題（如：### 詳細分析）
- 使用 **粗體** 強調重要內容
- 使用適當的段落分隔，讓內容易於閱讀

特別注意：
- 將評分轉換為文字描述（如：7分 → "整體運勢相當不錯"）
- 將陣列項目自然融入段落中
- 保持專業術語的準確性
- 讓讀者感受到個人化的關懷

請撰寫一篇溫暖、專業、易懂的 Markdown 格式命理分析論述。"""
```
**用意**:
- 專門處理結構化JSON轉論述的情況
- 提供詳細的轉換要求和格式規範
- 強調Markdown格式的使用
- 注重人文關懷和個性化表達
- 將技術性數據轉為易懂的文字描述

```python
        else:
            # 原來的 prompt（處理非結構化內容）
            prompt = f"""請將以下紫微斗數分析內容整理成一篇完整、流暢的{domain_desc}分析論述：

原始分析內容：
{task.content}

領域類型：{task.domain_type}

論述要求：
1. 以自然流暢的中文撰寫，避免條列式表達
2. 結構清晰，包含：命盤概述、詳細分析、人生建議、注意事項
3. 語調溫和專業，富有人文關懷
4. 融合傳統命理智慧與現代生活實用性
5. 字數控制在800-1200字之間
6. 使用繁體中文
7. **使用 Markdown 格式撰寫**

格式要求：
- 使用 ## 作為主要章節標題（如：## 命盤整體印象）
- 使用 ### 作為次級標題（如：### 詳細分析）
- 使用 **粗體** 強調重要內容
- 使用適當的段落分隔，讓內容易於閱讀

論述結構建議：
- 開頭：簡要介紹命盤特色和整體印象
- 主體：深入分析性格特質、運勢走向、人生格局
- 建議：提供具體可行的人生指導
- 結尾：溫馨提醒和鼓勵話語

請撰寫一篇完整的 Markdown 格式命理分析論述，讓讀者能夠深入理解自己的命盤特色。"""

        if task.user_profile:
            prompt += f"\n\n用戶背景：{task.user_profile}\n請根據用戶特點調整論述內容和建議。"

        return prompt
```
**用意**:
- 處理非結構化內容的論述生成
- 提供完整的論述結構建議
- 強調傳統智慧與現代實用性的結合
- 支援用戶背景的個性化調整

### 內容結構分析方法 (第366-385行)

```python
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """分析內容結構，判斷是否包含 JSON 結構化數據"""

        # 檢查是否包含 JSON 關鍵字
        json_indicators = [
            "overall_rating", "detailed_analysis", "suggestions",
            "precautions", "love_fortune", "wealth_fortune",
            "future_fortune", "comprehensive_analysis"
        ]

        has_json_structure = any(indicator in content for indicator in json_indicators)

        # 檢查是否包含 Agent 標識
        has_agent_responses = any(agent in content for agent in ["Claude Agent", "GPT Agent", "Domain Agent"])

        return {
            "has_json_structure": has_json_structure,
            "has_agent_responses": has_agent_responses,
            "content_length": len(content)
        }
```
**用意**:
- 智能分析輸入內容的結構類型
- 檢測JSON關鍵字以判斷是否為結構化數據
- 識別多代理系統的回應標識
- 提供內容長度等統計信息
- 為選擇適當的處理策略提供依據

### 系統提示詞方法 (第387-434行)

```python
    def _get_narrative_system_prompt(self) -> str:
        """獲取論述格式的系統提示詞"""

        return """你是一位資深的紫微斗數命理師，擅長將複雜的命盤分析轉化為溫暖、易懂的人生指導。

你的寫作特色：
1. 文筆優美流暢，富有文學性和感染力
2. 深入淺出，將專業術語轉化為生活化的表達
3. 充滿人文關懷，給予讀者溫暖和希望
4. 理論與實踐並重，提供具體可行的建議
5. 保持客觀理性，避免過於絕對的預測

寫作原則：
- 以讀者為中心，關注其內心需求和人生困惑
- 用故事化的方式呈現命理分析
- 強調個人成長和自我實現的可能性
- 提供正面積極的人生態度和價值觀
- 語言親切自然，如同面對面的深度對話

格式要求：
- 使用 Markdown 格式撰寫
- 使用 ## 作為主要章節標題（如：## 命盤整體印象）
- 使用 ### 作為次級標題（如：### 詳細分析）
- 使用 **粗體** 強調重要內容
- 使用適當的段落分隔，讓內容易於閱讀
- 保持 Markdown 語法的正確性

請撰寫一篇完整、深入、溫暖的 Markdown 格式命理分析論述。"""
```
**用意**:
- 定義論述格式化的AI角色和特色
- 強調人文關懷和溫暖的寫作風格
- 提供明確的寫作原則和格式要求
- 確保輸出的專業性和可讀性
- 注重讀者體驗和情感連接

```python
    def _get_system_prompt(self) -> str:
        """獲取系統提示詞"""

        return """你是一個專業的JSON格式化專家，專門負責將紫微斗數分析結果格式化為標準JSON格式。

你的任務：
1. 將非結構化的分析文本轉換為結構化的JSON
2. 確保JSON格式完全正確且可解析
3. 保持原始分析的準確性和專業性
4. 按照指定的模板結構組織內容

格式化原則：
- 嚴格遵循JSON語法規則
- 使用雙引號包圍所有字符串
- 確保數字格式正確
- 陣列和物件結構完整
- 避免特殊字符導致的解析錯誤

請始終返回有效的JSON格式，不包含任何額外的說明或標記。"""
```
**用意**:
- 定義JSON格式化的AI角色和任務
- 強調格式正確性和可解析性
- 提供明確的格式化原則
- 確保輸出的技術規範性

### JSON格式驗證方法 (第436-469行)

```python
    async def _validate_json_format(self, json_content: str) -> bool:
        """驗證JSON格式"""

        try:
            # 嘗試解析JSON
            parsed = json.loads(json_content)

            # 檢查必要欄位
            required_fields = ["analysis_type", "timestamp", "success", "data"]
            for field in required_fields:
                if field not in parsed:
                    self.logger.warning(f"Missing required field: {field}")
                    return False

            # 檢查data欄位結構
            data = parsed.get("data", {})
            if not isinstance(data, dict):
                self.logger.warning("Data field is not a dictionary")
                return False

            # 檢查評分範圍
            overall_rating = data.get("overall_rating", 0)
            if not isinstance(overall_rating, (int, float)) or not (1 <= overall_rating <= 10):
                self.logger.warning(f"Invalid overall_rating: {overall_rating}")
                return False

            return True

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"JSON validation failed: {str(e)}")
            return False
```
**用意**:
- 完整的JSON格式驗證機制
- 檢查JSON語法正確性
- 驗證必要欄位的存在
- 檢查數據類型和值範圍
- 詳細的錯誤日誌記錄
- 確保輸出符合預期格式

### 簡單回應格式化方法 (第471-515行)

```python
    async def format_simple_response(self,
                                   content: str,
                                   response_type: str = "general") -> FormattedOutput:
        """格式化簡單回應"""

        start_time = time.time()

        try:
            simple_template = {
                "response_type": response_type,
                "timestamp": "2025-07-11T00:00:00Z",
                "success": True,
                "content": content,
                "metadata": {
                    "formatted_by": "gpt-4o",
                    "processing_time": 0
                }
            }

            formatted_content = json.dumps(simple_template, ensure_ascii=False, indent=2)
            processing_time = time.time() - start_time

            return FormattedOutput(
                success=True,
                formatted_content=formatted_content,
                metadata={
                    "model": self.model,
                    "response_type": response_type
                },
                processing_time=processing_time,
                validation_passed=True
            )

        except Exception as e:
            self.logger.error(f"Simple formatting failed: {str(e)}")

            return FormattedOutput(
                success=False,
                formatted_content=json.dumps({
                    "error": "簡單格式化失敗",
                    "message": str(e)
                }, ensure_ascii=False, indent=2),
                metadata={"error": str(e)},
                processing_time=time.time() - start_time
            )
```
**用意**:
- 提供簡單內容的快速格式化
- 不需要複雜的AI處理
- 使用預定義的簡單模板
- 適用於錯誤訊息或狀態回應
- 保持與主要格式化方法的一致性

### 資源清理方法 (第517-524行)

```python
    async def cleanup(self):
        """清理格式化器資源"""
        try:
            if hasattr(self.client, 'close'):
                await self.client.close()
            self.logger.info("GPT4oFormatter 資源清理完成")
        except Exception as e:
            self.logger.error(f"GPT4oFormatter 清理失敗: {str(e)}")
```
**用意**:
- 正確清理OpenAI客戶端資源
- 防止資源洩漏
- 記錄清理狀態
- 異常處理確保清理過程的穩定性

### 全域實例和便利函數 (第526-538行)

```python
# 全域格式化器實例
gpt4o_formatter = GPT4oFormatter()

async def format_final_output(coordination_result: CoordinationResult,
                            domain_type: str,
                            user_profile: Optional[Dict[str, Any]] = None) -> FormattedOutput:
    """格式化最終輸出的便利函數"""

    return await gpt4o_formatter.format_coordination_result(
        coordination_result,
        domain_type,
        user_profile
    )
```
**用意**:
- 提供全域的格式化器實例
- 簡化外部調用接口
- 封裝複雜的參數傳遞
- 提供模組級別的便利函數

## 整體架構分析

### 設計原則
1. **多格式支援**:
   - JSON結構化輸出
   - Markdown論述格式
   - 混合模式（JSON轉論述）

2. **領域特化**:
   - 愛情運勢專用模板
   - 財運事業專用模板
   - 未來運勢專用模板
   - 綜合分析通用模板

3. **智能處理**:
   - 內容結構自動分析
   - 適應性提示詞選擇
   - 個性化用戶調整

4. **品質保證**:
   - 完整的格式驗證
   - 詳細的錯誤處理
   - 處理時間追蹤

### 技術亮點
1. **AI驅動格式化**:
   - 使用GPT-4o進行智能格式化
   - 低溫度確保一致性
   - JSON模式確保格式正確

2. **模板系統**:
   - 領域特化的JSON模板
   - 靈活的結構定義
   - 標準化的輸出格式

3. **內容分析**:
   - 智能識別內容類型
   - 自適應處理策略
   - 結構化數據檢測

4. **人文關懷**:
   - 溫暖的論述風格
   - 個性化建議調整
   - 專業與易懂的平衡

### 使用場景
- Multi-Agent系統的最終輸出格式化
- 紫微斗數分析結果標準化
- 用戶友好的論述生成
- API回應的統一格式化

### 擴展可能性
- 支援更多輸出格式（PDF、HTML等）
- 添加多語言支援
- 實現批量格式化
- 集成模板自定義功能
- 添加格式化品質評估

## 總結
這個GPT-4o格式化器實現了完整的多格式輸出系統，從結構化JSON到人文關懷的論述格式，展現了現代AI應用的技術深度和人文溫度。代碼設計精良，功能完備，具有很好的擴展性和實用價值，是一個高質量的格式化解決方案。
