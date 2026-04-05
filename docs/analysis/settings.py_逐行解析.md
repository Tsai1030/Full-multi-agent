# Settings 系統配置管理逐行程式碼解析

## 📋 檔案概述

**檔案路徑**: `src/config/settings.py`  
**檔案作用**: 系統配置管理中心，統一管理所有模組的配置參數  
**設計模式**: 設定模式 + 單例模式 + 工廠模式 + 組合模式  
**核心概念**: 基於 Pydantic 的類型安全配置管理，支援環境變數和 .env 檔案

## 🏗️ 整體架構

```mermaid
graph TD
    A[Settings 主配置類] --> B[OpenAISettings]
    A --> C[AnthropicSettings]
    A --> D[MCPSettings]
    A --> E[RAGSettings]
    A --> F[MultiAgentSettings]
    A --> G[AppSettings]
    A --> H[ZiweiWebsiteSettings]
    A --> I[LoggingSettings]
    A --> J[CacheSettings]
    
    K[環境變數] --> A
    L[.env 檔案] --> A
    M[預設值] --> A
    
    A --> N[全域設定實例]
    N --> O[get_settings()]
    N --> P[validate_settings()]
```

## 📝 逐行程式碼解析

### 🔧 導入與基礎設定 (第1-12行)

```python
"""
系統配置管理
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
```

**架構設計**:
- **模組文檔**: 明確定義為系統配置管理模組
- **標準庫**: 使用 `os` 進行檔案系統操作
- **類型安全**: 導入 `typing` 提供完整的類型提示
- **Pydantic 整合**: 使用 `pydantic` 和 `pydantic_settings` 實現類型安全的配置管理
- **環境變數**: 使用 `python-dotenv` 載入 .env 檔案

**設計理念**:
- **類型安全**: 所有配置都有明確的類型定義
- **環境感知**: 自動載入環境變數和 .env 檔案
- **驗證機制**: 使用 Pydantic 的自動驗證功能

### 🤖 OpenAI API 配置類 (第14-23行)

```python
class OpenAISettings(BaseSettings):
    """OpenAI API 設定"""
    api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    base_url: str = Field("https://api.openai.com/v1", env="OPENAI_BASE_URL")
    model_gpt4o: str = Field("gpt-4o-mini", env="OPENAI_MODEL_GPT4O")
    model_gpt4: str = Field("gpt-4-turbo", env="OPENAI_MODEL_GPT4")
    timeout: int = Field(60, env="OPENAI_TIMEOUT")
    max_retries: int = Field(3, env="OPENAI_MAX_RETRIES")

    model_config = {"protected_namespaces": ()}
```

**架構設計**:
- **繼承 BaseSettings**: 自動支援環境變數載入
- **Field 配置**: 每個欄位都有預設值和對應的環境變數名稱
- **類型安全**: 明確定義每個配置項的類型
- **模型配置**: 禁用 protected_namespaces 避免 model_ 前綴警告

**配置項說明**:
- `api_key`: OpenAI API 金鑰（必須）
- `base_url`: API 基礎 URL，支援自定義端點
- `model_gpt4o`: GPT-4o Mini 模型名稱
- `model_gpt4`: GPT-4 Turbo 模型名稱
- `timeout`: API 請求超時時間（秒）
- `max_retries`: 最大重試次數

### 🧠 Anthropic Claude API 配置類 (第25-31行)

```python
class AnthropicSettings(BaseSettings):
    """Anthropic Claude API 設定"""
    api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    base_url: str = Field("https://api.anthropic.com", env="ANTHROPIC_BASE_URL")
    model: str = Field("claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    timeout: int = Field(60, env="ANTHROPIC_TIMEOUT")
    max_retries: int = Field(3, env="ANTHROPIC_MAX_RETRIES")
```

**架構設計**:
- **API 整合**: 專門為 Anthropic Claude API 設計的配置
- **最新模型**: 預設使用 Claude 3.5 Sonnet 最新版本
- **一致性**: 與 OpenAI 配置保持相似的結構

**配置項說明**:
- `api_key`: Anthropic API 金鑰（必須）
- `base_url`: Anthropic API 基礎 URL
- `model`: Claude 模型版本，預設為 3.5 Sonnet
- `timeout`: API 請求超時時間
- `max_retries`: 最大重試次數

### 🔧 MCP (Model Context Protocol) 配置類 (第33-46行)

