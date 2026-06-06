# 🔮 紫微斗數 Multi-Agent AI 系統

[![GitHub Stars](https://img.shields.io/github/stars/Tsai1030/Full-multi-agent?style=social)](https://github.com/Tsai1030/Full-multi-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Gemini-3.5%20Flash-8E75B2.svg)](https://ai.google.dev/)
[![iztro](https://img.shields.io/badge/iztro-2.5-purple.svg)](https://github.com/SylarLong/iztro)

> 一套以 **真實命盤** 為基礎的紫微斗數 AI 分析系統。
> 命盤由官方 **iztro 排盤引擎** 精準計算（不由 LLM 編造），再交給 **LangGraph multi-agent**
> 結合 **ChromaDB RAG 知識庫** 與 **Web Search** 進行深度解盤。全系統僅需一把 **Google Gemini** 金鑰。

---

## ✨ 核心特色

### 🧮 真實命盤，絕不編造
- 命盤由 [**iztro**](https://github.com/SylarLong/iztro) 官方排盤引擎在**前端**直接計算，結果與 iztro 完全一致。
- 完整呈現十二宮：主星（含廟旺亮度）、輔星、雜曜、**生年四化（祿權科忌）**、大限、命主／身主、五行局、身宮。
- LLM 只負責「解讀」命盤，**不負責排盤**，從根本杜絕星曜幻覺。

### 🎨 自訂主題命盤盤面
- 傳統 **4×4 十二宮格** 盤面，中央顯示基本命格資訊。
- 沿用金色／星空神秘主題，四化以彩色標籤標示，響應式設計。

### 🤖 LangGraph Multi-Agent（ReAct Loop）
- `orchestrator → tools → synthesizer` 的 Graph 架構，動態決定工具呼叫順序。
- 讀取已排好的命盤，自主查詢知識庫 / 網路，最後彙整成結構化解析報告。
- 迭代上限保護，確保回應時間可控。

### 📚 RAG 專業知識庫
- **ChromaDB** 持久化向量庫，啟動時自動索引（idempotent）。
- 嵌入模型使用 **Gemini Embedding**，紫微斗數知識庫（JSON chunks）。

### 🌐 Web Search
- 主要使用 **Tavily**，未設金鑰時自動 fallback 至 **DuckDuckGo**。

### 🟣 單一金鑰即可運行
- LLM（`gemini-3.5-flash`）與 Embedding（`gemini-embedding-2`）皆使用 **Google Gemini**，只需一把金鑰。

---

## 🏗️ 系統架構

```
┌──────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 14)                         │
│                                                                    │
│   出生資料表單 ──▶ iztro 排盤引擎（瀏覽器端，精準計算命盤）          │
│        │                    │                                      │
│        │                    ▼                                      │
│        │            <ZiweiChart> 主題盤面（十二宮 / 四化 / 大限）   │
│        │                                                          │
│        └────── POST /api/analyze  { birth_data, chart } ──────┐   │
└──────────────────────────────────────────────────────────────┼───┘
                                                                │
┌───────────────────────────────────────────────────────────────▼──┐
│                       FastAPI (port 8000)                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   LangGraph StateGraph                       │ │
│  │                                                              │ │
│  │   START → orchestrator ──┐  (命盤已注入 prompt)              │ │
│  │               ▲          │ tool_calls?                       │ │
│  │               │ loop     ▼                                   │ │
│  │             tools ◄──────┘                                   │ │
│  │               │  max_iterations                              │ │
│  │               ▼                                              │ │
│  │          synthesizer → END （結構化解盤報告）                │ │
│  └──────────────┬──────────────────────┬────────────────────────┘ │
│                 │                      │                          │
│         search_ziwei_knowledge    web_search                     │
│            (ChromaDB +          (Tavily / DuckDuckGo)             │
│             Gemini Embedding)                                    │
│                                                                  │
│   LLM：Google Gemini（gemini-3.5-flash）via langchain-google-genai│
└──────────────────────────────────────────────────────────────────┘
```

> **設計重點**：命盤計算在前端用 iztro 完成（單一可信來源），同一份命盤 JSON 同時用於
> 「畫盤」與「送後端解盤」，後端不再爬取外部網站，準確且穩定。

---

## 🚀 快速開始

### 環境需求

| 工具 | 版本 | 說明 |
|------|------|------|
| Python | 3.10+ | 後端 |
| [uv](https://docs.astral.sh/uv/) | 最新版 | Python 套件 / 環境管理 |
| Node.js | 18+ | 前端 |
| Yarn | 1.x | 前端套件管理 |
| Google Gemini API Key | — | [免費取得](https://aistudio.google.com/apikey) |

### 1. 複製專案

```bash
git clone https://github.com/Tsai1030/Full-multi-agent.git
cd Full-multi-agent
```

### 2. 設定環境變數

複製範例檔並填入你的 Gemini 金鑰（`.env` 已被 git 忽略，不會上傳）：

```bash
cp .env.example .env
```

`.env` 至少需填：

```env
GOOGLE_API_KEY=你的_gemini_api_key
```

其餘設定（模型名稱、RAG 路徑、CORS 等）已有合理預設值，詳見 [`.env.example`](.env.example)。

### 3. 啟動後端（uv）

```bash
cd backend
uv sync                       # 建立 .venv 並安裝所有依賴
uv run python api_server.py   # 首次啟動會自動建立 RAG 向量庫
```

後端啟動於 `http://localhost:8000`。

### 4. 啟動前端（yarn）

另開一個終端：

```bash
cd frontend
yarn install
yarn dev
```

前端啟動於 `http://localhost:3000`。

### 5. 開始使用

| 服務 | URL |
|------|-----|
| 前端 | http://localhost:3000 |
| 命盤分析 | http://localhost:3000/analyze |
| Swagger UI | http://localhost:8000/docs |
| 健康檢查 | http://localhost:8000/health |

---

## 🔮 使用流程

1. 前往 `http://localhost:3000/analyze`
2. 填入出生資料：性別、西元年月日、時辰（地支）
3. 選擇分析領域：愛情 / 財富 / 未來 / 綜合
4. （選填）輸入具體問題
5. 送出後，前端用 **iztro 即時排盤** 並顯示**命盤盤面**
6. 命盤同步送至後端，**LangGraph multi-agent** 進行解盤
7. 查看「命盤盤面 + AI 深度解析報告」

### 分析領域

| 領域 | 說明 |
|------|------|
| 💕 愛情感情 | 桃花運、夫妻宮、感情運勢與正緣分析 |
| 💰 財富事業 | 財帛宮、官祿宮、求財方位與事業契機 |
| 🔮 未來運勢 | 大限流年、人生關鍵時機與趨勢 |
| 🌟 綜合分析 | 全方位十二宮整合解析 |

---

## 📁 專案結構

```
Full-multi-agent/
├── .env.example                  # 環境變數範例（複製為 .env）
├── zi_wei_dou_shu_rag_chunks.json # RAG 知識庫資料（73 chunks）
│
├── backend/
│   ├── pyproject.toml            # uv 專案定義（Gemini + LangGraph + RAG）
│   ├── uv.lock
│   ├── api_server.py             # FastAPI 主程式，lifespan 自動建 RAG
│   └── src/
│       ├── config/settings.py    # Pydantic 設定（讀 repo 根目錄 .env）
│       ├── ziwei/
│       │   └── format.py         # 命盤 JSON → 中文摘要（餵給 agent）
│       ├── graph/
│       │   ├── state.py          # GraphState（含 chart_data）
│       │   ├── nodes.py          # orchestrator / tool_node / synthesizer（Gemini）
│       │   ├── edges.py          # should_continue 條件路由
│       │   └── builder.py        # StateGraph 編譯（lru_cache 單例）
│       ├── tools/
│       │   ├── rag_tool.py       # @tool search_ziwei_knowledge
│       │   └── web_search.py     # @tool web_search（Tavily + DDG）
│       ├── rag/
│       │   ├── vector_store.py   # ChromaDB（依 provider 選 embedding）
│       │   ├── embeddings.py     # Gemini / OpenAI embedding provider
│       │   ├── indexer.py        # 首次啟動建索引
│       │   └── retriever.py      # 語意搜尋 + 格式化
│       ├── mcp/                  # 自訂 Python MCP server（保留，命盤已改前端）
│       └── api/
│           ├── models.py         # 請求/回應模型（AnalysisRequest.chart）
│           └── router.py         # /api/analyze, /api/status, /api/domains
│
└── frontend/
    ├── tailwind.config.ts        # cosmos / gold / mystic 色票與動畫
    └── src/
        ├── app/analyze/page.tsx  # form → loading → result 狀態機
        ├── components/
        │   ├── ZiweiChart.tsx    # ★ 自訂主題命盤盤面（4×4 十二宮）
        │   ├── BirthDataForm.tsx
        │   ├── ResultDisplay.tsx
        │   └── ...
        ├── hooks/useAnalysis.ts  # 排盤 + 呼叫後端的狀態機 hook
        ├── lib/
        │   ├── ziwei.ts          # ★ iztro 排盤封裝（computeChart）
        │   └── api.ts
        └── types/index.ts        # BirthData / ZiweiChart / Palace / Star
```

---

## 🔧 API 端點

### `POST /api/analyze`

```json
{
  "birth_data": {
    "gender": "男",
    "birth_year": 1990,
    "birth_month": 5,
    "birth_day": 20,
    "birth_hour": "午"
  },
  "domain_type": "comprehensive",
  "user_question": "今年事業運如何？",
  "chart": { "...": "前端 iztro 計算好的命盤 JSON（十二宮 / 星曜 / 四化）" }
}
```

> `chart` 由前端排盤後附上；後端據此解盤，不會自行排盤。

回應：

```json
{
  "success": true,
  "result": "## 命盤基本格局\n...",
  "metadata": { "domain_type": "comprehensive", "iterations": 6, "elapsed_ms": 18234 }
}
```

| 端點 | 說明 |
|------|------|
| `POST /api/analyze` | 命盤解析（主要端點） |
| `GET /api/status` | 系統狀態（RAG 文件數、工具清單） |
| `GET /api/domains` | 四大分析領域 |
| `GET /api/birth-hours` | 十二時辰對照 |
| `GET /health` | 健康檢查 |

---

## ⚙️ 設定說明

所有設定皆可於 `.env` 覆寫（鍵名見 [`.env.example`](.env.example)）。

| 變數 | 預設 | 說明 |
|------|------|------|
| `GOOGLE_API_KEY` | — | **必填**，Gemini 金鑰 |
| `GEMINI_MODEL` | `gemini-3.5-flash` | multi-agent 使用的 LLM |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-2` | RAG 嵌入模型 |
| `EMBEDDING_PROVIDER` | `gemini` | `gemini` 或 `openai` |
| `TAVILY_API_KEY` | 空 | 留空則用 DuckDuckGo |
| `GRAPH_MAX_ITERATIONS` | `6` | ReAct loop 最大迭代次數 |
| `RAG_TOP_K` / `RAG_MIN_SCORE` | `5` / `0.3` | RAG 檢索參數 |
| `APP_CORS_ORIGINS` | `http://localhost:3000` | 前端來源白名單 |

> **時辰對應**：地支 `子→0 … 亥→11`（`子時` 取 `00:00–01:00` 早子，與一般 iztro 應用一致）。

---

## 🧩 技術細節

- **命盤一致性**：前端 [`lib/ziwei.ts`](frontend/src/lib/ziwei.ts) 呼叫 `astro.bySolar(date, timeIndex, gender, true, 'zh-TW')`，序列化後同時供 [`ZiweiChart.tsx`](frontend/src/components/ZiweiChart.tsx) 畫盤與後端解盤。
- **後端格式化**：[`ziwei/format.py`](backend/src/ziwei/format.py) 把命盤 JSON 轉成中文摘要，注入 orchestrator prompt，明確要求 LLM「以此命盤為唯一依據」。
- **Gemini 相容處理**：`gemini-3.5-flash` 回覆為 thinking 分段（已轉純文字）；且 function-call turn 必須緊接 user / function-response turn，因此 orchestrator 首回合會將使用者訊息持久化進 state。
- **設定載入**：`settings.py` 以絕對路徑讀取 **repo 根目錄** 的 `.env`，無論從哪個 cwd 啟動皆可。

---

## 🐛 常見問題

| 問題 | 解決方式 |
|------|---------|
| `RAG init failed: API key required` | `.env` 未填 `GOOGLE_API_KEY`，或 `.env` 不在 repo 根目錄 |
| 命盤日期錯誤 / 排盤失敗 | 確認出生年月日為有效國曆日期 |
| 前端連不到後端 | 確認後端已啟動於 `:8000`，且 `APP_CORS_ORIGINS` 含前端位址 |
| 分析很慢 | 正常，multi-agent 會多輪查詢知識庫；可調低 `GRAPH_MAX_ITERATIONS` |
| 想換模型 | 改 `.env` 的 `GEMINI_MODEL` / `GEMINI_EMBEDDING_MODEL` 即可 |

---

## 📦 技術棧

**Backend** — FastAPI · LangGraph · langchain-google-genai（Gemini）· ChromaDB · Tavily · Loguru · pydantic-settings · uv

**Frontend** — Next.js 14（App Router）· TypeScript · Tailwind CSS · Framer Motion · **iztro** · Yarn

---

## 📝 版本記錄

### v2.1.0（2026-06-06）— 當前版本
- **新增命盤功能**：以官方 **iztro** 引擎在前端精準排盤，新增自訂主題 **十二宮命盤盤面**。
- **全面改用 Google Gemini**：LLM 換成 `gemini-3.5-flash`、Embedding 換成 `gemini-embedding-2`，全系統只需一把金鑰。
- **命盤驅動解盤**：前端排好的命盤 JSON 一併送後端，agent 以真實命盤解讀，後端不再爬取外部網站。
- **uv 化後端**：新增 `pyproject.toml` / `uv.lock`，以 `uv sync` / `uv run` 管理。
- **設定修正**：`.env` 改由 repo 根目錄絕對路徑載入，修正從 `backend/` 啟動時金鑰讀不到的問題。

### v2.0.0（2026-04-29）
- 架構全面重寫：LangGraph StateGraph、自訂 Python MCP Server、Next.js 14 前端。

### v1.x（2025-07）
- 初始版本：Multi-Agent coordinator + Node.js MCP + React CRA。

---

## 📄 授權

本專案採用 [MIT License](LICENSE)。

---

<div align="center">

**🔮 以 AI 之眼，洞見命理之道 🔮**

*Built with ❤️ by [Tsai1030](https://github.com/Tsai1030)*

</div>
