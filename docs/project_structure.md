# 紫微斗數AI系統 - 專案結構

## 目錄結構
```
ziwei_ai_system/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── react_agent.py          # ReAct Agent核心邏輯
│   │   └── agent_controller.py     # Agent控制器
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── mcp_server.py          # MCP服務器
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   └── ziwei_tool.py      # 紫微斗數網站調用工具
│   │   └── parsers/
│   │       ├── __init__.py
│   │       └── ziwei_parser.py    # 網站結果解析器
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── vector_store.py        # 向量資料庫
│   │   ├── document_loader.py     # 文檔載入器
│   │   └── retriever.py          # 檢索器
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system_prompts.py      # 系統prompt
│   │   ├── domain_prompts.py      # 領域專業prompt
│   │   └── format_prompts.py      # JSON格式化prompt
│   ├── api/
│   │   ├── __init__.py
│   │   ├── claude_client.py       # Claude API客戶端
│   │   └── main_api.py           # 主要API端點
│   ├── frontend/
│   │   ├── static/
│   │   ├── templates/
│   │   └── app.py                # Flask/FastAPI應用
│   └── utils/
│       ├── __init__.py
│       ├── validators.py         # 輸入驗證
│       └── formatters.py        # 格式化工具
├── data/
│   ├── documents/               # 紫微斗數文檔
│   └── vector_db/              # 向量資料庫文件
├── config/
│   ├── settings.py             # 配置設定
│   └── prompts.json           # Prompt配置
├── tests/
│   ├── test_agent.py
│   ├── test_mcp.py
│   ├── test_rag.py
│   └── test_integration.py
├── requirements.txt
├── environment.yml            # Conda環境配置
└── README.md
```

## 核心組件說明

### 1. ReAct Agent (src/agent/)
- 實現Action-Reasoning-Observation循環
- 協調MCP工具調用和RAG檢索
- 管理整體工作流程

### 2. MCP工具層 (src/mcp/)
- 紫微斗數網站API調用
- 結果解析和結構化
- 錯誤處理和重試機制

### 3. RAG系統 (src/rag/)
- 向量資料庫建置
- 文檔檢索和相似度匹配
- 知識片段提取

### 4. Prompt系統 (src/prompts/)
- 系統基礎prompt
- 三種專業領域prompt
- JSON格式化prompt

### 5. API層 (src/api/)
- Claude API整合
- RESTful API端點
- 請求/回應處理

## 技術棧
- **AI Agent**: LangChain + Custom ReAct Implementation
- **MCP**: Custom MCP Server with HTTP tools
- **RAG**: ChromaDB/Pinecone + OpenAI Embeddings
- **LLM**: Claude API (Anthropic)
- **Backend**: FastAPI/Flask
- **Frontend**: React/Vue.js (可選)
- **Database**: SQLite/PostgreSQL (用戶數據)
- **Vector DB**: ChromaDB/Pinecone