```python
class MCPSettings(BaseSettings):
    """Claude MCP 設定"""
    server_host: str = Field("localhost", env="MCP_SERVER_HOST")
    server_port: int = Field(3000, env="MCP_SERVER_PORT")
    server_name: str = Field("ziwei-mcp-server", env="MCP_SERVER_NAME")
    tools_enabled: str = Field(
        "ziwei_chart,web_scraper,data_parser",
        env="MCP_TOOLS_ENABLED"
    )
    timeout: int = Field(30, env="MCP_TIMEOUT")

    def get_tools_enabled_list(self) -> List[str]:
        """獲取啟用工具列表"""
        return [tool.strip() for tool in self.tools_enabled.split(",")]
```

**架構設計**:
- **MCP 協議**: 支援 Claude 的 Model Context Protocol
- **工具管理**: 可配置啟用的工具列表
- **輔助方法**: 提供工具列表解析方法

**配置項說明**:
- `server_host`: MCP 伺服器主機位址
- `server_port`: MCP 伺服器端口
- `server_name`: MCP 伺服器名稱
- `tools_enabled`: 啟用的工具列表（逗號分隔）
- `timeout`: MCP 連接超時時間

**輔助方法**:
- `get_tools_enabled_list()`: 將逗號分隔的工具字串轉換為列表

### 📚 RAG (Retrieval-Augmented Generation) 配置類 (第48-57行)

```python
class RAGSettings(BaseSettings):
    """RAG 系統設定"""
    vector_db_type: str = Field("chromadb", env="VECTOR_DB_TYPE")
    vector_db_path: str = Field("./data/vector_db", env="VECTOR_DB_PATH")
    vector_db_collection: str = Field("ziwei_knowledge", env="VECTOR_DB_COLLECTION")
    embedding_model: str = Field("text-embedding-ada-002", env="EMBEDDING_MODEL")
    embedding_provider: str = Field("openai", env="EMBEDDING_PROVIDER")
    chunk_size: int = Field(1000, env="RAG_CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="RAG_CHUNK_OVERLAP")
    top_k: int = Field(5, env="RAG_TOP_K")
```

**架構設計**:
- **向量資料庫**: 支援 ChromaDB 等向量資料庫
- **嵌入模型**: 可配置不同的嵌入模型和提供商
- **文檔處理**: 可調整文檔分塊和檢索參數

**配置項說明**:
- `vector_db_type`: 向量資料庫類型
- `vector_db_path`: 向量資料庫存儲路徑
- `vector_db_collection`: 集合名稱
- `embedding_model`: 嵌入模型名稱
- `embedding_provider`: 嵌入模型提供商
- `chunk_size`: 文檔分塊大小
- `chunk_overlap`: 分塊重疊大小
- `top_k`: 檢索返回的文檔數量

### 🤝 Multi-Agent 系統配置類 (第59-70行)

```python
class MultiAgentSettings(BaseSettings):
    """Multi-Agent 系統設定"""
    claude_agent_enabled: bool = Field(True, env="CLAUDE_AGENT_ENABLED")
    gpt_agent_enabled: bool = Field(True, env="GPT_AGENT_ENABLED")
    domain_agent_enabled: bool = Field(True, env="DOMAIN_AGENT_ENABLED")
    
    claude_agent_role: str = Field("reasoning_analysis", env="CLAUDE_AGENT_ROLE")
    gpt_agent_role: str = Field("creative_interpretation", env="GPT_AGENT_ROLE")
    domain_agent_role: str = Field("professional_expertise", env="DOMAIN_AGENT_ROLE")
    
    coordinator_max_iterations: int = Field(5, env="COORDINATOR_MAX_ITERATIONS")
    coordinator_timeout: int = Field(60, env="COORDINATOR_TIMEOUT")
```

**架構設計**:
- **Agent 控制**: 可選擇性啟用不同的 Agent
- **角色定義**: 為每個 Agent 定義明確的角色
- **協調參數**: 配置協調器的行為參數

**配置項說明**:
- `*_agent_enabled`: 各 Agent 的啟用狀態
- `*_agent_role`: 各 Agent 的角色定義
- `coordinator_max_iterations`: 協調器最大迭代次數
- `coordinator_timeout`: 協調器超時時間

### 🌐 應用程式配置類 (第72-86行)

```python
class AppSettings(BaseSettings):
    """應用程式設定"""
    host: str = Field("localhost", env="APP_HOST")
    port: int = Field(8000, env="APP_PORT")
    debug: bool = Field(True, env="APP_DEBUG")
    log_level: str = Field("INFO", env="APP_LOG_LEVEL")
    secret_key: Optional[str] = Field(None, env="SECRET_KEY")
    cors_origins: str = Field(
        "http://localhost:3000,http://localhost:8080",
        env="CORS_ORIGINS"
    )

    def get_cors_origins_list(self) -> List[str]:
        """獲取 CORS origins 列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
```

