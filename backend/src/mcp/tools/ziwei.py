"""
紫微斗數命盤工具
爬取 windada.com 並解析命盤 HTML
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from .base import BaseMCPTool

# 時辰對應表
HOUR_MAP: dict[str, str] = {
    "子": "0", "丑": "1", "寅": "2", "卯": "3",
    "辰": "4", "巳": "5", "午": "6", "未": "7",
    "申": "8", "酉": "9", "戌": "10", "亥": "11",
}

GENDER_MAP: dict[str, str] = {"男": "0", "女": "1"}


class ZiweiChartTool(BaseMCPTool):
    """向 windada.com 取得紫微斗數命盤並解析"""

    name: ClassVar[str] = "ziwei_chart"
    description: ClassVar[str] = (
        "根據出生年月日時和性別，取得紫微斗數命盤資料。"
        "返回各宮位主星資訊，供後續解盤使用。"
    )
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "gender": {
                "type": "string",
                "enum": ["男", "女"],
                "description": "性別",
            },
            "birth_year": {
                "type": "integer",
                "minimum": 1900,
                "maximum": 2100,
                "description": "出生年份（西元）",
            },
            "birth_month": {
                "type": "integer",
                "minimum": 1,
                "maximum": 12,
                "description": "出生月份",
            },
            "birth_day": {
                "type": "integer",
                "minimum": 1,
                "maximum": 31,
                "description": "出生日期",
            },
            "birth_hour": {
                "type": "string",
                "description": "出生時辰（子/丑/寅/卯/辰/巳/午/未/申/酉/戌/亥）",
            },
        },
        "required": ["gender", "birth_year", "birth_month", "birth_day", "birth_hour"],
    }

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def _execute(
        self,
        gender: str,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        birth_hour: str,
        **_: Any,
    ) -> dict[str, Any]:
        params = self._build_params(gender, birth_year, birth_month, birth_day, birth_hour)
        html = await self._fetch_chart(params)
        return self._parse_chart(html, gender, birth_year, birth_month, birth_day, birth_hour)

    # ── private helpers ────────────────────────────────────────

    def _build_params(
        self,
        gender: str,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        birth_hour: str,
    ) -> dict[str, str]:
        return {
            "TypeCode": "0",
            "Sex": GENDER_MAP.get(gender, "0"),
            "Year": str(birth_year),
            "Month": str(birth_month),
            "Day": str(birth_day),
            "Hour": HOUR_MAP.get(birth_hour, "0"),
            "HourM": "0",
        }

    async def _fetch_chart(self, params: dict[str, str]) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "zh-TW,zh;q=0.9",
        }
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            resp = await client.post(self._base_url, data=params, headers=headers)
            resp.raise_for_status()

        raw = resp.content
        # Taiwan sites typically use cp950 (Microsoft Big5); fall back gracefully
        for enc in ("cp950", "big5-hkscs", "big5", "utf-8"):
            try:
                text = raw.decode(enc)
                if "命" in text or "紫微" in text:
                    logger.debug(f"HTML decoded with {enc}")
                    return text
            except (UnicodeDecodeError, LookupError):
                continue

        return raw.decode("cp950", errors="replace")

    def _parse_chart(
        self,
        html: str,
        gender: str,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        birth_hour: str,
    ) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")

        palaces: dict[str, list[str]] = {}
        main_stars: list[str] = []

        # 嘗試解析表格中的宮位資料
        tables = soup.find_all("table")
        for table in tables:
            cells = table.find_all("td")
            for cell in cells:
                text = cell.get_text(separator="\n", strip=True)
                if not text:
                    continue
                palace_name = self._extract_palace_name(text)
                if palace_name:
                    stars = self._extract_stars(text)
                    palaces[palace_name] = stars
                    main_stars.extend(stars)

        # 擷取命宮主星（key 已正規化為無「宮」後綴）
        ming_gong_stars = palaces.get("命", [])

        if not palaces:
            logger.warning("無法解析命盤 HTML，回傳原始摘要")
            return {
                "success": False,
                "birth_info": {
                    "gender": gender,
                    "year": birth_year,
                    "month": birth_month,
                    "day": birth_day,
                    "hour": birth_hour,
                },
                "raw_text": soup.get_text()[:2000],
                "palaces": {},
                "main_star": None,
            }

        return {
            "success": True,
            "birth_info": {
                "gender": gender,
                "year": birth_year,
                "month": birth_month,
                "day": birth_day,
                "hour": birth_hour,
            },
            "palaces": palaces,
            "main_star": ming_gong_stars[0] if ming_gong_stars else None,
            "all_stars": list(set(main_stars)),
        }

    # ── star / palace extraction ───────────────────────────────

    _PALACE_NAMES = [
        "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
        "遷移宮", "奴僕宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
        "兄弟", "夫妻", "子女", "財帛", "疾厄", "遷移",
        "奴僕", "官祿", "田宅", "福德", "父母",
    ]

    _STAR_PATTERN = re.compile(
        r"(紫微|天機|太陽|武曲|天同|廉貞|天府|太陰|貪狼|巨門|天相|天梁|七殺|破軍"
        r"|左輔|右弼|文昌|文曲|天魁|天鉞|祿存|天馬|擎羊|陀羅|火星|鈴星"
        r"|化祿|化權|化科|化忌)"
    )

    def _extract_palace_name(self, text: str) -> str | None:
        for name in self._PALACE_NAMES:
            if name in text:
                # Normalize: strip trailing 宮 for consistent dict keys
                return name[:-1] if name.endswith("宮") else name
        return None

    def _extract_stars(self, text: str) -> list[str]:
        return self._STAR_PATTERN.findall(text)
