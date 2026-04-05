"""
ReAct Agent 核心實現
實現 Action-Reasoning-Observation 循環邏輯
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    """Agent可執行的動作類型"""
    VALIDATE_INPUT = "validate_input"
    CALL_MCP_TOOL = "call_mcp_tool"
    QUERY_RAG = "query_rag"
    GENERATE_RESPONSE = "generate_response"
    FORMAT_OUTPUT = "format_output"

@dataclass
class AgentState:
    """Agent狀態"""
    current_step: int = 0
    user_input: Dict[str, Any] = None
    mcp_result: Dict[str, Any] = None
    rag_context: List[str] = None
    reasoning_log: List[str] = None
    observations: List[str] = None
    final_response: Dict[str, Any] = None

class ReActAgent:
    """
    ReAct Agent 主要類別
    實現 Reasoning and Acting 的循環邏輯
    """
    
    def __init__(self, mcp_client, rag_system, claude_client, logger=None):
        self.mcp_client = mcp_client
        self.rag_system = rag_system
        self.claude_client = claude_client
        self.logger = logger or logging.getLogger(__name__)
        self.state = AgentState()
        self.max_iterations = 10
        
    def reset_state(self):
        """重置Agent狀態"""
        self.state = AgentState()
        self.state.reasoning_log = []
        self.state.observations = []
    
    def reason(self, context: str) -> str:
        """
        推理步驟：分析當前情況並決定下一步行動
        """
        reasoning_prompt = f"""
        當前情況：{context}
        
        請分析當前狀況並決定下一步最合適的行動。
        
        可選行動：
        1. VALIDATE_INPUT - 驗證用戶輸入
        2. CALL_MCP_TOOL - 調用MCP工具獲取紫微斗數
        3. QUERY_RAG - 查詢RAG知識庫
        4. GENERATE_RESPONSE - 生成最終回應
        5. FORMAT_OUTPUT - 格式化輸出
        
        請說明你的推理過程和選擇的行動。
        """
        
        reasoning = self._internal_reasoning(reasoning_prompt)
        self.state.reasoning_log.append(reasoning)
        self.logger.info(f"Reasoning: {reasoning}")
        return reasoning
    
    def act(self, action_type: ActionType, **kwargs) -> Any:
        """
        執行行動
        """
        self.logger.info(f"Executing action: {action_type.value}")
        
        if action_type == ActionType.VALIDATE_INPUT:
            return self._validate_input(kwargs.get('user_input'))
        
        elif action_type == ActionType.CALL_MCP_TOOL:
            return self._call_mcp_tool(kwargs.get('birth_data'))
        
        elif action_type == ActionType.QUERY_RAG:
            return self._query_rag(kwargs.get('query'))
        
        elif action_type == ActionType.GENERATE_RESPONSE:
            return self._generate_response(kwargs.get('domain_type'))
        
        elif action_type == ActionType.FORMAT_OUTPUT:
            return self._format_output(kwargs.get('response'))
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    def observe(self, action_result: Any, action_type: ActionType) -> str:
        """
        觀察行動結果
        """
        observation = f"Action {action_type.value} completed. "
        
        if action_type == ActionType.VALIDATE_INPUT:
            if action_result.get('valid'):
                observation += "Input validation successful."
                self.state.user_input = action_result['data']
            else:
                observation += f"Input validation failed: {action_result.get('error')}"
        
        elif action_type == ActionType.CALL_MCP_TOOL:
            if action_result.get('success'):
                observation += "MCP tool call successful. Retrieved ziwei chart data."
                self.state.mcp_result = action_result['data']
            else:
                observation += f"MCP tool call failed: {action_result.get('error')}"
        
        elif action_type == ActionType.QUERY_RAG:
            if action_result.get('success'):
                observation += f"RAG query successful. Retrieved {len(action_result['documents'])} relevant documents."
                self.state.rag_context = action_result['documents']
            else:
                observation += f"RAG query failed: {action_result.get('error')}"
        
        elif action_type == ActionType.GENERATE_RESPONSE:
            if action_result.get('success'):
                observation += "Response generation successful."
                self.state.final_response = action_result['response']
            else:
                observation += f"Response generation failed: {action_result.get('error')}"
        
        self.state.observations.append(observation)
        self.logger.info(f"Observation: {observation}")
        return observation
    
    def run(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行完整的ReAct循環
        """
        self.reset_state()
        self.logger.info("Starting ReAct agent execution")
        
        # 初始化
        context = f"User request: {user_input}"
        
        for iteration in range(self.max_iterations):
            self.state.current_step = iteration + 1
            self.logger.info(f"ReAct iteration {self.state.current_step}")
            
            # Reasoning
            reasoning = self.reason(context)
            
            # 決定行動
            action_type = self._determine_action(reasoning)
            
            # Acting
            try:
                if action_type == ActionType.VALIDATE_INPUT:
                    result = self.act(action_type, user_input=user_input)
                elif action_type == ActionType.CALL_MCP_TOOL:
                    result = self.act(action_type, birth_data=self.state.user_input)
                elif action_type == ActionType.QUERY_RAG:
                    query = self._generate_rag_query()
                    result = self.act(action_type, query=query)
                elif action_type == ActionType.GENERATE_RESPONSE:
                    result = self.act(action_type, domain_type=user_input.get('domain_type'))
                elif action_type == ActionType.FORMAT_OUTPUT:
                    result = self.act(action_type, response=self.state.final_response)
                    # 格式化完成，返回結果
                    return result
                else:
                    result = {"success": False, "error": "Unknown action"}
                
            except Exception as e:
                self.logger.error(f"Action execution failed: {str(e)}")
                result = {"success": False, "error": str(e)}
            
            # Observation
            observation = self.observe(result, action_type)
            
            # 更新context為下一次推理
            context = f"Previous action: {action_type.value}, Result: {observation}"
            
            # 檢查是否完成
            if action_type == ActionType.FORMAT_OUTPUT and result.get('success'):
                break
        
        # 如果達到最大迭代次數仍未完成
        if self.state.final_response:
            return self.state.final_response
        else:
            return {
                "success": False,
                "error": "Agent execution exceeded maximum iterations",
                "debug_info": {
                    "reasoning_log": self.state.reasoning_log,
                    "observations": self.state.observations
                }
            }
    
    def _internal_reasoning(self, prompt: str) -> str:
        """內部推理邏輯（簡化版）"""
        # 這裡可以使用簡單的規則或調用LLM進行推理
        # 為了示例，使用簡化的規則推理
        
        if not self.state.user_input:
            return "Need to validate user input first. Action: VALIDATE_INPUT"
        elif not self.state.mcp_result:
            return "Need to get ziwei chart data. Action: CALL_MCP_TOOL"
        elif not self.state.rag_context:
            return "Need to query knowledge base. Action: QUERY_RAG"
        elif not self.state.final_response:
            return "Need to generate response. Action: GENERATE_RESPONSE"
        else:
            return "Need to format output. Action: FORMAT_OUTPUT"
    
    def _determine_action(self, reasoning: str) -> ActionType:
        """根據推理結果決定行動"""
        if "VALIDATE_INPUT" in reasoning:
            return ActionType.VALIDATE_INPUT
        elif "CALL_MCP_TOOL" in reasoning:
            return ActionType.CALL_MCP_TOOL
        elif "QUERY_RAG" in reasoning:
            return ActionType.QUERY_RAG
        elif "GENERATE_RESPONSE" in reasoning:
            return ActionType.GENERATE_RESPONSE
        elif "FORMAT_OUTPUT" in reasoning:
            return ActionType.FORMAT_OUTPUT
        else:
            return ActionType.VALIDATE_INPUT  # 默認行動
    
    def _validate_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """驗證用戶輸入"""
        required_fields = ['gender', 'birth_year', 'birth_month', 'birth_day', 'birth_hour', 'domain_type']
        
        for field in required_fields:
            if field not in user_input:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # 驗證數據格式
        try:
            year = int(user_input['birth_year'])
            month = int(user_input['birth_month'])
            day = int(user_input['birth_day'])
            
            if not (1900 <= year <= 2100):
                return {"valid": False, "error": "Invalid birth year"}
            if not (1 <= month <= 12):
                return {"valid": False, "error": "Invalid birth month"}
            if not (1 <= day <= 31):
                return {"valid": False, "error": "Invalid birth day"}
                
        except ValueError:
            return {"valid": False, "error": "Invalid date format"}
        
        return {"valid": True, "data": user_input}
    
    def _call_mcp_tool(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """調用MCP工具"""
        try:
            result = self.mcp_client.get_ziwei_chart(birth_data)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _query_rag(self, query: str) -> Dict[str, Any]:
        """查詢RAG系統"""
        try:
            documents = self.rag_system.search(query, top_k=5)
            return {"success": True, "documents": documents}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_response(self, domain_type: str) -> Dict[str, Any]:
        """生成最終回應"""
        try:
            # 準備prompt和數據
            from ..prompts.system_prompts import get_full_prompt_chain
            
            prompts = get_full_prompt_chain(domain_type)
            context = {
                "ziwei_data": self.state.mcp_result,
                "knowledge_context": self.state.rag_context
            }
            
            response = self.claude_client.generate_response(prompts, context)
            return {"success": True, "response": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_output(self, response: Any) -> Dict[str, Any]:
        """格式化輸出"""
        try:
            # 確保輸出是有效的JSON格式
            if isinstance(response, str):
                formatted_response = json.loads(response)
            else:
                formatted_response = response
            
            return {
                "success": True,
                "data": formatted_response,
                "metadata": {
                    "reasoning_steps": len(self.state.reasoning_log),
                    "observations": len(self.state.observations)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Output formatting failed: {str(e)}"}
    
    def _generate_rag_query(self) -> str:
        """生成RAG查詢語句"""
        if self.state.mcp_result:
            # 根據紫微斗數結果生成查詢
            main_stars = self.state.mcp_result.get('main_stars', [])
            query = f"紫微斗數 {' '.join(main_stars)} 解釋 分析"
            return query
        else:
            return "紫微斗數 基本概念"
