# create_vector_db.py 逐行解析文檔

## 檔案概述
這是向量資料庫建立程式，專門用於處理紫微斗數PDF文件並建立持久化向量庫。該檔案實現了完整的PDF處理流程，包括內容提取、智能分塊、內容分類和向量化存儲。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-16行)

```python
"""
簡單的向量資料庫建立程式
使用 BGE-M3 處理紫微斗數PDF文件，建立持久化向量庫
"""
```
**用意**: 檔案說明文檔，明確這是專門處理紫微斗數PDF的向量庫建立工具

```python
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import chromadb
from chromadb.config import Settings
```
**用意**: 導入必要的模組
- `os`, `pathlib`: 文件系統操作
- `logging`: 日誌記錄
- `typing`: 類型提示
- `PyPDF2`: PDF文件處理
- `chromadb`: 向量資料庫

```python
# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
```
**用意**: 
- 配置INFO級別的日誌
- 設置時間戳格式
- 創建模組專用日誌記錄器

### PDF內容提取方法 (第18-42行)

```python
def extract_pdf_content(pdf_path: str) -> str:
    """提取PDF內容"""
    logger.info(f"開始提取PDF內容: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            logger.info(f"PDF總頁數: {total_pages}")
```
**用意**: 
- 定義PDF內容提取函數
- 使用PyPDF2讀取PDF文件
- 記錄總頁數用於進度追蹤

```python
            full_text = ""
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                full_text += text + "\n"
                
                if (page_num + 1) % 50 == 0:
                    logger.info(f"已處理 {page_num + 1}/{total_pages} 頁")
```
**用意**: 
- 逐頁提取文本內容
- 每頁之間添加換行符
- 每50頁記錄一次進度
- 累積所有頁面的文本

```python
            logger.info(f"PDF內容提取完成，總字數: {len(full_text)}")
            return full_text
            
    except Exception as e:
        logger.error(f"PDF提取失敗: {str(e)}")
        raise
```
**用意**: 
- 記錄提取完成和總字數
- 完整的異常處理
- 重新拋出異常供上層處理

### 內容結構分析方法 (第44-76行)

```python
def analyze_content_structure(text: str) -> Dict[str, Any]:
    """分析內容結構"""
    logger.info("分析PDF內容結構...")
    
    # 檢查常見的紫微斗數關鍵詞
    keywords = {
        '主星': ['紫微星', '天機星', '太陽星', '武曲星', '天同星', '廉貞星', '天府星', '太陰星', '貪狼星', '巨門星', '天相星', '天梁星', '七殺星', '破軍星'],
        '宮位': ['命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮', '遷移宮', '奴僕宮', '官祿宮', '田宅宮', '福德宮', '父母宮'],
        '輔星': ['左輔', '右弼', '天魁', '天鉞', '文昌', '文曲', '祿存', '天馬'],
        '煞星': ['擎羊', '陀羅', '火星', '鈴星', '地空', '地劫'],
        '格局': ['格局', '三合', '對宮', '會照', '同宮'],
        '運勢': ['大限', '流年', '小限', '運勢', '流月', '流日']
    }
```
**用意**: 
- 定義紫微斗數的核心關鍵詞分類
- 涵蓋十四主星、十二宮位、輔星煞星
- 包含格局和運勢相關術語
- 用於內容分析和分類

```python
    analysis = {
        'total_length': len(text),
        'keyword_counts': {},
        'estimated_sections': 0
    }
    
    # 統計關鍵詞出現次數
    for category, words in keywords.items():
        count = sum(text.count(word) for word in words)
        analysis['keyword_counts'][category] = count
        logger.info(f"{category}相關內容: {count} 次提及")
```
**用意**: 
- 創建分析結果結構
- 統計每個類別的關鍵詞出現次數
- 記錄各類別的內容豐富度
- 為後續分塊策略提供依據

```python
    # 估算章節數量（基於常見分隔符）
    section_markers = text.count('第') + text.count('章') + text.count('節')
    analysis['estimated_sections'] = section_markers
    
    logger.info(f"估計章節數量: {section_markers}")
    
    return analysis
```
**用意**: 
- 通過常見分隔符估算文檔結構
- 幫助理解文檔的組織方式
- 為智能分塊提供結構信息

