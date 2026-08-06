from pathlib import Path
from typing import Dict, Any, List
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("SizeAnalyzerService")

class SizeAnalyzerService:
    """Service analyzing asset disk space consumption and warning thresholds."""
    
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

        full_size_bytes = _dir_size(wallpapers_dir / "full")
        thumb_size_bytes = _dir_size(wallpapers_dir / "thumbnails")
        metadata_size_bytes = _dir_size(metadata_dir)

        total_bytes = full_size_bytes + thumb_size_bytes + metadata_size_bytes
        total_mb = total_bytes / (1024 * 1024)

        issues: List[Dict[str, Any]] = []
        if total_mb > max_limit_mb:
            issues.append({
                "category": "Storage Limit",
                "severity": "Warning",
                "location": "assets/",
                "problem": f"Total assets size ({total_mb:.1f} MB) exceeds configured warning limit ({max_limit_mb} MB).",
                "fix": "Re-compress wallpapers using Compact WebP preset or remove unused wallpapers."
            })

        return {
            "full_size_mb": round(full_size_bytes / (1024 * 1024), 2),
            "thumb_size_mb": round(thumb_size_bytes / (1024 * 1024), 2),
            "metadata_size_mb": round(metadata_size_bytes / (1024 * 1024), 2),
            "total_size_mb": round(total_mb, 2),
            "max_limit_mb": max_limit_mb,
            "issues": issues
        }
