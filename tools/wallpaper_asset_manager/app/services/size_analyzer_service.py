from pathlib import Path
from typing import Dict, Any, List
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("SizeAnalyzerService")

class SizeAnalyzerService:
    """Service analyzing asset disk space consumption, footprint estimation, and warning thresholds."""
    
    @staticmethod
    def analyze_storage_size(
        workspace_root: Path | None = None,
        max_limit_mb: float = 200.0
    ) -> Dict[str, Any]:
        root = workspace_root or PathHelper.get_workspace_root()
        wallpapers_dir = root / "assets" / "wallpapers"
        metadata_dir = root / "assets" / "metadata"

        def _dir_size(p: Path) -> int:
            if not p.exists():
                return 0
            tot = 0
            for r, _, files in p.walk():
                for f in files:
                    fp = r / f
                    if fp.is_file():
                        tot += fp.stat().st_size
            return tot

        wallpaper_assets_bytes = _dir_size(wallpapers_dir)
        metadata_size_bytes = _dir_size(metadata_dir)

        total_bytes = wallpaper_assets_bytes + metadata_size_bytes
        total_mb = round(total_bytes / (1024 * 1024), 2)
        wallpaper_assets_mb = round(wallpaper_assets_bytes / (1024 * 1024), 2)
        metadata_size_mb = round(metadata_size_bytes / (1024 * 1024), 2)
        remaining_mb = round(max_limit_mb - total_mb, 2)

        # Health Level Calculation
        ratio = total_mb / max_limit_mb if max_limit_mb > 0 else 0.0
        if ratio < 0.75:
            health_status = "Healthy"
        elif ratio < 0.90:
            health_status = "Notice"
        elif ratio <= 1.00:
            health_status = "Warning"
        else:
            health_status = "Critical"

        issues: List[Dict[str, Any]] = []
        if total_mb > max_limit_mb:
            issues.append({
                "category": "Storage Limit",
                "severity": "Warning",
                "location": "assets/",
                "problem": f"Total assets size ({total_mb} MB) exceeds configured warning limit ({max_limit_mb} MB).",
                "fix": "Re-compress wallpapers using Compact WebP preset or run Asset Cleanup to remove unreferenced wallpapers."
            })

        return {
            "wallpaper_assets_mb": wallpaper_assets_mb,
            "full_size_mb": wallpaper_assets_mb,
            "thumb_size_mb": 0.0,
            "metadata_size_mb": metadata_size_mb,
            "total_size_mb": total_mb,
            "max_limit_mb": max_limit_mb,
            "remaining_mb": remaining_mb,
            "health_status": health_status,
            "issues": issues
        }
