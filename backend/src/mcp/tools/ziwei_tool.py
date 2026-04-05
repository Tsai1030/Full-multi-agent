"""
紫微斗數網站調用工具
實現MCP工具來調用 https://fate.windada.com/cgi-bin/fate
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import logging

class ZiweiTool:
    """紫微斗數網站調用工具"""
    
    def __init__(self, logger=None):
        self.base_url = "https://fate.windada.com/cgi-bin/fate"
        self.session = requests.Session()
        self.logger = logger or logging.getLogger(__name__)
        
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
    
    def get_ziwei_chart(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        獲取紫微斗數命盤

        Args:
            birth_data: 包含性別、出生年月日時的字典

        Returns:
            解析後的紫微斗數數據
        """
        try:
            # 1. 驗證輸入數據
            validation_result = self._validate_birth_data(birth_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"輸入數據驗證失敗: {validation_result['error']}"
                }

            # 2. 準備請求參數
            params = self._prepare_request_params(birth_data)

            # 3. 發送請求（帶重試機制）
            response = self._send_request_with_retry(params)

            # 4. 解析回應
            parsed_data = self._parse_response(response)

            # 5. 驗證解析結果
            validation_result = self._validate_parsed_data(parsed_data)
            if not validation_result["valid"]:
                self.logger.warning(f"解析數據不完整: {validation_result['warnings']}")
                # 嘗試補充缺失數據
                parsed_data = self._supplement_missing_data(parsed_data, birth_data)

            return {
                "success": True,
                "data": parsed_data,
                "data_quality": validation_result,
                "raw_response": response.text  # 保留完整原始回應
            }

        except Exception as e:
            self.logger.error(f"Error getting ziwei chart: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_request_params(self, birth_data: Dict[str, Any]) -> Dict[str, str]:
        """準備請求參數"""

        # 驗證必要參數
        required_fields = ['gender', 'birth_year', 'birth_month', 'birth_day', 'birth_hour']
        for field in required_fields:
            if field not in birth_data:
                raise ValueError(f"Missing required field: {field}")

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

        # 修復編碼問題 - 使用正確的UTF-8解碼
        # 直接從bytes解碼，避免requests的自動編碼檢測問題
        content = response.content.decode('utf-8')

        # 創建一個模擬的response對象來保持兼容性
        class MockResponse:
            def __init__(self, text, headers=None):
                self.text = text
                self.headers = headers or {}
                self.status_code = 200

        response = MockResponse(content, response.headers)

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

        # 提取命宮主星（用於後續分析）
        ming_gong_stars = []
        if '命宮-身宮' in palaces:
            ming_gong_data = palaces['命宮-身宮']
            ming_gong_stars = [star for star in ming_gong_data.get('stars', []) if star.startswith('主星:')]
        elif '命宮' in palaces:
            ming_gong_data = palaces['命宮']
            ming_gong_stars = [star for star in ming_gong_data.get('stars', []) if star.startswith('主星:')]

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
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取基本信息"""
        basic_info = {}

        try:
            # 查找包含基本信息的中央表格
            info_text = soup.get_text()

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

        except Exception as e:
            self.logger.warning(f"Error extracting basic info: {str(e)}")

        return basic_info
    
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
                    
        except Exception as e:
            self.logger.warning(f"Error extracting chart info: {str(e)}")
            
        return chart_info

    def _validate_birth_data(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """驗證出生數據的完整性和有效性"""
        errors = []

        # 檢查必要欄位
        required_fields = ['gender', 'birth_year', 'birth_month', 'birth_day', 'birth_hour']
        for field in required_fields:
            if field not in birth_data or birth_data[field] is None:
                errors.append(f"缺少必要欄位: {field}")

        if errors:
            return {"valid": False, "error": "; ".join(errors)}

        # 檢查數據範圍
        try:
            year = int(birth_data['birth_year'])
            month = int(birth_data['birth_month'])
            day = int(birth_data['birth_day'])

            if not (1900 <= year <= 2100):
                errors.append(f"出生年份超出範圍: {year}")
            if not (1 <= month <= 12):
                errors.append(f"出生月份無效: {month}")
            if not (1 <= day <= 31):
                errors.append(f"出生日期無效: {day}")

        except ValueError as e:
            errors.append(f"數據格式錯誤: {str(e)}")

        # 檢查性別
        if birth_data['gender'] not in ['男', '女']:
            errors.append(f"性別格式錯誤: {birth_data['gender']}")

        # 檢查時辰
        valid_hours = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        if birth_data['birth_hour'] not in valid_hours:
            errors.append(f"時辰格式錯誤: {birth_data['birth_hour']}")

        if errors:
            return {"valid": False, "error": "; ".join(errors)}

        return {"valid": True}

    def _send_request_with_retry(self, params: Dict[str, Any], max_retries: int = 3) -> requests.Response:
        """帶重試機制的請求發送"""
        last_exception = None

        for attempt in range(max_retries):
            try:
                self.logger.info(f"發送請求 (嘗試 {attempt + 1}/{max_retries})")
                response = self._send_request(params)

                # 檢查回應是否包含錯誤
                if "錯誤" in response.text or "error" in response.text.lower():
                    raise ValueError("網站返回錯誤信息")

                # 檢查回應長度
                if len(response.text) < 1000:
                    raise ValueError("回應內容過短，可能獲取失敗")

                return response

            except Exception as e:
                last_exception = e
                self.logger.warning(f"請求失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # 等待2秒後重試

        raise last_exception

    def _validate_parsed_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """驗證解析數據的完整性"""
        warnings = []
        quality_score = 0

        # 檢查基本信息
        basic_info = parsed_data.get('basic_info', {})
        if basic_info:
            quality_score += 20
            if 'solar_date' in basic_info:
                quality_score += 10
            if 'lunar_date' in basic_info:
                quality_score += 10
        else:
            warnings.append("缺少基本信息")

        # 檢查宮位信息
        palaces = parsed_data.get('palaces', {})
        if palaces:
            quality_score += 30
            palace_count = len(palaces)
            if palace_count >= 12:
                quality_score += 20
            elif palace_count >= 8:
                quality_score += 10
            else:
                warnings.append(f"宮位數量不足: {palace_count}/12")
        else:
            warnings.append("缺少宮位信息")

        # 檢查主要星曜
        main_stars = parsed_data.get('main_stars', [])
        if main_stars:
            quality_score += 20
            if len(main_stars) >= 10:
                quality_score += 10
        else:
            warnings.append("缺少主要星曜信息")

        # 檢查命宮主星
        ming_gong_stars = parsed_data.get('ming_gong_stars', [])
        if not ming_gong_stars:
            warnings.append("缺少命宮主星信息")

        return {
            "valid": quality_score >= 60,
            "quality_score": quality_score,
            "warnings": warnings
        }

    def _supplement_missing_data(self, parsed_data: Dict[str, Any], birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """補充缺失的數據"""
        self.logger.info("嘗試補充缺失的數據...")

        # 補充基本信息
        if not parsed_data.get('basic_info'):
            parsed_data['basic_info'] = {
                'gender': birth_data.get('gender', ''),
                'birth_year': birth_data.get('birth_year', ''),
                'birth_month': birth_data.get('birth_month', ''),
                'birth_day': birth_data.get('birth_day', ''),
                'birth_hour': birth_data.get('birth_hour', ''),
                'note': '部分信息由系統補充'
            }

        # 補充空的宮位列表
        if not parsed_data.get('palaces'):
            parsed_data['palaces'] = {}

        # 補充空的主星列表
        if not parsed_data.get('main_stars'):
            parsed_data['main_stars'] = []

        # 添加數據質量標記
        parsed_data['data_supplemented'] = True

        return parsed_data
    
    def _extract_palaces(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取十二宮位信息"""
        palaces = {}

        try:
            # 查找所有包含宮位信息的td元素
            palace_cells = soup.find_all('td', style=re.compile(r'border:1px solid black'))

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

        except Exception as e:
            self.logger.warning(f"Error extracting palaces: {str(e)}")

        return palaces
    
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
                        
        except Exception as e:
            self.logger.warning(f"Error extracting palace stars for {palace_name}: {str(e)}")
            
        return palace_data
    
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

        except Exception as e:
            self.logger.warning(f"Error extracting main stars: {str(e)}")

        return main_stars

# MCP工具接口
class MCPZiweiTool:
    """MCP協議的紫微斗數工具包裝器"""
    
    def __init__(self):
        self.ziwei_tool = ZiweiTool()
    
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
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具"""
        return self.ziwei_tool.get_ziwei_chart(parameters)
