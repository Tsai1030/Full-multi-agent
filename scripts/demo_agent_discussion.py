"""
Agent 閮??瞍內
撅內 Agent 銋?憒??脰???閮??劑隢?
"""

import asyncio
import logging
import json
from datetime import datetime

# 閮剔蔭?亥?
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_section(title):
    """?蝡?璅?"""
    print(f"\n{'='*60}")
    print(f"?? {title}")
    print('='*60)

def print_subsection(title):
    """?摮?蝭璅?"""
    print(f"\n{'?'*40}")
    print(f"?? {title}")
    print('?'*40)

async def demo_discussion_vs_parallel():
    """瞍內閮?璅∪? vs 銝西?璅∪??榆??""
    print_section("閮?璅∪? vs 銝西?璅∪?瘥?")
    
    try:
        from backend.src.agents.coordinator import MultiAgentCoordinator, CoordinationStrategy
        from backend.src.agents.claude_agent import ClaudeAgent
        from backend.src.agents.gpt_agent import GPTAgent
        from backend.src.agents.domain_agent import DomainAgent
        
        # ?萄遣?矽?典? Agent
        coordinator = MultiAgentCoordinator()
        
        # ???萄遣 Agent嚗芋?祆芋撘?銝祕?矽??API嚗?
        claude_agent = ClaudeAgent("claude_logic")
        gpt_agent = GPTAgent("gpt_creative")
        love_agent = DomainAgent("love_expert", "love")
        
        coordinator.agents = {
            "claude_logic": claude_agent,
            "gpt_creative": gpt_agent,
            "love_expert": love_agent
        }
        
        print("???矽?典? Agent 閮剔蔭摰?")
        
        # 皞?皜祈岫?豢?
        test_input = {
            'chart_data': {
                'success': True,
                'data': {
                    'palace': {
                        '?賢悅': ['蝝怠凝??, '憭拙???],
                        '憭怠氖摰?: ['憭芷??, '撌券???],
                        '鞎∪?摰?: ['憭拇???, '憭芷??]
                    }
                }
            },
            'knowledge_context': '蝝怠凝?誨銵券?撠??憭芷?誨銵函????憭拇??誨銵冽?扯???..',
            'birth_data': {
                "gender": "憟?,
                "birth_year": 1990,
                "birth_month": 8,
                "birth_day": 15,
                "birth_hour": "??
            }
        }
        
        strategies_to_test = [
            ("銝西?璅∪?", CoordinationStrategy.PARALLEL),
            ("閮?璅∪?", CoordinationStrategy.DISCUSSION),
            ("颲航?璅∪?", CoordinationStrategy.DEBATE)
        ]
        
        results = {}
        
        for strategy_name, strategy in strategies_to_test:
            print_subsection(f"皜祈岫 {strategy_name}")
            
            try:
                start_time = datetime.now()
                
                result = await coordinator.coordinate_analysis(
                    input_data=test_input,
                    domain_type="love",
                    strategy=strategy
                )
                
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                if result.success:
                    results[strategy_name] = {
                        'success': True,
                        'processing_time': processing_time,
                        'responses': len(result.responses),
                        'has_discussion': result.discussion_result is not None,
                        'discussion_rounds': len(result.discussion_result.rounds) if result.discussion_result else 0,
                        'integrated_result': result.integrated_result[:200] + "..." if result.integrated_result else "?⊥????
                    }
                    
                    print(f"??{strategy_name} ?瑁???")
                    print(f"   ?梧?  ????: {processing_time:.2f} 蝘?)
                    print(f"   ?? Agent ???? {len(result.responses)}")
                    
                    if result.discussion_result:
                        discussion = result.discussion_result
                        print(f"   ? 閮?頛芣活: {len(discussion.rounds)}")
                        print(f"   ? ?蝯霅? {discussion.final_consensus[:100]}...")
                        
                        if discussion.key_insights:
                            print(f"   ? ?瘣?: {len(discussion.key_insights)} 璇?)
                            for i, insight in enumerate(discussion.key_insights[:2], 1):
                                print(f"      {i}. {insight[:80]}...")
                        
                        if discussion.disagreements:
                            print(f"   ??  ?郁暺? {len(discussion.disagreements)} 璇?)
                    
                    print(f"   ?? ?游?蝯?: {result.integrated_result[:150]}...")
                    
                else:
                    results[strategy_name] = {'success': False}
                    print(f"??{strategy_name} ?瑁?憭望?")
                    
            except Exception as e:
                results[strategy_name] = {'success': False, 'error': str(e)}
                print(f"??{strategy_name} ?潛??航炊: {str(e)}")
        
        # 瘥?蝯?
        print_subsection("蝑瘥?蝮賜?")
        
        for strategy_name, result in results.items():
            if result.get('success'):
                print(f"\n? {strategy_name}:")
                print(f"   ????: {result.get('processing_time', 0):.2f} 蝘?)
                print(f"   Agent ??: {result.get('responses', 0)} ??)
                print(f"   閮?頛芣活: {result.get('discussion_rounds', 0)} 頛?)
                print(f"   ??隢??? {'?? if result.get('has_discussion') else '??}")
            else:
                print(f"\n? {strategy_name}: ?瑁?憭望?")
        
        return True
        
    except Exception as e:
        print(f"??瞍內憭望?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def demo_discussion_rounds():
    """瞍內閮?頛芣活?底蝝圈?蝔?""
    print_section("閮?頛芣活閰喟敦瞍內")
    
    try:
        from backend.src.agents.coordinator import MultiAgentCoordinator, DiscussionRound, DiscussionResult
        from backend.src.agents.base_agent import AgentResponse, AgentRole
        
        coordinator = MultiAgentCoordinator()
        
        print("?? 璅⊥憭憚閮???...")
        
        # 璅⊥蝚砌?頛芾?隢?
        round1_responses = [
            AgentResponse(
                agent_id="claude_logic",
                role=AgentRole.ANALYST,
                content="敺?頛臬???摨佗?蝝怠凝???賢悅銵函內甇支犖?瑟?憭拍???撠??甈????予摨?嚗耦?換摨?摰柴撅嚗誨銵函帘??鞎砌遙???拙?蝞∠??瑚?????寥嚗車鈭粹虜瘥??改??????????,
                confidence=0.85,
                success=True
            ),
            AgentResponse(
                agent_id="gpt_creative",
                role=AgentRole.CREATIVE,
                content="?函???瘥靘牧嚗換敺桀予摨?摰桀停?憭拍??EO嚗??撠????帘?亦?蝞∠?憸冽???銝哨?憟孵停?銝雿??憟喟?嚗??詨????甈??憟寡??瘞?釭?犖????閬釣??憭芷??批?賣?霈??撩撠?鈭答瞍怨敶押?,
                confidence=0.78,
                success=True
            ),
            AgentResponse(
                agent_id="love_expert",
                role=AgentRole.EXPERT,
                content="敺???璆剛?摨血???憭怠氖摰格?憭芷撌券?嚗云?賣?隞?”???望?嚗?撌券??捆??皞?憿???蝷箸??葉?航??隤斗????遣霅啣??銝剛?憭????踹??隤方圾????整?,
                confidence=0.82,
                success=True
            )
        ]
        
        round1 = DiscussionRound(
            round_number=1,
            topic="????",
            participants=["claude_logic", "gpt_creative", "love_expert"],
            responses=round1_responses,
            consensus_level=0.6
        )
        
        print_subsection("蝚砌?頛迎?????")
        for response in round1_responses:
            print(f"\n?? {response.agent_id} (靽∪?摨? {response.confidence:.2f}):")
            print(f"   {response.content}")
        
        print(f"\n?? 蝚砌?頛芸霅?摨? {round1.consensus_level:.2f}")
        
        # 璅⊥蝚砌?頛芾?隢?鈭??嚗?
        round2_responses = [
            AgentResponse(
                agent_id="claude_logic",
                role=AgentRole.ANALYST,
                content="?????摰園??潦戊?鞈芰?瘥嚗??閬????荔???撠振??云?賢楊?蝯?蝣箏祕?閬釣???摩銝???蝝怠凝???抒鞈芷??楊?????憿??航??憟孵銵券??????潛?伐?摰寞??瑕拿?啣??嫘遣霅啣飛蝧皞怠????撘?,
                confidence=0.88,
                success=True
            ),
            AgentResponse(
                agent_id="gpt_creative",
                role=AgentRole.CREATIVE,
                content="?摩撠振隤芸?敺?嚗??唾????荔?憭芷撌券????撖虫??迤?Ｘ?蝢押云?賜????臭誑?圾撌券???嚗??菜閬飛?牧閰梁????停??忽???脖?璅???冽澈?????餃?閫?炊?遣霅啣旦?冽??葉憭霈????蛛?撠?寡???鞎研?,
                confidence=0.83,
                success=True
            ),
            AgentResponse(
                agent_id="love_expert",
                role=AgentRole.EXPERT,
                content="?拐?撠振???敺移?Ｕ?閬撥隤輻??荔?蝝怠凝憭拙??犖?冽??葉敺敺???潸?擃?摰寞?撠撈靘嗉?瘙?憭??云?賢楊?????憿?撱箄降憟寡?摮豢?????嚗??捆撠??摰?????鞎∪?摰桃?憭拇?憭芷?內憟寧????航???啁?瞈?蝝蔣?踴?,
                confidence=0.86,
                success=True
            )
        ]
        
        round2 = DiscussionRound(
            round_number=2,
            topic="鈭文?閮??楛??,
            participants=["claude_logic", "gpt_creative", "love_expert"],
            responses=round2_responses,
            consensus_level=0.78
        )
        
        print_subsection("蝚砌?頛迎?鈭文?閮??楛??)
        for response in round2_responses:
            print(f"\n?? {response.agent_id} (靽∪?摨? {response.confidence:.2f}):")
            print(f"   {response.content}")
        
        print(f"\n?? 蝚砌?頛芸霅?摨? {round2.consensus_level:.2f}")
        print(f"?? ?梯???: {round2.consensus_level - round1.consensus_level:.2f}")
        
        # ???蝯?隢???
        discussion_result = DiscussionResult(
            rounds=[round1, round2],
            final_consensus="蝬??抵憚閮?嚗?撠振???梯?嚗迨?賜銝颱犖?瑟????寡釭雿??皞??閬釣??撌改?撱箄降憭皞怠??孵?銵券?嚗?雿??潘?銝行釣??瞈?蝝????蔣?踴?,
            key_insights=[
                "蝝怠凝憭拙??悅敶Ｘ?憭拍????撅",
                "憭芷撌券?蝯??閬釣????撌?,
                "?抒鞈芸?賢蔣?踵??”??,
                "蝬????航敶梢???澆?"
            ],
            disagreements=[
                "撠憭芷撌券?蝯??迤鞎敶梢蝔漲摮銝???"
            ]
        )
        
        print_subsection("閮?蝮賜?")
        print(f"? ?蝯霅? {discussion_result.final_consensus}")
        
        print(f"\n? ?瘣?:")
        for i, insight in enumerate(discussion_result.key_insights, 1):
            print(f"   {i}. {insight}")
        
        print(f"\n??  ?郁暺?")
        for i, disagreement in enumerate(discussion_result.disagreements, 1):
            print(f"   {i}. {disagreement}")
        
        return True
        
    except Exception as e:
        print(f"??閮?頛芣活瞍內憭望?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def demo_consensus_evaluation():
    """瞍內?梯?閰摯璈"""
    print_section("?梯?閰摯璈瞍內")
    
    try:
        from backend.src.agents.coordinator import MultiAgentCoordinator
        from backend.src.agents.base_agent import AgentResponse, AgentRole
        
        coordinator = MultiAgentCoordinator()
        
        print("?? 皜祈岫銝??梯?蝔漲????..")
        
        # 擃霅???
        high_consensus_responses = [
            AgentResponse(
                agent_id="agent1",
                role=AgentRole.ANALYST,
                content="蝝怠凝???踝??瑟????賢?嚗扳蝛拚?嚗瓷?蔔嚗?恣?極雿?,
                confidence=0.9,
                success=True
            ),
            AgentResponse(
                agent_id="agent2",
                role=AgentRole.CREATIVE,
                content="蝝怠凝??鈭箏予?停??撠除鞈迎?蝛拚??舫?嚗瓷???荔?敺?銝餌恣",
                confidence=0.8,
                success=True
            ),
            AgentResponse(
                agent_id="agent3",
                role=AgentRole.EXPERT,
                content="蝝怠凝?蜓撠????寡釭?＊嚗帘?扳嚗瓷?憟踝?蝞∠??瑚??雿?,
                confidence=0.85,
                success=True
            )
        ]
        
        # 銝剔??梯???
        medium_consensus_responses = [
            AgentResponse(
                agent_id="agent1",
                role=AgentRole.ANALYST,
                content="蝝怠凝???踝??瑟????賢?嚗????銝??,
                confidence=0.7,
                success=True
            ),
            AgentResponse(
                agent_id="agent2",
                role=AgentRole.CREATIVE,
                content="憭拇???霈??寡釭嚗??敹?霈?鈭平?絲隡?,
                confidence=0.6,
                success=True
            ),
            AgentResponse(
                agent_id="agent3",
                role=AgentRole.EXPERT,
                content="憭芷?????雿捆?????亙熒?閬釣??,
                confidence=0.65,
                success=True
            )
        ]
        
        # 雿霅???
        low_consensus_responses = [
            AgentResponse(
                agent_id="agent1",
                role=AgentRole.ANALYST,
                content="蝝怠凝???踝?鞎⊿?敺末嚗??鞈?鞎?,
                confidence=0.7,
                success=True
            ),
            AgentResponse(
                agent_id="agent2",
                role=AgentRole.CREATIVE,
                content="?渲????游??撥嚗??捆??瘜Ｘ?嚗?閬牲??,
                confidence=0.6,
                success=True
            ),
            AgentResponse(
                agent_id="agent3",
                role=AgentRole.EXPERT,
                content="銝捏?蜓畾箔?嚗?璆剔奎?剜????亙熒?銝蔔",
                confidence=0.5,
                success=True
            )
        ]
        
        # 閰摯?梯?蝔漲
        test_cases = [
            ("擃霅???, high_consensus_responses),
            ("銝剔??梯???", medium_consensus_responses),
            ("雿霅???, low_consensus_responses)
        ]
        
        for case_name, responses in test_cases:
            print_subsection(case_name)
            
            consensus_score = await coordinator._evaluate_consensus(responses)
            
            print(f"?? ?梯??: {consensus_score:.3f}")
            
            print(f"?? ???批捆:")
            for i, response in enumerate(responses, 1):
                print(f"   {i}. {response.agent_id}: {response.content}")
            
            # ???梯?蝔漲
            if consensus_score >= 0.7:
                print(f"??擃霅?- Agent ?銝餉?閫暺???銝??)
            elif consensus_score >= 0.4:
                print(f"??  銝剔??梯? - Agent ???典??勗?閫暺?)
            else:
                print(f"??雿霅?- Agent ??暺?甇扯?憭?)
        
        return True
        
    except Exception as e:
        print(f"???梯?閰摯瞍內憭望?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """銝餅?蝷箏??""
    print("?? Agent 閮??摰瞍內")
    print(f"瞍內??: {datetime.now()}")
    print("=" * 60)
    
    print("? ?祆?蝷箏?撅內:")
    print("   1. 閮?璅∪? vs 銝西?璅∪??榆??)
    print("   2. 憭憚閮??底蝝圈?蝔?)
    print("   3. ?梯?閰摯璈")
    print("   4. Agent 銋???雿???)
    
    demos = [
        ("閮?璅∪?瘥?", demo_discussion_vs_parallel),
        ("閮?頛芣活瞍內", demo_discussion_rounds),
        ("?梯?閰摯瞍內", demo_consensus_evaluation)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n?? ?? {demo_name}...")
            result = await demo_func()
            results.append((demo_name, result))
            
            if result:
                print(f"??{demo_name} 瞍內??")
            else:
                print(f"??{demo_name} 瞍內憭望?")
                
        except Exception as e:
            print(f"??{demo_name} 瞍內?啣虜: {str(e)}")
            results.append((demo_name, False))
    
    # 蝮賜?
    print_section("瞍內蝮賜?")
    
    successful_demos = sum(1 for _, success in results if success)
    total_demos = len(results)
    
    print(f"?? 瞍內蝯?: {successful_demos}/{total_demos} ??蝷箸???)
    
    for demo_name, success in results:
        status = "????" if success else "??憭望?"
        print(f"   {demo_name}: {status}")
    
    if successful_demos == total_demos:
        print(f"\n?? ???蝷箸???Agent 閮??摰???嚗?)
        
        print(f"\n?? ?啣??賭漁暺?")
        print(f"   ??Agent 銋??臭誑?脰??迤??隢?颲航?")
        print(f"   ??憭憚閮?璈霈???楛??)
        print(f"   ???芸?閰摯?梯?蝔漲嚗Ⅱ靽釭??)
        print(f"   ??瘥?Agent ?賣??函??隢◢??)
        print(f"   ??蝟餌絞?質??亙?甇折?銝血?瘙霅?)
        
        print(f"\n?? 撖阡???孵?")
        print(f"   ? ?游?Ｙ??賜???")
        print(f"   ? 憭?摨衣?閫暺??)
        print(f"   ? 皜??桐? Agent ??閬?)
        print(f"   ? ????蝯??靽∪漲")
        print(f"   ? ?渲?撖?瘣??遣霅?)
        
    else:
        print(f"\n??  ?典?瞍內憭望?嚗??詨??撌脣祕??)
    
    print(f"\n?? 銝?甇亙遣霅?")
    print(f"   1. 閮剔蔭 API 撖?脰?撖阡?皜祈岫")
    print(f"   2. 隤踵閮??內閰誑?脣??游末??")
    print(f"   3. ?芸??梯?閰摯蝞?")
    print(f"   4. 瘛餃??游?撠平????Agent")
    print(f"   5. ? Web ?撅內閮???")

if __name__ == "__main__":
    asyncio.run(main())

