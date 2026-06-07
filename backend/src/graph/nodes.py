"""
Graph Nodes — 真正的 Multi-Agent（全部使用 Gemini）

流程：
  researcher → ┌ reasoning_agent ┐
               ├ domain_agent     ┤→ coordinator → END
               └ creative_agent   ┘
                 （三者並行 fan-out / fan-in）

每個專家 agent 是一顆獨立 persona 的 Gemini 呼叫，各自針對同一份命盤分析；
最後由 coordinator 整合三方觀點成最終報告。
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from loguru import logger

from .state import GraphState
from ..tools import search_ziwei_knowledge, web_search
from ..utils.llm import content_to_text as _content_to_text
from ..utils.llm import get_gemini as _get_llm
from ..ziwei import format_chart_for_llm

# 供 /api/status 列出（researcher 內部使用知識庫；web_search 視需要）
AGENT_TOOLS = [search_ziwei_knowledge, web_search]


# ── persona 系統提示 ──────────────────────────────────────────

REASONING_PERSONA = """\
你是「推理分析師」，紫微斗數團隊中負責嚴謹邏輯推演的命理師。

你的職責：
- 從命盤結構出發：命宮主星與格局、身宮、五行局、命主／身主
- 分析三方四正（命宮、財帛、官祿、遷移）的星曜組合與相互牽引
- 點出主星廟旺亮度、生年四化（祿權科忌）對格局的關鍵影響
- 推論性格底層特質與人生主軸，論述要有因果、有依據

要求：以繁體中文、條理清晰地論述（非 JSON）；只依據附上的命盤與知識，不杜撰星曜。
"""

CREATIVE_PERSONA = """\
你是「創意詮釋師」，紫微斗數團隊中負責把命理轉成生活語言的命理師。

你的職責：
- 把抽象的星曜格局，轉成貼近現代生活、具體可感的描述與比喻
- 著重當事人的生活情境、人際互動、心態與成長建議
- 語氣溫暖、鼓勵、有畫面感，但不浮誇、不做絕對化的負面預言

要求：以繁體中文散文書寫（非 JSON）；以附上的命盤為依據，與推理分析互補而非重複堆砌術語。
"""

DOMAIN_PERSONA_BASE = """\
你是「領域專家」，紫微斗數團隊中針對特定主題深入剖析的資深命理師。
請以繁體中文、專業而實用地論述（非 JSON），只依據附上的命盤與知識。

本次聚焦領域與重點：
"""

DOMAIN_FOCUS: dict[str, str] = {
    "love": (
        "【感情姻緣】\n"
        "- 夫妻宮主星與特質、福德宮（情感內在）、遷移宮（外緣）\n"
        "- 桃花星（紅鸞、天喜、咸池、天姚）與正緣／桃花格局\n"
        "- 感情中的優勢與課題、適合的對象類型、感情發展時機與化解建議"
    ),
    "wealth": (
        "【財富事業】\n"
        "- 財帛宮、官祿宮（事業）主星與財星組合（武曲、太陰、天府等）\n"
        "- 求財方式與適合行業、事業發展策略、投資理財風格與風險\n"
        "- 財運高低週期與提升財運的具體方法"
    ),
    "career": (
        "【事業工作】\n"
        "- 官祿宮（事業宮）主星與命宮、財帛宮三方四正的牽引\n"
        "- 職業性向與適合行業、上班受僱 vs 創業自立的傾向\n"
        "- 求職與轉職時機、職場貴人與人際、升遷與發展策略\n"
        "- 工作中的優勢、潛在課題與具體精進建議"
    ),
    "future": (
        "【未來運勢】\n"
        "- 當前大限與未來流年趨勢、人生階段定位\n"
        "- 重要轉折點與機會、健康與家庭人際面向\n"
        "- 趨吉避凶的時機掌握與人生規劃建議"
    ),
    "comprehensive": (
        "【綜合命盤】\n"
        "- 十二宮整體格局的統合：命格高低、主軸與隱憂\n"
        "- 感情、財富事業、健康、家庭、人際的全方位重點\n"
        "- 一生格局走勢與最關鍵的人生建議"
    ),
}

COORDINATOR_PERSONA = """\
你是紫微斗數團隊的「首席命理師（整合者）」。
團隊中的推理分析師、領域專家、創意詮釋師已各自完成分析，
請你彙整三方觀點，產出一份完整、連貫、不重複的最終解析報告。

要求：
1. 以繁體中文撰寫
2. 融合三位的洞見：保留推理的嚴謹、領域的專業、創意的生活感
3. 若三方有分歧，做出平衡判斷並說明
4. 語氣專業而親切，避免絕對化的負面預測
5. 結尾給出具體、可執行的建議

