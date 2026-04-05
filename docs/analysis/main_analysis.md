# main.py 逐行解析文檔

## 檔案概述
這是紫微斗數AI系統的主程式入口，整合了Multi-Agent協作、Claude MCP、RAG檢索和GPT-4o格式化的完整系統。該檔案是整個AI系統的核心控制器，負責協調各個組件的工作流程。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-26行)

```python
"""
紫微斗數AI系統 - 主程式
整合 Multi-Agent + Claude MCP + RAG + GPT-4o 的完整系統
"""
```
**用意**: 檔案說明文檔，明確這是整合多種AI技術的完整系統

```python
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
```
**用意**: 導入標準庫模組
- `asyncio`: 異步編程支援
- `logging`: 日誌記錄
- `json`: JSON數據處理
- `time`: 時間測量
- `datetime`: 時間戳生成
- `typing`: 類型提示
- `pathlib`: 路徑處理

```python
# 強制載入環境變數
from dotenv import load_dotenv
load_dotenv(override=True)
```
**用意**: 
- 強制重新載入環境變數
- 使用override=True確保覆蓋現有變數
- 確保配置的正確載入

```python
# 導入系統組件
from src.agents.coordinator import MultiAgentCoordinator, CoordinationStrategy
from src.mcp.tools.ziwei_tool import ZiweiTool
from src.rag.rag_system import ZiweiRAGSystem
from src.output.gpt4o_formatter import GPT4oFormatter
from src.config.settings import get_settings

# 載入設定
settings = get_settings()
```
**用意**: 
- 導入所有核心系統組件
- 載入全域配置設定
- 為系統初始化做準備

### ZiweiAISystem 類定義與初始化 (第28-69行)

```python
class ZiweiAISystem:
    """紫微斗數AI系統主類"""
    
    def __init__(self, logger=None):
        """初始化系統"""
        self.logger = logger or self._setup_logger()
        
        # 系統組件
        self.coordinator = None
        self.ziwei_tool = None
        self.rag_system = None
        self.formatter = None
        
        # 系統狀態
        self.is_initialized = False
        self.initialization_time = None
        
        self.logger.info("ZiweiAISystem initialized")
```
**用意**: 
- 定義系統主類
- 初始化四個核心組件為None
- 設置系統狀態追蹤
- 記錄初始化日誌

```python
    def _setup_logger(self) -> logging.Logger:
        """設置日誌系統"""
        logger = logging.getLogger("ZiweiAI")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 控制台處理器
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 文件處理器
            log_file = Path("logs/ziwei_ai.log")
            log_file.parent.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(console_formatter)
            logger.addHandler(file_handler)
        
        return logger
```
**用意**: 
- 設置雙重日誌輸出（控制台+文件）
- 自動創建日誌目錄
- 使用UTF-8編碼支援中文
- 避免重複添加處理器

### 系統初始化方法 (第71-103行)

```python
    async def initialize(self):
        """初始化所有系統組件"""
        try:
            start_time = time.time()
            self.logger.info("開始初始化紫微斗數AI系統...")
            
            # 1. 初始化 Multi-Agent 協調器
            self.logger.info("初始化 Multi-Agent 協調器...")
            self.coordinator = MultiAgentCoordinator(logger=self.logger)
            
            # 2. 初始化紫微斗數工具
            self.logger.info("初始化紫微斗數工具...")
            self.ziwei_tool = ZiweiTool(logger=self.logger)
            
            # 3. 初始化 RAG 系統
            self.logger.info("初始化 RAG 系統...")
            self.rag_system = await self._initialize_rag_system()
            
            # 4. 初始化 GPT-4o 格式化器
            self.logger.info("初始化 GPT-4o 格式化器...")
            self.formatter = GPT4oFormatter(logger=self.logger)
            
            # 5. 載入紫微斗數知識庫
            await self._load_knowledge_base()
            
            self.initialization_time = time.time() - start_time
            self.is_initialized = True
            
            self.logger.info(f"系統初始化完成，耗時 {self.initialization_time:.2f} 秒")
            
        except Exception as e:
            self.logger.error(f"系統初始化失敗: {str(e)}")
            raise
```
**用意**: 
- 按順序初始化四個核心組件
- 測量初始化時間
- 載入知識庫並驗證
- 完整的錯誤處理和日誌記錄

