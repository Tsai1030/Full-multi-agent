"""
查看現有向量資料庫列表
檢查所有可用的向量資料庫名稱和狀態
"""

import os
import glob
from pathlib import Path
import chromadb
from chromadb.config import Settings
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_vector_databases():
    """列出所有可用的向量資料庫"""
    
    print("🔍 掃描向量資料庫...")
    print("=" * 60)
    
    # 當前目錄
    current_dir = Path(".")
    
    # 查找所有 vector_db_ 開頭的資料夾
    db_patterns = [
        "vector_db_*",
        "data/vector_db*",
        "./vector_db*"
    ]
    
    found_databases = []
    
    for pattern in db_patterns:
        db_paths = glob.glob(pattern)
        for db_path in db_paths:
            if os.path.isdir(db_path):
                found_databases.append(db_path)
    
    # 去重並排序
    found_databases = sorted(list(set(found_databases)))
    
    if not found_databases:
        print("❌ 未找到任何向量資料庫")
        return []
    
    print(f"📊 找到 {len(found_databases)} 個向量資料庫:")
    print()
    
    database_info = []
    
    for i, db_path in enumerate(found_databases, 1):
        print(f"🗄️  資料庫 {i}: {db_path}")
        
        # 提取資料庫名稱
        if "vector_db_" in db_path:
            db_name = db_path.split("vector_db_")[-1]
        else:
            db_name = os.path.basename(db_path)
        
        try:
            # 連接到資料庫
            client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 獲取所有集合
            collections = client.list_collections()
            
            db_info = {
                "name": db_name,
                "path": db_path,
                "collections": [],
                "total_documents": 0,
                "status": "正常"
            }
            
            print(f"   📁 路徑: {db_path}")
            print(f"   🏷️  名稱: {db_name}")
            print(f"   📚 集合數: {len(collections)}")
            
            if collections:
                print("   📋 集合詳情:")
                for collection in collections:
                    try:
                        count = collection.count()
                        collection_info = {
                            "name": collection.name,
                            "document_count": count
                        }
                        db_info["collections"].append(collection_info)
                        db_info["total_documents"] += count
                        
                        print(f"      • {collection.name}: {count} 文檔")
                    except Exception as e:
                        print(f"      • {collection.name}: 無法讀取 ({str(e)})")
                        db_info["status"] = "部分錯誤"
            else:
                print("      (無集合)")
            
            print(f"   📊 總文檔數: {db_info['total_documents']}")
            print(f"   ✅ 狀態: {db_info['status']}")
            
        except Exception as e:
            print(f"   ❌ 連接失敗: {str(e)}")
            db_info = {
                "name": db_name,
                "path": db_path,
                "collections": [],
                "total_documents": 0,
                "status": f"錯誤: {str(e)}"
            }
        
        database_info.append(db_info)
        print("-" * 40)
    
    return database_info

def get_database_summary():
    """獲取資料庫摘要信息"""
    databases = list_vector_databases()
    
    if not databases:
        return None
    
    print("\n📈 資料庫摘要:")
    print("=" * 60)
    
    total_databases = len(databases)
    total_collections = sum(len(db["collections"]) for db in databases)
    total_documents = sum(db["total_documents"] for db in databases)
    healthy_databases = sum(1 for db in databases if db["status"] == "正常")
    
    print(f"🗄️  總資料庫數: {total_databases}")
    print(f"📚 總集合數: {total_collections}")
    print(f"📊 總文檔數: {total_documents}")
    print(f"✅ 健康資料庫: {healthy_databases}/{total_databases}")
    
    if healthy_databases < total_databases:
        print(f"⚠️  有問題的資料庫: {total_databases - healthy_databases}")
    
    print("\n🎯 推薦使用的資料庫:")
    for db in databases:
        if db["status"] == "正常" and db["total_documents"] > 0:
            print(f"   • {db['name']} ({db['total_documents']} 文檔)")
    
    return {
        "total_databases": total_databases,
        "total_collections": total_collections,
        "total_documents": total_documents,
        "healthy_databases": healthy_databases,
        "databases": databases
    }

def check_specific_database(db_name: str):
    """檢查特定資料庫的詳細信息"""
    
    possible_paths = [
        f"./vector_db_{db_name}",
        f"data/vector_db_{db_name}",
        f"vector_db_{db_name}",
        db_name  # 如果直接提供路徑
    ]
    
    print(f"🔍 檢查資料庫: {db_name}")
    print("=" * 60)
    
    for db_path in possible_paths:
        if os.path.exists(db_path) and os.path.isdir(db_path):
            print(f"📁 找到資料庫: {db_path}")
            
            try:
                client = chromadb.PersistentClient(
                    path=db_path,
                    settings=Settings(anonymized_telemetry=False)
                )
                
                collections = client.list_collections()
                
                print(f"📚 集合數量: {len(collections)}")
                
                for collection in collections:
                    print(f"\n📋 集合: {collection.name}")
                    try:
                        count = collection.count()
                        print(f"   📊 文檔數: {count}")
                        
                        if count > 0:
                            # 獲取樣本文檔
                            sample = collection.get(limit=3)
                            docs = sample.get('documents', [])
                            metadatas = sample.get('metadatas', [])
                            
                            print(f"   📄 樣本文檔:")
                            for i, (doc, meta) in enumerate(zip(docs, metadatas), 1):
                                print(f"      {i}. {doc[:100]}...")
                                if meta:
                                    print(f"         元數據: {meta}")
                    
                    except Exception as e:
                        print(f"   ❌ 讀取集合失敗: {str(e)}")
                
                return True
                
            except Exception as e:
                print(f"❌ 連接資料庫失敗: {str(e)}")
                return False
    
    print(f"❌ 未找到資料庫: {db_name}")
    return False

def main():
    """主函數"""
    print("🌟 向量資料庫管理工具")
    print("=" * 60)
    
    # 列出所有資料庫
    summary = get_database_summary()
    
    if summary:
        print(f"\n💡 使用建議:")
        print("   1. 選擇文檔數最多的資料庫以獲得最佳效果")
        print("   2. 確保資料庫狀態為'正常'")
        print("   3. 如需檢查特定資料庫，請使用 check_specific_database() 函數")
    else:
        print("\n💡 建議:")
        print("   1. 請先運行 create_vector_db.py 創建向量資料庫")
        print("   2. 確保 PDF 文件路徑正確")
        print("   3. 檢查 BGE-M3 模型是否正確安裝")

if __name__ == "__main__":
    main()
