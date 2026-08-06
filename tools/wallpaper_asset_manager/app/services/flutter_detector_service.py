from pathlib import Path
from typing import Tuple, List, Dict
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("FlutterDetectorService")

class FlutterDetectorService:
    """Service detecting Flutter project environment and verifying pubspec.yaml asset definitions."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()

    def is_valid_flutter_project(self) -> Tuple[bool, str]:
        pubspec_path = self.workspace_root / "pubspec.yaml"
        lib_path = self.workspace_root / "lib"
        
        if not pubspec_path.exists():
            return False, f"pubspec.yaml not found at {self.workspace_root}"
        if not lib_path.exists():
            return False, f"lib/ folder not found at {self.workspace_root}"

        return True, "Valid Flutter workspace detected."

    def verify_pubspec_assets(self) -> Tuple[bool, List[str]]:
        """Checks whether pubspec.yaml contains entries for wallpapers and metadata assets."""
        pubspec_path = self.workspace_root / "pubspec.yaml"
        if not pubspec_path.exists():
            return False, ["pubspec.yaml missing"]

        warnings = []
        try:
            content = pubspec_path.read_text(encoding="utf-8")
            required_assets = [
                "assets/wallpapers/full/",
                "assets/wallpapers/thumbnails/",
                "assets/metadata/"
            ]
            for asset in required_assets:
                if asset not in content:
                    warnings.append(f"Asset path '{asset}' not explicitly listed in pubspec.yaml assets section.")
        except Exception as e:
            warnings.append(f"Error reading pubspec.yaml: {e}")

        is_ok = len(warnings) == 0
        logger.info("Pubspec asset verification completed. Warnings: %d", len(warnings))
        return is_ok, warnings
