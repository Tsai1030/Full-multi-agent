# api_server.py 逐行解析文檔

## 檔案概述
這是紫微斗數AI系統的FastAPI後端服務器，提供RESTful API接口供前端React應用調用。該檔案實現了完整的Web API服務，包括命盤分析、系統狀態檢查和配置信息獲取。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-18行)

```python
"""
FastAPI 後端服務器
"""
```
**用意**: 檔案說明文檔，明確這是FastAPI後端服務器

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import logging
from datetime import datetime
```
**用意**: 導入必要的模組
- `FastAPI`: 現代高性能Web框架
- `CORSMiddleware`: 跨域資源共享中間件
- `pydantic`: 數據驗證和序列化
- `typing`: 類型提示
- `asyncio`: 異步編程支援
- `logging`: 日誌記錄
- `datetime`: 時間處理

```python
# 導入我們的 AI 系統
from main import ZiweiAISystem

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```
**用意**: 
- 導入自定義的AI系統
- 配置INFO級別的日誌
- 創建模組專用的日誌記錄器

### FastAPI應用創建與配置 (第20-37行)

```python
# 創建 FastAPI 應用
app = FastAPI(
    title="紫微斗數 AI 系統 API",
    description="Multi-Agent 紫微斗數命理分析系統",
    version="1.0.0"
)
```
**用意**: 
- 創建FastAPI應用實例
- 設置API文檔的標題和描述
- 指定版本號用於API版本管理

```python
# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React 開發服務器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
**用意**: 
- 配置跨域資源共享(CORS)
- 允許React開發服務器(端口3000)的請求
- 允許所有HTTP方法和標頭
- 支援憑證傳遞

```python
# 全局 AI 系統實例
ai_system: Optional[ZiweiAISystem] = None
```
**用意**: 
- 定義全域AI系統實例變數
- 使用Optional類型提示表示可能為None
- 在應用啟動時初始化

### 數據模型定義 (第39-64行)

```python
# 請求模型
class BirthData(BaseModel):
    gender: str = Field(..., description="性別：男/女")
    birth_year: int = Field(..., ge=1900, le=2100, description="出生年份")
    birth_month: int = Field(..., ge=1, le=12, description="出生月份")
    birth_day: int = Field(..., ge=1, le=31, description="出生日期")
    birth_hour: str = Field(..., description="出生時辰")
```
**用意**: 
- 定義出生資料的數據模型
- 使用Field進行數據驗證
- 設置年份範圍(1900-2100)和月日範圍
- 提供中文描述便於API文檔

```python
class AnalysisRequest(BaseModel):
    birth_data: BirthData
    domain_type: str = Field(default="comprehensive", description="分析領域")
    output_format: str = Field(default="json_to_narrative", description="輸出格式")
    show_agent_process: bool = Field(default=False, description="是否顯示 Agent 過程") # 🎯 顯示 Agent 過程
```
**用意**: 
- 定義分析請求的完整數據模型
- 包含出生資料、分析領域、輸出格式
- 支援顯示Agent處理過程的選項
- 提供合理的默認值

```python
# 響應模型
class AnalysisResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SystemStatus(BaseModel):
    status: str
    initialized: bool
    components: Dict[str, bool]
    timestamp: str
```
**用意**: 
- 定義API響應的標準格式
- 包含成功狀態、結果、錯誤信息和元數據
- 定義系統狀態檢查的響應格式
- 確保API響應的一致性

### 應用生命週期事件 (第66-90行)

```python
# 啟動事件
@app.on_event("startup")
async def startup_event():
    """啟動時初始化 AI 系統"""
    global ai_system
    try:
        logger.info("🚀 正在初始化紫微斗數 AI 系統...")
        ai_system = ZiweiAISystem()
        await ai_system.initialize()
        logger.info("✅ AI 系統初始化完成")
    except Exception as e:
        logger.error(f"❌ AI 系統初始化失敗: {str(e)}")
        ai_system = None
```
**用意**: 
- 在應用啟動時自動初始化AI系統
- 使用異步初始化支援複雜的啟動流程
- 完整的錯誤處理，失敗時設為None
- 使用表情符號增強日誌可讀性

```python
# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    """關閉時清理資源"""
    global ai_system
    if ai_system:
        try:
            await ai_system.cleanup()
            logger.info("✅ AI 系統資源清理完成")
        except Exception as e:
            logger.error(f"❌ 清理失敗: {str(e)}")
```
**用意**: 
- 在應用關閉時自動清理資源
- 防止資源洩漏和不正常關閉
- 異步清理支援複雜的清理流程
- 錯誤處理確保清理過程的穩定性

### 基礎API路由 (第92-129行)

```python
@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "紫微斗數 AI 系統 API",
        "version": "1.0.0",
        "status": "running"
    }
```
**用意**: 
- 提供API根路由的基本信息
- 返回服務名稱、版本和狀態
- 用於快速檢查API是否正常運行

