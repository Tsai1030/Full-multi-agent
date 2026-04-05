# 🌟 紫微斗數 AI 系統 - 前端設置指南

> **注意**: 這是 GitHub 版本的設置指南，包含完整的前後端系統。

## 📋 系統架構

```
紫微斗數 AI 系統
├── 後端 (FastAPI)
│   ├── api_server.py          # API 服務器
│   ├── main.py               # AI 系統核心
│   └── src/                  # 源代碼
└── 前端 (React)
    ├── public/               # 靜態資源
    ├── src/
    │   ├── components/       # React 組件
    │   ├── App.js           # 主應用
    │   └── index.js         # 入口文件
    └── package.json         # 依賴配置
```

## 🚀 快速啟動

### 1. 安裝 Node.js 和 npm

確保您的系統已安裝：
- Node.js (版本 16 或更高)
- npm (通常隨 Node.js 一起安裝)

檢查版本：
```bash
node --version
npm --version
```

### 2. 安裝前端依賴

```bash
cd frontend
npm install
```

### 3. 啟動開發服務器

**方式一：使用啟動腳本（推薦）**
```bash
# 在項目根目錄執行
start_server.bat
```

**方式二：手動啟動**
```bash
# 終端 1：啟動後端
python api_server.py

# 終端 2：啟動前端
cd frontend
npm start
```

### 4. 訪問應用

- 🌐 前端界面: http://localhost:3000
- 📡 後端 API: http://localhost:8000
- 📚 API 文檔: http://localhost:8000/docs

## 🎨 前端功能特色

### ✨ 動態效果
- **粒子背景**: 動態星空效果
- **載入動畫**: 多階段載入進度
- **頁面轉場**: 流暢的動畫過渡
- **懸停效果**: 互動式按鈕和卡片

### 🎯 用戶界面
- **響應式設計**: 支援桌面和移動設備
- **玻璃擬態**: 現代化半透明設計
- **漸變主題**: 紫色系科技感配色
- **中文字體**: 優化的中文顯示

### 📱 交互功能
- **表單驗證**: 即時輸入驗證
- **領域選擇**: 三種分析模式
- **結果展示**: 美觀的報告顯示
- **操作按鈕**: 分享、下載、重新分析

## 🔧 技術棧

### 前端技術
- **React 18**: 現代化前端框架
- **Material-UI**: Google Material Design
- **Framer Motion**: 高性能動畫庫
- **Styled Components**: CSS-in-JS 樣式

### 動畫庫
- **Particles.js**: 粒子背景效果
- **Lottie React**: 複雜動畫支援
- **React Spring**: 彈性動畫

### 工具庫
- **Axios**: HTTP 請求處理
- **React Hook Form**: 表單管理
- **React Toastify**: 通知提示

## 📂 組件結構

### 主要組件

**App.js** - 主應用組件
- 狀態管理
- 路由控制
- 主題配置

**ZiweiForm.js** - 輸入表單
- 出生資訊輸入
- 領域選擇
- 表單驗證

**LoadingAnimation.js** - 載入動畫
- 進度顯示
- 步驟提示
- 動態效果

**ResultDisplay.js** - 結果顯示
- 分析報告
- 操作按鈕
- 技術詳情

**Header.js** - 頁面標題
- 品牌標識
- 導航信息

## 🎨 自定義樣式

### 主題配置
```javascript
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#667eea' },
    secondary: { main: '#764ba2' },
  },
  typography: {
    fontFamily: '"Noto Sans TC", "Cinzel", sans-serif',
  },
});
```

### 動畫效果
- **fadeInUp**: 淡入向上
- **slideInLeft**: 左側滑入
- **pulse**: 脈衝效果
- **glow**: 發光效果
- **float**: 浮動效果

## 🔄 API 整合

### 請求格式
```javascript
const response = await fetch('/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    birth_data: formData,
    domain_type: domain.id,
    output_format: 'json_to_narrative',
    show_agent_process: false,
  }),
});
```

### 響應處理
```javascript
const result = await response.json();
if (result.success) {
  setAnalysisResult(result);
  setCurrentStep('result');
}
```

## 📱 響應式設計

### 斷點設置
- **xs**: 0px - 599px (手機)
- **sm**: 600px - 959px (平板)
- **md**: 960px - 1279px (小桌面)
- **lg**: 1280px+ (大桌面)

### 適配策略
- 彈性佈局 (Flexbox)
- 網格系統 (Grid)
- 相對單位 (rem, %)
- 媒體查詢 (@media)

## 🛠️ 開發指南

### 添加新組件
1. 在 `src/components/` 創建組件文件
2. 使用 Material-UI 和 Framer Motion
3. 遵循現有的樣式規範
4. 添加適當的動畫效果

### 修改樣式
1. 使用 `styled()` 創建樣式組件
2. 遵循主題配色方案
3. 保持響應式設計
4. 測試不同設備尺寸

### 調試技巧
- 使用 React Developer Tools
- 檢查 Network 標籤頁
- 查看 Console 錯誤信息
- 測試 API 端點

## 🚨 常見問題

### Q: 前端無法連接後端？
A: 檢查後端是否在 8000 端口運行，確認 CORS 設置正確。

### Q: 動畫效果不流暢？
A: 檢查瀏覽器性能，考慮減少粒子數量或禁用某些效果。

### Q: 移動設備顯示異常？
A: 檢查響應式斷點設置，調整組件的移動端樣式。

### Q: 字體顯示不正確？
A: 確認 Google Fonts 載入成功，檢查網絡連接。

## 📈 性能優化

### 建議措施
- 使用 React.memo 避免不必要的重渲染
- 懶加載大型組件
- 優化圖片和資源大小
- 使用 CDN 加速字體載入

### 監控工具
- React DevTools Profiler
- Chrome DevTools Performance
- Lighthouse 性能評分

## 🎯 未來擴展

### 計劃功能
- 用戶登錄系統
- 歷史記錄保存
- 社交分享功能
- 多語言支援
- PWA 支援

### 技術升級
- TypeScript 遷移
- Next.js 服務端渲染
- 狀態管理 (Redux/Zustand)
- 測試覆蓋 (Jest/Testing Library)

---

🎉 **恭喜！您已成功設置紫微斗數 AI 系統前端！**

如有問題，請查看控制台輸出或聯繫開發團隊。
