"""
GPT-4o 輸出格式化器
負責將Multi-Agent的分析結果格式化為最終的JSON輸出
"""

import json
import asyncio
import time
from typing import Dict, Any, List, Optional
import openai
from dataclasses import dataclass

from ..config.settings import get_settings
from ..agents.coordinator import CoordinationResult

settings = get_settings()

@dataclass
class FormattingTask:
    """格式化任務"""
    content: str
    domain_type: str
    output_format: str = "json"
    user_profile: Optional[Dict[str, Any]] = None

@dataclass
class FormattedOutput:
    """格式化輸出"""
    success: bool
    formatted_content: str
    metadata: Dict[str, Any]
    processing_time: float
    validation_passed: bool = False

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
        
    async def format_coordination_result(self,
                                       coordination_result: CoordinationResult,
                                       domain_type: str,
                                       user_profile: Optional[Dict[str, Any]] = None,
                                       output_format: str = "json") -> FormattedOutput:
        """格式化協調結果"""
        
        start_time = time.time()
        
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

        # 修復編號格式問題
        formatted_text = self._fix_numbering_format(response.choices[0].message.content)

        return formatted_text

    def _fix_numbering_format(self, text: str) -> str:
        """修復編號格式問題，確保編號連續"""
        import re

        lines = text.split('\n')
        fixed_lines = []
        current_number = 1

        for line in lines:
            # 檢查是否為編號行
            match = re.match(r'^(\s*)(\d+)\.\s+(.+)', line)
            if match:
                indent = match.group(1)
                original_number = int(match.group(2))
                content = match.group(3)

                # 如果原始編號是1，但當前編號不是1，說明可能是重新開始的編號
                if original_number == 1 and current_number > 1:
                    # 檢查是否真的是新的列表開始（通過檢查前面的內容）
                    # 如果前面有標題或空行，可能是新列表
                    prev_lines = fixed_lines[-3:] if len(fixed_lines) >= 3 else fixed_lines
                    has_section_break = any(
                        line.strip().startswith('#') or
                        '**' in line or
                        line.strip() == '' or
                        any(keyword in line for keyword in ['建議', '注意', '提醒', '指導'])
                        for line in prev_lines
                    )

                    if not has_section_break:
                        # 不是新列表，繼續編號
                        fixed_line = f"{indent}{current_number}. {content}"
                    else:
                        # 是新列表，但仍然繼續編號以保持一致性
                        fixed_line = f"{indent}{current_number}. {content}"
                else:
                    # 使用當前編號
                    fixed_line = f"{indent}{current_number}. {content}"

                fixed_lines.append(fixed_line)
                current_number += 1
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _get_json_template(self, domain_type: str) -> Dict[str, Any]:
        """獲取JSON模板"""
        
        base_template = {
            "analysis_type": domain_type,
            "timestamp": "2025-07-11T00:00:00Z",
            "success": True,
            "data": {}
        }
        
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
- suggestions 應包含3-5個實用建議，每個建議都是完整的句子
- precautions 應包含2-3個注意事項，每個注意事項都是完整的句子
- detailed_analysis 應該是完整的分析總結
- 所有評分和時間預測要合理
- 建議和注意事項不要包含編號，只需要純文字內容

請直接返回格式化後的JSON，不要包含其他說明文字。"""

        if task.user_profile:
            prompt += f"\n\n用戶背景：{task.user_profile}\n請根據用戶特點調整建議內容。"
        
        return prompt

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
- 對於建議和注意事項，使用連續的編號格式，不要在不同段落中重新開始編號

特別注意編號格式：
- 如果有多個列表段落（如建議、注意事項），編號必須連續進行
- 例如：建議部分用1.2.3.4.5.，注意事項部分接續用6.7.8.
- 絕對不要在新段落中重新從1.開始編號
- 將評分轉換為文字描述（如：7分 → "整體運勢相當不錯"）
- 將陣列項目自然融入段落中，如果是建議列表請使用連續的編號格式
- 保持專業術語的準確性
- 讓讀者感受到個人化的關懷

請撰寫一篇溫暖、專業、易懂的 Markdown 格式命理分析論述。"""
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

    async def cleanup(self):
        """清理格式化器資源"""
        try:
            if hasattr(self.client, 'close'):
                await self.client.close()
            self.logger.info("GPT4oFormatter 資源清理完成")
        except Exception as e:
            self.logger.error(f"GPT4oFormatter 清理失敗: {str(e)}")

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