```python
@app.get("/health", response_model=SystemStatus)
async def health_check():
    """健康檢查"""
    global ai_system
    
    if not ai_system:
        return SystemStatus(
            status="error",
            initialized=False,
            components={},
            timestamp=datetime.now().isoformat()
        )
    
    try:
        system_status = ai_system.get_system_status()
        return SystemStatus(
            status="healthy" if system_status["initialized"] else "initializing",
            initialized=system_status["initialized"],
            components=system_status["components"],
            timestamp=system_status["timestamp"]
        )
    except Exception as e:
        return SystemStatus(
            status="error",
            initialized=False,
            components={},
            timestamp=datetime.now().isoformat()
        )
```
**用意**: 
- 提供系統健康狀態檢查接口
- 檢查AI系統是否正常初始化
- 返回各組件的狀態信息
- 支援監控和運維需求

### 核心分析API (第131-175行)

```python
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_chart(request: AnalysisRequest):
    """分析紫微斗數命盤"""
    global ai_system
    
    if not ai_system:
        raise HTTPException(
            status_code=503, 
            detail="AI 系統未初始化，請稍後再試"
        )
```
**用意**: 
- 定義核心的命盤分析API
- 檢查AI系統是否已初始化
- 返回503服務不可用狀態碼

```python
    try:
        logger.info(f"🔮 開始分析命盤: {request.birth_data.dict()}")
        
        # 轉換請求數據
        birth_data = request.birth_data.dict()
        
        # 執行分析
        result = await ai_system.analyze_ziwei_chart(
            birth_data=birth_data,
            domain_type=request.domain_type,
            output_format=request.output_format,
            show_agent_process=request.show_agent_process
        )
```
**用意**: 
- 記錄分析請求的詳細信息
- 將Pydantic模型轉換為字典
- 調用AI系統的異步分析方法
- 傳遞所有請求參數

```python
        if result["success"]:
            logger.info("✅ 分析完成")
            return AnalysisResponse(
                success=True,
                result=result["result"],
                metadata=result["metadata"]
            )
        else:
            logger.error(f"❌ 分析失敗: {result['error']}")
            return AnalysisResponse(
                success=False,
                error=result["error"]
            )
            
    except Exception as e:
        logger.error(f"❌ API 錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析過程中發生錯誤: {str(e)}"
        )
```
**用意**: 
- 根據分析結果返回相應的響應
- 記錄成功和失敗的日誌
- 完整的異常處理
- 返回用戶友好的錯誤信息

## 程式碼架構總結

### 設計模式
1. **RESTful API**: 標準的REST接口設計
2. **數據驗證**: 使用Pydantic進行請求驗證
3. **異步處理**: 全面使用async/await模式
4. **中間件模式**: 使用CORS中間件處理跨域

### 主要特點
- **類型安全**: 完整的類型提示和數據驗證
- **錯誤處理**: 多層次的異常處理機制
- **生命週期管理**: 自動的資源初始化和清理
- **監控支援**: 健康檢查和狀態監控接口

### 配置信息API (第177-221行)

```python
@app.get("/domains")
async def get_domains():
    """獲取可用的分析領域"""
    return {
        "domains": [
            {
                "id": "love",
                "name": "愛情感情",
                "description": "專精於感情運勢、桃花運、婚姻分析",
                "icon": "💕"
            },
            {
                "id": "wealth",
                "name": "財富事業",
                "description": "專精於財運分析、事業發展、投資理財",
                "icon": "💰"
            },
            {
                "id": "future",
                "name": "未來運勢",
                "description": "專精於大限流年、人生規劃、趨勢預測",
                "icon": "🔮"
            }
        ]
    }
```
**用意**:
- 提供前端可用的分析領域配置
- 包含ID、名稱、描述和圖標
- 支援三大專業分析領域
- 便於前端動態生成選項

```python
@app.get("/birth-hours")
async def get_birth_hours():
    """獲取時辰選項"""
    return {
        "hours": [
            {"id": "子", "name": "子時", "time": "23:00-01:00"},
            {"id": "丑", "name": "丑時", "time": "01:00-03:00"},
            {"id": "寅", "name": "寅時", "time": "03:00-05:00"},
            {"id": "卯", "name": "卯時", "time": "05:00-07:00"},
            {"id": "辰", "name": "辰時", "time": "07:00-09:00"},
            {"id": "巳", "name": "巳時", "time": "09:00-11:00"},
            {"id": "午", "name": "午時", "time": "11:00-13:00"},
            {"id": "未", "name": "未時", "time": "13:00-15:00"},
            {"id": "申", "name": "申時", "time": "15:00-17:00"},
            {"id": "酉", "name": "酉時", "time": "17:00-19:00"},
            {"id": "戌", "name": "戌時", "time": "19:00-21:00"},
            {"id": "亥", "name": "亥時", "time": "21:00-23:00"}
        ]
    }
```
**用意**:
- 提供完整的十二時辰配置
- 包含時辰ID、名稱和對應時間
- 支援前端時辰選擇器
- 確保時辰數據的一致性

