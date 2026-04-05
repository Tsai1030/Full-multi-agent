# Full Multi-Agent 紫微斗數 AI 系統架構文檔

## 📋 系統概述

這是一個基於多智能體協作的紫微斗數命理分析系統，結合了現代 AI 技術、RAG（檢索增強生成）系統和 Web 爬蟲技術，提供專業的命理分析服務。

### 🎯 核心特色
- **Multi-Agent 協作**：Claude、GPT、Domain 三個 AI 智能體協同工作
- **RAG 知識檢索**：基於 BGE-M3 嵌入模型的向量數據庫
- **Web 爬蟲整合**：自動獲取紫微斗數命盤數據
- **React 前端界面**：現代化的用戶交互體驗
- **FastAPI 後端**：高性能的 API 服務

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ ZiweiForm   │ │ LoadingAnim │ │ ResultDisplay           │ │
│  │ 用戶輸入     │ │ 載入動畫     │ │ 結果顯示 (Markdown)      │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 ZiweiAISystem                           │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │ WebScraper  │ │ Multi-Agent │ │ GPT4o Formatter     │ │ │
│  │  │ 命盤爬取     │ │ 協調器       │ │ 輸出格式化           │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Multi-Agent Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ Claude      │ │ GPT Agent   │ │ Domain Agent            │ │
│  │ 邏輯推理     │ │ 創意解釋     │ │ 專業領域分析             │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    RAG System                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ BGE-M3      │ │ ChromaDB    │ │ GPT4o Generator         │ │
│  │ 嵌入模型     │ │ 向量數據庫   │ │ 知識檢索回答             │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📁 目錄結構與文件作用

### 🎨 Frontend (React)
```
frontend/
├── src/
│   ├── components/
│   │   ├── ZiweiForm.js              # 用戶輸入表單組件
│   │   ├── LoadingAnimation.js       # 標準載入動畫
│   │   ├── WizardDivination.js       # 巫師占卜動畫
│   │   ├── ResultDisplay.js          # 結果顯示組件 (含 Markdown 處理)
│   │   ├── Header.js                 # 頁面標題組件
│   │   └── SimpleBackground.js       # 背景組件
│   ├── App.js                        # 主應用組件
│   ├── App.css                       # 全局樣式
│   └── index.js                      # React 入口點
├── public/
│   └── wizard_icon/                  # 巫師主題圖標資源
└── package.json                      # 前端依賴配置
```

### 🚀 Backend (FastAPI)
```
src/
├── config/
│   └── settings.py                   # 系統配置管理
├── agents/
│   ├── base_agent.py                 # Agent 基礎類別
│   ├── claude_agent.py               # Claude 智能體 (邏輯推理)
│   ├── gpt_agent.py                  # GPT 智能體 (創意解釋)
│   └── domain_agent.py               # 領域智能體 (專業分析)
├── coordination/
│   ├── coordinator.py                # Multi-Agent 協調器
│   └── discussion.py                 # Agent 討論機制
├── rag/
│   ├── rag_system.py                 # RAG 系統主控制器
│   ├── bge_embeddings.py             # BGE-M3 嵌入模型
│   ├── vector_store.py               # ChromaDB 向量數據庫
│   └── gpt4o_generator.py            # GPT4o 知識檢索生成器
├── output/
│   └── gpt4o_formatter.py            # GPT4o 輸出格式化器
├── web_scraper/
│   ├── ziwei_scraper.py              # 紫微斗數網站爬蟲
│   └── data_parser.py                # 命盤數據解析器
└── main.py                           # 系統主控制器
```

### 🔧 配置與工具
```
├── api_server.py                     # FastAPI 服務器
├── .env                              # 環境變數配置
├── .env.example                      # 配置範例
├── requirements.txt                  # Python 依賴
└── test_*.py                         # 各種測試腳本
```

## 🔄 系統運作流程

### 1. 用戶交互流程
```
用戶輸入 → 表單驗證 → API 請求 → 載入動畫 → 結果顯示
```

### 2. 後端處理流程
```
API 接收 → 命盤爬取 → Multi-Agent 協作 → 結果格式化 → 返回前端
```

### 3. 詳細執行步驟

