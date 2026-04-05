# 📋 GitHub 上傳檢查清單

## ✅ 上傳前必須檢查的項目

### 🔒 安全性檢查
- [ ] 確認沒有真實的 API 金鑰在代碼中
- [ ] 檢查 `.env` 文件已被 `.gitignore` 排除
- [ ] 確認 `.env.example` 只包含範本，沒有真實金鑰
- [ ] 檢查所有配置文件沒有敏感信息

### 📁 文件清理
- [ ] 刪除所有測試文件 (`test_*.py`, `debug_*.py`)
- [ ] 刪除臨時 HTML 文件 (`*_response_*.html`)
- [ ] 刪除測試結果文件 (`test_*.json`, `*_test.txt`)
- [ ] 清理快取目錄 (`cache/`, `__pycache__/`)
- [ ] 刪除向量資料庫文件 (`vector_db_*/`)
- [ ] 刪除日誌文件 (`logs/`)
- [ ] 刪除 PDF 文件（版權問題）
- [ ] 刪除批次檔案 (`*.bat`)

### 📦 依賴和配置
- [ ] 確認 `requirements.txt` 是最新的
- [ ] 檢查 `package.json` 文件完整
- [ ] 確認 `.gitignore` 規則正確
- [ ] 檢查 `README.md` 內容完整

### 🖼️ 媒體文件
- [ ] 確認圖片文件大小合理（<5MB）
- [ ] 檢查圖片路徑在 README.md 中正確
- [ ] 考慮是否保留 `前後端呈現畫面/` 目錄

### 📊 項目結構
- [ ] 確認核心目錄存在：`src/`, `frontend/`, `mcp-server/`
- [ ] 檢查主要文件存在：`main.py`, `api_server.py`
- [ ] 確認文檔目錄：`docs/`, `examples/`

## 🚀 執行上傳

### 1. 自動清理（推薦）
```bash
python cleanup_for_github.py
```

### 2. 手動檢查
```bash
# 檢查敏感文件
find . -name "*.env" -not -name ".env.example"
find . -name "*key*" -not -path "./.git/*"
find . -name "*secret*" -not -path "./.git/*"

# 檢查大文件
find . -size +10M -not -path "./.git/*"

# 檢查項目大小
du -sh .
```

### 3. Git 操作
```bash
# 檢查狀態
git status

# 檢查將要提交的文件
git add --dry-run .

# 實際添加文件
git add .

# 提交
git commit -m "Initial commit: 紫微斗數AI系統

Features:
- Multi-Agent 協作系統 (Claude + GPT + Domain Agents)
- RAG 知識檢索系統 (BGE-M3 + ChromaDB)
- 真實命盤數據抓取
- React 前端界面
- FastAPI 後端服務
- 性能優化和錯誤處理
- 編號格式修復"

# 推送到 GitHub
git push -u origin main
```

## 📝 上傳後的設定

### GitHub Repository 設定
- [ ] 設定 Repository 描述
- [ ] 添加 Topics: `ziwei`, `ai`, `multi-agent`, `rag`, `react`, `fastapi`, `claude`, `gpt`
- [ ] 設定 README.md 作為主頁
- [ ] 檢查 About 部分的鏈接

### 文檔更新
- [ ] 確認 README.md 在 GitHub 上顯示正確
- [ ] 檢查圖片是否正常顯示
- [ ] 更新安裝指南（如果需要）

### 測試
- [ ] 在新環境中克隆測試
- [ ] 確認依賴安裝正確
- [ ] 測試基本功能

## ⚠️ 常見問題

### 文件太大
- 向量資料庫文件通常很大，已在 `.gitignore` 中排除
- PDF 文件可能很大，建議排除
- 如果 Repository 超過 1GB，考慮使用 Git LFS

### 圖片顯示問題
- 確認圖片路徑使用相對路徑
- 檢查圖片文件名沒有中文字符
- 考慮將圖片上傳到 GitHub 或使用 CDN

### 依賴問題
- 確認 `requirements.txt` 包含所有必要依賴
- 檢查版本號是否正確
- 測試在乾淨環境中安裝

## 🎯 成功指標

上傳成功後，您的 Repository 應該：
- ✅ 沒有敏感信息洩露
- ✅ 文件大小合理（<100MB）
- ✅ README.md 顯示完整
- ✅ 圖片正常顯示
- ✅ 代碼結構清晰
- ✅ 文檔完整易懂

## 📞 需要幫助？

如果遇到問題：
1. 檢查 `.gitignore` 設定
2. 確認文件權限
3. 檢查網絡連接
4. 查看 Git 錯誤信息
5. 考慮分批上傳大文件
