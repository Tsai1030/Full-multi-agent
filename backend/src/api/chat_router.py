"""
與大師對談 Router — /api/chat
建立 / 列出對談 session、讀取訊息、送出訊息並取得大師回覆。對談紀錄存 DB。
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..chat import generate_master_reply, stream_master_reply
from ..db import get_db
from ..db.models import ChartProfile, ChatMessage, ChatSession, User
from .models import (
    ChatMessageResponse,
    ChatSendRequest,
    ChatSessionCreate,
    ChatSessionResponse,
)

chat_router = APIRouter(prefix="/api/chat", tags=["chat"])


def _session_response(s: ChatSession) -> ChatSessionResponse:
    return ChatSessionResponse(
        id=str(s.id),
        profile_id=str(s.profile_id),
        title=s.title,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def _message_response(m: ChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse(id=str(m.id), role=m.role, content=m.content, created_at=m.created_at)


def _parse_uuid(value: str, what: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{what}不存在")


async def _get_owned_session(session_id: str, user: User, db: AsyncSession) -> ChatSession:
    sess = await db.get(ChatSession, _parse_uuid(session_id, "對談"))
    if sess is None or sess.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="對談不存在")
    return sess


@chat_router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    req: ChatSessionCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ChatSessionResponse:
    profile = await db.get(ChartProfile, _parse_uuid(req.profile_id, "命盤"))
    if profile is None or profile.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="命盤不存在")

    sess = ChatSession(
        user_id=user.id,
        profile_id=profile.id,
        title=req.title or f"與大師對談 · {profile.label}",
    )
    db.add(sess)
    await db.commit()
    await db.refresh(sess)
    return _session_response(sess)


@chat_router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    profile_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatSessionResponse]:
    stmt = select(ChatSession).where(ChatSession.user_id == user.id)
    if profile_id:
        stmt = stmt.where(ChatSession.profile_id == _parse_uuid(profile_id, "命盤"))
    stmt = stmt.order_by(ChatSession.updated_at.desc())
    rows = await db.scalars(stmt)
    return [_session_response(s) for s in rows]


@chat_router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(
    session_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ChatMessageResponse]:
    await _get_owned_session(session_id, user, db)
    rows = await db.scalars(
        select(ChatMessage).where(ChatMessage.session_id == uuid.UUID(session_id)).order_by(ChatMessage.created_at)
    )
    return [_message_response(m) for m in rows]


@chat_router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: str,
    req: ChatSendRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    sess = await _get_owned_session(session_id, user, db)
    profile = await db.get(ChartProfile, sess.profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="命盤不存在")

    # 既有歷史（產生回覆的上下文）
    rows = await db.scalars(
        select(ChatMessage).where(ChatMessage.session_id == sess.id).order_by(ChatMessage.created_at)
    )
    history = [{"role": m.role, "content": m.content} for m in rows]

    # 存使用者訊息
    db.add(ChatMessage(session_id=sess.id, role="user", content=req.content))

    # 產生大師回覆
    reply_text = await generate_master_reply(profile.chart_json, history, req.content)
    master_msg = ChatMessage(session_id=sess.id, role="master", content=reply_text)
    db.add(master_msg)

    await db.commit()
    await db.refresh(master_msg)
    return _message_response(master_msg)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@chat_router.post("/sessions/{session_id}/messages/stream")
async def stream_message(
    session_id: str,
    req: ChatSendRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """逐字串流大師回覆（SSE）。先存使用者訊息，串流結束後存大師訊息。"""
    sess = await _get_owned_session(session_id, user, db)
    profile = await db.get(ChartProfile, sess.profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="命盤不存在")

    rows = await db.scalars(
        select(ChatMessage).where(ChatMessage.session_id == sess.id).order_by(ChatMessage.created_at)
    )
    history = [{"role": m.role, "content": m.content} for m in rows]

    db.add(ChatMessage(session_id=sess.id, role="user", content=req.content))
    await db.commit()

    async def event_gen():
        parts: list[str] = []
        try:
            async for delta in stream_master_reply(profile.chart_json, history, req.content):
                parts.append(delta)
                yield _sse({"delta": delta})
        except Exception as exc:  # 串流中斷仍存下已產生的內容
            logger.error(f"[chat stream] failed: {exc}")
            yield _sse({"error": "大師暫時無法回應，請稍後再試"})

        reply = "".join(parts).strip() or "（大師沉吟片刻，請再問一次。）"
        master_msg = ChatMessage(session_id=sess.id, role="master", content=reply)
        db.add(master_msg)
        await db.commit()
        await db.refresh(master_msg)
        yield _sse({"done": True, "id": str(master_msg.id), "created_at": master_msg.created_at.isoformat()})

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
