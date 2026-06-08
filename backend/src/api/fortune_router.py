"""
Fortune follow-up chat — ephemeral, no DB persistence.
/api/fortune/stream — SSE streaming based on analysis context.
/api/analyze/compatibility — dual-chart love compatibility.
"""

from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..auth.permissions import require_feature, require_tokens
from ..chat.fortune import stream_fortune_reply
from ..config.settings import get_settings
from ..db import get_db
from ..db.models import User
from ..graph.builder import get_compiled_graph
from ..graph.state import GraphState
from ..prompts.fortune_prompt import COMPATIBILITY_PERSONA
from ..ziwei import format_chart_for_llm
from .models import FortuneStreamRequest

fortune_router = APIRouter(prefix="/api/fortune", tags=["fortune"])


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@fortune_router.post("/stream")
async def stream_fortune(
    req: FortuneStreamRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _tokens: None = Depends(require_tokens("fortune_followup")),
) -> StreamingResponse:
    """Ephemeral follow-up chat — uses analysis result as context, no DB persistence."""

    async def event_gen():
        parts: list[str] = []
        try:
            async for delta in stream_fortune_reply(
                domain=req.domain,
                analysis_context=req.analysis_context,
                chart_text=req.chart_text,
                history=req.messages,
                user_message=req.user_message,
            ):
                parts.append(delta)
                yield _sse({"delta": delta})
        except Exception as exc:
            logger.error(f"[fortune stream] failed: {exc}")
            yield _sse({"error": "暫時無法回應，請稍後再試"})

        yield _sse({"done": True})

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Compatibility Analysis ────────────────────────────────────


class CompatibilityRequest:
    pass


from pydantic import BaseModel, Field
from typing import Any


class CompatibilityAnalysisRequest(BaseModel):
    birth_data_1: dict[str, Any] = Field(..., description="Person 1 birth data")
    birth_data_2: dict[str, Any] = Field(..., description="Person 2 birth data")
    chart_1: dict[str, Any] = Field(..., description="Person 1 iztro chart JSON")
    chart_2: dict[str, Any] = Field(..., description="Person 2 iztro chart JSON")
    user_question: str = Field("", description="Optional question")


@fortune_router.post("/compatibility")
async def analyze_compatibility(
    req: CompatibilityAnalysisRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Dual-chart love compatibility analysis using multi-agent graph."""
    # Feature + token gates
    feat_check = require_feature("compatibility")
    await feat_check(user=user, db=db)
    token_check = require_tokens("compatibility_analysis")
    await token_check(user=user, db=db)

    settings = get_settings()
    t0 = time.perf_counter()

    try:
        chart_text_1 = format_chart_for_llm(req.chart_1)
        chart_text_2 = format_chart_for_llm(req.chart_2)

        combined_question = (
            f"請進行合盤分析（雙人配對）。\n\n"
            f"=== 第一人命盤 ===\n{chart_text_1}\n\n"
            f"=== 第二人命盤 ===\n{chart_text_2}\n\n"
            f"分析要點：雙方夫妻宮互動、性格契合度、桃花與正緣呼應、五行相生相剋、相處優勢與課題。\n"
        )
        if req.user_question:
            combined_question += f"\n使用者特別想了解：{req.user_question}"

        graph = get_compiled_graph()

        initial_state: GraphState = {
            "messages": [],
            "birth_data": req.birth_data_1,
            "domain_type": "love",
            "user_question": combined_question,
            "chart_data": req.chart_1,
            "rag_context": "",
            "agent_outputs": [],
            "rag_results": [],
            "search_results": [],
            "iterations": 0,
            "max_iterations": settings.graph_max_iterations,
            "should_end": False,
            "final_answer": None,
        }

        final_state = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": settings.graph_recursion_limit},
        )

        elapsed = round((time.perf_counter() - t0) * 1000)
        answer = final_state.get("final_answer") or "（無法產生合盤分析結果）"
        agent_outputs = [
            o for o in final_state.get("agent_outputs", []) if o.get("content")
        ]

        return {
            "success": True,
            "result": answer,
            "agents": agent_outputs or None,
            "metadata": {
                "domain_type": "compatibility",
                "agents_used": len(agent_outputs),
                "elapsed_ms": elapsed,
            },
        }

    except Exception as exc:
        logger.exception(f"Compatibility analysis failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
