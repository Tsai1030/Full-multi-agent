"""
API Router - 主要 FastAPI 路由
掛載在 /api 前綴下
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException
from loguru import logger

from .models import AnalysisRequest, AnalysisResponse, SystemStatusResponse
from ..config.settings import get_settings
from ..graph.builder import get_compiled_graph
from ..graph.state import GraphState

api_router = APIRouter(prefix="/api", tags=["analysis"])


@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_chart(request: AnalysisRequest) -> AnalysisResponse:
    """
    執行紫微斗數命盤分析（主要端點）
    - 呼叫 LangGraph multi-agent graph
    - graph 內部會依序呼叫 get_ziwei_chart / search_ziwei_knowledge / web_search
    - 最後由 synthesizer 產生報告
    """
    settings = get_settings()
    t0 = time.perf_counter()

    try:
        graph = get_compiled_graph()

        initial_state: GraphState = {
            "messages": [],
            "birth_data": request.birth_data.model_dump(),
            "domain_type": request.domain_type,
            "user_question": request.user_question or f"{request.domain_type} 分析",
            "chart_data": None,
            "rag_results": [],
            "search_results": [],
            "iterations": 0,
            "max_iterations": settings.graph_max_iterations,
            "should_end": False,
            "final_answer": None,
        }

        logger.info(
            f"Graph invoke: birth={request.birth_data.birth_year}/"
            f"{request.birth_data.birth_month}/{request.birth_data.birth_day}, "
            f"domain={request.domain_type}"
        )

        final_state: GraphState = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": settings.graph_recursion_limit},
        )

        elapsed = round((time.perf_counter() - t0) * 1000)
        answer = final_state.get("final_answer") or "（無法產生分析結果）"

        return AnalysisResponse(
            success=True,
            result=answer,
            metadata={
                "domain_type": request.domain_type,
                "iterations": final_state.get("iterations", 0),
                "elapsed_ms": elapsed,
            },
        )

    except Exception as exc:
        logger.exception(f"Analysis failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@api_router.get("/status", response_model=SystemStatusResponse)
async def system_status() -> SystemStatusResponse:
    """系統狀態檢查"""
    from ..rag.vector_store import ZiweiVectorStore
    from ..mcp.tools import ToolRegistry, ZiweiChartTool
    from ..graph.nodes import AGENT_TOOLS

    settings = get_settings()

    # RAG 文件數
    try:
        store = ZiweiVectorStore(
            persist_directory=settings.rag_vector_db_path,
            collection_name=settings.rag_collection_name,
            openai_api_key=settings.openai_api_key,
        )
        rag_docs = store.count()
    except Exception:
        rag_docs = -1

    return SystemStatusResponse(
        status="ok",
        rag_docs=rag_docs,
        tools=[t.name for t in AGENT_TOOLS],
        graph_nodes=["orchestrator", "tools", "synthesizer"],
    )


@api_router.get("/domains")
async def list_domains() -> dict[str, Any]:
    return {
        "domains": [
            {"id": "love", "name": "愛情感情", "description": "感情運勢、桃花、婚姻"},
            {"id": "wealth", "name": "財富事業", "description": "財運、事業、投資"},
            {"id": "future", "name": "未來運勢", "description": "大限流年、人生趨勢"},
            {"id": "comprehensive", "name": "完整命盤", "description": "全方位命盤解析"},
        ]
    }


@api_router.get("/birth-hours")
async def list_birth_hours() -> dict[str, Any]:
    hours = [
        ("子", "23:00-01:00"), ("丑", "01:00-03:00"), ("寅", "03:00-05:00"),
        ("卯", "05:00-07:00"), ("辰", "07:00-09:00"), ("巳", "09:00-11:00"),
        ("午", "11:00-13:00"), ("未", "13:00-15:00"), ("申", "15:00-17:00"),
        ("酉", "17:00-19:00"), ("戌", "19:00-21:00"), ("亥", "21:00-23:00"),
    ]
    return {
        "hours": [{"id": h, "name": f"{h}時", "time": t} for h, t in hours]
    }