輸出格式：
## 命盤基本格局
## {domain} 深入解析
## 綜合建議與提醒
"""


# ── helpers ───────────────────────────────────────────────────

def _ming_gong_major_stars(chart: dict[str, Any] | None) -> list[str]:
    """取命宮主星名稱（供 researcher 組查詢）。"""
    for p in (chart or {}).get("palaces", []) or []:
        if isinstance(p, dict) and p.get("name") == "命宮":
            return [s.get("name") for s in p.get("majorStars", []) if isinstance(s, dict) and s.get("name")]
    return []


def _build_agent_input(state: GraphState) -> str:
    """組出每個 agent 共用的使用者訊息（命盤 + 知識脈絡 + 需求）。"""
    birth = state["birth_data"]
    chart_text = format_chart_for_llm(state.get("chart_data"))
    rag_context = state.get("rag_context") or "（無額外知識庫資料）"
    return (
        f"出生資料：{birth.get('gender')}，"
        f"{birth.get('birth_year')}年{birth.get('birth_month')}月{birth.get('birth_day')}日 "
        f"{birth.get('birth_hour')}時\n"
        f"分析領域：{state.get('domain_type')}\n"
        f"使用者問題：{state.get('user_question') or '整體命盤解析'}\n\n"
        f"=== 命盤（唯一依據）===\n{chart_text}\n\n"
        f"=== 紫微斗數知識庫參考 ===\n{rag_context}"
    )


async def _run_agent(
    state: GraphState, *, role: str, label: str, system_prompt: str
) -> dict[str, Any]:
    """執行單一專家 agent，回傳 agent_outputs 片段。"""
    logger.info(f"[agent:{role}] analyzing …")
    user_msg = _build_agent_input(state)
    try:
        llm = _get_llm()
        resp: AIMessage = await llm.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_msg)]
        )
        content = _content_to_text(resp.content).strip()
    except Exception as exc:  # 單一 agent 失敗不影響其他 agent
        logger.error(f"[agent:{role}] failed: {exc}")
        content = ""
    return {"agent_outputs": [{"role": role, "label": label, "content": content}]}


# ── researcher node ───────────────────────────────────────────

async def researcher_node(state: GraphState) -> dict[str, Any]:
    """依命盤主星 / 領域 / 問題檢索知識庫，組成共享 rag_context。"""
    from ..config.settings import get_settings
    from ..rag.retriever import RAGRetriever
    from ..rag.vector_store import ZiweiVectorStore

    s = get_settings()
    domain = state.get("domain_type", "comprehensive")
    stars = _ming_gong_major_stars(state.get("chart_data"))

    queries: list[str] = []
    if stars:
        queries.append(f"{' '.join(stars)} 坐命宮的特質與格局")
    domain_query = {
        "love": "夫妻宮 感情 桃花 婚姻運勢",
        "wealth": "財帛宮 官祿宮 財運 事業 財星",
        "career": "官祿宮 事業 職業 適合行業 求職 轉職",
        "future": "大限 流年 運勢 人生階段",
        "comprehensive": "命宮 格局 三方四正 整體命盤",
    }.get(domain, "命宮 格局 整體命盤")
    queries.append(domain_query)
    if state.get("user_question"):
        queries.append(state["user_question"])

    parts: list[str] = []
    try:
        store = ZiweiVectorStore(
            persist_directory=s.rag_vector_db_path,
            collection_name=s.rag_collection_name,
            api_key=s.google_api_key,
            embedding_model=s.gemini_embedding_model,
            provider=s.embedding_provider,
        )
        retriever = RAGRetriever(store, default_top_k=s.rag_top_k, default_min_score=s.rag_min_score)
        seen: set[str] = set()
        for q in queries:
            if q in seen:
                continue
            seen.add(q)
            ctx = retriever.search_and_format(q, top_k=3)
            if ctx:
                parts.append(f"〔查詢：{q}〕\n{ctx}")
    except Exception as exc:
        logger.warning(f"[researcher] RAG failed (non-fatal): {exc}")

    rag_context = "\n\n".join(parts)
    logger.info(f"[researcher] gathered {len(rag_context)} chars from {len(queries)} queries")
    return {"rag_context": rag_context}


# ── specialist agents（並行）──────────────────────────────────

async def reasoning_agent_node(state: GraphState) -> dict[str, Any]:
    return await _run_agent(
        state, role="reasoning", label="推理分析師", system_prompt=REASONING_PERSONA
    )


async def domain_agent_node(state: GraphState) -> dict[str, Any]:
    domain = state.get("domain_type", "comprehensive")
    focus = DOMAIN_FOCUS.get(domain, DOMAIN_FOCUS["comprehensive"])
    system_prompt = DOMAIN_PERSONA_BASE + focus
    return await _run_agent(
        state, role="domain", label="領域專家", system_prompt=system_prompt
    )


async def creative_agent_node(state: GraphState) -> dict[str, Any]:
    return await _run_agent(
        state, role="creative", label="創意詮釋師", system_prompt=CREATIVE_PERSONA
    )


# ── coordinator node（整合）───────────────────────────────────

async def coordinator_node(state: GraphState) -> dict[str, Any]:
    """整合三個 agent 的輸出，產生最終報告。"""
    logger.info("[coordinator] integrating agent outputs")
    outputs = state.get("agent_outputs", []) or []
    domain = state.get("domain_type", "comprehensive")

    present = [o for o in outputs if o.get("content")]
    if not present:
        return {"final_answer": "（多代理人皆未能產生分析，請稍後再試）"}

    sections = "\n\n".join(
        f"### 【{o.get('label', o.get('role'))}】的分析\n{o['content']}" for o in present
    )
    system_prompt = COORDINATOR_PERSONA.replace("{domain}", domain)
    chart_text = format_chart_for_llm(state.get("chart_data"))
    user_msg = (
        f"命盤摘要：\n{chart_text}\n\n"
        f"以下是團隊三位命理師各自的分析，請整合成最終報告：\n\n{sections}"
    )

    try:
        llm = _get_llm()
        resp: AIMessage = await llm.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_msg)]
        )
        final = _content_to_text(resp.content).strip()
    except Exception as exc:
        logger.error(f"[coordinator] failed: {exc}")
        # 退而求其次：直接串接各 agent 輸出
        final = "\n\n".join(f"## {o.get('label')}\n{o['content']}" for o in present)

    return {"final_answer": final, "should_end": True}
