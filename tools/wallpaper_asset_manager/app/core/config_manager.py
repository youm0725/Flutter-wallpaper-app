import copy
import tomllib
import tomli_w
from pathlib import Path
from typing import Any, Dict
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("ConfigManager")

DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {
        "name": "Wallpaper Asset Manager",
        "version": "1.0.0",
        "theme": "Dark",
    },
    "paths": {
        "input_folder": "input",
        "output_folder": "output",
        "flutter_assets_folder": "../../assets",
    },
    "processing": {
        "quality_full": 85,
        "quality_thumb": 75,
        "full_width": 1080,
        "full_height": 1920,
        "thumb_width": 360,
        "thumb_height": 640,
        "format": "WEBP",
    },
    "logging": {
        "level": "INFO",
    }
}

class ConfigManager:
    """Manages reading and writing application configuration in TOML format."""
    
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path if config_path is not None else PathHelper.get_config_path()
        self.config_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Loads configuration from config.toml, creating default if missing."""
        if not self.config_path.exists():
            logger.info("Config file not found. Creating default config at %s", self.config_path)
            self.config_data = copy.deepcopy(DEFAULT_CONFIG)
            self.save_config()
            return self.config_data

        try:
            with open(self.config_path, "rb") as f:
                self.config_data = tomllib.load(f)
            logger.info("Loaded configuration from %s", self.config_path)
        except Exception as e:
            logger.error("Failed to parse config file %s: %s. Using defaults.", self.config_path, e)
            self.config_data = copy.deepcopy(DEFAULT_CONFIG)
            
        return self.config_data

    def save_config(self) -> bool:
        """Saves current configuration state to config.toml."""
        try:
            with open(self.config_path, "wb") as f:
                tomli_w.dump(self.config_data, f)
            logger.info("Configuration saved successfully to %s", self.config_path)
            return True
        except Exception as e:
            logger.error("Error saving configuration to %s: %s", self.config_path, e)
            return False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.config_data.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value
        self.save_config()