### RAG系統初始化方法 (第105-158行)

```python
    async def _initialize_rag_system(self) -> ZiweiRAGSystem:
        """初始化 RAG 系統，使用持久化向量庫 test1"""
        try:
            # 配置使用 test1 向量資料庫
            rag_config = {
                "vector_store": {
                    "persist_directory": "./vector_db_test1",
                    "collection_name": "ziwei_knowledge_test1",
                    "embedding_provider": "huggingface",
                    "embedding_model": "BAAI/bge-m3",
                    "embedding_config": {
                        "device": "cpu",
                        "max_length": 1024,
                        "batch_size": 8,
                        "use_fp16": False,
                        "openai_fallback": True,
                        "openai_model": "text-embedding-ada-002"
                    }
                },
                "generator": {
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "rag": {
                    "top_k": 5,
                    "min_score": 0.6,
                    "max_context_length": 4000
                }
            }
```
**用意**: 
- 明確使用test1向量資料庫
- 配置BGE-M3嵌入模型
- 設置CPU運行和較小的批次大小
- 提供OpenAI作為備用嵌入
- 配置RAG檢索參數

```python
            # 創建 RAG 系統實例，使用 test1 資料庫
            rag_system = ZiweiRAGSystem(config=rag_config, logger=self.logger)

            # 檢查 test1 向量庫狀態
            stats = rag_system.get_system_status()
            vector_stats = stats.get('vector_store_stats', {})
            total_docs = vector_stats.get('total_documents', 0)

            self.logger.info(f"使用持久化向量資料庫: test1")
            self.logger.info(f"資料庫位置: ./vector_db_test1")
            self.logger.info(f"集合名稱: ziwei_knowledge_test1")
            self.logger.info(f"包含文檔數: {total_docs}")

            if total_docs > 0:
                self.logger.info("✅ 成功連接到 test1 向量資料庫")
                return rag_system
            else:
                self.logger.warning("⚠️ test1 向量資料庫為空，請檢查資料庫是否正確建立")
                return rag_system
```
**用意**: 
- 創建RAG系統實例
- 檢查向量資料庫狀態
- 記錄詳細的連接信息
- 警告空資料庫但不中斷運行

### 知識庫檢查方法 (第163-187行)

```python
    async def _load_knowledge_base(self):
        """檢查 test1 向量資料庫狀態"""
        try:
            # 顯示 test1 向量庫統計
            stats = self.rag_system.get_system_status()
            vector_stats = stats.get('vector_store_stats', {})
            total_docs = vector_stats.get('total_documents', 0)

            self.logger.info(f"📊 test1 向量資料庫統計:")
            self.logger.info(f"   總文檔數: {total_docs}")
            self.logger.info(f"   資料庫路徑: {vector_stats.get('persist_directory', 'unknown')}")
            self.logger.info(f"   集合名稱: {vector_stats.get('collection_name', 'unknown')}")

            if total_docs > 0:
                self.logger.info("✅ test1 向量資料庫已就緒，包含紫微斗數集成全書內容")

                # 測試搜索功能
                self.logger.info("🔍 測試向量資料庫搜索功能...")
                test_results = self.rag_system.search_knowledge("紫微星", top_k=2)
                self.logger.info(f"   搜索測試成功，找到 {len(test_results)} 條相關結果")
            else:
                self.logger.warning("⚠️ test1 向量資料庫為空，請重新建立資料庫")
```
**用意**: 
- 顯示詳細的資料庫統計信息
- 測試搜索功能確保系統正常
- 使用表情符號增強日誌可讀性
- 提供問題診斷信息

## 程式碼架構總結

### 設計模式
1. **外觀模式**: ZiweiAISystem作為統一的系統接口
2. **組合模式**: 整合多個AI組件協同工作
3. **策略模式**: 支援不同的分析領域和輸出格式
4. **模板方法**: 標準化的分析流程

### 主要特點
- **異步架構**: 全面使用async/await提高性能
- **組件化設計**: 清晰的職責分離和模組化
- **配置驅動**: 靈活的配置管理和環境變數
- **錯誤恢復**: 完整的異常處理和資源清理

