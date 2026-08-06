import os
from pathlib import Path

class PathHelper:
    """Utility class for resolving application paths."""
    
    @staticmethod
    def get_manager_root() -> Path:
        """Returns Path object to tools/wallpaper_asset_manager."""
        return Path(__file__).resolve().parent.parent.parent

    @staticmethod
    def get_tool_root() -> Path:
        """Returns Path object to tools/wallpaper_asset_manager."""
        return PathHelper.get_manager_root()

    @staticmethod
    def get_workspace_root() -> Path:
        """Returns Path object to the main Flutter project root directory."""
        return PathHelper.get_manager_root().parent.parent

    @staticmethod
    def get_config_dir() -> Path:
        config_dir = PathHelper.get_manager_root() / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @staticmethod
    def get_config_path() -> Path:
        return PathHelper.get_config_dir() / "config.toml"

    @staticmethod
    def get_logs_dir() -> Path:
        logs_dir = PathHelper.get_manager_root() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    @staticmethod
    def get_input_dir() -> Path:
        input_dir = PathHelper.get_manager_root() / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        return input_dir

    @staticmethod
    def get_output_dir() -> Path:
        output_dir = PathHelper.get_manager_root() / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
