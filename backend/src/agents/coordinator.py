"""
Multi-Agent 協調器
負責協調多個Agent的工作，整合分析結果
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent, AgentTask, AgentResponse, AgentRole
from .claude_agent import ClaudeAgent
from .gpt_agent import GPTAgent
from .domain_agent import DomainAgent
from ..config.settings import get_settings

settings = get_settings()

class CoordinationStrategy(Enum):
    """協調策略"""
    SEQUENTIAL = "sequential"  # 順序執行
    PARALLEL = "parallel"     # 並行執行
    HIERARCHICAL = "hierarchical"  # 階層式執行
    DISCUSSION = "discussion"  # 討論式協作
    DEBATE = "debate"         # 辯論式協作

@dataclass
class AgentAssignment:
    """Agent任務分配"""
    agent: BaseAgent
    task: AgentTask
    priority: int = 1
    timeout: int = 45  # 減少單個Agent超時時間

@dataclass
class DiscussionRound:
    """討論輪次"""
    round_number: int
    topic: str
    participants: List[str]  # Agent IDs
    responses: List[AgentResponse]
    consensus_level: float = 0.0  # 共識程度 0-1

@dataclass
class DiscussionResult:
    """討論結果"""
    rounds: List[DiscussionRound]
    final_consensus: str
    key_insights: List[str]
    disagreements: List[str]

@dataclass
class CoordinationResult:
    """協調結果"""
    success: bool
    responses: List[AgentResponse]
    integrated_result: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    total_time: Optional[float] = None
    discussion_result: Optional[DiscussionResult] = None

class MultiAgentCoordinator:
    """Multi-Agent 協調器"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化Agents
        self.agents = {}
        self._initialize_agents()
        
        # 協調設定
        self.max_iterations = settings.multi_agent.coordinator_max_iterations
        self.timeout = settings.multi_agent.coordinator_timeout
        self.default_strategy = CoordinationStrategy.DISCUSSION

        # 討論設定 # 優化執行速度
        self.max_discussion_rounds = 2  # 減少討論輪次從3到2
        self.consensus_threshold = 0.6  # 降低共識閾值，更容易達成共識
        self.discussion_timeout = 90    # 減少討論超時從120到90秒
        
    def _initialize_agents(self):
        """初始化所有Agent"""
        try:
            # Claude Agent
            if settings.multi_agent.claude_agent_enabled:
                self.agents['claude'] = ClaudeAgent(logger=self.logger)
                self.logger.info("Claude Agent initialized")
            
            # GPT Agent
            if settings.multi_agent.gpt_agent_enabled:
                self.agents['gpt'] = GPTAgent(logger=self.logger)
                self.logger.info("GPT Agent initialized")
            
            # Domain Agents
            if settings.multi_agent.domain_agent_enabled:
                domain_types = ['love', 'wealth', 'future']
                for domain in domain_types:
                    agent_id = f"domain_{domain}"
                    self.agents[agent_id] = DomainAgent(
                        agent_id=agent_id,
                        domain_type=domain,
                        logger=self.logger
                    )
                    self.logger.info(f"Domain Agent ({domain}) initialized")
                    
        except Exception as e:
            self.logger.error(f"Agent initialization failed: {str(e)}")
            raise
    
    async def coordinate_analysis(self, 
                                input_data: Dict[str, Any],
                                domain_type: str = "general",
                                strategy: CoordinationStrategy = None) -> CoordinationResult:
        """協調多Agent分析"""
        
        start_time = time.time()
        strategy = strategy or self.default_strategy
        
        try:
            self.logger.info(f"Starting multi-agent coordination for {domain_type}")
            
            # 1. 準備任務
            tasks = await self._prepare_tasks(input_data, domain_type)
            
            # 2. 分配Agent
            assignments = await self._assign_agents(tasks, domain_type)
            
            # 3. 執行協調策略
            if strategy == CoordinationStrategy.SEQUENTIAL:
                responses = await self._execute_sequential(assignments)
            elif strategy == CoordinationStrategy.PARALLEL:
                responses = await self._execute_parallel(assignments)
            elif strategy == CoordinationStrategy.DISCUSSION:
                responses, discussion_result = await self._execute_discussion(assignments, input_data, domain_type)
            elif strategy == CoordinationStrategy.DEBATE:
                responses, discussion_result = await self._execute_debate(assignments, input_data, domain_type)
            else:  # HIERARCHICAL
                responses = await self._execute_hierarchical(assignments)
                discussion_result = None
            
            # 4. 整合結果
            integrated_result = await self._integrate_responses(responses, domain_type)
            
            total_time = time.time() - start_time
            
            return CoordinationResult(
                success=True,
                responses=responses,
                integrated_result=integrated_result,
                metadata={
                    "strategy": strategy.value,
                    "domain_type": domain_type,
                    "agents_used": [r.agent_id for r in responses],
                    "total_agents": len(assignments),
                    "discussion_rounds": getattr(discussion_result, 'rounds', []) if 'discussion_result' in locals() else []
                },
                total_time=total_time,
                discussion_result=discussion_result if 'discussion_result' in locals() else None
            )
            
        except Exception as e:
            self.logger.error(f"Coordination failed: {str(e)}")
            return CoordinationResult(
                success=False,
                responses=[],
                metadata={"error": str(e)},
                total_time=time.time() - start_time
            )
    
    async def _prepare_tasks(self, input_data: Dict[str, Any], domain_type: str) -> List[AgentTask]:
        """準備Agent任務"""
        
        tasks = []
        
        # Claude Agent 任務 - 邏輯分析
        if 'claude' in self.agents:
            claude_task = AgentTask(
                task_id="claude_analysis",
                task_type="ziwei_analysis",
                input_data={
                    "chart_data": input_data.get('chart_data', {}),
                    "domain_type": domain_type
                },
                context={"analysis_type": "logical_reasoning"}
            )
            tasks.append(claude_task)
        
        # GPT Agent 任務 - 創意解釋
        if 'gpt' in self.agents:
            gpt_task = AgentTask(
                task_id="gpt_interpretation",
                task_type="creative_interpretation",
                input_data={
                    "analysis_data": input_data.get('chart_data', {}),
                    "domain_type": domain_type,
                    "user_profile": input_data.get('user_profile', {})
                },
                context={"interpretation_style": "creative"}
            )
            tasks.append(gpt_task)
        
        # Domain Agent 任務 - 專業分析
        domain_agent_id = f"domain_{domain_type}"
        if domain_agent_id in self.agents:
            domain_task = AgentTask(
                task_id=f"domain_{domain_type}_analysis",
                task_type="professional_analysis",
                input_data={
                    "chart_data": input_data.get('chart_data', {}),
                    "user_concerns": input_data.get('user_concerns', []),
                    "career_stage": input_data.get('career_stage', ''),
                    "time_range": input_data.get('time_range', '未來5年')
                },
                context={"domain_type": domain_type}
            )
            tasks.append(domain_task)
        
        return tasks
    
    async def _assign_agents(self, tasks: List[AgentTask], domain_type: str) -> List[AgentAssignment]:
        """分配Agent任務"""
        
        assignments = []
        
        for task in tasks:
            # 根據任務類型選擇合適的Agent
            if task.task_type == "ziwei_analysis" and 'claude' in self.agents:
                agent = self.agents['claude']
                priority = 1  # 邏輯分析優先級最高
                
            elif task.task_type == "creative_interpretation" and 'gpt' in self.agents:
                agent = self.agents['gpt']
                priority = 2  # 創意解釋次之
                
            elif task.task_type == "professional_analysis":
                domain_agent_id = f"domain_{domain_type}"
                if domain_agent_id in self.agents:
                    agent = self.agents[domain_agent_id]
                    priority = 1  # 專業分析也是高優先級
                else:
                    continue  # 跳過沒有對應Agent的任務
            else:
                continue  # 跳過無法處理的任務
            
            assignment = AgentAssignment(
                agent=agent,
                task=task,
                priority=priority,
                timeout=self.timeout
            )
            assignments.append(assignment)
        
        # 按優先級排序
        assignments.sort(key=lambda x: x.priority)
        
        return assignments
    
    async def _execute_sequential(self, assignments: List[AgentAssignment]) -> List[AgentResponse]:
        """順序執行策略"""
        
        responses = []
        
        for assignment in assignments:
            try:
                self.logger.info(f"Executing task {assignment.task.task_id} on {assignment.agent.agent_id}")
                
                response = await asyncio.wait_for(
                    assignment.agent.process_task(assignment.task),
                    timeout=assignment.timeout
                )
                
                responses.append(response)
                
            except asyncio.TimeoutError:
                self.logger.warning(f"Task {assignment.task.task_id} timed out")
            except Exception as e:
                self.logger.error(f"Task {assignment.task.task_id} failed: {str(e)}")
        
        return responses
    
    async def _execute_parallel(self, assignments: List[AgentAssignment]) -> List[AgentResponse]:
        """並行執行策略"""
        
        # 創建並行任務
        tasks = []
        for assignment in assignments:
            task = asyncio.create_task(
                self._execute_single_assignment(assignment)
            )
            tasks.append(task)
        
        # 等待所有任務完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾成功的回應
        responses = []
        for result in results:
            if isinstance(result, AgentResponse):
                responses.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Parallel task failed: {str(result)}")
        
        return responses
    
    async def _execute_hierarchical(self, assignments: List[AgentAssignment]) -> List[AgentResponse]:
        """階層式執行策略"""
        
        responses = []
        
        # 第一層：邏輯分析 (Claude)
        logical_assignments = [a for a in assignments if a.agent.role == AgentRole.REASONING_ANALYSIS]
        if logical_assignments:
            logical_responses = await self._execute_parallel(logical_assignments)
            responses.extend(logical_responses)
        
        # 第二層：專業分析 (Domain Agent)
        domain_assignments = [a for a in assignments if a.agent.role == AgentRole.PROFESSIONAL_EXPERTISE]
        if domain_assignments:
            # 將邏輯分析結果作為上下文
            for assignment in domain_assignments:
                if logical_responses:
                    assignment.task.context['logical_analysis'] = logical_responses[0].content
            
            domain_responses = await self._execute_parallel(domain_assignments)
            responses.extend(domain_responses)
        
        # 第三層：創意解釋 (GPT)
        creative_assignments = [a for a in assignments if a.agent.role == AgentRole.CREATIVE_INTERPRETATION]
        if creative_assignments:
            # 將前面的分析結果作為上下文
            for assignment in creative_assignments:
                assignment.task.context['previous_analysis'] = [r.content for r in responses]
            
            creative_responses = await self._execute_parallel(creative_assignments)
            responses.extend(creative_responses)
        
        return responses
    
    async def _execute_single_assignment(self, assignment: AgentAssignment) -> AgentResponse:
        """執行單個Agent任務"""
        
        try:
            self.logger.info(f"Executing task {assignment.task.task_id} on {assignment.agent.agent_id}")
            
            response = await asyncio.wait_for(
                assignment.agent.process_task(assignment.task),
                timeout=assignment.timeout
            )
            
            return response
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Task {assignment.task.task_id} timed out")
            raise
        except Exception as e:
            self.logger.error(f"Task {assignment.task.task_id} failed: {str(e)}")
            raise
    
    async def _integrate_responses(self, responses: List[AgentResponse], domain_type: str) -> str:
        """整合多Agent回應"""
        
        if not responses:
            return "無法獲得分析結果"
        
        # 按Agent角色分組
        logical_analysis = []
        creative_interpretation = []
        professional_expertise = []
        
        for response in responses:
            if response.role == AgentRole.REASONING_ANALYSIS:
                logical_analysis.append(response)
            elif response.role == AgentRole.CREATIVE_INTERPRETATION:
                creative_interpretation.append(response)
            elif response.role == AgentRole.PROFESSIONAL_EXPERTISE:
                professional_expertise.append(response)
        
        # 構建整合結果
        integrated_parts = []
        
        if logical_analysis:
            integrated_parts.append("## 邏輯分析")
            for response in logical_analysis:
                integrated_parts.append(response.content)
        
        if professional_expertise:
            integrated_parts.append(f"## {domain_type}專業分析")
            for response in professional_expertise:
                integrated_parts.append(response.content)
        
        if creative_interpretation:
            integrated_parts.append("## 創意解釋")
            for response in creative_interpretation:
                integrated_parts.append(response.content)
        
        return "\n\n".join(integrated_parts)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """獲取所有Agent狀態"""
        
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = agent.get_agent_info()
        
        return status
    
    async def health_check(self) -> Dict[str, bool]:
        """檢查所有Agent健康狀態"""
        
        health_status = {}
        
        for agent_id, agent in self.agents.items():
            try:
                is_healthy = await agent.health_check()
                health_status[agent_id] = is_healthy
            except Exception as e:
                self.logger.error(f"Health check failed for {agent_id}: {str(e)}")
                health_status[agent_id] = False
        
        return health_status

    async def _execute_discussion(self, assignments: List[AgentAssignment],
                                 input_data: Dict[str, Any],
                                 domain_type: str) -> Tuple[List[AgentResponse], DiscussionResult]:
        """執行討論式協作"""

        self.logger.info("Starting discussion-based coordination")

        # 初始化討論
        discussion_rounds = []
        all_responses = []

        # 第一輪：初始分析
        self.logger.info("Discussion Round 1: Initial Analysis")
        initial_responses = await self._execute_parallel(assignments)
        all_responses.extend(initial_responses)

        round_1 = DiscussionRound(
            round_number=1,
            topic="初始分析",
            participants=[r.agent_id for r in initial_responses],
            responses=initial_responses,
            consensus_level=0.0
        )
        discussion_rounds.append(round_1)

        # 後續討論輪次
        for round_num in range(2, self.max_discussion_rounds + 1):
            self.logger.info(f"Discussion Round {round_num}: Cross-Agent Discussion")

            # 準備討論上下文
            discussion_context = self._build_discussion_context(discussion_rounds, domain_type)

            # 讓每個 Agent 對其他 Agent 的觀點進行回應
            round_responses = await self._conduct_discussion_round(
                assignments, discussion_context, round_num, domain_type
            )

            if round_responses:
                all_responses.extend(round_responses)

                # 評估共識程度
                consensus_level = await self._evaluate_consensus(round_responses)

                discussion_round = DiscussionRound(
                    round_number=round_num,
                    topic=f"交叉討論 - 輪次 {round_num}",
                    participants=[r.agent_id for r in round_responses],
                    responses=round_responses,
                    consensus_level=consensus_level
                )
                discussion_rounds.append(discussion_round)

                # 如果達到共識閾值，提前結束
                if consensus_level >= self.consensus_threshold:
                    self.logger.info(f"Consensus reached at round {round_num}")
                    break

        # 生成最終共識和洞察
        final_consensus = await self._generate_final_consensus(discussion_rounds, domain_type)
        key_insights = await self._extract_key_insights(discussion_rounds)
        disagreements = await self._identify_disagreements(discussion_rounds)

        discussion_result = DiscussionResult(
            rounds=discussion_rounds,
            final_consensus=final_consensus,
            key_insights=key_insights,
            disagreements=disagreements
        )

        return all_responses, discussion_result

    async def _execute_debate(self, assignments: List[AgentAssignment],
                             input_data: Dict[str, Any],
                             domain_type: str) -> Tuple[List[AgentResponse], DiscussionResult]:
        """執行辯論式協作"""

        self.logger.info("Starting debate-based coordination")

        # 初始化辯論
        discussion_rounds = []
        all_responses = []

        # 第一輪：立場陳述
        self.logger.info("Debate Round 1: Position Statements")
        initial_responses = await self._execute_parallel(assignments)
        all_responses.extend(initial_responses)

        round_1 = DiscussionRound(
            round_number=1,
            topic="立場陳述",
            participants=[r.agent_id for r in initial_responses],
            responses=initial_responses,
            consensus_level=0.0
        )
        discussion_rounds.append(round_1)

        # 辯論輪次：挑戰和反駁
        for round_num in range(2, self.max_discussion_rounds + 1):
            self.logger.info(f"Debate Round {round_num}: Challenge and Rebuttal")

            # 準備辯論上下文
            debate_context = self._build_debate_context(discussion_rounds, domain_type)

            # 讓 Agent 互相挑戰對方的觀點
            round_responses = await self._conduct_debate_round(
                assignments, debate_context, round_num, domain_type
            )

            if round_responses:
                all_responses.extend(round_responses)

                # 評估辯論收斂程度
                consensus_level = await self._evaluate_debate_convergence(round_responses)

                discussion_round = DiscussionRound(
                    round_number=round_num,
                    topic=f"挑戰與反駁 - 輪次 {round_num}",
                    participants=[r.agent_id for r in round_responses],
                    responses=round_responses,
                    consensus_level=consensus_level
                )
                discussion_rounds.append(discussion_round)

        # 生成辯論總結
        final_consensus = await self._generate_debate_synthesis(discussion_rounds, domain_type)
        key_insights = await self._extract_debate_insights(discussion_rounds)
        disagreements = await self._identify_persistent_disagreements(discussion_rounds)

        discussion_result = DiscussionResult(
            rounds=discussion_rounds,
            final_consensus=final_consensus,
            key_insights=key_insights,
            disagreements=disagreements
        )

        return all_responses, discussion_result

    def _build_discussion_context(self, rounds: List[DiscussionRound], domain_type: str) -> str:
        """構建討論上下文"""

        context_parts = [f"## 紫微斗數 {domain_type} 分析討論"]

        for round_info in rounds:
            context_parts.append(f"\n### 第 {round_info.round_number} 輪：{round_info.topic}")

            for response in round_info.responses:
                context_parts.append(f"\n**{response.agent_id} 的觀點：**")
                context_parts.append(response.content[:500] + "..." if len(response.content) > 500 else response.content)

        context_parts.append("\n### 討論指引")
        context_parts.append("請基於以上各方觀點，提出您的補充見解、質疑或支持論點。")
        context_parts.append("重點關注：")
        context_parts.append("1. 其他 Agent 可能遺漏的重要面向")
        context_parts.append("2. 不同觀點之間的矛盾或互補")
        context_parts.append("3. 更深層的命理洞察")

        return "\n".join(context_parts)

    def _build_debate_context(self, rounds: List[DiscussionRound], domain_type: str) -> str:
        """構建辯論上下文"""

        context_parts = [f"## 紫微斗數 {domain_type} 分析辯論"]

        for round_info in rounds:
            context_parts.append(f"\n### 第 {round_info.round_number} 輪：{round_info.topic}")

            for response in round_info.responses:
                context_parts.append(f"\n**{response.agent_id} 的立場：**")
                context_parts.append(response.content[:500] + "..." if len(response.content) > 500 else response.content)

        context_parts.append("\n### 辯論指引")
        context_parts.append("請針對其他 Agent 的觀點進行建設性的挑戰或反駁。")
        context_parts.append("重點要求：")
        context_parts.append("1. 指出其他觀點的潛在問題或不足")
        context_parts.append("2. 提供更有力的證據或論證")
        context_parts.append("3. 維護您認為正確的命理解釋")
        context_parts.append("4. 保持專業和尊重的態度")

        return "\n".join(context_parts)

    async def _conduct_discussion_round(self, assignments: List[AgentAssignment],
                                       context: str, round_num: int,
                                       domain_type: str) -> List[AgentResponse]:
        """進行討論輪次"""

        responses = []

        for assignment in assignments:
            try:
                # 創建討論任務
                discussion_task = AgentTask(
                    task_id=f"discussion_round_{round_num}_{assignment.agent.agent_id}",
                    task_type="discussion_response",
                    input_data={
                        "discussion_context": context,
                        "round_number": round_num,
                        "domain_type": domain_type
                    },
                    context={
                        "mode": "discussion",
                        "focus": "collaborative_analysis"
                    }
                )

                # 執行任務
                response = await assignment.agent.process_task(discussion_task)
                if response and response.success:
                    responses.append(response)

            except Exception as e:
                self.logger.error(f"Discussion round failed for {assignment.agent.agent_id}: {str(e)}")

        return responses

    async def _conduct_debate_round(self, assignments: List[AgentAssignment],
                                   context: str, round_num: int,
                                   domain_type: str) -> List[AgentResponse]:
        """進行辯論輪次"""

        responses = []

        for assignment in assignments:
            try:
                # 創建辯論任務
                debate_task = AgentTask(
                    task_id=f"debate_round_{round_num}_{assignment.agent.agent_id}",
                    task_type="debate_response",
                    input_data={
                        "debate_context": context,
                        "round_number": round_num,
                        "domain_type": domain_type
                    },
                    context={
                        "mode": "debate",
                        "focus": "critical_analysis"
                    }
                )

                # 執行任務
                response = await assignment.agent.process_task(debate_task)
                if response and response.success:
                    responses.append(response)

            except Exception as e:
                self.logger.error(f"Debate round failed for {assignment.agent.agent_id}: {str(e)}")

        return responses

    async def _evaluate_consensus(self, responses: List[AgentResponse]) -> float:
        """評估討論共識程度"""

        if len(responses) < 2:
            return 1.0

        # 簡化的共識評估：基於關鍵詞重疊和情感一致性
        keywords_sets = []
        sentiments = []

        for response in responses:
            # 提取關鍵詞（簡化版）
            content = response.content.lower()
            keywords = set()

            # 紫微斗數相關關鍵詞
            ziwei_terms = ['紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府', '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍']
            for term in ziwei_terms:
                if term in content:
                    keywords.add(term)

            # 評價詞彙
            positive_terms = ['好', '佳', '優', '強', '旺', '吉', '利']
            negative_terms = ['差', '弱', '凶', '煞', '忌', '沖', '破']

            sentiment_score = 0
            for term in positive_terms:
                sentiment_score += content.count(term)
            for term in negative_terms:
                sentiment_score -= content.count(term)

            keywords_sets.append(keywords)
            sentiments.append(sentiment_score)

        # 計算關鍵詞重疊度
        if keywords_sets:
            intersection = set.intersection(*keywords_sets) if len(keywords_sets) > 1 else keywords_sets[0]
            union = set.union(*keywords_sets) if len(keywords_sets) > 1 else keywords_sets[0]
            keyword_overlap = len(intersection) / len(union) if union else 0
        else:
            keyword_overlap = 0

        # 計算情感一致性
        if sentiments:
            sentiment_variance = sum((s - sum(sentiments)/len(sentiments))**2 for s in sentiments) / len(sentiments)
            sentiment_consistency = max(0, 1 - sentiment_variance / 10)  # 正規化
        else:
            sentiment_consistency = 0

        # 綜合共識分數
        consensus_score = (keyword_overlap * 0.6 + sentiment_consistency * 0.4)
        return min(1.0, max(0.0, consensus_score))

    async def _evaluate_debate_convergence(self, responses: List[AgentResponse]) -> float:
        """評估辯論收斂程度"""

        # 辯論的收斂程度通常較低，因為重點在於探索不同觀點
        base_consensus = await self._evaluate_consensus(responses)

        # 辯論中的收斂更注重論點的深度和完整性
        return base_consensus * 0.7  # 辯論天然具有較低的共識度

    async def _generate_final_consensus(self, rounds: List[DiscussionRound], domain_type: str) -> str:
        """生成最終共識"""

        consensus_parts = [f"## {domain_type} 領域討論共識"]

        # 收集所有觀點
        all_points = []
        for round_info in rounds:
            for response in round_info.responses:
                all_points.append(f"**{response.agent_id}**: {response.content[:200]}...")

        consensus_parts.append("### 各方觀點整合")
        consensus_parts.extend(all_points)

        consensus_parts.append("### 共識結論")
        consensus_parts.append("基於多輪討論，各 Agent 在以下方面達成共識：")
        consensus_parts.append("1. 命盤基本格局的判斷")
        consensus_parts.append("2. 主要星曜的影響力評估")
        consensus_parts.append("3. 整體運勢的發展趨勢")

        return "\n".join(consensus_parts)

    async def _generate_debate_synthesis(self, rounds: List[DiscussionRound], domain_type: str) -> str:
        """生成辯論綜合結論"""

        synthesis_parts = [f"## {domain_type} 領域辯論綜合"]

        synthesis_parts.append("### 辯論過程回顧")
        for round_info in rounds:
            synthesis_parts.append(f"**第 {round_info.round_number} 輪 - {round_info.topic}**")
            for response in round_info.responses:
                synthesis_parts.append(f"- {response.agent_id}: {response.content[:150]}...")

        synthesis_parts.append("### 綜合結論")
        synthesis_parts.append("經過多輪辯論，形成以下綜合性見解：")
        synthesis_parts.append("1. 不同角度的分析都有其合理性")
        synthesis_parts.append("2. 命理解釋需要考慮多重因素")
        synthesis_parts.append("3. 最終建議融合各方優點")

        return "\n".join(synthesis_parts)

    async def _extract_key_insights(self, rounds: List[DiscussionRound]) -> List[str]:
        """提取關鍵洞察"""

        insights = []

        # 從各輪討論中提取洞察
        for round_info in rounds:
            for response in round_info.responses:
                content = response.content

                # 尋找洞察性語句（簡化版）
                if any(keyword in content for keyword in ['重要的是', '關鍵在於', '值得注意', '特別是']):
                    # 提取包含這些關鍵詞的句子
                    sentences = content.split('。')
                    for sentence in sentences:
                        if any(keyword in sentence for keyword in ['重要的是', '關鍵在於', '值得注意', '特別是']):
                            insights.append(f"{response.agent_id}: {sentence.strip()}")

        return insights[:10]  # 限制數量

    async def _extract_debate_insights(self, rounds: List[DiscussionRound]) -> List[str]:
        """提取辯論洞察"""

        insights = []

        # 從辯論中提取深層洞察
        for round_info in rounds:
            for response in round_info.responses:
                content = response.content

                # 尋找辯論性和批判性語句
                if any(keyword in content for keyword in ['然而', '但是', '相反', '另一方面', '更準確的說']):
                    sentences = content.split('。')
                    for sentence in sentences:
                        if any(keyword in sentence for keyword in ['然而', '但是', '相反', '另一方面', '更準確的說']):
                            insights.append(f"{response.agent_id}: {sentence.strip()}")

        return insights[:10]

    async def _identify_disagreements(self, rounds: List[DiscussionRound]) -> List[str]:
        """識別分歧點"""

        disagreements = []

        # 簡化的分歧識別
        topics = ['財運', '事業', '感情', '健康', '性格']

        for topic in topics:
            topic_responses = []
            for round_info in rounds:
                for response in round_info.responses:
                    if topic in response.content:
                        topic_responses.append(f"{response.agent_id}: {topic}相關觀點")

            if len(topic_responses) > 1:
                disagreements.append(f"{topic}方面存在不同觀點：{', '.join(topic_responses)}")

        return disagreements[:5]

    async def _identify_persistent_disagreements(self, rounds: List[DiscussionRound]) -> List[str]:
        """識別持續性分歧"""

        # 辯論中的持續分歧更加明顯
        disagreements = await self._identify_disagreements(rounds)

        # 標記為持續性分歧
        persistent = [f"持續分歧：{disagreement}" for disagreement in disagreements]

        return persistent

    async def cleanup(self):
        """清理協調器資源"""
        try:
            # 清理所有 Agent
            for agent_id, agent in self.agents.items():
                if hasattr(agent, 'cleanup'):
                    await agent.cleanup()
                    self.logger.info(f"Agent {agent_id} 清理完成")

            self.agents.clear()
            self.logger.info("MultiAgentCoordinator 資源清理完成")

        except Exception as e:
            self.logger.error(f"MultiAgentCoordinator 清理失敗: {str(e)}")
