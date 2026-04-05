"""
瞍內 Agent ????憿舐內?
"""

import asyncio
from backend.main import ZiweiAISystem

async def demo_agent_process_display():
    """瞍內 Agent ??憿舐內??????""
    print("?? Agent ????憿舐內瞍內")
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
        
        # 瞍內1嚗??Agent ??嚗?隤芋撘?
        print("?? 瞍內1嚗??Agent ????")
        print("-" * 40)
        print("show_agent_process=False嚗?隤?")
        print("?芷＊蝷箸?蝯???銝＊蝷?Agent 皞?蝔n")
        
        result1 = await system.analyze_ziwei_chart(
            birth_data=sample_birth_data,
            domain_type="love",
            output_format="json_to_narrative",
            show_agent_process=False  # ? ?梯???
        )
        
        if result1['success']:
            print("????摰?嚗??蝔芋撘?")
            print(f"?梧?  ????: {result1['metadata']['processing_time']:.2f} 蝘?)
            print("?? 蝯??汗:", result1['result'][:100] + "...")
        
        print("\n" + "="*60)
        
        # 瞍內2嚗＊蝷?Agent ??嚗底蝝唳芋撘?
        print("?? 瞍內2嚗＊蝷?Agent ????")
        print("-" * 40)
        print("show_agent_process=True")
        print("憿舐內摰??Agent 皞?????\n")
        
        result2 = await system.analyze_ziwei_chart(
            birth_data=sample_birth_data,
            domain_type="wealth",
            output_format="json_to_narrative",
            show_agent_process=True  # ? 憿舐內??
        )
        
        if result2['success']:
            print("????摰?嚗＊蝷粹?蝔芋撘?")
            print(f"?梧?  ????: {result2['metadata']['processing_time']:.2f} 蝘?)
        
        # 瞍內3嚗?蝡?API 雿輻蝷箔?
        print("\n" + "="*60)
        print("? 敺垢 API 雿輻蝷箔?")
        print("-" * 40)
        
        print("""
?典?蝡?API 銝剔?雿輻?孵?嚗?

# ?孵?1嚗銝餌?摨葉閮剖?
result = await system.analyze_ziwei_chart(
    birth_data=birth_data,
    domain_type="love",
    output_format="json_to_narrative",
    show_agent_process=True  # ? ????憿舐內
)

# ?孵?2嚗??啣?霈?批
import os
show_process = os.getenv("SHOW_AGENT_PROCESS", "false").lower() == "true"

result = await system.analyze_ziwei_chart(
    birth_data=birth_data,
    domain_type="love", 
    output_format="json_to_narrative",
    show_agent_process=show_process
)

# ?孵?3嚗? API 隢???批
@app.post("/analyze")
async def analyze_chart(request_data):
    show_process = request_data.get("show_agent_process", False)
    
    result = await system.analyze_ziwei_chart(
        birth_data=request_data["birth_data"],
        domain_type=request_data.get("domain_type", "comprehensive"),
        output_format=request_data.get("output_format", "json"),
        show_agent_process=show_process  # ? 敺?蝡舀??
    )
    return result
        """)
        
        await system.cleanup()
        print("\n??瞍內摰?")
        
    except Exception as e:
        print(f"??瞍內憭望?: {str(e)}")
        import traceback
        traceback.print_exc()

async def demo_backend_visibility():
    """瞍內敺垢?航??扯牧??""
    print("\n?? 敺垢?航??扯牧??)
    print("=" * 60)
    
    print("""
?? Agent ??憿舐內?閬改?

?儭? 敺垢嚗??蝡荔?嚗?
   ???臭誑?摰??Agent ????
   ???臭誑??亥??矽閰虫縑??
   ???臭誑?批?臬憿舐內??
   ???拙???矽閰?

? ?垢嚗?嗥垢嚗?
   ???虜銝?? Agent ?折??
   ???芣?嗆?蝯???蝯?
   ???臭誑?? API ?隢???靽⊥嚗???蝡舀??
   ???拙??冽擃?

? 撱箄降雿輻?湔嚗?

??挾嚗?
- show_agent_process=True
- ?冽隤輯岫???Agent ??

??啣?嚗?
- show_agent_process=False嚗?隤?
- ?芾???蝯??策?冽
- ??靽⊥閮??典?蝡舀隤葉

?寞??瘙?
- ?臭誑?? API ?霈?蝡舫??行??蝔?
- ?拙??閬?摨衣?撠平?冽
    """)

if __name__ == "__main__":
    asyncio.run(demo_agent_process_display())
    asyncio.run(demo_backend_visibility())

