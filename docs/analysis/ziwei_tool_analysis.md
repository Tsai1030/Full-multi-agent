# ziwei_tool.py 逐行解析文檔

## 檔案概述
這是一個紫微斗數網站調用工具，實現了MCP（Model Context Protocol）工具來調用 https://fate.windada.com/cgi-bin/fate 網站進行紫微斗數命盤分析。

## 詳細逐行解析

### 檔案頭部與導入模組 (第1-12行)

```python
"""
紫微斗數網站調用工具
實現MCP工具來調用 https://fate.windada.com/cgi-bin/fate
"""
```
**用意**: 檔案說明文檔，描述此工具的主要功能

```python
import requests
import json
import re
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import logging
```
**用意**: 導入必要的模組
- `requests`: 用於HTTP請求
- `json`: JSON數據處理
- `re`: 正則表達式處理
- `typing`: 類型提示
- `BeautifulSoup`: HTML解析
- `logging`: 日誌記錄

### ZiweiTool 類定義與初始化 (第13-35行)

```python
class ZiweiTool:
    """紫微斗數網站調用工具"""
    
    def __init__(self, logger=None):
        self.base_url = "https://fate.windada.com/cgi-bin/fate"
        self.session = requests.Session()
        self.logger = logger or logging.getLogger(__name__)
```
**用意**: 
- 定義主要工具類
- 設置目標網站URL
- 創建HTTP會話以保持連接
- 設置日誌記錄器

```python
        # 時辰對應表 - 對應網站的Hour參數值
        self.hour_mapping = {
            "子": 0,   # 00:00~00:59
            "丑": 1,   # 01:00~01:59
            "寅": 3,   # 03:00~03:59
            "卯": 5,   # 05:00~05:59
            "辰": 7,   # 07:00~07:59
            "巳": 9,   # 09:00~09:59
            "午": 11,  # 11:00~11:59
            "未": 13,  # 13:00~13:59
            "申": 15,  # 15:00~15:59
            "酉": 17,  # 17:00~17:59
            "戌": 19,  # 19:00~19:59
            "亥": 21   # 21:00~21:59
        }
```
**用意**: 建立中國傳統時辰與24小時制的對應關係，用於轉換用戶輸入的時辰到網站所需的數字格式

### 主要方法 get_ziwei_chart (第37-68行)

```python
    def get_ziwei_chart(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        獲取紫微斗數命盤
        
        Args:
            birth_data: 包含性別、出生年月日時的字典
            
        Returns:
            解析後的紫微斗數數據
        """
```
**用意**: 主要公開方法，接收出生資料並返回紫微斗數分析結果

```python
        try:
            # 準備請求參數
            params = self._prepare_request_params(birth_data)
            
            # 發送請求
            response = self._send_request(params)
            
            # 解析回應
            parsed_data = self._parse_response(response)
            
            return {
                "success": True,
                "data": parsed_data,
                "raw_response": response.text[:1000]  # 保留部分原始回應用於調試
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ziwei chart: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
```
**用意**: 
- 實現三步驟處理流程：準備參數→發送請求→解析回應
- 使用try-catch處理異常
- 返回標準化的結果格式，包含成功狀態和數據
- 保留部分原始回應用於調試

### 參數準備方法 _prepare_request_params (第70-125行)

```python
    def _prepare_request_params(self, birth_data: Dict[str, Any]) -> Dict[str, str]:
        """準備請求參數"""

        # 驗證必要參數
        required_fields = ['gender', 'birth_year', 'birth_month', 'birth_day', 'birth_hour']
        for field in required_fields:
            if field not in birth_data:
                raise ValueError(f"Missing required field: {field}")
```
**用意**: 驗證輸入數據的完整性，確保所有必要欄位都存在

```python
        # 驗證年份
        year = int(birth_data['birth_year'])
        if not (1900 <= year <= 2100):
            raise ValueError(f"Invalid birth year: {year}. Must be between 1900-2100")

        # 驗證月份
        month = int(birth_data['birth_month'])
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid birth month: {month}. Must be between 1-12")

        # 驗證日期
        day = int(birth_data['birth_day'])
        if not (1 <= day <= 31):
            raise ValueError(f"Invalid birth day: {day}. Must be between 1-31")
```
**用意**: 對年、月、日進行範圍驗證，確保數據的合理性

