"""
Claude MCP 客戶端
整合Claude MCP服務來調用紫微斗數工具
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
from ..config.settings import get_settings

settings = get_settings()

@dataclass
class MCPToolCall:
    """MCP工具調用"""
    name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None

@dataclass
class MCPToolResult:
    """MCP工具結果"""
    call_id: str
    content: Any
    is_error: bool = False
    error_message: Optional[str] = None

class ClaudeMCPClient:
    """Claude MCP 客戶端"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = f"http://{settings.mcp.server_host}:{settings.mcp.server_port}"
        self.timeout = settings.mcp.timeout
        self.session = None
        
    async def __aenter__(self):
        """異步上下文管理器進入"""
        self.session = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        if self.session:
            await self.session.aclose()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用的MCP工具"""
        try:
            response = await self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            
            tools_data = response.json()
            self.logger.info(f"Available MCP tools: {len(tools_data.get('tools', []))}")
            
            return tools_data.get('tools', [])
            
        except Exception as e:
            self.logger.error(f"Failed to list MCP tools: {str(e)}")
            return []
    
    async def call_tool(self, tool_call: MCPToolCall) -> MCPToolResult:
        """調用MCP工具"""
        try:
            payload = {
                "name": tool_call.name,
                "arguments": tool_call.arguments
            }
            
            if tool_call.call_id:
                payload["call_id"] = tool_call.call_id
            
            self.logger.info(f"Calling MCP tool: {tool_call.name}")
            
            response = await self.session.post(
                f"{self.base_url}/tools/call",
                json=payload
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            return MCPToolResult(
                call_id=tool_call.call_id or "default",
                content=result_data.get('content'),
                is_error=result_data.get('is_error', False),
                error_message=result_data.get('error_message')
            )
            
        except Exception as e:
            self.logger.error(f"MCP tool call failed: {str(e)}")
            return MCPToolResult(
                call_id=tool_call.call_id or "default",
                content=None,
                is_error=True,
                error_message=str(e)
            )
    
    async def get_ziwei_chart(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """獲取紫微斗數命盤"""
        tool_call = MCPToolCall(
            name="ziwei_chart",
            arguments=birth_data,
            call_id="ziwei_chart_call"
        )
        
        result = await self.call_tool(tool_call)
        
        if result.is_error:
            return {
                "success": False,
                "error": result.error_message,
                "data": None
            }
        
        return {
            "success": True,
            "data": result.content,
            "call_id": result.call_id
        }
    
    async def parse_web_content(self, html_content: str) -> Dict[str, Any]:
        """解析網頁內容"""
        tool_call = MCPToolCall(
            name="data_parser",
            arguments={"html_content": html_content, "parser_type": "ziwei"},
            call_id="parse_content_call"
        )
        
        result = await self.call_tool(tool_call)
        
        if result.is_error:
            return {
                "success": False,
                "error": result.error_message,
                "data": None
            }
        
        return {
            "success": True,
            "data": result.content,
            "call_id": result.call_id
        }
    
    async def scrape_website(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """爬取網站數據"""
        tool_call = MCPToolCall(
            name="web_scraper",
            arguments={"url": url, "params": params},
            call_id="web_scrape_call"
        )
        
        result = await self.call_tool(tool_call)
        
        if result.is_error:
            return {
                "success": False,
                "error": result.error_message,
                "data": None
            }
        
        return {
            "success": True,
            "data": result.content,
            "call_id": result.call_id
        }

class MCPToolRegistry:
    """MCP工具註冊表"""
    
    def __init__(self):
        self.tools = {}
        self.logger = logging.getLogger(__name__)
    
    def register_tool(self, name: str, tool_definition: Dict[str, Any]):
        """註冊MCP工具"""
        self.tools[name] = tool_definition
        self.logger.info(f"Registered MCP tool: {name}")
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """獲取工具定義"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有工具名稱"""
        return list(self.tools.keys())
    
    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """獲取工具的JSON Schema"""
        tool = self.get_tool(name)
        if not tool:
            return None
        
        return {
            "name": name,
            "description": tool.get("description", ""),
            "parameters": tool.get("parameters", {})
        }

# 全域工具註冊表
mcp_registry = MCPToolRegistry()

# 註冊紫微斗數工具
mcp_registry.register_tool("ziwei_chart", {
    "description": "獲取紫微斗數命盤分析",
    "parameters": {
        "type": "object",
        "properties": {
            "gender": {
                "type": "string",
                "description": "性別（男/女）",
                "enum": ["男", "女"]
            },
            "birth_year": {
                "type": "integer",
                "description": "出生年份（西元年）",
                "minimum": 1900,
                "maximum": 2100
            },
            "birth_month": {
                "type": "integer",
                "description": "出生月份",
                "minimum": 1,
                "maximum": 12
            },
            "birth_day": {
                "type": "integer",
                "description": "出生日期",
                "minimum": 1,
                "maximum": 31
            },
            "birth_hour": {
                "type": "string",
                "description": "出生時辰（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）"
            }
        },
        "required": ["gender", "birth_year", "birth_month", "birth_day", "birth_hour"]
    }
})

# 註冊網頁爬取工具
mcp_registry.register_tool("web_scraper", {
    "description": "爬取網站數據",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "目標網站URL"
            },
            "params": {
                "type": "object",
                "description": "請求參數"
            }
        },
        "required": ["url"]
    }
})

# 註冊數據解析工具
mcp_registry.register_tool("data_parser", {
    "description": "解析網頁或數據內容",
    "parameters": {
        "type": "object",
        "properties": {
            "html_content": {
                "type": "string",
                "description": "HTML內容"
            },
            "parser_type": {
                "type": "string",
                "description": "解析器類型",
                "enum": ["ziwei", "general"]
            }
        },
        "required": ["html_content", "parser_type"]
    }
})

async def test_mcp_connection():
    """測試MCP連接"""
    async with ClaudeMCPClient() as client:
        tools = await client.list_tools()
        print(f"Available tools: {[tool.get('name') for tool in tools]}")
        return len(tools) > 0
