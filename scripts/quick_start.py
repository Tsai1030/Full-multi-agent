"""
RAG 蝟餌絞敹恍?憪內靘?
雿輻 BGE-M3 + GPT-4o ?換敺格???RAG 蝟餌絞
"""

import os
from dotenv import load_dotenv

# 頛?啣?霈
load_dotenv()

def main():
    """敹恍?憪內靘?""
    print("?? 蝝怠凝? RAG 蝟餌絞敹恍?憪?)
    print("雿輻 BGE-M3 撋璅∪? + GPT-4o 頛詨璅∪?")
    print("=" * 60)
    
    try:
        # 1. 撠 RAG 蝟餌絞
        from backend.src.rag import create_rag_system
        
        print("? 甇?????RAG 蝟餌絞...")
        
        # 2. ?萄遣 RAG 蝟餌絞
        rag_system = create_rag_system()
        
        # 3. 瑼Ｘ蝟餌絞???
        status = rag_system.get_system_status()
        print(f"??蝟餌絞??? {status['system']}")
        print(f"?? ??摮: {status['components']['vector_store']}")
        print(f"?? ???? {status['components']['generator']}")
        
        # 4. 瘛餃?蝷箔??亥?
        print("\n?? 瘛餃?蝝怠凝??亥?...")
        
        sample_knowledge = [
            {
                "content": """蝝怠凝?蝝怠凝?銝剔?撣???雿??銝??葉憭柴?
                蝝怠凝???賜?鈭箏?誑銝鞈迎?
                1. 憭拍???撠??甈???
                2. ?迭??典?嚗?蝯勗鴃?
                3. 鞎砌遙?撥嚗?雿踹??
                4. 摰寞?敺隞犖????靽∩遙
                5. ?拙?敺?蝞∠???撠??祈撌乩?
                6. ?扳頛蝛拚?嚗?頛??寡?瘙箏?""",
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
                3. ?迭摮貊??啁霅?瘙?曉撥
                4. ?拇??賢?撘瘀??賣?撠???
                5. ??唳雁?????
                6. 摰寞?敹?摰??單?憭?
                7. ?拙?敺??銵?蝛嗆?憿批?撌乩?""",
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
                3. ?瑟?甇?儔??鞎砌遙敹?
                4. ?迭??曆犖?阡?
                5. ?拙??祈???扯?璆?
                6. 摰寞????漲嚗?瘜冽?隡
                7. ?瑕頛戊?賣?箸???"",
                "metadata": {
                    "category": "銝餅?閫??",
                    "star": "憭芷??, 
                    "palace": "?賢悅"
                }
            }
        ]
        
        success = rag_system.add_knowledge(sample_knowledge)
        if success:
            print(f"????瘛餃? {len(sample_knowledge)} 璇霅?)
        else:
            print("??瘛餃??亥?憭望?")
            return
        
        # 5. 皜祈岫?亥??揣
        print("\n?? 皜祈岫?亥??揣...")
        
        search_queries = [
            "蝝怠凝???寡釭",
            "?箸??",
            "???賢?"
        ]
        
        for query in search_queries:
            print(f"\n?亥岷: {query}")
            results = rag_system.search_knowledge(query, top_k=2, min_score=0.5)
            
            for i, result in enumerate(results, 1):
                print(f"  蝯? {i} (?訾撮摨? {result['score']:.3f}):")
                print(f"    {result['content'][:80]}...")
        
        # 6. 皜祈岫???
        print("\n? 皜祈岫???...")
        
        questions = [
            "蝝怠凝???賜?鈭箸?隞暻潛鞈迎?",
            "憭拇??誨銵其?暻潭???",
            "憭芷??鈭粹??暻澆極雿?"
        ]
        
        for question in questions:
            print(f"\n????: {question}")
            print("-" * 50)
            
            response = rag_system.generate_answer(
                query=question,
                context_type="auto"
            )
            
            if "error" not in response:
                print(f"?? ??: {response['answer']}")
                
                if 'retrieval_info' in response:
                    retrieval = response['retrieval_info']
                    print(f"?? 瑼Ｙ揣??{retrieval['relevant_docs']} 璇??瑼?)
                
                if 'usage' in response:
                    usage = response['usage']
                    print(f"? Token 雿輻: {usage['total_tokens']}")
            else:
                print(f"???航炊: {response['error']}")
        
        # 7. 皜祈岫蝝怠凝???
        print("\n? 皜祈岫蝝怠凝???...")
        
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
                    "secondary_stars": ["撌西?", "?喳撮"]
                },
                "鞎∪?摰?: {
                    "main_star": "憭拇???,
                    "secondary_stars": ["??", "?"]
                }
            }
        }
        
        print("???賜...")
        analysis = rag_system.analyze_ziwei_chart(
            chart_data=chart_data,
            analysis_type="comprehensive"
        )
        
        if "error" not in analysis:
            print("? ??蝯?:")
            print("-" * 50)
            print(analysis['answer'])
        else:
            print(f"?????航炊: {analysis['error']}")
        
        # 8. 憿舐內蝟餌絞蝯梯?
        print("\n?? 蝟餌絞蝯梯?靽⊥...")
        final_status = rag_system.get_system_status()
        
        if 'vector_store_stats' in final_status:
            stats = final_status['vector_store_stats']
            print(f"?? ??摨急?瑼?? {stats.get('total_documents', 'N/A')}")
        
        if 'generator_info' in final_status:
            gen_info = final_status['generator_info']
            print(f"?? ??璅∪?: {gen_info.get('model', 'N/A')}")
        
        print("\n?? 敹恍?憪內靘???")
        print("?典隞亦匱蝥溶?憭霅???嗡?????)
        
    except ImportError as e:
        print(f"??撠?航炊: {str(e)}")
        print("隢Ⅱ靽歇摰????鞈游?嚗ip install -r requirements.txt")
        
    except Exception as e:
        print(f"?????航炊: {str(e)}")
        print("隢炎?亦憓?蝵桀? API 撖閮剔蔭")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

