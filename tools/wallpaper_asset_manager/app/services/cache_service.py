import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("CacheService")

class CacheService:
    """Service managing offline statistics caching for high performance dashboard loading."""
    
    def __init__(self):
        self.cache_path = PathHelper.get_config_dir() / "stats_cache.json"

    def load_cache(self) -> Optional[Dict[str, Any]]:
        if not self.cache_path.exists():
            return None
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Loaded statistics cache from stats_cache.json")
            return data
        except Exception as e:
            logger.warning("Failed loading stats cache: %s", e)
            return None

    def save_cache(self, stats: Dict[str, Any]) -> bool:
        try:
            stats["cache_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)
            logger.info("Saved updated statistics cache.")
            return True
        except Exception as e:
            logger.error("Failed saving stats cache: %s", e)
            return False

    def invalidate_cache(self) -> None:
        if self.cache_path.exists():
            try:
                self.cache_path.unlink()
                logger.info("Invalidated statistics cache.")
            except Exception as e:
                logger.error("Error unlinking cache file: %s", e)
