import json
import time
from pathlib import Path
from typing import Any, Optional

from config import CACHE_DIR, CACHE_EXPIRY

class CacheManager:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> Optional[Any]:
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        with cache_path.open('r', encoding='utf-8') as f:
            cached_data = json.load(f)
            
        if time.time() - cached_data['timestamp'] > CACHE_EXPIRY:
            return None
            
        return cached_data['data']

    def set(self, key: str, value: Any) -> None:
        cache_path = self._get_cache_path(key)
        cache_data = {
            'timestamp': time.time(),
            'data': value
        }
        
        with cache_path.open('w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)