### 服務器啟動配置 (第223-238行)

```python
if __name__ == "__main__":
    import uvicorn

    print("🚀 啟動紫微斗數 AI 系統後端服務器...")
    print("📡 服務地址: http://localhost:8000")
    print("📚 API 文檔: http://localhost:8000/docs")
    print("🔄 前端代理: http://localhost:3000 -> http://localhost:8000")
    print("=" * 50)

    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",  # 改為 127.0.0.1 避免防火牆問題
        port=8000,
        reload=True,
        log_level="info"
    )
```
**用意**:
- 直接運行時啟動開發服務器
- 使用uvicorn作為ASGI服務器
- 設置主機為127.0.0.1避免防火牆問題
- 啟用熱重載便於開發
- 提供清晰的服務信息提示

## 深度架構分析

### API設計理念

#### 1. RESTful設計原則
- **資源導向**: 每個端點代表特定資源
- **HTTP動詞**: 使用GET/POST等標準方法
- **狀態碼**: 正確使用HTTP狀態碼
- **統一接口**: 一致的請求/響應格式

#### 2. 數據驗證策略
```python
birth_year: int = Field(..., ge=1900, le=2100, description="出生年份")
```
- **自動驗證**: Pydantic自動驗證請求數據
- **範圍檢查**: 設置合理的數值範圍
- **類型安全**: 強制類型檢查
- **錯誤提示**: 自動生成驗證錯誤信息

#### 3. 異步處理優勢
```python
async def analyze_chart(request: AnalysisRequest):
    result = await ai_system.analyze_ziwei_chart(...)
```
- **非阻塞I/O**: 提高並發處理能力
- **資源效率**: 減少線程開銷
- **響應性**: 更好的用戶體驗

### 錯誤處理機制

#### 1. 多層次錯誤處理
- **數據驗證錯誤**: Pydantic自動處理
- **業務邏輯錯誤**: AI系統內部處理
- **API層錯誤**: HTTPException處理
- **系統級錯誤**: 全局異常處理

#### 2. 用戶友好的錯誤信息
```python
raise HTTPException(
    status_code=503,
    detail="AI 系統未初始化，請稍後再試"
)
```
- **中文錯誤信息**: 便於用戶理解
- **適當的狀態碼**: 正確的HTTP狀態
- **詳細的錯誤描述**: 幫助問題診斷

### 系統集成特點

#### 1. 前後端分離架構
```python
allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
```
- **CORS配置**: 支援跨域請求
- **端口分離**: 前端3000，後端8000
- **開發友好**: 支援熱重載和調試

#### 2. 生命週期管理
```python
@app.on_event("startup")
async def startup_event():
    ai_system = ZiweiAISystem()
    await ai_system.initialize()
```
- **自動初始化**: 應用啟動時自動設置
- **資源清理**: 關閉時自動清理
- **狀態管理**: 全域狀態管理

### 監控和運維支援

#### 1. 健康檢查接口
```python
@app.get("/health", response_model=SystemStatus)
```
- **系統狀態**: 檢查各組件狀態
- **初始化狀態**: 確認系統就緒
- **時間戳**: 提供狀態檢查時間

#### 2. 日誌記錄
```python
logger.info(f"🔮 開始分析命盤: {request.birth_data.dict()}")
```
- **結構化日誌**: 便於分析和監控
- **表情符號**: 增強日誌可讀性
- **詳細信息**: 記錄關鍵操作

### 安全性考量

#### 1. 輸入驗證
- **數據類型檢查**: 防止類型錯誤
- **範圍驗證**: 防止無效數據
- **必填欄位**: 確保數據完整性

#### 2. 錯誤信息控制
- **不洩露內部信息**: 適當的錯誤抽象
- **用戶友好**: 提供有用的錯誤提示
- **日誌記錄**: 詳細記錄用於調試

## 使用場景

### 1. Web應用後端
- 為React前端提供API服務
- 支援單頁應用(SPA)架構
- 提供實時的命盤分析服務

### 2. 微服務架構
- 作為命理分析微服務
- 支援水平擴展
- 便於集成到更大的系統

### 3. 開發和測試
- 自動生成API文檔
- 支援熱重載開發
- 便於單元測試和集成測試

## 擴展可能性

### 1. 功能擴展
- 添加用戶認證和授權
- 實現分析歷史記錄
- 支援批量分析
- 添加WebSocket實時通信

### 2. 性能優化
- 實現請求緩存
- 添加限流機制
- 支援負載均衡
- 數據庫集成

### 3. 運維增強
- 添加指標監控
- 實現分散式追蹤
- 支援配置中心
- 容器化部署

## 總結

這個FastAPI後端服務器展現了現代Web API的最佳實踐，通過異步處理、數據驗證、錯誤處理和生命週期管理，提供了穩定可靠的紫微斗數分析服務。其清晰的架構設計和完整的功能實現，為前端應用提供了強大的後端支援。