### 協作過程顯示方法 (第189-238行)

```python
    async def _coordinate_with_process_display(self,
                                             agent_input: Dict[str, Any],
                                             domain_type: str,
                                             show_process: bool = False) -> Any:
        """帶過程顯示的協調分析"""
        from src.agents.coordinator import CoordinationStrategy

        if show_process:
            print(f"📊 分析領域: {domain_type}")
            print(f"🎯 協調策略: 討論式協作")
            print(f"👥 參與 Agent: Claude Agent, GPT Agent")
            print("-" * 60)

        # 執行協調分析
        coordination_result = await self.coordinator.coordinate_analysis(
            input_data=agent_input,
            domain_type=domain_type,
            strategy=CoordinationStrategy.DISCUSSION
        )

        if show_process:
            self._display_coordination_process(coordination_result)

        return coordination_result
```
**用意**:
- 提供可選的過程顯示功能
- 使用討論式協作策略
- 顯示分析領域和參與的Agent
- 條件性顯示詳細過程

```python
    def _display_coordination_process(self, coordination_result):
        """顯示協調過程詳情"""
        print("\n📋 協作分析結果:")
        print(f"✅ 協作狀態: {'成功' if coordination_result.success else '失敗'}")
        print(f"⏱️  協作耗時: {coordination_result.total_time:.2f} 秒")
        print(f"🤖 參與 Agent 數量: {len(coordination_result.responses)}")

        if coordination_result.discussion_result:
            discussion = coordination_result.discussion_result
            print(f"💬 討論輪次: {len(discussion.rounds)}")

            for i, round_info in enumerate(discussion.rounds, 1):
                print(f"\n🔄 第 {i} 輪討論 - {round_info.topic}")
                print(f"   參與者: {', '.join(round_info.participants)}")
                print(f"   共識程度: {round_info.consensus_level:.2f}")

                for response in round_info.responses:
                    print(f"\n   🤖 {response.agent_id}:")
                    print(f"      信心度: {response.confidence:.2f}")
                    print(f"      處理時間: {response.processing_time:.2f}s")
                    # 顯示回應內容的前100字
                    content_preview = response.content[:100] + "..." if len(response.content) > 100 else response.content
                    print(f"      回應預覽: {content_preview}")

        print("\n" + "="*60)
```
**用意**:
- 詳細顯示協作分析的結果
- 包含成功狀態、耗時、參與者信息
- 顯示討論輪次和共識程度
- 提供每個Agent的信心度和處理時間
- 預覽回應內容避免過長輸出

### 核心分析方法 (第243-352行)

```python
    async def analyze_ziwei_chart(self,
                                 birth_data: Dict[str, Any],
                                 domain_type: str = "comprehensive",
                                 user_profile: Optional[Dict[str, Any]] = None,
                                 output_format: str = "json",
                                 show_agent_process: bool = False) -> Dict[str, Any]:
        """
        完整的紫微斗數分析流程

        Args:
            birth_data: 出生資料 (gender, birth_year, birth_month, birth_day, birth_hour)
            domain_type: 分析領域 (love, wealth, future, comprehensive)
            user_profile: 用戶背景資料

        Returns:
            完整的分析結果
        """
        if not self.is_initialized:
            await self.initialize()
```
**用意**:
- 定義系統的核心分析方法
- 支援多種分析領域和輸出格式
- 可選的Agent過程顯示
- 自動初始化檢查

