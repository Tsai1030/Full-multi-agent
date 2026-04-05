"""
基礎Agent類別
定義所有Agent的共同介面和行為
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio

class AgentRole(Enum):
    """Agent角色類型"""
    REASONING_ANALYSIS = "reasoning_analysis"
    CREATIVE_INTERPRETATION = "creative_interpretation"
    PROFESSIONAL_EXPERTISE = "professional_expertise"
    ANALYST = "analyst"  # 分析師角色
    CREATIVE = "creative"  # 創意角色
    EXPERT = "expert"  # 專家角色

class AgentStatus(Enum):
    """Agent狀態"""
    IDLE = "idle"
    THINKING = "thinking"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentMessage:
    """Agent訊息"""
    content: str
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

@dataclass
class AgentResponse:
    """Agent回應"""
    agent_id: str
    role: AgentRole
    content: str
    confidence: float
    success: bool = True
    reasoning: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

@dataclass
class AgentTask:
    """Agent任務"""
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    priority: int = 1
    timeout: int = 60

class BaseAgent(ABC):
    """基礎Agent抽象類別"""
    
    def __init__(self, 
                 agent_id: str,
                 role: AgentRole,
                 model_name: str,
                 logger: Optional[logging.Logger] = None):
        self.agent_id = agent_id
        self.role = role
        self.model_name = model_name
        self.status = AgentStatus.IDLE
        self.logger = logger or logging.getLogger(f"{__name__}.{agent_id}")
        
        # Agent能力和特性
        self.capabilities = []
        self.specializations = []
        self.max_context_length = 4000
        self.temperature = 0.7
        
    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """處理任務 - 子類必須實現"""
        pass
    
    @abstractmethod
    async def generate_response(self, 
                              messages: List[AgentMessage], 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """生成回應 - 子類必須實現"""
        pass
    
    def set_status(self, status: AgentStatus):
        """設置Agent狀態"""
        self.status = status
        self.logger.info(f"Agent {self.agent_id} status changed to {status.value}")
    
    def add_capability(self, capability: str):
        """添加能力"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.logger.info(f"Added capability: {capability}")
    
    def add_specialization(self, specialization: str):
        """添加專業領域"""
        if specialization not in self.specializations:
            self.specializations.append(specialization)
            self.logger.info(f"Added specialization: {specialization}")
    
    def can_handle_task(self, task: AgentTask) -> bool:
        """檢查是否能處理任務"""
        # 基本檢查 - 子類可以覆寫
        return task.task_type in self.capabilities
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據"""
        try:
            # 基本驗證邏輯
            if not input_data:
                return False
            
            # 子類可以覆寫進行更詳細的驗證
            return True
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return False
    
    async def preprocess_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """預處理輸入數據"""
        # 基本預處理 - 子類可以覆寫
        return input_data
    
    async def postprocess_output(self, output: str, context: Optional[Dict[str, Any]] = None) -> str:
        """後處理輸出"""
        # 基本後處理 - 子類可以覆寫
        return output.strip()
    
    def get_system_prompt(self) -> str:
        """獲取系統提示詞"""
        base_prompt = f"""你是一個專業的AI助手，角色是{self.role.value}。

你的特點：
- Agent ID: {self.agent_id}
- 專業領域: {', '.join(self.specializations) if self.specializations else '通用'}
- 核心能力: {', '.join(self.capabilities) if self.capabilities else '基礎分析'}

請根據你的角色和專業領域提供準確、有用的回應。"""
        
        return base_prompt
    
    def get_agent_info(self) -> Dict[str, Any]:
        """獲取Agent信息"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "model_name": self.model_name,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "specializations": self.specializations,
            "max_context_length": self.max_context_length,
            "temperature": self.temperature
        }
    
    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            # 基本健康檢查
            test_message = AgentMessage(content="健康檢查測試")
            response = await self.generate_response([test_message])
            return bool(response and len(response) > 0)
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

class AgentMetrics:
    """Agent性能指標"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        self.total_processing_time = 0.0
        self.average_processing_time = 0.0
        self.last_activity = None
    
    def record_task_start(self):
        """記錄任務開始"""
        self.total_tasks += 1
        self.last_activity = asyncio.get_event_loop().time()
    
    def record_task_success(self, processing_time: float):
        """記錄任務成功"""
        self.successful_tasks += 1
        self.total_processing_time += processing_time
        self.average_processing_time = self.total_processing_time / self.successful_tasks
    
    def record_task_failure(self):
        """記錄任務失敗"""
        self.failed_tasks += 1
    
    def get_success_rate(self) -> float:
        """獲取成功率"""
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks
    
    def get_metrics(self) -> Dict[str, Any]:
        """獲取所有指標"""
        return {
            "agent_id": self.agent_id,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": self.get_success_rate(),
            "average_processing_time": self.average_processing_time,
            "last_activity": self.last_activity
        }