```python
        # 轉換時辰格式
        birth_hour = birth_data.get('birth_hour', '子')
        if birth_hour in self.hour_mapping:
            hour_value = self.hour_mapping[birth_hour]
        else:
            # 如果是數字格式，轉換為時辰
            try:
                hour_num = int(birth_hour)
                if 0 <= hour_num <= 23:
                    hour_value = hour_num
                else:
                    raise ValueError(f"Hour number must be 0-23, got {hour_num}")
            except ValueError as ve:
                if "Hour number" in str(ve):
                    raise ve
                raise ValueError(f"Invalid birth hour: {birth_hour}. Must be one of {list(self.hour_mapping.keys())} or 0-23")
```
**用意**: 
- 處理時辰格式轉換，支援中文時辰和數字小時兩種格式
- 提供靈活的輸入方式
- 詳細的錯誤處理和提示

```python
        # 使用正確的參數名稱
        params = {
            'FUNC': 'Basic',
            'Target': '0',
            'SubTarget': '-1',
            'Sex': '1' if birth_data.get('gender', '男') == '男' else '0',
            'Solar': '1',  # 國曆
            'Year': str(year),
            'Month': str(month),
            'Day': str(day),
            'Hour': str(hour_value)
        }

        self.logger.info(f"Request params: {params}")
        return params
```
**用意**: 
- 構建符合目標網站API要求的參數格式
- 性別轉換：男=1，女=0
- 使用國曆（Solar=1）
- 記錄請求參數用於調試

### HTTP請求方法 _send_request (第127-164行)

```python
    def _send_request(self, params: Dict[str, str]) -> requests.Response:
        """發送HTTP請求"""

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
```
**用意**: 
- 設置HTTP標頭模擬真實瀏覽器請求
- 避免被網站識別為機器人
- 支援中文內容（zh-TW, zh）

```python
        # 先獲取頁面以建立session
        self.session.get("https://fate.windada.com/", headers=headers)

        # 發送POST請求
        response = self.session.post(
            self.base_url,
            data=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
```
**用意**: 
- 先訪問主頁建立會話，模擬正常用戶行為
- 發送POST請求到目標API
- 設置30秒超時
- 檢查HTTP狀態碼

```python
        # 設置正確的編碼
        response.encoding = 'utf-8'

        # 如果utf-8解碼失敗，嘗試其他編碼
        try:
            test_content = response.text[:100]
            if not any('\u4e00' <= char <= '\u9fff' for char in test_content):
                # 沒有中文字符，嘗試其他編碼
                response.encoding = 'big5'
        except:
            response.encoding = 'utf-8'

        return response
```
**用意**: 
- 處理中文編碼問題
- 檢測是否包含中文字符（Unicode範圍 \u4e00-\u9fff）
- 如果UTF-8無法正確顯示中文，嘗試Big5編碼
- 確保中文內容正確顯示

### 回應解析主方法 _parse_response (第166-206行)

```python
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """解析網站回應"""

        soup = BeautifulSoup(response.text, 'html.parser')

        # 解析基本信息
        basic_info = self._extract_basic_info(soup)

        # 解析命盤信息
        chart_info = self._extract_chart_info(soup)

        # 解析十二宮位
        palaces = self._extract_palaces(soup)

        # 解析主要星曜
        main_stars = self._extract_main_stars(soup)
```
**用意**: 
- 使用BeautifulSoup解析HTML
- 分模組提取不同類型的信息
- 結構化處理，便於維護

```python
        # 提取命宮主星（用於後續分析）
        ming_gong_stars = []
        if '命宮-身宮' in palaces:
            ming_gong_data = palaces['命宮-身宮']
            ming_gong_stars = [star for star in ming_gong_data.get('stars', []) if star.startswith('主星:')]
        elif '命宮' in palaces:
            ming_gong_data = palaces['命宮']
            ming_gong_stars = [star for star in ming_gong_data.get('stars', []) if star.startswith('主星:')]
```
**用意**: 
- 特別提取命宮主星信息
- 處理命宮和身宮可能合併的情況
- 為後續分析提供關鍵數據

