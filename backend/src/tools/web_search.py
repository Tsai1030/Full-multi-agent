"""
Web Search Tool
優先使用 Tavily API，無 key 則 fallback 到 DuckDuckGo HTML 解析
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool
from loguru import logger


@tool
async def web_search(query: str) -> str:
    """
    在網路上搜索資訊。
    適合查詢最新事件、時事運勢、補充命理知識等。

    Args:
        query: 搜索關鍵字或問題

    Returns:
        搜索結果摘要（JSON 字串）
    """
    from ..config.settings import get_settings

    settings = get_settings()

    if settings.tavily_api_key:
        return await _tavily_search(query, settings.tavily_api_key, settings.tavily_max_results)
    else:
        return await _duckduckgo_search(query)


async def _tavily_search(query: str, api_key: str, max_results: int) -> str:
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)
        results = client.search(query=query, max_results=max_results)
        formatted = []
        for r in results.get("results", []):
            formatted.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],
            })
        return json.dumps(formatted, ensure_ascii=False)
    except Exception as exc:
        logger.warning(f"Tavily search failed: {exc}, falling back to DuckDuckGo")
        return await _duckduckgo_search(query)


async def _duckduckgo_search(query: str) -> str:
    """DuckDuckGo HTML 無 API 搜索（fallback）"""
    import httpx
    from bs4 import BeautifulSoup

    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    params = {"q": query, "kl": "tw-tzh"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, data=params, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for result in soup.select(".result")[:5]:
            title_el = result.select_one(".result__title")
            snippet_el = result.select_one(".result__snippet")
            link_el = result.select_one(".result__url")

            if title_el and snippet_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": link_el.get_text(strip=True) if link_el else "",
                    "content": snippet_el.get_text(strip=True),
                })

        if not results:
            return json.dumps([{"content": "No search results found."}], ensure_ascii=False)

        return json.dumps(results, ensure_ascii=False)

    except Exception as exc:
        logger.error(f"DuckDuckGo search failed: {exc}")
        return json.dumps([{"error": str(exc)}], ensure_ascii=False)
