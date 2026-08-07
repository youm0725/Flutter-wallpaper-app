from pathlib import Path
from typing import Dict, List, Any, Optional
from app.utils.path_helper import PathHelper
from app.services.metadata_service import MetadataService
from app.services.sync_backup_service import SyncBackupService
from app.core.logger import get_logger

logger = get_logger("CleanupService")

class CleanupService:
    """Service discovering and safely cleaning up unreferenced/orphaned asset files."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.metadata_service = MetadataService(workspace_root=self.workspace_root)
        self.backup_service = SyncBackupService(workspace_root=self.workspace_root)

    def find_orphaned_assets(self) -> Dict[str, Any]:
        """Scans assets/wallpapers on disk and returns files not referenced by metadata."""
        wallpapers_dir = self.workspace_root / "assets" / "wallpapers"
        wallpapers = self.metadata_service.load_wallpapers_json()

        referenced_paths = set()
        for w in wallpapers:
            rel_img = w.get("imagePath", "")
            if rel_img:
                referenced_paths.add(str((self.workspace_root / rel_img).resolve()))
            rel_thumb = w.get("thumbnailPath", "")
            if rel_thumb:
                referenced_paths.add(str((self.workspace_root / rel_thumb).resolve()))

        orphaned_files: List[Dict[str, Any]] = []
        total_orphan_bytes = 0

        if wallpapers_dir.exists():
            for root, _, files in wallpapers_dir.walk():
                for f in files:
                    fp = (root / f).resolve()
                    if fp.is_file() and fp.suffix.lower() == ".webp":
                        if str(fp) not in referenced_paths:
                            size_b = fp.stat().st_size
                            total_orphan_bytes += size_b
                            orphaned_files.append({
                                "file_path": str(fp),
                                "filename": fp.name,
                                "relative_path": str(fp.relative_to(self.workspace_root)),
                                "file_size_bytes": size_b,
                                "file_size_mb": round(size_b / (1024 * 1024), 2)
                            })

        return {
            "orphan_count": len(orphaned_files),
            "total_orphan_mb": round(total_orphan_bytes / (1024 * 1024), 2),
            "orphaned_files": orphaned_files
        }

    def delete_orphaned_assets(
        self,
        file_paths: List[str],
        create_backup_first: bool = True
    ) -> Dict[str, Any]:
        """Deletes selected orphaned asset files on disk with automated backup."""
        if not file_paths:
            return {"deleted_count": 0, "freed_mb": 0.0, "success": True}

        backup_path = None
        if create_backup_first:
            backup_path = self.backup_service.create_sync_backup(label="cleanup")

        deleted_count = 0
        freed_bytes = 0
        failed_count = 0

        for p_str in file_paths:
            p = Path(p_str)
            if p.exists() and p.is_file():
                try:
                    freed_bytes += p.stat().st_size
                    p.unlink()
                    deleted_count += 1
                    logger.info("Deleted orphaned asset: %s", p.name)
                except Exception as e:
                    logger.error("Failed to delete orphan file %s: %s", p, e)
                    failed_count += 1

        freed_mb = round(freed_bytes / (1024 * 1024), 2)
        return {
            "deleted_count": deleted_count,
            "failed_count": failed_count,
            "freed_mb": freed_mb,
            "backup_path": str(backup_path) if backup_path else None,
            "success": failed_count == 0
        }
