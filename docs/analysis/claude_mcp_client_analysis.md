# claude_mcp_client.py 逐行解析文檔

## 檔案概述
這是一個Claude MCP（Model Context Protocol）客戶端實現，用於整合Claude MCP服務來調用紫微斗數工具。該檔案實現了完整的MCP客戶端功能，包括工具調用、數據解析和工具註冊管理。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-14行)

```python
"""
Claude MCP 客戶端
整合Claude MCP服務來調用紫微斗數工具
"""
```
**用意**: 檔案說明文檔，描述此客戶端的主要功能

```python
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
from ..config.settings import get_settings
```
**用意**: 導入必要的模組
- `json`: JSON數據處理
- `asyncio`: 異步編程支援
- `logging`: 日誌記錄
- `typing`: 類型提示
- `dataclasses`: 數據類裝飾器
- `httpx`: 現代異步HTTP客戶端
- `settings`: 項目配置設定

```python
settings = get_settings()
```
**用意**: 獲取全域配置設定，用於後續的服務器連接配置

### 數據類定義 (第16-29行)

```python
@dataclass
class MCPToolCall:
    """MCP工具調用"""
    name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None
```
**用意**: 
- 定義MCP工具調用的數據結構
- `name`: 工具名稱
- `arguments`: 工具參數字典
- `call_id`: 可選的調用ID，用於追蹤請求

```python
@dataclass
class MCPToolResult:
    """MCP工具結果"""
    call_id: str
    content: Any
    is_error: bool = False
    error_message: Optional[str] = None
```
**用意**: 
- 定義MCP工具執行結果的數據結構
- `call_id`: 對應的調用ID
- `content`: 執行結果內容
- `is_error`: 是否發生錯誤
- `error_message`: 錯誤訊息（如果有）

### ClaudeMCPClient 類定義與初始化 (第31-38行)

```python
class ClaudeMCPClient:
    """Claude MCP 客戶端"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = f"http://{settings.mcp.server_host}:{settings.mcp.server_port}"
        self.timeout = settings.mcp.timeout
        self.session = None
```
**用意**: 
- 定義主要的MCP客戶端類
- 設置日誌記錄器
- 從配置中構建服務器URL
- 設置請求超時時間
- 初始化HTTP會話為None（稍後創建）

### 異步上下文管理器 (第40-48行)

```python
    async def __aenter__(self):
        """異步上下文管理器進入"""
        self.session = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        if self.session:
            await self.session.aclose()
```
**用意**: 
- 實現異步上下文管理器協議
- 進入時創建httpx異步客戶端
- 退出時正確關閉HTTP會話
- 確保資源的正確管理和清理

### 工具列表方法 (第50-63行)

```python
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
```
**用意**: 
- 異步獲取服務器上可用的MCP工具列表
- 發送GET請求到 `/tools` 端點
- 檢查HTTP狀態碼
- 解析JSON回應並提取工具列表
- 記錄可用工具數量
- 異常處理：失敗時返回空列表

### 工具調用方法 (第65-100行)

```python
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
```
**用意**: 
- 構建工具調用的請求負載
- 包含工具名稱和參數
- 可選地包含調用ID
- 記錄工具調用日誌

```python
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
```
**用意**: 
- 發送POST請求到 `/tools/call` 端點
- 使用JSON格式發送負載
- 檢查HTTP狀態碼
- 解析回應並創建MCPToolResult對象
- 提供默認調用ID如果未指定

```python
        except Exception as e:
            self.logger.error(f"MCP tool call failed: {str(e)}")
            return MCPToolResult(
                call_id=tool_call.call_id or "default",
                content=None,
                is_error=True,
                error_message=str(e)
            )
```
**用意**: 
- 捕獲所有異常
- 記錄錯誤日誌
- 返回錯誤狀態的MCPToolResult
- 確保方法總是返回有效結果

### 紫微斗數命盤獲取方法 (第102-123行)

```python
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
```
**用意**: 
- 專門用於紫微斗數命盤獲取的便利方法
- 創建特定的MCPToolCall對象
- 調用通用的call_tool方法
- 標準化返回格式，包含成功狀態
- 提供統一的錯誤處理

### 網頁內容解析方法 (第125-146行)

```python
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
```
**用意**: 
- 專門用於解析HTML內容的便利方法
- 指定解析器類型為"ziwei"
- 遵循相同的錯誤處理模式
- 返回標準化的結果格式

### 網站爬取方法 (第148-169行)

```python
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
```
**用意**: 
- 專門用於網站爬取的便利方法
- 接受URL和參數
- 使用web_scraper工具
- 保持一致的API設計模式

## 程式碼架構總結