#### 步驟 1: 用戶輸入處理
1. **ZiweiForm.js** 收集用戶輸入：
   - 性別、出生年月日、出生時辰
   - 分析領域選擇 (愛情/財富/未來)
   - 動畫偏好設置

2. **表單驗證**：
   - 檢查必填欄位
   - 驗證日期格式
   - 確認時辰選擇

#### 步驟 2: API 請求與載入
1. **HTTP POST** 到 `/analyze` 端點
2. **載入動畫顯示**：
   - WizardDivination.js (巫師占卜動畫)
   - LoadingAnimation.js (標準進度條)

#### 步驟 3: 後端命盤獲取
1. **ZiweiScraper** 爬取命盤：
   ```python
   # ziwei_scraper.py
   async def get_ziwei_chart(birth_data):
       # 構建請求參數
       # 發送 HTTP 請求到紫微斗數網站
       # 解析 HTML 響應
       return chart_data
   ```

2. **DataParser** 解析命盤數據：
   ```python
   # data_parser.py
   def parse_chart_data(html_content):
       # 提取宮位信息
       # 解析主星配置
       # 整理命盤結構
       return structured_data
   ```

#### 步驟 4: Multi-Agent 協作分析
1. **Coordinator** 初始化三個 Agent：
   ```python
   # coordinator.py
   agents = [
       ClaudeAgent(),    # 邏輯推理分析
       GPTAgent(),       # 創意解釋表達
       DomainAgent()     # 專業領域知識
   ]
   ```

2. **Agent 協作討論**：
   ```python
   # discussion.py
   for round in range(max_rounds):
       for agent in agents:
           response = await agent.analyze(chart_data, context)
           discussion_context.add_response(response)
       
       if consensus_reached():
           break
   ```

3. **各 Agent 的職責**：
   - **Claude Agent**: 深度邏輯推理，命盤結構分析
   - **GPT Agent**: 創意表達，生動的命理解釋
   - **Domain Agent**: 專業領域知識，針對性建議

#### 步驟 5: RAG 知識檢索增強
1. **BGE-M3 嵌入**：
   ```python
   # bge_embeddings.py
   embeddings = model.encode(query_text)
   ```

2. **ChromaDB 檢索**：
   ```python
   # vector_store.py
   results = collection.query(
       query_embeddings=embeddings,
       n_results=top_k
   )
   ```

3. **GPT4o 知識生成**：
   ```python
   # gpt4o_generator.py
   response = await client.chat.completions.create(
       model="gpt-4o-mini",
       messages=[
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": f"Context: {context}\nQuery: {query}"}
       ]
   )
   ```

#### 步驟 6: 輸出格式化
1. **GPT4o Formatter** 統一格式：
   ```python
   # gpt4o_formatter.py
   formatted_result = await format_coordination_result(
       coordination_result=agent_responses,
       domain_type=domain,
       output_format="json_to_narrative"
   )
   ```

