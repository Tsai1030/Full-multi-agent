"""
快取管理器 - 提升系統性能
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
import logging

class CacheManager:
    """智能快取管理器"""
    
    def __init__(self, cache_dir: str = "cache", ttl: int = 3600):
        """
        初始化快取管理器
        
        Args:
            cache_dir: 快取目錄
            ttl: 快取存活時間（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
        self.logger = logging.getLogger(__name__)
        
        # 記憶體快取
        self.memory_cache = {}
        self.cache_timestamps = {}
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """生成快取鍵"""
        # 將數據序列化並生成哈希
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """檢查快取是否有效"""
        return time.time() - timestamp < self.ttl
    
    def get_from_memory(self, key: str) -> Optional[Any]:
        """從記憶體快取獲取數據"""
        if key in self.memory_cache:
            timestamp = self.cache_timestamps.get(key, 0)
            if self._is_cache_valid(timestamp):
                self.logger.debug(f"Memory cache hit: {key}")
                return self.memory_cache[key]
            else:
                # 清理過期快取
                del self.memory_cache[key]
                del self.cache_timestamps[key]
        return None
    
    def set_to_memory(self, key: str, value: Any):
        """設置記憶體快取"""
        self.memory_cache[key] = value
        self.cache_timestamps[key] = time.time()
        self.logger.debug(f"Memory cache set: {key}")
    
    def get_from_disk(self, key: str) -> Optional[Any]:
        """從磁盤快取獲取數據"""
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                timestamp = cache_data.get('timestamp', 0)
                if self._is_cache_valid(timestamp):
                    self.logger.debug(f"Disk cache hit: {key}")
                    return cache_data.get('data')
                else:
                    # 刪除過期快取
                    cache_file.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to read cache {key}: {e}")
        
        return None
    
    def set_to_disk(self, key: str, value: Any):
        """設置磁盤快取"""
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            cache_data = {
                'data': value,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"Disk cache set: {key}")
        except Exception as e:
            self.logger.warning(f"Failed to write cache {key}: {e}")
    
    def get(self, data: Dict[str, Any]) -> Optional[Any]:
        """獲取快取數據（先記憶體後磁盤）"""
        key = self._generate_cache_key(data)
        
        # 先檢查記憶體快取
        result = self.get_from_memory(key)
        if result is not None:
            return result
        
        # 再檢查磁盤快取
        result = self.get_from_disk(key)
        if result is not None:
            # 將磁盤快取載入到記憶體
            self.set_to_memory(key, result)
            return result
        
        return None
    
    def set(self, data: Dict[str, Any], value: Any):
        """設置快取數據（同時設置記憶體和磁盤）"""
        key = self._generate_cache_key(data)
        
        # 設置記憶體快取
        self.set_to_memory(key, value)
        
        # 設置磁盤快取
        self.set_to_disk(key, value)
    
    def clear_expired(self):
        """清理過期快取"""
        # 清理記憶體快取
        expired_keys = []
        for key, timestamp in self.cache_timestamps.items():
            if not self._is_cache_valid(timestamp):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            del self.cache_timestamps[key]
        
        # 清理磁盤快取
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                timestamp = cache_data.get('timestamp', 0)
                if not self._is_cache_valid(timestamp):
                    cache_file.unlink()
            except Exception:
                # 如果讀取失敗，刪除該快取文件
                cache_file.unlink()
        
        self.logger.info("Expired cache cleared")
    
    def clear_all(self):
        """清理所有快取"""
        # 清理記憶體快取
        self.memory_cache.clear()
        self.cache_timestamps.clear()
        
        # 清理磁盤快取
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        
        self.logger.info("All cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取快取統計"""
        memory_count = len(self.memory_cache)
        disk_count = len(list(self.cache_dir.glob("*.json")))
        
        return {
            'memory_cache_count': memory_count,
            'disk_cache_count': disk_count,
            'cache_dir': str(self.cache_dir),
            'ttl': self.ttl
        }


# 全局快取實例
_global_cache = None

def get_cache_manager() -> CacheManager:
    """獲取全局快取管理器"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