```python
        return {
            "basic_info": basic_info,
            "chart_info": chart_info,
            "palaces": palaces,
            "main_stars": main_stars,
            "ming_gong_stars": ming_gong_stars,
            "total_palaces": len(palaces),
            "total_main_stars": len(main_stars),
            "timestamp": response.headers.get('Date', ''),
            "success_indicators": {
                "has_basic_info": bool(basic_info),
                "has_palaces": len(palaces) > 0,
                "has_main_stars": len(main_stars) > 0
            }
        }
```
**用意**: 
- 返回結構化的解析結果
- 包含統計信息（宮位數量、主星數量）
- 提供成功指標用於驗證解析效果
- 記錄時間戳用於追蹤

## 程式碼架構總結

### 設計模式
1. **單一職責原則**: 每個方法負責特定功能
2. **錯誤處理**: 完整的異常捕獲和處理
3. **可擴展性**: 模組化設計便於添加新功能
4. **調試友好**: 保留原始數據和詳細日誌

### 主要流程
1. 參數驗證與轉換
2. HTTP請求發送
3. HTML內容解析
4. 結構化數據提取
5. 結果格式化返回

### 技術特點
- 支援中文編碼處理
- 模擬真實瀏覽器行為
- 靈活的時辰格式支援
- 完整的錯誤處理機制

## 詳細方法解析（續）

### 基本信息提取方法 _extract_basic_info (第208-250行)

```python
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取基本信息"""
        basic_info = {}

        try:
            # 查找包含基本信息的中央表格
            info_text = soup.get_text()
```
**用意**:
- 從HTML中提取純文本內容
- 準備進行正則表達式匹配

```python
            # 提取陽曆信息
            solar_match = re.search(r'陽曆︰(\d+年\s*\d+月\d+日\d+時)', info_text)
            if solar_match:
                basic_info['solar_date'] = solar_match.group(1)

            # 提取農曆信息
            lunar_match = re.search(r'農曆︰(\d+年\s*\d+月\d+日\w+時)', info_text)
            if lunar_match:
                basic_info['lunar_date'] = lunar_match.group(1)

            # 提取干支信息
            ganzhi_match = re.search(r'干支︰(\w+年\w+月\w+日\w+時)', info_text)
            if ganzhi_match:
                basic_info['ganzhi'] = ganzhi_match.group(1)
```
**用意**:
- 使用正則表達式提取日期信息
- 支援陽曆、農曆、干支三種日期格式
- 容錯處理，如果某項信息不存在不會影響其他項目

```python
            # 提取五行局
            wuxing_match = re.search(r'五行局:\s*(\w+)', info_text)
            if wuxing_match:
                basic_info['wuxing_ju'] = wuxing_match.group(1)

            # 提取生年四化
            sihua_match = re.search(r'生年四化:([^<\n]+)', info_text)
            if sihua_match:
                basic_info['sihua'] = sihua_match.group(1).strip()

            # 提取命主身主
            mingzhu_match = re.search(r'命主:(\w+),\s*身主:(\w+)', info_text)
            if mingzhu_match:
                basic_info['ming_zhu'] = mingzhu_match.group(1)
                basic_info['shen_zhu'] = mingzhu_match.group(2)
```
**用意**:
- 提取紫微斗數的核心概念信息
- 五行局：決定命盤的基本屬性
- 生年四化：重要的星曜變化
- 命主身主：命盤的主導星曜

```python
        except Exception as e:
            self.logger.warning(f"Error extracting basic info: {str(e)}")

        return basic_info
```
**用意**:
- 異常處理，確保單個提取失敗不影響整體
- 記錄警告日誌用於調試

### 命盤信息提取方法 _extract_chart_info (第252-272行)

```python
    def _extract_chart_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取命盤信息"""
        chart_info = {}

        try:
            # 查找命盤相關信息
            chart_elements = soup.find_all(['td', 'div'], string=re.compile(r'命宮|身宮|五行'))

            for element in chart_elements:
                text = element.get_text().strip()
                if '命宮' in text:
                    chart_info['ming_palace'] = text
                elif '身宮' in text:
                    chart_info['shen_palace'] = text
                elif '五行' in text:
                    chart_info['wu_xing'] = text
```
**用意**:
- 查找包含關鍵詞的HTML元素
- 分類提取命宮、身宮、五行相關信息
- 使用正則表達式進行模糊匹配