### 智能文本分塊方法 (第78-141行)

```python
def smart_text_chunking(text: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """智能文本分塊"""
    logger.info("開始智能文本分塊...")
    
    # 根據內容分析決定分塊策略
    total_length = analysis['total_length']
    
    if total_length < 50000:  # 短文檔
        chunk_size = 800
        overlap = 100
    elif total_length < 200000:  # 中等文檔
        chunk_size = 1200
        overlap = 200
    else:  # 長文檔
        chunk_size = 1500
        overlap = 300
```
**用意**: 
- 根據文檔長度動態調整分塊策略
- 短文檔使用較小的塊避免過度分割
- 長文檔使用較大的塊提高效率
- 設置適當的重疊避免信息丟失

```python
    logger.info(f"選擇分塊策略: 塊大小={chunk_size}, 重疊={overlap}")
    
    chunks = []
    start = 0
    chunk_id = 1
    
    while start < len(text):
        end = start + chunk_size
        
        # 尋找合適的分割點
        if end < len(text):
            # 優先在句號處分割
            last_period = text.rfind('。', start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
            else:
                # 其次在逗號處分割
                last_comma = text.rfind('，', start, end)
                if last_comma > start + chunk_size // 2:
                    end = last_comma + 1
```
**用意**: 
- 智能尋找語義完整的分割點
- 優先在句號處分割保持語義完整
- 次選逗號處分割
- 避免在詞語中間分割

```python
        chunk_text = text[start:end].strip()
        
        if len(chunk_text) > 50:  # 只保留有意義的塊
            # 簡單的內容分類
            content_type = classify_content(chunk_text)
            
            chunk_data = {
                'content': chunk_text,
                'metadata': {
                    'chunk_id': chunk_id,
                    'start_pos': start,
                    'end_pos': end,
                    'content_type': content_type,
                    'source': '紫微斗数集成全书.pdf'
                }
            }
            chunks.append(chunk_data)
            chunk_id += 1
```
**用意**: 
- 過濾過短的無意義文本塊
- 對每個塊進行內容分類
- 創建包含內容和元數據的結構
- 記錄位置信息便於追蹤

### 內容分類方法 (第143-169行)

```python
def classify_content(text: str) -> str:
    """簡單的內容分類"""
    text_lower = text.lower()
    
    # 主星相關
    main_stars = ['紫微星', '天機星', '太陽星', '武曲星', '天同星', '廉貞星', '天府星', '太陰星', '貪狼星', '巨門星', '天相星', '天梁星', '七殺星', '破軍星']
    if any(star in text for star in main_stars):
        return '主星解析'
    
    # 宮位相關
    palaces = ['命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮', '遷移宮', '奴僕宮', '官祿宮', '田宅宮', '福德宮', '父母宮']
    if any(palace in text for palace in palaces):
        return '宮位解析'
    
    # 格局相關
    if any(word in text for word in ['格局', '三合', '對宮', '會照']):
        return '格局分析'
    
    # 運勢相關
    if any(word in text for word in ['大限', '流年', '運勢', '流月']):
        return '運勢分析'
    
    # 基礎理論
    if any(word in text for word in ['基礎', '理論', '概念', '原理']):
        return '基礎理論'
    
    return '一般內容'
```
**用意**: 
- 根據關鍵詞自動分類文本內容
- 提供六種主要內容類型
- 優先級順序：主星→宮位→格局→運勢→理論→一般
- 便於後續的專業化檢索

## 程式碼架構總結

### 設計模式
1. **管道模式**: PDF提取→內容分析→智能分塊→向量化存儲
2. **策略模式**: 根據文檔大小選擇不同的分塊策略
3. **分類模式**: 基於關鍵詞的內容自動分類
4. **批次處理**: 分批處理大量文檔提高效率

