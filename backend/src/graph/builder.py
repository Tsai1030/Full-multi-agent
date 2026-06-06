"""
Graph Builder
組裝 LangGraph StateGraph，編譯成可執行的 CompiledGraph

Multi-Agent 結構（並行 fan-out / fan-in）：

    START
      │
      ▼
  researcher
      │  fan-out（三者並行執行）
      ├──────────────┬──────────────┐
      ▼              ▼              ▼
  reasoning_agent  domain_agent  creative_agent
      └──────────────┴──────────────┘
                     │  fan-in（等三者都完成）
                     ▼
                coordinator
                     │
                    END
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from .nodes import (
    coordinator_node,
    creative_agent_node,
    domain_agent_node,
    reasoning_agent_node,
    researcher_node,
)
from .state import GraphState

_AGENTS = ("reasoning_agent", "domain_agent", "creative_agent")


def build_graph() -> StateGraph:
    """建構 StateGraph（未編譯）"""

    builder = StateGraph(GraphState)

    # ── 節點 ──────────────────────────────────────────────────
    builder.add_node("researcher", researcher_node)
    builder.add_node("reasoning_agent", reasoning_agent_node)
    builder.add_node("domain_agent", domain_agent_node)
    builder.add_node("creative_agent", creative_agent_node)
    builder.add_node("coordinator", coordinator_node)

    # ── 邊 ────────────────────────────────────────────────────
    builder.add_edge(START, "researcher")

    # researcher → 三個 agent（fan-out，並行）
    # 三個 agent → coordinator（fan-in，等全部完成）
    for agent in _AGENTS:
        builder.add_edge("researcher", agent)
        builder.add_edge(agent, "coordinator")

    builder.add_edge("coordinator", END)

    return builder


@lru_cache(maxsize=1)
def get_compiled_graph():
    """
    回傳已編譯的 graph（單例，lru_cache 保證全域只建一次）。
    呼叫方：直接 await graph.ainvoke(initial_state)
    """
    from ..config.settings import get_settings

    s = get_settings()
    graph = build_graph().compile()
    graph.recursion_limit = s.graph_recursion_limit
    return graph
