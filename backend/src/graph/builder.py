"""
Graph Builder
組裝 LangGraph StateGraph，編譯成可執行的 CompiledGraph

Graph 結構（帶 loop）：

    START
      │
      ▼
  orchestrator  ◄─────────────────────┐
      │                               │
      ▼  (should_continue)            │
  ┌─────────────────┐                 │
  │  tool_calls?    │                 │
  ├─── YES ──► tools ─────────────────┘
  └─── NO  ──► synthesizer
                  │
                 END
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from .edges import should_continue
from .nodes import orchestrator_node, synthesizer_node, tool_node
from .state import GraphState


def build_graph() -> StateGraph:
    """建構 StateGraph（未編譯）"""

    builder = StateGraph(GraphState)

    # ── 節點 ──────────────────────────────────────────────────
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("tools", tool_node)
    builder.add_node("synthesizer", synthesizer_node)

    # ── 邊 ────────────────────────────────────────────────────
    builder.add_edge(START, "orchestrator")

    # orchestrator → tools | synthesizer （條件路由）
    builder.add_conditional_edges(
        "orchestrator",
        should_continue,
        {
            "tools": "tools",
            "synthesizer": "synthesizer",
        },
    )

    # tools → orchestrator（loop 回去）
    builder.add_edge("tools", "orchestrator")

    # synthesizer → END
    builder.add_edge("synthesizer", END)

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
