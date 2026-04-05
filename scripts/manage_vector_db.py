"""
??摨怎恣?極??
?冽蝞∠?蝝怠凝??亥???摨?
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import argparse

from backend.src.rag.rag_system import ZiweiRAGSystem

# 閮剔蔭?亥?
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VectorDBManager:
    """??摨怎恣?"""
    
    def __init__(self):
        self.rag_system = None
    
    async def initialize(self):
        """????RAG 蝟餌絞"""
        try:
            self.rag_system = ZiweiRAGSystem(logger=logger)
            logger.info("RAG 蝟餌絞??????)
        except Exception as e:
            logger.error(f"RAG 蝟餌絞???仃?? {str(e)}")
            raise
    
    def show_status(self):
        """憿舐內??摨怎???""
        try:
            stats = self.rag_system.get_system_status()
            
            print("\n=== ??摨怎???===")
            print(f"蝟餌絞??? {stats.get('system', 'unknown')}")
            
            vector_stats = stats.get('vector_store', {})
            print(f"蝮賣?瑼: {vector_stats.get('total_documents', 0)}")
            print(f"???迂: {vector_stats.get('collection_name', 'unknown')}")
            print(f"????? {vector_stats.get('persist_directory', 'unknown')}")
            
            generator_stats = stats.get('generator', {})
            print(f"???函??? {generator_stats.get('status', 'unknown')}")
            print(f"雿輻璅∪?: {generator_stats.get('model', 'unknown')}")
            
        except Exception as e:
            logger.error(f"?脣???仃?? {str(e)}")
    
    def add_knowledge_from_file(self, file_path: str):
        """敺?隞嗆溶?霅?""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"?辣銝??? {file_path}")
                return False
            
            logger.info(f"敺?隞嗉??亦霅? {file_path}")
            
            if file_path.suffix == '.json':
                # JSON ?澆?
                with open(file_path, 'r', encoding='utf-8') as f:
                    knowledge_data = json.load(f)
                
                if isinstance(knowledge_data, list):
                    success = self.rag_system.add_knowledge(knowledge_data)
                    if success:
                        logger.info(f"??瘛餃? {len(knowledge_data)} 璇霅?)
                        return True
                else:
                    logger.error("JSON ?辣?澆??航炊嚗?閰脫?亥????銵?)
                    return False
            
            else:
                # ??澆?
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    knowledge_item = {
                        "content": content,
                        "metadata": {
                            "source": file_path.name,
                            "category": "?冽瘛餃?",
                            "file_type": file_path.suffix
                        }
                    }
                    
                    success = self.rag_system.add_knowledge([knowledge_item])
                    if success:
                        logger.info(f"??瘛餃??亥??辣: {file_path.name}")
                        return True
                
            return False
            
        except Exception as e:
            logger.error(f"瘛餃??亥?憭望?: {str(e)}")
            return False
    
    def add_knowledge_from_directory(self, dir_path: str):
        """敺??溶?霅?""
        try:
            dir_path = Path(dir_path)
            
            if not dir_path.exists() or not dir_path.is_dir():
                logger.error(f"?桅?銝??? {dir_path}")
                return False
            
            # ?舀??隞嗆撘?
            supported_extensions = ['.txt', '.md', '.json']
            knowledge_files = []
            
            for ext in supported_extensions:
                knowledge_files.extend(dir_path.glob(f"*{ext}"))
            
            if not knowledge_files:
                logger.warning("?芰?暹?渡??亥??辣")
                return False
            
            logger.info(f"?潛 {len(knowledge_files)} ?霅?隞?)
            
            success_count = 0
            for file_path in knowledge_files:
                if self.add_knowledge_from_file(str(file_path)):
                    success_count += 1
            
            logger.info(f"???? {success_count}/{len(knowledge_files)} ??隞?)
            return success_count > 0
            
        except Exception as e:
            logger.error(f"?寥?瘛餃??亥?憭望?: {str(e)}")
            return False
    
    def search_knowledge(self, query: str, top_k: int = 5):
        """?揣?亥?"""
        try:
            results = self.rag_system.search_knowledge(query, top_k=top_k)
            
            print(f"\n=== ?揣蝯? (?亥岷: '{query}') ===")
            
            if not results:
                print("?芣?啁?霅?)
                return
            
            for i, result in enumerate(results, 1):
                print(f"\n--- 蝯? {i} (?訾撮摨? {result.get('score', 0):.3f}) ---")
                print(f"?批捆: {result['content'][:200]}...")
                
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"??? {metadata}")
                    
        except Exception as e:
            logger.error(f"?揣憭望?: {str(e)}")
    
    def clear_database(self):
        """皜征??摨?""
        try:
            # 瘜冽?嚗?雿??芷????
            confirm = input("??  蝣箏?閬?蝛箏??澈?????芷????(頛詨 'YES' 蝣箄?): ")
            
            if confirm != 'YES':
                print("??撌脣?瘨?)
                return False
            
            # ??萄遣??摨恬???皜征?豢?嚗?
            self.rag_system = ZiweiRAGSystem(logger=logger)
            logger.info("??摨怠歇皜征")
            return True
            
        except Exception as e:
            logger.error(f"皜征??摨怠仃?? {str(e)}")
            return False
    
    def export_knowledge(self, output_file: str):
        """撠?亥?嚗????閰梧?"""
        try:
            # ?銝?陛??撠?
            # 撖阡?撖衣?航?閬?亥赤??ChromaDB
            logger.warning("撠?撠摰撖衣")
            logger.info("撱箄降?湔?遢 data/vector_db ?桅?")
            
        except Exception as e:
            logger.error(f"撠憭望?: {str(e)}")


async def main():
    """銝餃??""
    parser = argparse.ArgumentParser(description="蝝怠凝???摨怎恣?極??)
    parser.add_argument('action', choices=['status', 'add-file', 'add-dir', 'search', 'clear', 'export'],
                       help='閬銵???')
    parser.add_argument('--file', '-f', help='?辣頝臬?')
    parser.add_argument('--directory', '-d', help='?桅?頝臬?')
    parser.add_argument('--query', '-q', help='?揣?亥岷')
    parser.add_argument('--output', '-o', help='頛詨?辣頝臬?')
    parser.add_argument('--top-k', '-k', type=int, default=5, help='?揣蝯??賊?')
    
    args = parser.parse_args()
    
    # ???恣?
    manager = VectorDBManager()
    await manager.initialize()
    
    # ?瑁???
    if args.action == 'status':
        manager.show_status()
    
    elif args.action == 'add-file':
        if not args.file:
            print("?航炊: 隢?摰?隞嗉楝敺?--file")
            return
        manager.add_knowledge_from_file(args.file)
        manager.show_status()
    
    elif args.action == 'add-dir':
        if not args.directory:
            print("?航炊: 隢?摰?楝敺?--directory")
            return
        manager.add_knowledge_from_directory(args.directory)
        manager.show_status()
    
    elif args.action == 'search':
        if not args.query:
            print("?航炊: 隢?摰?蝝Ｘ閰?--query")
            return
        manager.search_knowledge(args.query, args.top_k)
    
    elif args.action == 'clear':
        manager.clear_database()
        manager.show_status()
    
    elif args.action == 'export':
        if not args.output:
            print("?航炊: 隢?摰撓?箸?隞嗉楝敺?--output")
            return
        manager.export_knowledge(args.output)


if __name__ == "__main__":
    print("?? 蝝怠凝???摨怎恣?極??)
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n??撌脣?瘨?)
    except Exception as e:
        logger.error(f"蝔??瑁?憭望?: {str(e)}")
        import traceback
        traceback.print_exc()