### 主要特點
- **智能分塊**: 根據文檔大小和語義邊界進行分塊
- **內容分析**: 專業的紫微斗數關鍵詞分析
- **自動分類**: 基於內容的智能分類系統
- **進度追蹤**: 詳細的處理進度和統計信息

### 向量資料庫建立方法 (第171-258行)

```python
def create_vector_database(chunks: List[Dict[str, Any]], db_name: str = "test1"):
    """建立向量資料庫"""
    logger.info(f"開始建立向量資料庫: {db_name}")

    try:
        # 設置 BGE-M3 嵌入
        from src.rag.bge_embeddings import BGEM3Embeddings

        # 創建嵌入模型
        embeddings = BGEM3Embeddings(
            model_name="BAAI/bge-m3",
            device="cpu",
            max_length=1024,
            batch_size=8,
            use_fp16=False
        )

        logger.info("BGE-M3 嵌入模型載入成功")
```
**用意**:
- 定義向量資料庫建立函數
- 導入自定義的BGE-M3嵌入模型
- 配置CPU運行和較小的批次大小
- 使用1024最大長度適合中文文本

```python
        # 創建 ChromaDB 客戶端
        persist_directory = f"./vector_db_{db_name}"
        client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # 創建或獲取集合
        collection_name = f"ziwei_knowledge_{db_name}"
        try:
            collection = client.get_collection(collection_name)
            logger.info(f"使用現有集合: {collection_name}")
        except:
            collection = client.create_collection(collection_name)
            logger.info(f"創建新集合: {collection_name}")
```
**用意**:
- 創建持久化的ChromaDB客戶端
- 使用動態的資料庫名稱支援多個版本
- 嘗試載入現有集合，不存在則創建新的
- 關閉匿名遙測保護隱私

```python
        # 批次處理文檔
        batch_size = 50
        total_chunks = len(chunks)

        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i + batch_size]

            # 準備批次數據
            texts = [chunk['content'] for chunk in batch_chunks]
            metadatas = [chunk['metadata'] for chunk in batch_chunks]
            ids = [f"chunk_{chunk['metadata']['chunk_id']}" for chunk in batch_chunks]

            # 生成嵌入
            logger.info(f"處理批次 {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}")
            embeddings_vectors = embeddings.embed_documents(texts)

            # 添加到向量庫
            collection.add(
                embeddings=embeddings_vectors,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"已添加 {len(batch_chunks)} 個文檔到向量庫")
```
**用意**:
- 使用50個文檔的批次大小平衡效率和內存
- 分別提取文本、元數據和ID
- 生成唯一的文檔ID
- 批次生成嵌入向量提高效率
- 記錄詳細的處理進度

```python
        # 檢查最終狀態
        final_count = collection.count()
        logger.info(f"向量資料庫建立完成！")
        logger.info(f"資料庫名稱: {db_name}")
        logger.info(f"存儲路徑: {persist_directory}")
        logger.info(f"集合名稱: {collection_name}")
        logger.info(f"總文檔數: {final_count}")

        # 測試搜索
        logger.info("測試搜索功能...")
        test_query = "紫微星的特質"
        query_embedding = embeddings.embed_query(test_query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        logger.info(f"搜索測試成功，找到 {len(results['documents'][0])} 條相關結果")

        return True
```
**用意**:
- 驗證最終的文檔數量
- 記錄完整的資料庫信息
- 執行搜索測試確保功能正常
- 使用紫微斗數相關查詢進行測試
- 返回成功狀態

### 主程式入口 (第260-302行)

```python
def main():
    """主函數"""
    pdf_path = r"C:\Users\user\Desktop\test2\紫微斗数集成全书.pdf"
    db_name = "test1"

    print("🌟 紫微斗數向量資料庫建立程式")
    print(f"📁 PDF文件: {pdf_path}")
    print(f"🗄️ 資料庫名稱: {db_name}")
    print("=" * 60)
```
**用意**:
- 定義主程式入口函數
- 設置PDF文件路徑和資料庫名稱
- 使用表情符號增強用戶體驗
- 顯示清晰的程式信息

