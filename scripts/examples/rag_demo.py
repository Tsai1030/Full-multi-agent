"""
RAG 蝟餌絞瞍內?單
撅內憒?雿輻 BGE-M3 + GPT-4o ??RAG 蝟餌絞
"""

import os
import sys
import json
import logging
from pathlib import Path

# 瘛餃???寧?頝臬?
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.src.rag.rag_system import ZiweiRAGSystem, create_rag_system


def setup_logging():
    """閮剔蔭?亥?"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demo_basic_usage():
    """瞍內?箸?冽?"""
    print("=== RAG 蝟餌絞?箸?冽?瞍內 ===")
    
    # ?萄遣 RAG 蝟餌絞
    rag_system = create_rag_system()
    
    # 瑼Ｘ蝟餌絞???
    status = rag_system.get_system_status()
    print(f"蝟餌絞??? {status['system']}")
    print(f"??摮: {status['components']['vector_store']}")
    print(f"???? {status['components']['generator']}")
    
    return rag_system


def demo_add_knowledge(rag_system):
    """瞍內瘛餃??亥?"""
    print("\n=== 瘛餃??亥?瞍內 ===")
    
    # 蝷箔?蝝怠凝??亥?
    sample_knowledge = [
        {
            "content": """蝝怠凝?蝝怠凝?銝剔?撣???隞?”???賢???憡?
            蝝怠凝???賜?鈭粹虜?瑟?隞乩??寡釭嚗?
            1. 憭拍???撠???
            2. ?迭??典?
            3. ?痊隞餅??蝙?賣?
            4. 摰寞?敺隞犖????
            5. ?拙?敺?蝞∠???撠極雿?"",
            "metadata": {
                "category": "銝餅?閫??",
                "star": "蝝怠凝??,
                "palace": "?賢悅"
            }
        },
        {
            "content": """憭拇???箸銋?嚗誨銵刻???箏?霈???
            憭拇????寡釭?嚗?
            1. ?雁?嚗??翰??
            2. ??????
            3. ?迭摮貊??啁霅?
            4. ?拇??賢?撘?
            5. 摰寞?敹?摰?"",
            "metadata": {
                "category": "銝餅?閫??",
                "star": "憭拇???,
                "palace": "?賢悅"
            }
        },
        {
            "content": """憭芷?誨銵典????憟蝎曄???
            憭芷???賜?鈭箇暺?
            1. ?扳??嚗?之??
            2. 璅?拐犖嚗?憟蝎曄?
            3. ?瑟?甇?儔??
            4. ?拙??祈???平
            5. 摰寞????漲""",
            "metadata": {
                "category": "銝餅?閫??",
                "star": "憭芷??,
                "palace": "?賢悅"
            }
        }
    ]
    
    # 瘛餃??亥?
    success = rag_system.add_knowledge(sample_knowledge)
    if success:
        print(f"??瘛餃? {len(sample_knowledge)} 璇霅?)
    else:
        print("瘛餃??亥?憭望?")
    
    # 瑼Ｘ??摮蝯梯?
    stats = rag_system.vector_store.get_collection_stats()
    print(f"??摨怎絞閮? {stats}")


def demo_search_knowledge(rag_system):
    """瞍內?亥??揣"""
    print("\n=== ?亥??揣瞍內 ===")
    
    # ?揣?亥岷
    queries = [
        "蝝怠凝???寡釭",
        "???賢?",
        "?箸??",
        "憭芷?扳"
    ]
    
    for query in queries:
        print(f"\n?亥岷: {query}")
        results = rag_system.search_knowledge(query, top_k=3, min_score=0.5)
        
        for i, result in enumerate(results, 1):
            print(f"  蝯? {i} (?訾撮摨? {result['score']:.3f}):")
            print(f"    {result['content'][:100]}...")
            if result['metadata']:
                print(f"    ??? {result['metadata']}")


def demo_generate_answers(rag_system):
    """瞍內????"""
    print("\n=== ????瞍內 ===")
    
    # 皜祈岫??
    questions = [
        "蝝怠凝???賜?鈭箸?隞暻潛鞈迎?",
        "憭拇??誨銵其?暻潭???",
        "憭芷??鈭粹??暻澆極雿?",
        "憒??斗銝?犖??撠??"
    ]
    
    for question in questions:
        print(f"\n??: {question}")
        print("-" * 50)
        
        # ????
        response = rag_system.generate_answer(
            query=question,
            context_type="auto",
            temperature=0.7
        )
        
        print(f"??: {response['answer']}")
        
        if 'retrieval_info' in response:
            retrieval = response['retrieval_info']
            print(f"瑼Ｙ揣靽⊥: ?曉 {retrieval['relevant_docs']} 璇??瑼?)
        
        if 'usage' in response:
            usage = response['usage']
            print(f"Token 雿輻: {usage['total_tokens']} (頛詨: {usage['prompt_tokens']}, 頛詨: {usage['completion_tokens']})")


def demo_ziwei_analysis(rag_system):
    """瞍內蝝怠凝???"""
    print("\n=== 蝝怠凝???瞍內 ===")
    
    # 蝷箔??賜?豢?
    chart_data = {
        "main_stars": ["蝝怠凝??, "憭拇???],
        "palaces": ["?賢悅", "鞎∪?摰?, "鈭平摰?],
        "birth_info": {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14
        },
        "palace_details": {
            "?賢悅": {
                "main_star": "蝝怠凝??,
                "secondary_stars": ["撌西?", "?喳撮"],
                "four_modernizations": []
            },
            "鞎∪?摰?: {
                "main_star": "憭拇???,
                "secondary_stars": ["??", "?"],
                "four_modernizations": []
            }
        }
    }
    
    print("???賜?豢?:")
    print(json.dumps(chart_data, ensure_ascii=False, indent=2))
    
    # ????
    analysis = rag_system.analyze_ziwei_chart(
        chart_data=chart_data,
        analysis_type="comprehensive"
    )
    
    print("\n??蝯?:")
    print("-" * 50)
    print(analysis['answer'])
    
    if 'usage' in analysis:
        usage = analysis['usage']
        print(f"\nToken 雿輻: {usage['total_tokens']}")


def demo_system_configuration():
    """瞍內蝟餌絞?蔭"""
    print("\n=== 蝟餌絞?蔭瞍內 ===")
    
    # ?芸?蝢拚?蝵?
    custom_config = {
        "vector_store": {
            "persist_directory": "./data/custom_vector_db",
            "collection_name": "custom_ziwei",
            "embedding_provider": "huggingface",
            "embedding_model": "BAAI/bge-m3",
            "embedding_config": {
                "device": "cpu",
                "max_length": 4096,
                "batch_size": 16,
                "use_fp16": False,
                "openai_fallback": True
            }
        },
        "generator": {
            "model": "gpt-4o",
            "temperature": 0.8,
            "max_tokens": 1500
        },
        "rag": {
            "top_k": 3,
            "min_score": 0.8
        }
    }
    
    print("?芸?蝢拚?蝵?")
    print(json.dumps(custom_config, ensure_ascii=False, indent=2))
    
    # 雿輻?芸?蝢拚?蝵桀撱箇頂蝯?
    custom_rag = create_rag_system(custom_config)
    
    # 瑼Ｘ???
    status = custom_rag.get_system_status()
    print(f"\n?芸?蝢拍頂蝯梁??? {status['system']}")
    print(f"?蔭: {status['config']['rag']}")


def main():
    """銝餃??""
    setup_logging()
    
    print("蝝怠凝? RAG 蝟餌絞瞍內")
    print("雿輻 BGE-M3 撋璅∪? + GPT-4o 頛詨璅∪?")
    print("=" * 60)
    
    try:
        # ?箸?冽?瞍內
        rag_system = demo_basic_usage()
        
        # 瘛餃??亥?瞍內
        demo_add_knowledge(rag_system)
        
        # ?揣?亥?瞍內
        demo_search_knowledge(rag_system)
        
        # ????瞍內
        demo_generate_answers(rag_system)
        
        # 蝝怠凝???瞍內
        demo_ziwei_analysis(rag_system)
        
        # 蝟餌絞?蔭瞍內
        demo_system_configuration()
        
        print("\n瞍內摰?嚗?)
        
    except Exception as e:
        print(f"瞍內??銝剔?隤? {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

