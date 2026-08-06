import time
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter
from PIL import Image

from app.utils.path_helper import PathHelper
from app.services.cache_service import CacheService
from app.services.metadata_service import MetadataService
from app.services.size_analyzer_service import SizeAnalyzerService
from app.core.logger import get_logger

logger = get_logger("StatisticsService")

class StatisticsService:
    """Service providing library analytics, storage breakdowns, image stats, and dashboard data."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.cache_service = CacheService()
        self.metadata_service = MetadataService(workspace_root=self.workspace_root)

    def get_dashboard_analytics(self, force_refresh: bool = False) -> Dict[str, Any]:
        if not force_refresh:
            cached = self.cache_service.load_cache()
            if cached:
                return cached

        # Compute fresh analytics
        start_time = time.time()
        wallpapers = self.metadata_service.load_wallpapers_json()
        categories = self.metadata_service.load_categories_json()
        collections = self.metadata_service.load_collections_json()
        
        storage_stats = SizeAnalyzerService.analyze_storage_size(self.workspace_root)
        
        total_wallpapers = len(wallpapers)
        total_categories = len(categories)
        total_collections = len(collections)
        featured_count = sum(1 for w in wallpapers if w.get("isFeatured", w.get("featured", False)))

        # Category Analytics Breakdown
        cat_counts = Counter(w.get("category", "general").lower() for w in wallpapers)
        cat_breakdown = []
        for c in categories:
            cid = c.get("id", "").lower()
            cnt = cat_counts.get(cid, 0)
            cat_breakdown.append({
                "id": cid,
                "name": c.get("name", cid.capitalize()),
                "count": cnt
            })

        # Collection Analytics Breakdown
        col_breakdown = []
        for col in collections:
            col_id = col.get("id", "").lower()
            col_name = col.get("name", col_id)
            cnt = sum(1 for w in wallpapers if any(c.lower() == col_id for c in w.get("collections", [])))
            col_breakdown.append({
                "id": col_id,
                "name": col_name,
                "count": cnt
            })

        # Most Used Tags
        all_tags = []
        for w in wallpapers:
            all_tags.extend(w.get("tags", []))
        top_tags = [item[0] for item in Counter(all_tags).most_common(6)]

        # Image Size & Resolution Metrics
        file_sizes = []
        resolutions = []
        for w in wallpapers:
            rel_p = w.get("imagePath")
            if rel_p:
                full_p = self.workspace_root / rel_p
                if full_p.exists():
                    file_sizes.append(full_p.stat().st_size)
            if w.get("resolution"):
                resolutions.append(w.get("resolution"))

        avg_size_kb = round((sum(file_sizes) / len(file_sizes) / 1024), 1) if file_sizes else 0.0
        largest_kb = round(max(file_sizes) / 1024, 1) if file_sizes else 0.0
        smallest_kb = round(min(file_sizes) / 1024, 1) if file_sizes else 0.0
        common_res = Counter(resolutions).most_common(1)[0][0] if resolutions else "1080x1920"

        # Backups Size Calculation
        backups_dir = PathHelper.get_tool_root() / "backups"
        backups_bytes = 0
        if backups_dir.exists():
            for r, _, files in backups_dir.walk():
                for f in files:
                    fp = r / f
                    if fp.is_file():
                        backups_bytes += fp.stat().st_size
        backups_size_mb = round(backups_bytes / (1024 * 1024), 2)

        # Health & Recent Activity Timeline
        health_status = "Healthy" if not storage_stats["issues"] else "Action Required"
        
        recent_activity = [
            {"time": "Just now", "event": f"Loaded {total_wallpapers} wallpapers & metadata"},
            {"time": time.strftime("%H:%M"), "event": "Completed asset integrity scan"},
            {"time": time.strftime("%Y-%m-%d"), "event": "Synchronized asset manager cache"}
        ]

        analytics = {
            "total_wallpapers": total_wallpapers,
            "total_categories": total_categories,
            "total_collections": total_collections,
            "featured_count": featured_count,
            "total_storage_mb": storage_stats["total_size_mb"],
            "full_size_mb": storage_stats["full_size_mb"],
            "thumb_size_mb": storage_stats["thumb_size_mb"],
            "metadata_size_mb": storage_stats["metadata_size_mb"],
            "backups_size_mb": backups_size_mb,
            "projected_app_mb": storage_stats["total_size_mb"],
            "remaining_mb": round(200.0 - storage_stats["total_size_mb"], 1),
            "max_limit_mb": 200.0,
            "avg_size_kb": avg_size_kb,
            "largest_kb": largest_kb,
            "smallest_kb": smallest_kb,
            "common_resolution": common_res,
            "category_breakdown": cat_breakdown,
            "collection_breakdown": col_breakdown,
            "top_tags": top_tags,
            "health_status": health_status,
            "issues_count": len(storage_stats["issues"]),
            "recent_activity": recent_activity
        }

        self.cache_service.save_cache(analytics)
        logger.info("Rebuilt statistics analytics in %.2fs.", time.time() - start_time)
        return analytics