2. **Markdown 格式生成**：
   - 結構化標題 (##, ###)
   - 重點標記 (**粗體**)
   - 列表建議 (1. 項目)

#### 步驟 7: 前端結果顯示
1. **ResultDisplay.js** 處理響應：
   ```javascript
   // 自定義 Markdown 處理器
   const processMarkdown = (text) => {
       text = text.replace(/^## (.+)$/gm, '<h2 class="md-h2">$1</h2>');
       text = text.replace(/\*\*(.+?)\*\*/g, '<strong class="md-strong">$1</strong>');
       return text;
   };
   ```

2. **樣式渲染**：
   - 白色標題文字，帶底線分隔
   - 白色粗體重點標記
   - 適當的間距和行高

## 🔧 核心技術組件

### Multi-Agent 協作機制
- **異步並行處理**：三個 Agent 同時分析
- **討論共識機制**：多輪對話達成一致
- **角色專業化**：每個 Agent 專精不同領域

### RAG 檢索增強
- **BGE-M3 嵌入**：多語言、高質量的文本嵌入
- **ChromaDB 向量庫**：高效的相似性檢索
- **GPT4o Mini**：成本優化的知識生成

### Web 爬蟲系統
- **異步 HTTP 請求**：高效的網站數據獲取
- **HTML 解析**：結構化命盤數據提取
- **錯誤處理**：網絡異常和數據異常處理

### 前端 Markdown 處理
- **自定義處理器**：避免 React 組件錯誤
- **CSS 樣式控制**：完全控制顯示效果
- **安全 HTML 渲染**：防止 XSS 攻擊

## 🚀 系統啟動流程

### 1. 後端啟動
```bash
# 安裝依賴
pip install -r requirements.txt

# 配置環境變數
cp .env.example .env
# 編輯 .env 填入 API 金鑰

# 啟動 FastAPI 服務器
python api_server.py
# 或
python main.py
```

### 2. 前端啟動
```bash
cd frontend
npm install
npm start
```

### 3. 系統初始化
1. **RAG 系統初始化**：載入 BGE-M3 模型
2. **向量數據庫連接**：建立 ChromaDB 連接
3. **Agent 初始化**：配置 Claude、GPT、Domain Agent
4. **API 服務啟動**：FastAPI 服務器監聽 8000 端口
5. **前端服務啟動**：React 開發服務器監聽 3000 端口

## 📊 性能優化

### 成本優化
- **GPT-4o Mini**：相比 GPT-4o 節省 90%+ 成本
- **異步處理**：提高並發處理能力
- **向量檢索**：減少 LLM 調用次數

### 用戶體驗
- **載入動畫**：巫師主題的視覺反饋
- **Markdown 渲染**：結構化的結果顯示
- **響應式設計**：適配不同設備

### 系統穩定性
- **錯誤處理**：完善的異常捕獲機制
- **重試機制**：網絡請求失敗重試
- **日誌記錄**：詳細的系統運行日誌

## 🔮 未來擴展方向

1. **更多 AI 模型整合**：支持更多 LLM 提供商
2. **知識庫擴充**：增加更多命理知識內容
3. **個性化推薦**：基於用戶歷史的個性化分析
4. **移動端適配**：開發移動應用版本
5. **實時協作**：支持多用戶實時討論功能

## ⚙️ 配置管理

### 環境變數配置
```bash
# AI 模型 API 金鑰
OPENAI_API_KEY=sk-proj-...                    # OpenAI API 金鑰
ANTHROPIC_API_KEY=sk-ant-...                  # Claude API 金鑰
OPENAI_MODEL_GPT4O=gpt-4o-mini               # 使用 GPT-4o Mini 節省成本

# RAG 系統配置
EMBEDDING_MODEL=BAAI/bge-m3                   # BGE-M3 嵌入模型
EMBEDDING_PROVIDER=huggingface                # 使用 HuggingFace
EMBEDDING_DEVICE=cpu                          # CPU 運行 (可改為 cuda)
VECTOR_DB_PATH=./data/vector_db               # 向量數據庫路徑

# 紫微斗數網站配置
ZIWEI_WEBSITE_URL=https://fate.windada.com/cgi-bin/fate
ZIWEI_REQUEST_TIMEOUT=30                      # 請求超時時間
ZIWEI_MAX_RETRIES=3                          # 最大重試次數

# 服務配置
APP_HOST=localhost                            # 服務主機
APP_PORT=8000                                # 後端端口
CORS_ORIGINS=http://localhost:3000           # 前端跨域配置
```

### Agent 配置參數
```python
# Claude Agent 配置
CLAUDE_MODEL=claude-3-5-sonnet-20241022      # Claude 模型版本
CLAUDE_TEMPERATURE=0.3                       # 邏輯推理低溫度
CLAUDE_MAX_TOKENS=4000                       # 最大輸出長度

# GPT Agent 配置
GPT_MODEL=gpt-4o-mini                        # GPT 模型版本
GPT_TEMPERATURE=0.7                          # 創意表達中等溫度
GPT_MAX_TOKENS=4000                          # 最大輸出長度

# Domain Agent 配置
DOMAIN_TEMPERATURE=0.5                       # 專業分析中低溫度
DOMAIN_MAX_TOKENS=4000                       # 最大輸出長度
```

## 🔍 關鍵程式碼邏輯

### 1. 主系統控制器 (main.py)
```python
class ZiweiAISystem:
    async def analyze_ziwei_chart(self, birth_data, domain_type, output_format):
        # 步驟 1: 獲取命盤數據
        chart_data = await self.scraper.get_ziwei_chart(birth_data)

        # 步驟 2: Multi-Agent 協作分析
        coordination_result = await self.coordinator.coordinate_analysis(
            chart_data, domain_type
        )

        # 步驟 3: RAG 知識檢索增強
        enhanced_result = await self.rag_system.enhance_analysis(
            coordination_result, domain_type
        )

        # 步驟 4: 格式化輸出
        formatted_result = await self.formatter.format_result(
            enhanced_result, output_format
        )

        return formatted_result
```

### 2. Multi-Agent 協調器 (coordinator.py)
```python
class MultiAgentCoordinator:
    async def coordinate_analysis(self, chart_data, domain_type):
        # 初始化討論上下文
        discussion = DiscussionContext(chart_data, domain_type)

        # 多輪協作討論
        for round_num in range(self.max_rounds):
            # 並行執行三個 Agent 分析
            tasks = [
                self.claude_agent.analyze(discussion.get_context()),
                self.gpt_agent.analyze(discussion.get_context()),
                self.domain_agent.analyze(discussion.get_context())
            ]

            responses = await asyncio.gather(*tasks)
            discussion.add_round(responses)

            # 檢查是否達成共識
            if discussion.check_consensus():
                break

        return discussion.get_final_result()
```

### 3. RAG 檢索系統 (rag_system.py)
```python
class RAGSystem:
    async def enhance_analysis(self, analysis_result, domain_type):
        # 提取關鍵詞進行檢索
        keywords = self.extract_keywords(analysis_result)

        # BGE-M3 嵌入
        embeddings = await self.embeddings.encode(keywords)

        # 向量檢索
        relevant_docs = await self.vector_store.search(
            embeddings, top_k=5
        )

        # GPT4o 知識增強
        enhanced_result = await self.generator.enhance_with_knowledge(
            analysis_result, relevant_docs, domain_type
        )

        return enhanced_result
```

### 4. 前端 Markdown 處理 (ResultDisplay.js)
```javascript
const processMarkdown = (text) => {
    if (!text || typeof text !== 'string') return '';

    let processedText = text;

    // 標題處理
    processedText = processedText.replace(/^## (.+)$/gm, '<h2 class="md-h2">$1</h2>');
    processedText = processedText.replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>');

    // 粗體和斜體
    processedText = processedText.replace(/\*\*(.+?)\*\*/g, '<strong class="md-strong">$1</strong>');
    processedText = processedText.replace(/\*([^*]+?)\*/g, '<em class="md-em">$1</em>');

    // 列表處理
    processedText = processedText.replace(/^(\d+)\. (.+)$/gm, '<li class="md-li">$2</li>');
    processedText = processedText.replace(/^- (.+)$/gm, '<li class="md-li">$1</li>');

    return processedText;
};
```

## 🛠️ 開發工具與測試

### 測試腳本
```bash
# 測試 GPT-4o Mini 配置
python test_gpt4o_mini.py

# 測試 Markdown 輸出
python test_markdown_output.py

# 測試主系統
python test_main_system.py

# 測試已知可工作的數據
python test_with_working_data.py
```

### 調試工具
- **日誌系統**：詳細的運行日誌記錄
- **錯誤追蹤**：完整的異常堆棧信息
- **性能監控**：處理時間和資源使用統計
- **API 測試**：Postman 集合和自動化測試

## 📈 系統監控與維護

### 關鍵指標
- **響應時間**：平均分析處理時間
- **成功率**：請求成功完成比例
- **錯誤率**：各類錯誤發生頻率
- **資源使用**：CPU、內存、網絡使用情況

### 維護任務
- **定期更新**：AI 模型和依賴庫更新
- **數據備份**：向量數據庫和配置備份
- **性能優化**：根據使用情況調整參數
- **安全檢查**：API 金鑰和敏感信息保護

## 🔐 安全考量

### API 安全
- **環境變數**：敏感信息不直接寫入代碼
- **CORS 配置**：限制跨域請求來源
- **請求限制**：防止 API 濫用
- **錯誤處理**：不洩露系統內部信息

### 數據安全
- **用戶隱私**：不存儲個人敏感信息
- **傳輸加密**：HTTPS 加密通信
- **輸入驗證**：防止注入攻擊
- **HTML 安全**：防止 XSS 攻擊

---

*本文檔描述了 Full Multi-Agent 紫微斗數 AI 系統的完整架構和運作流程，為系統維護和擴展提供技術參考。*