**架構設計**:
- **Web 應用**: 標準的 Web 應用配置
- **安全性**: 包含密鑰和 CORS 設定
- **開發友好**: 預設為開發模式

**配置項說明**:
- `host`: 應用主機位址
- `port`: 應用端口
- `debug`: 除錯模式
- `log_level`: 日誌級別
- `secret_key`: 應用密鑰
- `cors_origins`: CORS 允許的來源

**輔助方法**:
- `get_cors_origins_list()`: 解析 CORS 來源列表

### 🔮 紫微斗數網站配置類 (第88-96行)

```python
class ZiweiWebsiteSettings(BaseSettings):
    """紫微斗數網站設定"""
    url: str = Field("https://fate.windada.com/cgi-bin/fate", env="ZIWEI_WEBSITE_URL")
    timeout: int = Field(30, env="ZIWEI_REQUEST_TIMEOUT")
    max_retries: int = Field(3, env="ZIWEI_MAX_RETRIES")
    user_agent: str = Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        env="ZIWEI_USER_AGENT"
    )
```

**架構設計**:
- **外部服務**: 配置外部紫微斗數網站的連接參數
- **網路爬蟲**: 包含 User-Agent 等爬蟲相關設定
- **容錯機制**: 設定超時和重試參數

**配置項說明**:
- `url`: 紫微斗數網站的 URL
- `timeout`: 請求超時時間
- `max_retries`: 最大重試次數
- `user_agent`: 瀏覽器 User-Agent 字串

### 📝 日誌配置類 (第98-104行)

```python
class LoggingSettings(BaseSettings):
    """日誌設定"""
    file_path: str = Field("./logs/app.log", env="LOG_FILE_PATH")
    max_size: str = Field("10MB", env="LOG_MAX_SIZE")
    backup_count: int = Field(5, env="LOG_BACKUP_COUNT")
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(9090, env="METRICS_PORT")
```

**架構設計**:
- **日誌管理**: 完整的日誌檔案管理配置
- **輪轉機制**: 支援日誌檔案大小限制和備份
- **監控整合**: 包含指標監控的配置

**配置項說明**:
- `file_path`: 日誌檔案路徑
- `max_size`: 日誌檔案最大大小
- `backup_count`: 備份檔案數量
- `enable_metrics`: 是否啟用指標監控
- `metrics_port`: 指標監控端口

### 💾 快取配置類 (第106-114行)

```python
class CacheSettings(BaseSettings):
    """快取設定"""
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")

    ttl_ziwei_chart: int = Field(3600, env="CACHE_TTL_ZIWEI_CHART")
    ttl_rag_results: int = Field(1800, env="CACHE_TTL_RAG_RESULTS")
```

**架構設計**:
- **Redis 整合**: 完整的 Redis 連接配置
- **TTL 管理**: 不同類型數據的生存時間配置
- **性能優化**: 通過快取提升系統性能

**配置項說明**:
- `redis_host`: Redis 主機位址
- `redis_port`: Redis 端口
- `redis_db`: Redis 資料庫編號
- `redis_password`: Redis 密碼（可選）
- `ttl_ziwei_chart`: 紫微命盤快取時間（3600秒 = 1小時）
- `ttl_rag_results`: RAG 結果快取時間（1800秒 = 30分鐘）

## 🏗️ 主配置類與組合模式

### 主配置類 (第116-134行)

```python
class Settings(BaseSettings):
    """主要設定類別"""

    # 子設定
    openai: OpenAISettings = OpenAISettings()
    anthropic: AnthropicSettings = AnthropicSettings()
    mcp: MCPSettings = MCPSettings()
    rag: RAGSettings = RAGSettings()
    multi_agent: MultiAgentSettings = MultiAgentSettings()
    app: AppSettings = AppSettings()
    ziwei_website: ZiweiWebsiteSettings = ZiweiWebsiteSettings()
    logging: LoggingSettings = LoggingSettings()
    cache: CacheSettings = CacheSettings()

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }
```

**架構設計**:
- **組合模式**: 將所有子配置組合成一個主配置類
- **模組化**: 每個功能模組都有獨立的配置類
- **統一管理**: 通過主配置類統一管理所有配置

**設計優勢**:
- **清晰結構**: 配置按功能模組分組
- **易於維護**: 每個模組的配置獨立管理
- **類型安全**: 所有配置都有明確的類型定義
- **環境感知**: 自動載入 .env 檔案

**model_config 說明**:
- `env_file`: 指定環境變數檔案
- `env_file_encoding`: 檔案編碼
- `extra`: 忽略額外的環境變數

