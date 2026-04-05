"""
PDF ?辣撠??鞈?摨怠極??
撠??冽??蝝怠凝?PDF?辣銝血遣蝡?銋???摨?
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import argparse

# 閮剔蔭?亥?
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """敺DF?辣???"""
    try:
        # ?岫雿輻 PyPDF2
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                logger.info(f"PDF 蝮賡??? {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    text += f"\n--- 蝚?{page_num} ??---\n{page_text}\n"
                    
                    if page_num % 10 == 0:
                        logger.info(f"撌脰???{page_num} ??..")
                
                logger.info(f"PDF ???摰?嚗蜇摮: {len(text)}")
                return text
                
        except ImportError:
            logger.warning("PyPDF2 ?芸?鋆??岫雿輻 pdfplumber...")
            
            # ?岫雿輻 pdfplumber
            try:
                import pdfplumber
                
                text = ""
                with pdfplumber.open(pdf_path) as pdf:
                    logger.info(f"PDF 蝮賡??? {len(pdf.pages)}")
                    
                    for page_num, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- 蝚?{page_num} ??---\n{page_text}\n"
                        
                        if page_num % 10 == 0:
                            logger.info(f"撌脰???{page_num} ??..")
                
                logger.info(f"PDF ???摰?嚗蜇摮: {len(text)}")
                return text
                
            except ImportError:
                logger.error("隢?鋆?PDF ??摨? pip install PyPDF2 ??pip install pdfplumber")
                return None
                
    except Exception as e:
        logger.error(f"PDF ???憭望?: {str(e)}")
        return None

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """撠?????憛?""
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # 憒?銝?敺?憛??岫?典???
        if end < text_length:
            # 撠?餈??亥?
            last_period = text.rfind('??, start, end)
            if last_period > start:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < text_length else end
    
    logger.info(f"??摰?嚗 {len(chunks)} ??")
    return chunks

def create_knowledge_from_chunks(chunks: List[str], source_file: str) -> List[Dict[str, Any]]:
    """撠??砍?頧??箇霅撘?""
    knowledge_items = []
    
    for i, chunk in enumerate(chunks, 1):
        # ?岫霅?批捆憿?
        content_type = "general"
        category = "蝝怠凝?"
        
        # 蝪∪?摰孵?憿?
        if any(star in chunk for star in ['蝝怠凝??, '憭拇???, '憭芷??, '甇行??, '憭拙???, '撱???]):
            content_type = "銝餅?閫??"
        elif any(palace in chunk for palace in ['?賢悅', '憭怠氖摰?, '鞎∪?摰?, '鈭平摰?]):
            content_type = "摰桐?閫??"
        elif any(concept in chunk for concept in ['?澆?', '蝯?', '?']):
            content_type = "?澆???"
        elif any(fortune in chunk for fortune in ['?', '瘚僑', '憭折?']):
            content_type = "???"
        
        knowledge_item = {
            "content": chunk,
            "metadata": {
                "source": source_file,
                "chunk_id": i,
                "category": category,
                "content_type": content_type,
                "total_chunks": len(chunks)
            }
        }
        
        knowledge_items.append(knowledge_item)
    
    return knowledge_items

async def import_pdf_to_vector_db(pdf_path: str, chunk_size: int = 1000, overlap: int = 200):
    """撠DF?辣撠??鞈?摨?""
    
    print(f"?? PDF 撠??鞈?摨怠極??)
    print(f"?? PDF ?辣: {pdf_path}")
    print("=" * 60)
    
    # 瑼Ｘ?辣?臬摮
    if not Path(pdf_path).exists():
        logger.error(f"PDF ?辣銝??? {pdf_path}")
        return False
    
    try:
        # 1. ??PDF?
        print("?? 甇仿? 1: ??PDF?...")
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            logger.error("PDF ???憭望?")
            return False
        
        print(f"???????嚗蜇摮: {len(text)}")
        
        # 2. ??
        print(f"??  甇仿? 2: ?? (憛之撠? {chunk_size}, ??: {overlap})...")
        chunks = split_text_into_chunks(text, chunk_size, overlap)
        
        if not chunks:
            logger.error("??憭望?")
            return False
        
        print(f"??????嚗 {len(chunks)} ??")
        
        # 3. ?萄遣?亥??澆?
        print("?? 甇仿? 3: 頧??箇霅撘?..")
        source_filename = Path(pdf_path).name
        knowledge_items = create_knowledge_from_chunks(chunks, source_filename)
        
        print(f"???亥??澆?頧???嚗 {len(knowledge_items)} 璇霅?)
        
        # 4. 靽??撇SON?辣嚗?賂?
        output_json = f"data/knowledge/{Path(pdf_path).stem}_knowledge.json"
        os.makedirs("data/knowledge", exist_ok=True)
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(knowledge_items, f, ensure_ascii=False, indent=2)
        
        print(f"???亥??辣撌脖?摮? {output_json}")
        
        # 5. 撠??鞈?摨?
        print("??儭? 甇仿? 4: 撠??鞈?摨?..")
        
        from backend.src.rag.rag_system import ZiweiRAGSystem
        
        # ?萄遣RAG蝟餌絞
        rag_system = ZiweiRAGSystem(logger=logger)
        
        # 瑼Ｘ??摨怎???
        stats = rag_system.get_system_status()
        vector_stats = stats.get('vector_store', {})
        initial_docs = vector_stats.get('total_documents', 0)
        
        print(f"?? ??摨怠?憪??? {initial_docs} 璇?瑼?)
        
        # 瘛餃??亥??啣??澈
        success = rag_system.add_knowledge(knowledge_items)
        
        if success:
            # 瑼Ｘ?湔敺????
            updated_stats = rag_system.get_system_status()
            updated_vector_stats = updated_stats.get('vector_store', {})
            final_docs = updated_vector_stats.get('total_documents', 0)
            
            added_docs = final_docs - initial_docs
            
            print(f"????摨怠??交???")
            print(f"   ?啣???: {added_docs}")
            print(f"   蝮賣?瑼: {final_docs}")
            print(f"   ??摨怨楝敺? {updated_vector_stats.get('persist_directory', 'unknown')}")
            
            # 皜祈岫?揣
            print("\n?? 皜祈岫?揣?...")
            test_query = "蝝怠凝??
            search_results = rag_system.search_knowledge(test_query, top_k=3)
            
            print(f"?揣 '{test_query}' ?曉 {len(search_results)} 璇???")
            for i, result in enumerate(search_results[:2], 1):
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"  {i}. {content_preview}")
            
            return True
        else:
            logger.error("??摨怠??亙仃??)
            return False
            
    except Exception as e:
        logger.error(f"PDF 撠??憭望?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """銝餃??""
    parser = argparse.ArgumentParser(description="PDF ?辣撠??鞈?摨怠極??)
    parser.add_argument('pdf_path', help='PDF ?辣頝臬?')
    parser.add_argument('--chunk-size', type=int, default=1000, help='?憛之撠?(暺?: 1000)')
    parser.add_argument('--overlap', type=int, default=200, help='?憛??之撠?(暺?: 200)')
    
    args = parser.parse_args()
    
    # ?瑁?撠
    success = await import_pdf_to_vector_db(
        pdf_path=args.pdf_path,
        chunk_size=args.chunk_size,
        overlap=args.overlap
    )
    
    if success:
        print("\n?? PDF 撠摰?嚗?)
        print("\n?? 銝?甇?")
        print("  1. ?? python main.py 雿輻摰蝟餌絞")
        print("  2. ?? python manage_vector_db.py status ?亦???摨怎???)
        print("  3. ?? python manage_vector_db.py search --query '?閰? 皜祈岫?揣")
    else:
        print("\n??PDF 撠憭望?嚗?瑼Ｘ?航炊靽⊥")

if __name__ == "__main__":
    print("?? 蝝怠凝?PDF撠撌亙")
    print("隢Ⅱ靽歇摰?PDF??摨?")
    print("  pip install PyPDF2")
    print("  ??)
    print("  pip install pdfplumber")
    print()
    
    asyncio.run(main())

