# 向量庫使用指南

## 📋 概覽

您的紫微斗數AI系統現在使用持久化向量庫，這意味著：
- ✅ 知識會永久保存，不會每次重啟都消失
- ✅ 系統啟動更快，不需要重複載入基礎知識
- ✅ 可以方便地添加新知識到向量庫
- ✅ 支援從文件和目錄批量載入知識

---

## 🔄 系統行為變化

### **之前的行為**
```
每次啟動 → 創建新向量庫 → 載入範例知識 → 開始服務
```

### **現在的行為**
```
啟動時檢查 → 如果向量庫存在且有數據 → 直接使用
           → 如果向量庫為空 → 載入基礎知識 → 開始服務
```

---

## 📁 向量庫位置

- **默認位置**: `./data/vector_db/`
- **集合名稱**: `ziwei_knowledge`
- **配置**: 可通過環境變數修改

```bash
# .env 文件配置
VECTOR_DB_PATH=./data/vector_db
VECTOR_DB_COLLECTION=ziwei_knowledge
```

---

## 🛠️ 向量庫管理

### **1. 查看向量庫狀態**
```bash
python manage_vector_db.py status
```

輸出範例：
```
=== 向量庫狀態 ===
系統狀態: ready
總文檔數: 15
集合名稱: ziwei_knowledge
持久化目錄: ./data/vector_db
生成器狀態: ready
使用模型: gpt-4o
```

### **2. 添加單個知識文件**
```bash
# 添加 JSON 格式的知識文件
python manage_vector_db.py add-file --file data/knowledge/example_knowledge.json

# 添加文本文件
python manage_vector_db.py add-file --file data/knowledge/new_knowledge.txt
```

### **3. 批量添加知識目錄**
```bash
python manage_vector_db.py add-dir --directory data/knowledge
```

### **4. 搜索知識**
```bash
# 搜索相關知識
python manage_vector_db.py search --query "紫微星的特質" --top-k 3
```

### **5. 清空向量庫**
```bash
# ⚠️ 危險操作：會刪除所有數據
python manage_vector_db.py clear
```

---

## 📝 知識文件格式

### **JSON 格式** (推薦)
```json
[
    {
        "content": "紫微星是紫微斗數中的帝王星...",
        "metadata": {
            "category": "主星解析",
            "star": "紫微星",
            "palace": "命宮"
        }
    },
    {
        "content": "天機星是智慧之星...",
        "metadata": {
            "category": "主星解析",
            "star": "天機星",
            "palace": "命宮"
        }
    }
]
```

### **文本格式**
```
# 文件名: ziwei_star_analysis.txt

紫微星是紫微斗數中的帝王星，具有領導能力和權威感。
紫微星坐命的人通常有以下特質：
1. 天生的領導能力
2. 喜歡掌控全局
3. 責任感強
...
```

### **Markdown 格式**
```markdown
# 紫微斗數基礎知識

## 紫微星

紫微星是紫微斗數中的帝王星...

## 天機星

天機星是智慧之星...
```

---

## 🚀 使用流程

### **首次使用**
1. 運行系統，會自動創建向量庫並載入基礎知識
2. 檢查狀態：`python manage_vector_db.py status`
3. 如需添加更多知識，使用管理工具

### **添加新知識**
1. 準備知識文件（JSON/TXT/MD 格式）
2. 放入 `data/knowledge/` 目錄
3. 使用管理工具添加：`python manage_vector_db.py add-dir --directory data/knowledge`
4. 重啟系統，新知識會自動載入

### **日常使用**
- 系統會自動使用現有的向量庫
- 無需手動操作，知識會持久保存
- 可隨時添加新知識而不影響現有數據

---

## 📊 性能優化

### **向量庫大小建議**
- **小型**: 100-500 條知識（適合個人使用）
- **中型**: 500-2000 條知識（適合專業使用）
- **大型**: 2000+ 條知識（適合企業使用）

### **知識質量建議**
- 每條知識 100-500 字為佳
- 包含豐富的元數據
- 避免重複內容
- 定期清理過時知識

---

## 🔧 故障排除

### **問題1: 向量庫初始化失敗**
```bash
# 檢查目錄權限
ls -la data/vector_db/

# 重新創建目錄
rm -rf data/vector_db
mkdir -p data/vector_db
```

### **問題2: 知識載入失敗**
```bash
# 檢查文件格式
python -m json.tool data/knowledge/example_knowledge.json

# 檢查文件編碼
file data/knowledge/example_knowledge.json
```

### **問題3: 搜索結果不準確**
- 檢查查詢關鍵詞
- 增加知識數量
- 調整搜索參數（top_k, min_score）

---

## 📚 範例知識文件

系統已包含範例知識文件：
- `data/knowledge/example_knowledge.json` - 完整的紫微斗數知識範例

您可以參考這個文件的格式來創建自己的知識文件。

---

## 🎯 最佳實踐

1. **定期備份**: 備份 `data/vector_db/` 目錄
2. **知識分類**: 使用有意義的 metadata 分類
3. **增量更新**: 定期添加新知識而不是重建
4. **質量控制**: 確保知識的準確性和相關性
5. **性能監控**: 定期檢查向量庫狀態和性能

---

**🎉 現在您的系統擁有了強大的持久化知識管理能力！**