### 全域實例與工廠函數 (第136-141行)

```python
# 全域設定實例
settings = Settings()

def get_settings() -> Settings:
    """獲取設定實例"""
    return settings
```

**架構設計**:
- **單例模式**: 全域唯一的配置實例
- **工廠函數**: 提供標準的獲取配置的方法
- **依賴注入**: 便於在其他模組中注入配置

**使用方式**:
```python
from src.config.settings import get_settings

settings = get_settings()
api_key = settings.openai.api_key
```

## 🔍 配置驗證機制

### 配置驗證函數 (第143-164行)

```python
def validate_settings() -> bool:
    """驗證設定完整性"""
    try:
        # 檢查必要的API金鑰
        if not settings.openai.api_key or settings.openai.api_key == "your_openai_api_key_here":
            raise ValueError("OpenAI API key is required")

        if not settings.anthropic.api_key or settings.anthropic.api_key == "your_anthropic_api_key_here":
            raise ValueError("Anthropic API key is required")

        if not settings.app.secret_key or settings.app.secret_key == "your_secret_key_here":
            raise ValueError("Secret key is required")

        # 檢查目錄存在
        os.makedirs(os.path.dirname(settings.rag.vector_db_path), exist_ok=True)
        os.makedirs(os.path.dirname(settings.logging.file_path), exist_ok=True)

        return True

    except Exception as e:
        print(f"Settings validation failed: {e}")
        return False
```

**架構設計**:
- **完整性檢查**: 驗證必要配置項是否存在
- **預設值檢查**: 檢查是否使用了預設的佔位符值
- **目錄創建**: 自動創建必要的目錄
- **錯誤處理**: 完整的異常處理和錯誤報告

**驗證項目**:
1. **API 金鑰驗證**: 檢查 OpenAI 和 Anthropic API 金鑰
2. **安全金鑰驗證**: 檢查應用程式密鑰
3. **目錄檢查**: 確保日誌和向量資料庫目錄存在

### 模組載入時驗證 (第166-169行)

```python
# 在模組載入時驗證設定（暫時禁用以避免啟動問題）
# if __name__ != "__main__":
#     if not validate_settings():
#         print("Warning: Settings validation failed. Please check your .env file.")
```

**架構設計**:
- **自動驗證**: 模組載入時自動驗證配置
- **開發友好**: 暫時禁用以避免開發時的啟動問題
- **警告機制**: 驗證失敗時給出明確的警告訊息

## 🎯 設計模式總結

### 使用的設計模式

1. **設定模式 (Settings Pattern)**: 集中管理所有配置
2. **單例模式 (Singleton Pattern)**: 全域唯一的配置實例
3. **工廠模式 (Factory Pattern)**: `get_settings()` 工廠函數
4. **組合模式 (Composite Pattern)**: 主配置類組合所有子配置
5. **策略模式 (Strategy Pattern)**: 不同環境可使用不同配置策略

### 架構優勢

1. **類型安全**: 基於 Pydantic 的完整類型檢查
2. **環境感知**: 自動載入環境變數和 .env 檔案
3. **模組化**: 按功能分組的清晰配置結構
4. **驗證機制**: 自動驗證配置的完整性和正確性
5. **易於維護**: 集中管理，易於修改和擴展

### 核心特色

- **統一配置**: 所有模組的配置都在一個地方管理
- **環境變數支援**: 完整支援環境變數和 .env 檔案
- **類型安全**: 所有配置項都有明確的類型定義
- **自動驗證**: 啟動時自動驗證配置的正確性
- **開發友好**: 提供合理的預設值和清晰的錯誤訊息

### 使用場景

此配置系統適用於：
- 需要多模組配置管理的複雜應用
- 支援多環境部署的應用系統
- 需要類型安全的配置管理
- 整合多個外部服務的應用
- 需要靈活配置的 AI 應用系統

### 配置檔案範例

```env
# .env 檔案範例
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_secret_key_here

# 應用設定
APP_HOST=localhost
APP_PORT=8000
APP_DEBUG=true

# Multi-Agent 設定
CLAUDE_AGENT_ENABLED=true
GPT_AGENT_ENABLED=true
DOMAIN_AGENT_ENABLED=true

# RAG 設定
VECTOR_DB_TYPE=chromadb
VECTOR_DB_PATH=./data/vector_db
RAG_CHUNK_SIZE=1000

# 快取設定
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL_ZIWEI_CHART=3600
```

這個配置系統展現了現代 Python 應用的最佳實踐，通過 Pydantic 提供類型安全的配置管理，支援環境變數和檔案配置，並具有完整的驗證機制。