### 宮位信息提取方法 _extract_palaces (第274-345行)

```python
    def _extract_palaces(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取十二宮位信息"""
        palaces = {}

        try:
            # 查找所有包含宮位信息的td元素
            palace_cells = soup.find_all('td', style=re.compile(r'border:1px solid black'))
```
**用意**:
- 根據CSS樣式定位宮位表格
- 使用邊框樣式作為識別標準

```python
            for cell in palace_cells:
                cell_text = cell.get_text()

                # 查找宮位名稱
                palace_match = re.search(r'【([^】]+宮[^】]*)】', cell_text)
                if palace_match:
                    palace_name = palace_match.group(1)

                    # 提取干支
                    ganzhi_match = re.search(r'^(\w+)', cell_text)
                    ganzhi = ganzhi_match.group(1) if ganzhi_match else ""

                    # 提取大限
                    daxian_match = re.search(r'大限:([^<\n]+)', cell_text)
                    daxian = daxian_match.group(1).strip() if daxian_match else ""

                    # 提取小限
                    xiaoxian_match = re.search(r'小限:([^<\n]+)', cell_text)
                    xiaoxian = xiaoxian_match.group(1).strip() if xiaoxian_match else ""
```
**用意**:
- 解析每個宮位的基本信息
- 提取宮位名稱（用【】包圍）
- 提取干支、大限、小限等時間信息

```python
                    # 提取星曜信息（查找有顏色標記的星曜）
                    stars = []

                    # 查找紅色星曜（主星）
                    red_stars = cell.find_all('font', color='red')
                    for star in red_stars:
                        star_text = star.get_text().strip()
                        if star_text:
                            stars.append(f"主星:{star_text}")

                    # 查找藍色星曜（輔星）
                    blue_stars = cell.find_all('font', color='blue')
                    for star in blue_stars:
                        star_text = star.get_text().strip()
                        if star_text:
                            stars.append(f"輔星:{star_text}")

                    # 查找黑色星曜（雜曜）
                    black_stars = cell.find_all('font', color='black')
                    for star in black_stars:
                        star_text = star.get_text().strip()
                        if star_text:
                            stars.append(f"雜曜:{star_text}")
```
**用意**:
- 根據顏色分類星曜
- 紅色：主星（最重要）
- 藍色：輔星（次要）
- 黑色：雜曜（其他）
- 為每個星曜添加分類標籤

```python
                    # 查找四化標記
                    sihua_elements = cell.find_all('element')
                    for element in sihua_elements:
                        title = element.get('title', '')
                        text = element.get_text().strip()
                        if title and text:
                            stars.append(f"四化:{title}-{text}")

                    palaces[palace_name] = {
                        'ganzhi': ganzhi,
                        'daxian': daxian,
                        'xiaoxian': xiaoxian,
                        'stars': stars,
                        'raw_text': cell_text[:200]  # 保留原始文本用於調試
                    }
```
**用意**:
- 提取四化信息（化祿、化權、化科、化忌）
- 組織宮位的完整信息
- 保留原始文本用於調試和驗證

### 特定宮位星曜提取方法 _extract_palace_stars (第347-370行)

```python
    def _extract_palace_stars(self, soup: BeautifulSoup, palace_name: str) -> Dict[str, Any]:
        """提取特定宮位的星曜信息"""
        palace_data = {
            "name": palace_name,
            "stars": [],
            "description": ""
        }

        try:
            # 查找該宮位相關的星曜
            # 這裡需要根據實際網站結構調整
            palace_section = soup.find('td', string=re.compile(palace_name))
            if palace_section:
                # 查找相鄰的星曜信息
                siblings = palace_section.find_next_siblings()
                for sibling in siblings[:3]:  # 限制查找範圍
                    text = sibling.get_text().strip()
                    if any(star in text for star in ['紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府', '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍']):
                        palace_data["stars"].append(text)
```
**用意**:
- 針對特定宮位進行深度星曜提取
- 查找相鄰HTML元素獲取更多信息
- 使用十四主星列表進行過濾
- 限制查找範圍避免過度匹配

### 主要星曜提取方法 _extract_main_stars (第372-397行)

