# GitHub 上傳指南

## 🚀 準備上傳到 GitHub

### 1. 檢查敏感信息

在上傳前，請確認以下敏感信息已被排除：

#### ✅ 已排除的文件類型：
- API 金鑰和密碼
- 向量資料庫文件 (`vector_db_*/`)
- 測試結果和調試文件
- 臨時文件和快取
- PDF 文件（版權問題）
- 大型模型文件

#### ⚠️ 需要手動檢查的文件：
```bash
# 檢查是否有 API 金鑰
grep -r "sk-" src/ --exclude-dir=__pycache__
grep -r "claude-" src/ --exclude-dir=__pycache__
grep -r "openai" src/config/ --exclude-dir=__pycache__

# 檢查環境變數文件
ls -la | grep env
```

### 2. 清理不需要的文件

```bash
# 刪除測試文件
rm -f test_*.py debug_*.py *_test.py
rm -f test_*.html test_*.json *_test.txt
rm -f *_response_*.html

# 刪除快取
rm -rf cache/
rm -rf __pycache__/
rm -rf src/__pycache__/

# 刪除向量資料庫
rm -rf vector_db_*/
rm -rf test_*_vector_db/

# 刪除日誌
rm -rf logs/
```

### 3. 創建環境變數範本

創建 `.env.example` 文件作為配置範本：

```bash
# OpenAI API 設定
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30

# Anthropic API 設定  
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_TIMEOUT=35

# MCP 設定
MCP_TIMEOUT=30

# 協調器設定
COORDINATOR_TIMEOUT=45

# 向量資料庫設定
VECTOR_DB_NAME=test1
VECTOR_DB_PATH=./vector_db_test1
```

### 4. 更新 README.md

確保 README.md 包含：
- 項目描述
- 安裝指南
- 配置說明
- 使用方法
- API 金鑰設定說明

### 5. Git 初始化和上傳

```bash
# 初始化 Git（如果還沒有）
git init

# 添加遠程倉庫
git remote add origin https://github.com/your-username/your-repo-name.git

# 檢查狀態
git status

# 添加文件
git add .

# 檢查將要提交的文件
git status

# 提交
git commit -m "Initial commit: 紫微斗數AI系統

- 完整的Multi-Agent協作系統
- 真實命盤數據抓取
- RAG知識檢索系統
- React前端界面
- 性能優化和錯誤處理
- 編號格式修復"

# 推送到 GitHub
git push -u origin main
```

### 6. 上傳後的設定

#### 在 GitHub 上：
1. 設定 Repository 描述
2. 添加 Topics 標籤：`ziwei`, `ai`, `multi-agent`, `rag`, `react`
3. 設定 README.md 作為主頁
4. 檢查 .gitignore 是否正確排除敏感文件

#### 設定 GitHub Secrets（如果需要 CI/CD）：
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

### 7. 項目結構說明

上傳後的主要目錄結構：
```
├── src/                    # 核心源代碼
│   ├── agents/            # Multi-Agent 系統
│   ├── config/            # 配置文件
│   ├── mcp/               # MCP 工具
│   ├── output/            # 輸出格式化
│   ├── rag/               # RAG 系統
│   └── utils/             # 工具函數
├── frontend/              # React 前端
├── mcp-server/           # MCP 服務器
├── docs/                 # 文檔
├── examples/             # 示例代碼
├── main.py               # 主程序
├── api_server.py         # API 服務器
├── requirements.txt      # Python 依賴
└── README.md            # 項目說明
```

### 8. 注意事項

#### 🔒 安全性：
- 絕對不要上傳 API 金鑰
- 檢查所有配置文件
- 使用環境變數管理敏感信息

#### 📦 文件大小：
- GitHub 單文件限制 100MB
- 向量資料庫文件太大，已排除
- PDF 文件有版權問題，已排除

#### 🧪 測試：
- 上傳後在新環境中測試
- 確認依賴安裝正確
- 驗證配置文件範本

### 9. 克隆後的設定指南

為其他用戶提供設定指南：

```bash
# 克隆倉庫
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# 安裝 Python 依賴
pip install -r requirements.txt

# 複製環境變數範本
cp .env.example .env

# 編輯 .env 文件，添加您的 API 金鑰
nano .env

# 安裝前端依賴
cd frontend
npm install
cd ..

# 創建向量資料庫
python create_vector_db.py

# 啟動系統
python main.py
```

### 10. 後續維護

- 定期更新依賴
- 添加新功能時更新文檔
- 保持 .gitignore 最新
- 監控倉庫大小