```python
        try:
            start_time = time.time()
            self.logger.info(f"開始分析紫微斗數命盤，領域: {domain_type}")

            # 1. 獲取紫微斗數命盤數據
            self.logger.info("步驟 1: 獲取命盤數據...")
            chart_data = self.ziwei_tool.get_ziwei_chart(birth_data)

            if not chart_data.get('success', False):
                raise ValueError(f"命盤獲取失敗: {chart_data.get('error', '未知錯誤')}")

            # 2. RAG 知識檢索
            self.logger.info("步驟 2: 檢索相關知識...")
            knowledge_context = await self._retrieve_knowledge(chart_data, domain_type)

            # 3. Multi-Agent 協作分析
            self.logger.info("步驟 3: Multi-Agent 協作分析...")

            if show_agent_process:
                print("\n" + "="*60)
                print("🤖 Multi-Agent 協作分析過程")
                print("="*60)

            agent_input = {
                'chart_data': chart_data,
                'knowledge_context': knowledge_context,
                'birth_data': birth_data,
                'user_profile': user_profile or {}
            }

            coordination_result = await self._coordinate_with_process_display(
                agent_input=agent_input,
                domain_type=domain_type,
                show_process=show_agent_process
            )

            if not coordination_result.success:
                raise ValueError("Multi-Agent 協作分析失敗")
```
**用意**:
- 實現四步驟分析流程
- 步驟1：獲取命盤數據
- 步驟2：RAG知識檢索
- 步驟3：Multi-Agent協作分析
- 條件性顯示Agent過程
- 完整的錯誤檢查

```python
            # 4. GPT-4o 格式化輸出
            self.logger.info("步驟 4: 格式化最終輸出...")
            formatted_result = await self.formatter.format_coordination_result(
                coordination_result=coordination_result,
                domain_type=domain_type,
                user_profile={
                    'birth_data': birth_data,
                    'analysis_time': datetime.now().isoformat(),
                    'processing_time': time.time() - start_time,
                    'agent_responses': len(coordination_result.responses)
                },
                output_format=output_format
            )

            processing_time = time.time() - start_time
            self.logger.info(f"分析完成，總耗時: {processing_time:.2f} 秒")

            # 檢查格式化是否成功
            if formatted_result.success:
                return {
                    'success': True,
                    'result': formatted_result.formatted_content,
                    'metadata': {
                        'processing_time': processing_time,
                        'formatting_time': formatted_result.processing_time,
                        'validation_passed': formatted_result.validation_passed,
                        'chart_data': chart_data,
                        'domain_type': domain_type,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            else:
                return {
                    'success': False,
                    'result': formatted_result.formatted_content,
                    'error': '格式化失敗',
                    'metadata': {
                        'processing_time': processing_time,
                        'chart_data': chart_data,
                        'domain_type': domain_type,
                        'timestamp': datetime.now().isoformat()
                    }
                }
```
**用意**:
- 步驟4：GPT-4o格式化輸出
- 構建詳細的用戶背景信息
- 測量總處理時間
- 返回結構化的分析結果
- 包含完整的元數據信息

### 知識檢索方法 (第354-388行)

```python
    async def _retrieve_knowledge(self, chart_data: Dict[str, Any], domain_type: str) -> str:
        """檢索相關知識"""
        try:
            # 構建查詢
            query_parts = []

            # 從命盤數據提取關鍵信息
            if 'data' in chart_data and 'palace' in chart_data['data']:
                palaces = chart_data['data']['palace']
                for palace_name, stars in palaces.items():
                    if isinstance(stars, list):
                        query_parts.extend(stars)
                    query_parts.append(palace_name)

            # 添加領域相關查詢
            domain_queries = {
                'love': ['愛情', '婚姻', '感情', '夫妻宮'],
                'wealth': ['財富', '財運', '財帛宮', '事業'],
                'future': ['未來', '運勢', '大運', '流年'],
                'comprehensive': ['命盤', '整體', '綜合']
            }

            query_parts.extend(domain_queries.get(domain_type, domain_queries['comprehensive']))

            # 執行知識檢索
            query = ' '.join(query_parts[:10])  # 限制查詢長度
            knowledge_results = self.rag_system.search_knowledge(query, top_k=5, min_score=0.6)

            # 整合知識片段
            knowledge_texts = [result['content'] for result in knowledge_results]
            return '\n\n'.join(knowledge_texts)

        except Exception as e:
            self.logger.error(f"知識檢索失敗: {str(e)}")
            return "無法檢索到相關知識"
```
**用意**:
- 智能提取命盤關鍵信息
- 根據分析領域添加專門查詢詞
- 限制查詢長度避免過長
- 使用較低的相似度閾值(0.6)
- 整合多個知識片段
- 優雅的錯誤處理

### 系統狀態和清理方法 (第390-439行)

