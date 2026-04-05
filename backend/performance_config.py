"""
性能優化配置文件
可以根據需要調整各種性能參數
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PerformanceConfig:
    """性能配置類"""
    
    # Multi-Agent 協調器設定
    max_discussion_rounds: int = 2  # 討論輪次 (原本3，優化為2)
    consensus_threshold: float = 0.6  # 共識閾值 (原本0.7，優化為0.6)
    discussion_timeout: int = 90  # 討論超時 (原本120，優化為90)
    agent_timeout: int = 45  # 單個Agent超時 (原本60，優化為45)
    
    # API 超時設定
    openai_timeout: int = 30  # OpenAI API超時 (原本60，優化為30)
    anthropic_timeout: int = 35  # Anthropic API超時 (原本60，優化為35)
    coordinator_timeout: int = 45  # 協調器超時 (原本60，優化為45)
    mcp_timeout: int = 30  # MCP工具超時 (保持30)
    
    # RAG 系統設定
    rag_top_k: int = 3  # 檢索數量 (原本5，優化為3)
    rag_min_score: float = 0.7  # 最小分數 (原本0.6，優化為0.7)
    rag_max_context_length: int = 3000  # 上下文長度 (原本4000，優化為3000)
    knowledge_query_limit: int = 8  # 查詢詞限制 (原本10，優化為8)
    
    # 快取設定
    cache_enabled: bool = True  # 啟用快取
    cache_ttl: int = 3600  # 快取存活時間（秒）
    memory_cache_enabled: bool = True  # 記憶體快取
    disk_cache_enabled: bool = True  # 磁盤快取
    
    # 並行處理設定
    enable_parallel_agents: bool = True  # 啟用Agent並行處理
    max_concurrent_agents: int = 3  # 最大並發Agent數量
    
    # 輸出格式設定
    enable_fast_format: bool = True  # 啟用快速格式化
    skip_validation: bool = False  # 跳過格式驗證（謹慎使用）

# 預設配置
DEFAULT_CONFIG = PerformanceConfig()

# 高速配置（犧牲一些質量換取速度）
FAST_CONFIG = PerformanceConfig(
    max_discussion_rounds=1,  # 只進行1輪討論
    consensus_threshold=0.5,  # 更低的共識要求
    discussion_timeout=60,    # 更短的討論時間
    agent_timeout=30,         # 更短的Agent超時
    openai_timeout=20,        # 更短的API超時
    anthropic_timeout=25,
    rag_top_k=2,             # 更少的檢索結果
    rag_min_score=0.8,       # 更高的分數要求（更精確但更少）
    knowledge_query_limit=6,  # 更少的查詢詞
    skip_validation=True      # 跳過驗證以節省時間
)

# 平衡配置（速度與質量的平衡）
BALANCED_CONFIG = PerformanceConfig(
    max_discussion_rounds=2,
    consensus_threshold=0.6,
    discussion_timeout=75,
    agent_timeout=40,
    openai_timeout=25,
    anthropic_timeout=30,
    rag_top_k=3,
    rag_min_score=0.7,
    knowledge_query_limit=7
)

# 高質量配置（優先質量，速度較慢）
QUALITY_CONFIG = PerformanceConfig(
    max_discussion_rounds=3,
    consensus_threshold=0.8,
    discussion_timeout=120,
    agent_timeout=60,
    openai_timeout=45,
    anthropic_timeout=50,
    rag_top_k=5,
    rag_min_score=0.6,
    knowledge_query_limit=10,
    skip_validation=False
)

def apply_config(config: PerformanceConfig) -> Dict[str, Any]:
    """
    應用性能配置到系統
    
    Args:
        config: 性能配置對象
        
    Returns:
        配置字典
    """
    return {
        'multi_agent': {
            'max_discussion_rounds': config.max_discussion_rounds,
            'consensus_threshold': config.consensus_threshold,
            'discussion_timeout': config.discussion_timeout,
            'agent_timeout': config.agent_timeout,
            'enable_parallel': config.enable_parallel_agents,
            'max_concurrent': config.max_concurrent_agents
        },
        'api_timeouts': {
            'openai': config.openai_timeout,
            'anthropic': config.anthropic_timeout,
            'coordinator': config.coordinator_timeout,
            'mcp': config.mcp_timeout
        },
        'rag': {
            'top_k': config.rag_top_k,
            'min_score': config.rag_min_score,
            'max_context_length': config.rag_max_context_length,
            'query_limit': config.knowledge_query_limit
        },
        'cache': {
            'enabled': config.cache_enabled,
            'ttl': config.cache_ttl,
            'memory_cache': config.memory_cache_enabled,
            'disk_cache': config.disk_cache_enabled
        },
        'output': {
            'fast_format': config.enable_fast_format,
            'skip_validation': config.skip_validation
        }
    }

def get_config_by_name(config_name: str) -> PerformanceConfig:
    """
    根據名稱獲取配置
    
    Args:
        config_name: 配置名稱 ('default', 'fast', 'balanced', 'quality')
        
    Returns:
        對應的配置對象
    """
    configs = {
        'default': DEFAULT_CONFIG,
        'fast': FAST_CONFIG,
        'balanced': BALANCED_CONFIG,
        'quality': QUALITY_CONFIG
    }
    
    return configs.get(config_name.lower(), DEFAULT_CONFIG)

def print_config_comparison():
    """打印各配置的比較"""
    configs = {
        'Default': DEFAULT_CONFIG,
        'Fast': FAST_CONFIG,
        'Balanced': BALANCED_CONFIG,
        'Quality': QUALITY_CONFIG
    }
    
    print("📊 性能配置比較")
    print("=" * 80)
    print(f"{'參數':<25} {'Default':<10} {'Fast':<10} {'Balanced':<10} {'Quality':<10}")
    print("-" * 80)
    
    attributes = [
        ('討論輪次', 'max_discussion_rounds'),
        ('共識閾值', 'consensus_threshold'),
        ('討論超時(s)', 'discussion_timeout'),
        ('Agent超時(s)', 'agent_timeout'),
        ('OpenAI超時(s)', 'openai_timeout'),
        ('RAG檢索數量', 'rag_top_k'),
        ('RAG最小分數', 'rag_min_score'),
        ('查詢詞限制', 'knowledge_query_limit')
    ]
    
    for attr_name, attr_key in attributes:
        row = f"{attr_name:<25}"
        for config_name, config in configs.items():
            value = getattr(config, attr_key)
            row += f"{value:<10}"
        print(row)
    
    print("\n💡 建議:")
    print("- Fast: 適合快速測試和演示，預計執行時間 30-60秒")
    print("- Balanced: 推薦的生產環境配置，預計執行時間 60-90秒")
    print("- Quality: 適合重要分析，預計執行時間 90-150秒")
    print("- Default: 當前優化後的配置，預計執行時間 60-90秒")

if __name__ == "__main__":
    print_config_comparison()
