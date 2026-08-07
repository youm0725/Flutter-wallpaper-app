import sys
import os
from pathlib import Path

class PathHelper:
    """Utility class for resolving application and workspace paths safely across dev & frozen environments."""
    
    @staticmethod
    def get_manager_root() -> Path:
        """Returns Path object to tools/wallpaper_asset_manager."""
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).resolve().parent
            # Check upward parents for main.py or tools directory
            for parent in [exe_dir] + list(exe_dir.parents):
                if (parent / "main.py").exists() or (parent.name == "wallpaper_asset_manager"):
                    return parent
            # Fallback for dist/WallpaperAssetManager/ -> tools/wallpaper_asset_manager
            if (exe_dir.parent.parent / "main.py").exists():
                return exe_dir.parent.parent
        return Path(__file__).resolve().parent.parent.parent

    @staticmethod
    def get_tool_root() -> Path:
        """Returns Path object to tools/wallpaper_asset_manager."""
        return PathHelper.get_manager_root()

    @staticmethod
    def get_workspace_root() -> Path:
        """Returns Path object to the main Flutter project root directory."""
        manager_root = PathHelper.get_manager_root()
        # Search upwards for pubspec.yaml
        for p in [manager_root] + list(manager_root.parents):
            if (p / "pubspec.yaml").exists():
                return p
        # Fallback to parent of tools/
        return manager_root.parent.parent

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