```python
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            'initialized': self.is_initialized,
            'initialization_time': self.initialization_time,
            'components': {
                'coordinator': self.coordinator is not None,
                'ziwei_tool': self.ziwei_tool is not None,
                'rag_system': self.rag_system is not None,
                'formatter': self.formatter is not None
            },
            'rag_stats': self.rag_system.get_system_status() if self.rag_system else None,
            'timestamp': datetime.now().isoformat()
        }
```
**用意**:
- 提供完整的系統狀態信息
- 檢查各組件的初始化狀態
- 包含RAG系統的詳細統計
- 提供時間戳用於監控

```python
    async def cleanup(self):
        """清理系統資源"""
        try:
            self.logger.info("開始清理系統資源...")

            # 清理各個組件
            if self.coordinator:
                # 如果協調器有清理方法，調用它
                if hasattr(self.coordinator, 'cleanup'):
                    await self.coordinator.cleanup()
                self.coordinator = None

            if self.ziwei_tool:
                # 如果工具有清理方法，調用它
                if hasattr(self.ziwei_tool, 'cleanup'):
                    await self.ziwei_tool.cleanup()
                self.ziwei_tool = None

            if self.rag_system:
                # 如果 RAG 系統有清理方法，調用它
                if hasattr(self.rag_system, 'cleanup'):
                    await self.rag_system.cleanup()
                self.rag_system = None

            if self.formatter:
                # 如果格式化器有清理方法，調用它
                if hasattr(self.formatter, 'cleanup'):
                    await self.formatter.cleanup()
                self.formatter = None

            self.is_initialized = False
            self.logger.info("✅ 系統資源清理完成")

        except Exception as e:
            self.logger.error(f"清理系統資源時發生錯誤: {str(e)}")
```
**用意**:
- 安全清理所有系統組件
- 使用hasattr檢查清理方法是否存在
- 重置組件引用為None
- 更新初始化狀態
- 完整的錯誤處理

### 便捷函數 (第442-453行)

```python
# 便捷函數
async def create_ziwei_ai_system() -> ZiweiAISystem:
    """創建並初始化紫微斗數AI系統"""
    system = ZiweiAISystem()
    await system.initialize()
    return system


async def quick_analysis(birth_data: Dict[str, Any], domain_type: str = "comprehensive") -> Dict[str, Any]:
    """快速分析函數"""
    system = await create_ziwei_ai_system()
    return await system.analyze_ziwei_chart(birth_data, domain_type)
```
**用意**:
- 提供模組級別的便捷函數
- 簡化系統創建和初始化過程
- 提供一鍵分析功能
- 便於外部調用和測試

### 主程式入口 (第456-549行)

```python
async def main():
    """主程式入口"""
    print("🌟 紫微斗數AI系統")
    print("=" * 50)

    try:
        # 創建系統
        system = await create_ziwei_ai_system()

        # 顯示系統狀態
        status = system.get_system_status()
        print(f"✅ 系統初始化完成")
        print(f"⏱️  初始化時間: {status['initialization_time']:.2f} 秒")

        # 示例分析
        print("\n📊 執行示例分析...")

        sample_birth_data = {
            "gender": "男",
            "birth_year": 1990,
            "birth_month": 5,
            "birth_day": 15,
            "birth_hour": "午"
        }

        # 測試 JSON 轉論述格式（使用 JSON prompt 但輸出論述）
        result = await system.analyze_ziwei_chart(
            birth_data=sample_birth_data,
            domain_type="comprehensive",  # 🎯 在這裡選擇領域：love, wealth, future, comprehensive
            output_format="json_to_narrative",  # 🎯 使用 JSON prompt 但輸出論述格式
            show_agent_process=True  # 🎯 顯示 Agent 協作過程（True=顯示, False=隱藏）
        )
```
**用意**:
- 提供完整的示例演示
- 使用示例出生資料進行測試
- 展示json_to_narrative格式的使用
- 啟用Agent過程顯示
- 提供清晰的配置註釋

