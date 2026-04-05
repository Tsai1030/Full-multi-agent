"""
敺垢?澆??豢?瞍內
"""

import asyncio
from backend.main import ZiweiAISystem

async def demo_backend_choices():
    """瞍內敺垢??蝔桅??""
    print("?? 敺垢?澆??豢?瞍內")
    print("=" * 60)
    
    sample_birth_data = {
        "gender": "??,
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_hour": "??
    }
    
    try:
        system = ZiweiAISystem()
        await system.initialize()
        print("??蝟餌絞?????n")
        
        # 瞍內1嚗??????豢?
        print("?? 瞍內1嚗?????Prompt ???)
        print("-" * 40)
        
        domains = {
            "love": "??????",
            "wealth": "鞎∪?鈭平??", 
            "future": "?芯????",
            "comprehensive": "蝬??賜??"
        }
        
        for domain_key, domain_name in domains.items():
            print(f"\n? {domain_name} (domain_type='{domain_key}')")
            print("   雿輻??Prompt嚗?)
            if domain_key == "love":
                print("   - 撠移?潭???????蝝怠凝??賜??葦")
                print("   - ??憭怠氖摰柴??望????撅")
            elif domain_key == "wealth":
                print("   - 撠移?潸瓷撖?璆剖???蝝怠凝??賜??葦")
                print("   - ??鞎∪?摰柴?璆剖悅?瓷????)
            elif domain_key == "future":
                print("   - 撠移?潭靘??ａ?皜祉?蝝怠凝??賜??葦")
                print("   - ??憭折?瘚僑?犖????")
            else:
                print("   - 蝬??抒?蝝怠凝??賜??葦")
                print("   - ?券???賜?澆?")
        
        # 瞍內2嚗??撓?箸撘??豢?
        print("\n\n?? 瞍內2嚗撓?箸撘??豢?")
        print("-" * 40)
        
        formats = {
            "json": "蝝?JSON 蝯??撘?,
            "narrative": "蝝?餈唳撘?,
            "json_to_narrative": "JSON Prompt + 隢膩頛詨嚗?佗?"
        }
        
        for format_key, format_desc in formats.items():
            print(f"\n? {format_desc} (output_format='{format_key}')")
            if format_key == "json":
                print("   - 雿輻蝯???JSON prompt")
                print("   - 頛詨蝯???JSON ?豢?")
            elif format_key == "narrative":
                print("   - 雿輻隢膩??prompt")
                print("   - 頛詨?芰隤?隢膩")
            else:
                print("   - 雿輻蝯???JSON prompt嚗移蝣箏???")
                print("   - 頛詨?芰隤?隢膩嚗?霈嚗?)
                print("   - ?? ?雿喲???澆蝎曄Ⅱ?批??航???)
        
        # 瞍內3嚗祕?誨蝣潛內靘?
        print("\n\n? 瞍內3嚗?蝡臭誨蝣潮??蝵?)
        print("-" * 40)
        
        print("""
??main.py 銝剔??豢?雿蔭嚗?

result = await system.analyze_ziwei_chart(
    birth_data=sample_birth_data,
    domain_type="love",              # ? ?豢???
    output_format="json_to_narrative" # ? ?豢?頛詨?澆?
)

?舫??domain_type嚗?
- "love"         ????????
- "wealth"       ??鞎∪?鈭平??  
- "future"       ???芯????
- "comprehensive" ??蝬??賜??

?舫??output_format嚗?
- "json"              ??蝝?JSON ?澆?
- "narrative"         ??蝝?餈唳撘?
- "json_to_narrative" ??JSON Prompt + 隢膩頛詨嚗?佗?
        """)
        
        # 瞍內4嚗祕?葫閰虫???
        print("\n?? 瞍內4嚗祕?葫閰?- ???? + JSON頧?餈?)
        print("-" * 40)
        
        result = await system.analyze_ziwei_chart(
            birth_data=sample_birth_data,
            domain_type="love",  # 雿輻??????prompt
            output_format="json_to_narrative"  # JSON prompt 雿?餈啗撓??
        )
        
        if result['success']:
            print("????摰?")
            print(f"?梧?  ????: {result['metadata']['processing_time']:.2f} 蝘?)
            print("\n?? ?????蝯?嚗?餈唳撘?:")
            print("-" * 50)
            print(result['result'])
        else:
            print(f"????憭望?: {result['error']}")
        
        await system.cleanup()
        print("\n??瞍內摰?")
        
    except Exception as e:
        print(f"??瞍內憭望?: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(demo_backend_choices())