```python
    def _extract_main_stars(self, soup: BeautifulSoup) -> List[str]:
        """提取主要星曜"""
        main_stars = []

        try:
            # 十四主星
            major_stars = [
                '紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府',
                '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍'
            ]

            # 查找紅色字體的主星（這些是命盤中的主要星曜）
            red_stars = soup.find_all('font', color='red')
            for star_element in red_stars:
                star_text = star_element.get_text().strip()
                for major_star in major_stars:
                    if major_star in star_text:
                        # 提取星曜名稱和亮度
                        star_info = star_text
                        if star_info not in main_stars:
                            main_stars.append(star_info)
```
**用意**:
- 定義紫微斗數的十四主星列表
- 專門查找紅色字體的星曜（通常表示主星）
- 避免重複添加相同星曜
- 保留星曜的完整信息（包含亮度等）

### MCP工具包裝器類 MCPZiweiTool (第399-448行)

```python
# MCP工具接口
class MCPZiweiTool:
    """MCP協議的紫微斗數工具包裝器"""

    def __init__(self):
        self.ziwei_tool = ZiweiTool()
```
**用意**:
- 實現MCP（Model Context Protocol）接口
- 包裝ZiweiTool類以符合MCP標準
- 提供標準化的工具接口

```python
    def get_tool_definition(self) -> Dict[str, Any]:
        """返回MCP工具定義"""
        return {
            "name": "get_ziwei_chart",
            "description": "獲取紫微斗數命盤分析",
            "parameters": {
                "type": "object",
                "properties": {
                    "gender": {
                        "type": "string",
                        "description": "性別（男/女）",
                        "enum": ["男", "女"]
                    },
                    "birth_year": {
                        "type": "integer",
                        "description": "出生年份（西元年）",
                        "minimum": 1900,
                        "maximum": 2100
                    },
                    "birth_month": {
                        "type": "integer",
                        "description": "出生月份",
                        "minimum": 1,
                        "maximum": 12
                    },
                    "birth_day": {
                        "type": "integer",
                        "description": "出生日期",
                        "minimum": 1,
                        "maximum": 31
                    },
                    "birth_hour": {
                        "type": "string",
                        "description": "出生時辰（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）"
                    }
                },
                "required": ["gender", "birth_year", "birth_month", "birth_day", "birth_hour"]
            }
        }
```
**用意**:
- 定義MCP工具的JSON Schema
- 指定每個參數的類型、描述和限制
- 設置必要參數列表
- 提供清晰的API文檔

```python
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具"""
        return self.ziwei_tool.get_ziwei_chart(parameters)
```
**用意**:
- 實現MCP工具的執行接口
- 簡單委託給內部ZiweiTool實例
- 保持接口的簡潔性

## 整體架構分析

### 設計原則
1. **分層架構**:
   - ZiweiTool：核心業務邏輯
   - MCPZiweiTool：MCP協議適配層

2. **單一職責**:
   - 每個方法專注於特定功能
   - 清晰的方法命名和職責劃分

3. **錯誤處理**:
   - 多層次異常處理
   - 詳細的錯誤信息和日誌

4. **可維護性**:
   - 模組化設計
   - 豐富的註釋和文檔
   - 保留調試信息

### 技術亮點
1. **網頁爬蟲技術**:
   - 模擬真實瀏覽器行為
   - 處理中文編碼問題
   - Session管理

2. **HTML解析**:
   - BeautifulSoup靈活解析
   - 正則表達式精確提取
   - 多種解析策略

3. **數據結構化**:
   - 將非結構化HTML轉為結構化數據
   - 分類整理不同類型信息
   - 提供統計和驗證信息

4. **協議適配**:
   - MCP標準接口實現
   - JSON Schema定義
   - 標準化輸入輸出

### 使用場景
- AI助手集成紫微斗數功能
- 自動化命盤分析系統
- 批量處理出生資料
- 紫微斗數數據研究

### 擴展可能性
- 支援更多紫微斗數網站
- 添加命盤解讀功能
- 整合其他命理系統
- 提供圖形化命盤顯示

## 總結
這個工具實現了完整的紫微斗數網站調用功能，從HTTP請求到數據解析，再到MCP協議適配，展現了良好的軟體工程實踐和技術深度。代碼結構清晰，錯誤處理完善，具有很好的實用價值和擴展性。