```python
        if result['success']:
            print("✅ 分析完成")
            print(f"⏱️  處理時間: {result['metadata']['processing_time']:.2f} 秒")
            print("\n📋 分析結果:")

            # 檢查輸出格式並相應處理
            formatted_result = result['result']

            # 檢查是否為論述格式（通常是純文本）
            if isinstance(formatted_result, str) and not formatted_result.strip().startswith('{'):
                # 論述格式，直接顯示
                print(formatted_result)
            elif isinstance(formatted_result, str):
                try:
                    # 嘗試解析 JSON 字符串
                    parsed_result = json.loads(formatted_result)
                    print(json.dumps(parsed_result, ensure_ascii=False, indent=2))
                except json.JSONDecodeError:
                    # 如果不是有效的 JSON，直接顯示字符串
                    print(formatted_result)
            else:
                # 如果已經是字典或其他對象，直接序列化
                print(json.dumps(formatted_result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 分析失敗: {result['error']}")

        # 清理系統資源
        await system.cleanup()
```
**用意**:
- 智能處理不同的輸出格式
- 自動檢測JSON和論述格式
- 優雅的JSON解析錯誤處理
- 確保系統資源的正確清理

### 異步任務清理 (第524-546行)

```python
    finally:
        # 確保清理所有 asyncio 任務
        try:
            # 取消所有未完成的任務（排除當前任務）
            current_task = asyncio.current_task()
            tasks = [task for task in asyncio.all_tasks() if not task.done() and task != current_task]
            if tasks:
                print(f"🧹 清理 {len(tasks)} 個未完成的任務...")
                for task in tasks:
                    if not task.cancelled():
                        task.cancel()

                # 等待任務取消完成，但設置超時避免無限等待
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    print("⚠️ 任務清理超時，但程序將正常退出")
        except Exception as cleanup_error:
            print(f"⚠️ 清理過程中發生錯誤: {cleanup_error}")
```
**用意**:
- 確保所有異步任務的正確清理
- 排除當前任務避免自我取消
- 設置5秒超時避免無限等待
- 優雅處理清理過程中的錯誤
- 防止程序掛起

```python
if __name__ == "__main__":
    asyncio.run(main())
```
**用意**:
- 標準的異步程式入口
- 使用asyncio.run()自動管理事件循環

## 深度架構分析

### 系統集成策略

#### 1. 四層架構設計
```
用戶輸入 → 命盤獲取 → RAG檢索 → Multi-Agent協作 → GPT-4o格式化 → 最終輸出
```
- **第一層**: 紫微斗數工具獲取命盤數據
- **第二層**: RAG系統檢索相關知識
- **第三層**: Multi-Agent協作分析
- **第四層**: GPT-4o格式化輸出

#### 2. 異步流水線處理
- 每個步驟都是異步執行
- 支援高並發和非阻塞處理
- 完整的錯誤傳播和處理

#### 3. 配置驅動設計
- 使用test1持久化向量資料庫
- 靈活的RAG配置參數
- 支援多種輸出格式

### 技術亮點

#### 1. 智能知識檢索
```python
domain_queries = {
    'love': ['愛情', '婚姻', '感情', '夫妻宮'],
    'wealth': ['財富', '財運', '財帛宮', '事業'],
    'future': ['未來', '運勢', '大運', '流年'],
    'comprehensive': ['命盤', '整體', '綜合']
}
```
- 根據分析領域動態構建查詢
- 結合命盤數據和領域關鍵詞
- 提高檢索的精確性

#### 2. 過程可視化
- 可選的Agent協作過程顯示
- 詳細的討論輪次和共識程度
- 實時的處理時間統計

#### 3. 資源管理
- 完整的組件生命週期管理
- 異步任務的安全清理
- 防止資源洩漏和程序掛起

## 使用場景

### 1. 命理分析服務
- 專業的紫微斗數命盤分析
- 支援多種分析領域
- 高質量的AI生成內容

### 2. 研究和開發
- Multi-Agent協作研究
- RAG系統效果評估
- AI輸出格式化測試

### 3. 系統集成
- 作為後端API服務
- 集成到更大的命理系統
- 支援批量分析處理

## 總結

main.py展現了現代AI系統的完整架構設計，通過異步處理、組件化設計、智能檢索和協作分析，構建了一個功能完整、性能優異的紫微斗數AI系統。其清晰的代碼結構、完整的錯誤處理和靈活的配置管理，為AI應用開發提供了優秀的參考範例。
