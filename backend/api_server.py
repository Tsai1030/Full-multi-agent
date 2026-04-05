"""
FastAPI 後端服務器
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

# 導入我們的 AI 系統
from .main import ZiweiAISystem

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="紫微斗數 AI 系統 API",
    description="Multi-Agent 紫微斗數命理分析系統",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React 開發服務器
    allow_origins=["*"],  # 確保是 * 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 AI 系統實例
ai_system: Optional[ZiweiAISystem] = None

# 請求模型
class BirthData(BaseModel):
    gender: str = Field(..., description="性別：男/女")
    birth_year: int = Field(..., ge=1900, le=2100, description="出生年份")
    birth_month: int = Field(..., ge=1, le=12, description="出生月份")
    birth_day: int = Field(..., ge=1, le=31, description="出生日期")
    birth_hour: str = Field(..., description="出生時辰")

class AnalysisRequest(BaseModel):
    birth_data: BirthData
    domain_type: str = Field(default="comprehensive", description="分析領域")
    output_format: str = Field(default="json_to_narrative", description="輸出格式")
    show_agent_process: bool = Field(default=False, description="是否顯示 Agent 過程") # 🎯 顯示 Agent 過程

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

# API 路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "紫微斗數 AI 系統 API",
        "version": "1.0.0",
        "status": "running"
    }

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

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_chart(request: AnalysisRequest):
    """分析紫微斗數命盤"""
    global ai_system
    
    if not ai_system:
        raise HTTPException(
            status_code=503, 
            detail="AI 系統未初始化，請稍後再試"
        )
    
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
