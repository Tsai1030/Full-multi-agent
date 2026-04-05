"""
錯誤處理和用戶指導系統
"""

from typing import Dict, Any, List
import logging

class ErrorHandler:
    """智能錯誤處理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_data_validation_error(self, error_details: str) -> str:
        """格式化數據驗證錯誤信息"""
        
        base_message = """
命盤分析面臨數據缺失的困境，請參考以下建議：

## 數據驗證失敗的解決方案

### 1. 確認數據格式的正確性
確保所提供的數據格式無誤，以免因格式問題而導致的數據缺失。

### 2. 檢查系統錯誤
在提供數據時，請確認所有關鍵信息均已提供，這樣才能避免不必要的困擾。

### 3. 驗證出生信息的完整性
請確保以下信息都已正確填寫：
- **性別**: 必須為'男'或'女'
- **出生年份**: 應在1900-2100年之間
- **出生月份**: 應在1-12月之間
- **出生日期**: 應在1-31日之間
- **出生時辰**: 應為十二時辰之一（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）

### 4. 常見問題排除
- 檢查是否有特殊字符或空格
- 確認數字格式是否正確
- 驗證時辰是否使用中文字符

### 5. 重新提交建議
如果問題持續存在，請：
- 重新檢查所有輸入信息
- 嘗試使用不同的瀏覽器
- 清除瀏覽器緩存後重試
        """
        
        if error_details:
            base_message += f"\n\n**詳細錯誤信息**: {error_details}"
        
        return base_message.strip()
    
    def format_network_error(self, error_details: str) -> str:
        """格式化網絡錯誤信息"""
        
        return f"""
## 網絡連接問題

命盤數據獲取失敗，可能是網絡連接問題：

### 1. 檢查網絡連接
請確認您的網絡連接是否正常，可以嘗試訪問其他網站進行驗證。

### 2. 服務器狀態
紫微斗數服務器可能暫時不可用，請稍後重試。

### 3. 防火牆設置
請檢查防火牆或安全軟件是否阻止了連接。

### 4. 重試建議
- 等待1-2分鐘後重新嘗試
- 刷新頁面重新提交
- 檢查網絡設置

**錯誤詳情**: {error_details}
        """.strip()
    
    def format_data_quality_warning(self, quality_info: Dict[str, Any]) -> str:
        """格式化數據質量警告"""
        
        quality_score = quality_info.get('quality_score', 0)
        warnings = quality_info.get('warnings', [])
        
        message = f"""
## 數據質量提醒

命盤數據已獲取，但質量評分為 {quality_score}/100。

### 數據完整性狀況
        """
        
        if warnings:
            message += "\n發現以下問題：\n"
            for i, warning in enumerate(warnings, 1):
                message += f"{i}. {warning}\n"
        
        message += """
### 建議處理方式
1. **繼續分析**: 系統會基於現有數據進行分析
2. **重新獲取**: 可以嘗試重新提交獲取更完整的數據
3. **參考價值**: 分析結果僅供參考，建議結合其他信息

### 提升數據質量的方法
- 確認出生時間的準確性
- 檢查農曆與國曆的轉換
- 驗證時辰的精確度
        """
        
        return message.strip()
    
    def get_user_guidance(self, error_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """獲取用戶指導信息"""
        
        guidance = {
            "error_type": error_type,
            "severity": "medium",
            "user_action_required": True,
            "retry_recommended": True,
            "message": "",
            "suggestions": []
        }
        
        if error_type == "data_validation":
            guidance["severity"] = "high"
            guidance["message"] = self.format_data_validation_error(
                context.get('error_details', '') if context else ''
            )
            guidance["suggestions"] = [
                "檢查所有必填欄位是否完整",
                "驗證數據格式是否正確",
                "確認時辰使用中文字符",
                "重新檢查出生年月日的準確性"
            ]
        
        elif error_type == "network_error":
            guidance["severity"] = "medium"
            guidance["retry_recommended"] = True
            guidance["message"] = self.format_network_error(
                context.get('error_details', '') if context else ''
            )
            guidance["suggestions"] = [
                "檢查網絡連接狀態",
                "等待1-2分鐘後重試",
                "嘗試刷新頁面",
                "檢查防火牆設置"
            ]
        
        elif error_type == "data_quality":
            guidance["severity"] = "low"
            guidance["user_action_required"] = False
            guidance["message"] = self.format_data_quality_warning(
                context.get('quality_info', {}) if context else {}
            )
            guidance["suggestions"] = [
                "可以繼續進行分析",
                "建議驗證出生時間準確性",
                "分析結果僅供參考"
            ]
        
        elif error_type == "parsing_error":
            guidance["severity"] = "high"
            guidance["message"] = """
## 數據解析錯誤

命盤數據解析過程中遇到問題：

### 可能原因
1. 服務器返回的數據格式異常
2. 網站結構發生變化
3. 特殊的出生信息導致解析困難

### 解決建議
1. 嘗試使用不同的出生時間格式
2. 檢查是否為特殊日期（如閏年、節氣邊界）
3. 聯繫技術支持獲取幫助
            """.strip()
            guidance["suggestions"] = [
                "嘗試調整出生時間",
                "檢查是否為特殊日期",
                "聯繫技術支持"
            ]
        
        return guidance

# 全局錯誤處理器實例
error_handler = ErrorHandler()

def get_error_guidance(error_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """獲取錯誤指導的便利函數"""
    return error_handler.get_user_guidance(error_type, context)
