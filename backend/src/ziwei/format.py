"""
命盤資料格式化

命盤由前端 iztro 計算後，連同 birth_data 一起送到後端。
此模組把 iztro 命盤 JSON 轉成易讀的繁體中文文字，
供 multi-agent（orchestrator / synthesizer）解盤使用。

iztro 命盤 JSON 結構（前端 serialize 後）：
    solarDate, lunarDate, chineseDate, time, timeRange, sign, zodiac,
    soul（命主）, body（身主）, fiveElementsClass（五行局）, gender,
    palaces: [ { name, isBodyPalace, heavenlyStem, earthlyBranch,
                 majorStars[], minorStars[], adjectiveStars[],
                 decadal{range}, ages[] } ]
    star: { name, brightness, mutagen }
"""

from __future__ import annotations

from typing import Any


def _fmt_stars(stars: list[dict[str, Any]] | None) -> str:
    """把星曜陣列格式化成『紫微(廟,化權) 天機(旺)』這種字串"""
    if not stars:
        return "—"
    parts: list[str] = []
    for s in stars:
        if not isinstance(s, dict):
            continue
        name = s.get("name", "")
        if not name:
            continue
        extras: list[str] = []
        brightness = s.get("brightness")
        if brightness:
            extras.append(str(brightness))
        mutagen = s.get("mutagen")
        if mutagen:
            extras.append(f"化{mutagen}")
        parts.append(f"{name}({','.join(extras)})" if extras else name)
    return " ".join(parts) if parts else "—"


def format_chart_for_llm(chart: dict[str, Any] | None) -> str:
    """把命盤 JSON 轉成繁中文字摘要"""
    if not chart or not isinstance(chart, dict):
        return "（無命盤資料）"

    lines: list[str] = ["# 紫微斗數命盤"]

    # ── 基本資訊 ───────────────────────────────────────────────
    basic = [
        ("性別", chart.get("gender")),
        ("陽曆", chart.get("solarDate")),
        ("農曆", chart.get("lunarDate")),
        ("干支", chart.get("chineseDate")),
        ("時辰", chart.get("time")),
        ("星座", chart.get("sign")),
        ("生肖", chart.get("zodiac")),
        ("五行局", chart.get("fiveElementsClass")),
        ("命主", chart.get("soul")),
        ("身主", chart.get("body")),
    ]
    lines.append("## 基本資訊")
    lines.extend(f"- {k}：{v}" for k, v in basic if v)

    # ── 十二宮 ─────────────────────────────────────────────────
    lines.append("\n## 十二宮位")
    palaces = chart.get("palaces") or []
    for p in palaces:
        if not isinstance(p, dict):
            continue
        name = p.get("name", "")
        stem = p.get("heavenlyStem", "")
        branch = p.get("earthlyBranch", "")
        body_mark = "（身宮）" if p.get("isBodyPalace") else ""
        header = f"### {name}{body_mark}　{stem}{branch}"

        major = _fmt_stars(p.get("majorStars"))
        minor = _fmt_stars(p.get("minorStars"))
        adj = _fmt_stars(p.get("adjectiveStars"))

        decadal = p.get("decadal") or {}
        drange = decadal.get("range") if isinstance(decadal, dict) else None
        daxian = f"{drange[0]}-{drange[1]}" if isinstance(drange, list) and len(drange) == 2 else "—"

        lines.append(header)
        lines.append(f"  主星：{major}")
        lines.append(f"  輔星：{minor}")
        lines.append(f"  雜曜：{adj}")
        lines.append(f"  大限：{daxian} 歲")

    return "\n".join(lines)