```python
    try:
        # 檢查文件是否存在
        if not Path(pdf_path).exists():
            logger.error(f"PDF文件不存在: {pdf_path}")
            return

        # 1. 提取PDF內容
        text = extract_pdf_content(pdf_path)

        # 2. 分析內容結構
        analysis = analyze_content_structure(text)

        # 3. 智能分塊
        chunks = smart_text_chunking(text, analysis)

        # 4. 建立向量資料庫
        success = create_vector_database(chunks, db_name)
```
**用意**:
- 檢查PDF文件是否存在
- 執行四步驟處理流程
- 每個步驟都有清晰的編號和說明
- 按順序執行確保數據流的正確性

```python
        if success:
            print("\n🎉 向量資料庫建立成功！")
            print(f"📍 位置: ./vector_db_{db_name}")
            print(f"📊 文檔數: {len(chunks)}")
            print("\n✅ 可以開始使用向量資料庫進行搜索了！")
        else:
            print("\n❌ 向量資料庫建立失敗")

    except Exception as e:
        logger.error(f"程式執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
```
**用意**:
- 根據執行結果顯示相應的成功或失敗信息
- 提供資料庫位置和統計信息
- 完整的異常處理和錯誤追蹤
- 標準的程式入口檢查

## 深度技術分析

### 智能分塊策略

#### 1. 動態分塊大小
```python
if total_length < 50000:  # 短文檔
    chunk_size = 800
elif total_length < 200000:  # 中等文檔
    chunk_size = 1200
else:  # 長文檔
    chunk_size = 1500
```
- **短文檔**: 使用較小塊避免過度分割
- **中等文檔**: 平衡塊大小和檢索精度
- **長文檔**: 使用較大塊提高處理效率

#### 2. 語義邊界分割
```python
last_period = text.rfind('。', start, end)
if last_period > start + chunk_size // 2:
    end = last_period + 1
```
- 優先在句號處分割保持語義完整
- 設置最小塊大小避免過小的片段
- 次選逗號處分割作為備選方案

#### 3. 重疊策略
- 根據塊大小設置相應的重疊長度
- 避免重要信息在分割邊界丟失
- 提高檢索的召回率

### 專業化內容處理

#### 1. 紫微斗數關鍵詞體系
- **十四主星**: 完整的主星列表
- **十二宮位**: 標準的宮位體系
- **輔星煞星**: 重要的輔助星曜
- **格局運勢**: 分析相關術語

#### 2. 內容分類系統
- 基於關鍵詞的自動分類
- 六種主要內容類型
- 優先級排序確保準確分類

### 向量化處理優化

#### 1. BGE-M3配置優化
```python
embeddings = BGEM3Embeddings(
    model_name="BAAI/bge-m3",
    device="cpu",
    max_length=1024,
    batch_size=8,
    use_fp16=False
)
```
- 使用CPU運行適合一般硬件
- 1024長度適合中文文本
- 較小批次大小避免內存問題

#### 2. 批次處理策略
- 50個文檔的批次大小
- 平衡處理效率和內存使用
- 詳細的進度追蹤

### 品質保證機制

#### 1. 多層驗證
- PDF文件存在性檢查
- 內容提取成功驗證
- 向量庫建立狀態檢查
- 搜索功能測試

#### 2. 錯誤處理
- 每個步驟的異常捕獲
- 詳細的錯誤日誌
- 完整的堆棧追蹤

## 使用場景

### 1. 知識庫建設
- 處理專業領域PDF文檔
- 建立持久化向量資料庫
- 支援語義搜索和檢索

### 2. 內容分析
- 自動分析文檔結構
- 統計關鍵詞分佈
- 評估內容豐富度

### 3. 系統初始化
- 為RAG系統提供知識基礎
- 一次性建立，多次使用
- 支援不同版本的資料庫

## 總結

create_vector_db.py實現了完整的PDF到向量資料庫的轉換流程，通過智能分塊、專業分類和高效向量化，為紫微斗數AI系統提供了高質量的知識基礎。其模組化設計、智能處理策略和完整的品質保證機制，使其成為構建專業領域RAG系統的優秀工具。
