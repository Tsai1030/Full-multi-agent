"""
蝪∪?????澈撱箇?蝔?
雿輻 BGE-M3 ??蝝怠凝?PDF?辣嚗遣蝡?銋???摨?
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import chromadb
from chromadb.config import Settings

# 閮剔蔭?亥?
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_pdf_content(pdf_path: str) -> str:
    """??PDF?批捆"""
    logger.info(f"????PDF?批捆: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            logger.info(f"PDF蝮賡??? {total_pages}")
            
            full_text = ""
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                full_text += text + "\n"
                
                if (page_num + 1) % 50 == 0:
                    logger.info(f"撌脰???{page_num + 1}/{total_pages} ??)
            
            logger.info(f"PDF?批捆??摰?嚗蜇摮: {len(full_text)}")
            return full_text
            
    except Exception as e:
        logger.error(f"PDF??憭望?: {str(e)}")
        raise

def analyze_content_structure(text: str) -> Dict[str, Any]:
    """???批捆蝯?"""
    logger.info("??PDF?批捆蝯?...")
    
    # 瑼Ｘ撣貉??換敺格??賊??菔?
    keywords = {
        '銝餅?': ['蝝怠凝??, '憭拇???, '憭芷??, '甇行??, '憭拙???, '撱???, '憭拙???, '憭芷??, '鞎芰??, '撌券???, '憭拍??, '憭拇???, '銝捏??, '?渲???],
        '摰桐?': ['?賢悅', '??摰?, '憭怠氖摰?, '摮戊摰?, '鞎∪?摰?, '?曉?摰?, '?瑞宏摰?, '憟游?摰?, '摰正摰?, '?啣?摰?, '蝳噸摰?, '?嗆?摰?],
        '頛?': ['撌西?', '?喳撮', '憭拚?', '憭拚?', '??', '?', '蟡踹?', '憭拚收'],
        '??': ['??', '?蝢?, '?急?', '?湔?', '?啁征', '?啣'],
        '?澆?': ['?澆?', '銝?', '撠悅', '?', '?悅'],
        '?': ['憭折?', '瘚僑', '撠?', '?', '瘚?', '瘚']
    }
    
    analysis = {
        'total_length': len(text),
        'keyword_counts': {},
        'estimated_sections': 0
    }
    
    # 蝯梯??閰?暹活??
    for category, words in keywords.items():
        count = sum(text.count(word) for word in words)
        analysis['keyword_counts'][category] = count
        logger.info(f"{category}?賊??批捆: {count} 甈⊥???)
    
    # 隡啁?蝡??賊?嚗?澆虜閬??泵嚗?
    section_markers = text.count('蝚?) + text.count('蝡?) + text.count('蝭')
    analysis['estimated_sections'] = section_markers
    
    logger.info(f"隡啗?蝡??賊?: {section_markers}")
    
    return analysis

def smart_text_chunking(text: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """?箄???"""
    logger.info("???箄???...")
    
    # ?寞??批捆??瘙箏???蝑
    total_length = analysis['total_length']
    
    if total_length < 50000:  # ?剜?瑼?
        chunk_size = 800
        overlap = 100
    elif total_length < 200000:  # 銝剔???
        chunk_size = 1200
        overlap = 200
    else:  # ?瑟?瑼?
        chunk_size = 1500
        overlap = 300
    
    logger.info(f"?豢???蝑: 憛之撠?{chunk_size}, ??={overlap}")
    
    chunks = []
    start = 0
    chunk_id = 1
    
    while start < len(text):
        end = start + chunk_size
        
        # 撠????脤?
        if end < len(text):
            # ?芸??典???
            last_period = text.rfind('??, start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
            else:
                # ?嗆活?券?????
                last_comma = text.rfind('嚗?, start, end)
                if last_comma > start + chunk_size // 2:
                    end = last_comma + 1
        
        chunk_text = text[start:end].strip()
        
        if len(chunk_text) > 50:  # ?芯????儔??
            # 蝪∪?摰孵?憿?
            content_type = classify_content(chunk_text)
            
            chunk_data = {
                'content': chunk_text,
                'metadata': {
                    'chunk_id': chunk_id,
                    'start_pos': start,
                    'end_pos': end,
                    'content_type': content_type,
                    'source': '蝝怠凝????其髡.pdf'
                }
            }
            chunks.append(chunk_data)
            chunk_id += 1
        
        start = end - overlap if end < len(text) else end
        
        if chunk_id % 100 == 0:
            logger.info(f"撌脰???{chunk_id} ???砍?...")
    
    logger.info(f"???摰?嚗 {len(chunks)} ??")
    return chunks

def classify_content(text: str) -> str:
    """蝪∪?摰孵?憿?""
    text_lower = text.lower()
    
    # 銝餅??賊?
    main_stars = ['蝝怠凝??, '憭拇???, '憭芷??, '甇行??, '憭拙???, '撱???, '憭拙???, '憭芷??, '鞎芰??, '撌券???, '憭拍??, '憭拇???, '銝捏??, '?渲???]
    if any(star in text for star in main_stars):
        return '銝餅?閫??'
    
    # 摰桐??賊?
    palaces = ['?賢悅', '??摰?, '憭怠氖摰?, '摮戊摰?, '鞎∪?摰?, '?曉?摰?, '?瑞宏摰?, '憟游?摰?, '摰正摰?, '?啣?摰?, '蝳噸摰?, '?嗆?摰?]
    if any(palace in text for palace in palaces):
        return '摰桐?閫??'
    
    # ?澆??賊?
    if any(word in text for word in ['?澆?', '銝?', '撠悅', '?']):
        return '?澆???'
    
    # ??賊?
    if any(word in text for word in ['憭折?', '瘚僑', '?', '瘚?']):
        return '???'
    
    # ?箇???
    if any(word in text for word in ['?箇?', '??', '璁艙', '??']):
        return '?箇???'
    
    return '銝?砍摰?

def create_vector_database(chunks: List[Dict[str, Any]], db_name: str = "test1"):
    """撱箇???鞈?摨?""
    logger.info(f"??撱箇???鞈?摨? {db_name}")
    
    try:
        # 閮剔蔭 BGE-M3 撋
        from backend.src.rag.bge_embeddings import BGEM3Embeddings
        
        # ?萄遣撋璅∪?
        embeddings = BGEM3Embeddings(
            model_name="BAAI/bge-m3",
            device="cpu",
            max_length=1024,
            batch_size=8,
            use_fp16=False
        )
        
        logger.info("BGE-M3 撋璅∪?頛??")
        
        # ?萄遣 ChromaDB 摰Ｘ蝡?
        persist_directory = f"./vector_db_{db_name}"
        client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # ?萄遣?????
        collection_name = f"ziwei_knowledge_{db_name}"
        try:
            collection = client.get_collection(collection_name)
            logger.info(f"雿輻?暹???: {collection_name}")
        except:
            collection = client.create_collection(collection_name)
            logger.info(f"?萄遣?圈??? {collection_name}")
        
        # ?寞活????
        batch_size = 50
        total_chunks = len(chunks)
        
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            # 皞??寞活?豢?
            texts = [chunk['content'] for chunk in batch_chunks]
            metadatas = [chunk['metadata'] for chunk in batch_chunks]
            ids = [f"chunk_{chunk['metadata']['chunk_id']}" for chunk in batch_chunks]
            
            # ??撋
            logger.info(f"???寞活 {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}")
            embeddings_vectors = embeddings.embed_documents(texts)
            
            # 瘛餃??啣??澈
            collection.add(
                embeddings=embeddings_vectors,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"撌脫溶??{len(batch_chunks)} ??瑼??摨?)
        
        # 瑼Ｘ?蝯???
        final_count = collection.count()
        logger.info(f"??鞈?摨怠遣蝡???")
        logger.info(f"鞈?摨怠?蝔? {db_name}")
        logger.info(f"摮頝臬?: {persist_directory}")
        logger.info(f"???迂: {collection_name}")
        logger.info(f"蝮賣?瑼: {final_count}")
        
        # 皜祈岫?揣
        logger.info("皜祈岫?揣?...")
        test_query = "蝝怠凝???寡釭"
        query_embedding = embeddings.embed_query(test_query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        logger.info(f"?揣皜祈岫??嚗??{len(results['documents'][0])} 璇????)
        
        return True
        
    except Exception as e:
        logger.error(f"??鞈?摨怠遣蝡仃?? {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """銝餃??""
    pdf_path = r"C:\Users\user\Desktop\test2\蝝怠凝????其髡.pdf"
    db_name = "test1"
    
    print("?? 蝝怠凝???鞈?摨怠遣蝡?撘?)
    print(f"?? PDF?辣: {pdf_path}")
    print(f"??儭?鞈?摨怠?蝔? {db_name}")
    print("=" * 60)
    
    try:
        # 瑼Ｘ?辣?臬摮
        if not Path(pdf_path).exists():
            logger.error(f"PDF?辣銝??? {pdf_path}")
            return
        
        # 1. ??PDF?批捆
        text = extract_pdf_content(pdf_path)
        
        # 2. ???批捆蝯?
        analysis = analyze_content_structure(text)
        
        # 3. ?箄??
        chunks = smart_text_chunking(text, analysis)
        
        # 4. 撱箇???鞈?摨?
        success = create_vector_database(chunks, db_name)
        
        if success:
            print("\n?? ??鞈?摨怠遣蝡???")
            print(f"?? 雿蔭: ./vector_db_{db_name}")
            print(f"?? ???? {len(chunks)}")
            print("\n???臭誑??雿輻??鞈?摨恍脰??揣鈭?")
        else:
            print("\n????鞈?摨怠遣蝡仃??)
            
    except Exception as e:
        logger.error(f"蝔??瑁?憭望?: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

