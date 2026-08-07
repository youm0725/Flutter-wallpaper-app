from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("AssetValidatorService")

class AssetValidatorService:
    """Service validating physical wallpaper WebP images on disk for resolution, corruption, and size."""
    
    @staticmethod
    def audit_assets(workspace_root: Path | None = None) -> List[Dict[str, Any]]:
        root = workspace_root or PathHelper.get_workspace_root()
        wallpapers_dir = root / "assets" / "wallpapers"
        issues: List[Dict[str, Any]] = []

        if not wallpapers_dir.exists():
            issues.append({
                "category": "Asset Validation",
                "severity": "Error",
                "location": str(wallpapers_dir),
                "problem": "assets/wallpapers folder missing in workspace.",
                "fix": "Run Flutter Sync Engine or recreate asset directory structure."
            })
            return issues

        # Scan wallpaper files in assets/wallpapers
        for root_path, _, files in wallpapers_dir.walk():
            for f in files:
                file_path = root_path / f
                if not file_path.is_file():
                    continue

                rel = file_path.relative_to(root)
                
                # Extension Check
                if file_path.suffix.lower() != ".webp":
                    issues.append({
                        "category": "Asset Validation",
                        "severity": "Warning",
                        "location": str(rel),
                        "problem": f"Non-WebP image format '{file_path.suffix}'.",
                        "fix": "Convert asset to WebP using Image Processing Engine."
                    })

                # Readability & Corruption Check
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                    with Image.open(file_path) as img:
                        w, h = img.size
                        if w < 720 or h < 1280:
                            issues.append({
                                "category": "Image Quality",
                                "severity": "Warning",
                                "location": str(rel),
                                "problem": f"Low resolution ({w}x{h}).",
                                "fix": "Re-import wallpaper with minimum 1080x1920 source image."
                            })
                        
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        if size_mb > 15.0:
                            issues.append({
                                "category": "Image Quality",
                                "severity": "Warning",
                                "location": str(rel),
                                "problem": f"Large file size ({size_mb:.1f} MB).",
                                "fix": "Re-compress using Compact preset."
                            })
                except Exception as e:
                    issues.append({
                        "category": "Asset Validation",
                        "severity": "Error",
                        "location": str(rel),
                        "problem": f"Corrupted or unreadable image file: {e}",
                        "fix": "Delete or re-process corrupted wallpaper image."
                    })

        logger.info("Asset validation audit completed. Found %d issues.", len(issues))
        return issues
