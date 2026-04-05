"""
瑼Ｘ test1 ??鞈?摨怎?撖阡????
"""

import chromadb
from chromadb.config import Settings

def check_test1_database():
    """瑼Ｘ test1 鞈?摨怎???""
    try:
        # ????test1 鞈?摨?
        client = chromadb.PersistentClient(
            path='./vector_db_test1',
            settings=Settings(anonymized_telemetry=False)
        )

        # ??????
        collections = client.list_collections()
        print(f'鞈?摨思葉???? {[c.name for c in collections]}')

        # 瑼Ｘ ziwei_knowledge_test1 ??
        try:
            collection = client.get_collection('ziwei_knowledge_test1')
            count = collection.count()
            print(f'ziwei_knowledge_test1 ?????? {count}')
            
            if count > 0:
                # ?脣?銝鈭見??
                results = collection.get(limit=3)
                docs = results.get('documents', [])
                print(f'璅????? {len(docs)}')
                for i, doc in enumerate(docs[:2]):
                    print(f'?? {i+1}: {doc[:100]}...')
            else:
                print('???箇征')
                
        except Exception as e:
            print(f'?脣???憭望?: {e}')
            
    except Exception as e:
        print(f'??鞈?摨怠仃?? {e}')

if __name__ == "__main__":
    check_test1_database()