### 設計模式
1. **異步編程**: 全面使用async/await模式
2. **上下文管理**: 實現資源自動管理
3. **數據類**: 使用dataclass簡化數據結構
4. **統一接口**: 所有工具調用使用相同模式

### 主要特點
- 完整的異步HTTP客戶端實現
- 標準化的錯誤處理
- 靈活的工具調用機制
- 清晰的數據結構定義

## 詳細方法解析（續）

### MCPToolRegistry 類定義 (第171-201行)

```python
class MCPToolRegistry:
    """MCP工具註冊表"""

    def __init__(self):
        self.tools = {}
        self.logger = logging.getLogger(__name__)
```
**用意**:
- 定義工具註冊表類，用於管理可用的MCP工具
- 使用字典存儲工具定義
- 設置專用的日誌記錄器

```python
    def register_tool(self, name: str, tool_definition: Dict[str, Any]):
        """註冊MCP工具"""
        self.tools[name] = tool_definition
        self.logger.info(f"Registered MCP tool: {name}")
```
**用意**:
- 註冊新的MCP工具到註冊表
- 存儲工具名稱和定義的映射
- 記錄註冊日誌用於追蹤

```python
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """獲取工具定義"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """列出所有工具名稱"""
        return list(self.tools.keys())
```
**用意**:
- 提供工具查詢接口
- get_tool: 根據名稱獲取完整工具定義
- list_tools: 獲取所有已註冊工具的名稱列表

```python
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
```
**用意**:
- 提取工具的JSON Schema格式
- 用於API文檔生成和驗證
- 標準化工具描述格式
- 安全處理不存在的工具

### 全域工具註冊表初始化 (第203-204行)

```python
# 全域工具註冊表
mcp_registry = MCPToolRegistry()
```
**用意**:
- 創建全域的工具註冊表實例
- 提供模組級別的工具管理
- 便於其他模組訪問和使用

### 紫微斗數工具註冊 (第206-242行)

```python
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
```
**用意**:
- 註冊紫微斗數命盤分析工具
- 定義完整的JSON Schema
- 指定每個參數的類型、描述和限制
- 設置必要參數列表
- 提供清晰的API文檔

### 網頁爬取工具註冊 (第244-261行)

```python
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
```
**用意**:
- 註冊網頁爬取工具
- 定義URL和參數的結構
- 只要求URL為必要參數
- 參數字段為可選的對象類型

### 數據解析工具註冊 (第263-281行)

```python
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
```
**用意**:
- 註冊數據解析工具
- 支援HTML內容解析
- 提供解析器類型選擇（ziwei/general）
- 兩個參數都是必要的

### 測試連接函數 (第283-288行)

```python
async def test_mcp_connection():
    """測試MCP連接"""
    async with ClaudeMCPClient() as client:
        tools = await client.list_tools()
        print(f"Available tools: {[tool.get('name') for tool in tools]}")
        return len(tools) > 0
```
**用意**:
- 提供MCP連接測試功能
- 使用異步上下文管理器
- 列出可用工具並顯示
- 返回連接是否成功的布林值

## 整體架構分析

### 設計原則
1. **分離關注點**:
   - ClaudeMCPClient：負責HTTP通信
   - MCPToolRegistry：負責工具管理
   - 數據類：負責數據結構定義

2. **異步優先**:
   - 全面使用async/await
   - 支援高並發操作
   - 非阻塞I/O操作

3. **標準化接口**:
   - 統一的工具調用模式
   - 一致的錯誤處理
   - 標準化的返回格式

4. **配置驅動**:
   - 從設定檔讀取配置
   - 靈活的服務器連接設定
   - 可調整的超時參數

### 技術亮點
1. **現代HTTP客戶端**:
   - 使用httpx替代requests
   - 原生異步支援
   - 更好的性能和功能

2. **資源管理**:
   - 異步上下文管理器
   - 自動資源清理
   - 防止資源洩漏

3. **類型安全**:
   - 完整的類型提示
   - 數據類驗證
   - IDE友好的開發體驗

4. **工具生態**:
   - 可擴展的工具註冊機制
   - JSON Schema驗證
   - 標準化的工具定義

### 使用場景
- AI助手與MCP服務器通信
- 紫微斗數命盤自動化分析
- 網頁數據爬取和解析
- 微服務架構中的工具調用

### 擴展可能性
- 添加更多專業工具
- 實現工具鏈組合
- 支援批量操作
- 添加緩存機制
- 實現負載均衡

## 總結
這個MCP客戶端實現了完整的Claude MCP協議支援，提供了靈活的工具調用機制和標準化的接口設計。代碼結構清晰，異步處理完善，具有很好的可擴展性和維護性，是一個高質量的MCP客戶端實現。
