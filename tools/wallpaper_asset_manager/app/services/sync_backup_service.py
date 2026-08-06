import shutil
import time
from pathlib import Path
from typing import List, Dict
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("SyncBackupService")

class SyncBackupService:
    """Service handling pre-sync snapshot backups and sync restoration."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.tool_root = PathHelper.get_tool_root()
        self.backups_dir = self.tool_root / "backups" / "sync_backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def create_sync_backup(self, label: str = "manual") -> Path:
        """Creates complete pre-sync backup of Flutter assets and metadata."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_folder = self.backups_dir / f"backup_{timestamp}_{label}"
        backup_folder.mkdir(parents=True, exist_ok=True)

        assets_src = self.workspace_root / "assets" / "wallpapers"
        metadata_src = self.workspace_root / "assets" / "metadata"

        if assets_src.exists():
            shutil.copytree(assets_src, backup_folder / "assets" / "wallpapers", dirs_exist_ok=True)
        if metadata_src.exists():
            shutil.copytree(metadata_src, backup_folder / "assets" / "metadata", dirs_exist_ok=True)

        logger.info("Created pre-sync backup at %s", backup_folder)
        return backup_folder

    def list_backups(self) -> List[Dict[str, str]]:
        """Lists available restore points."""
        results = []
        if not self.backups_dir.exists():
            return results

        for sub in sorted(self.backups_dir.iterdir(), reverse=True):
            if sub.is_dir() and sub.name.startswith("backup_"):
                stat = sub.stat()
                creation_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                results.append({
                    "name": sub.name,
                    "path": str(sub),
                    "created_at": creation_time
                })
        return results

    def restore_backup(self, backup_path: Path) -> bool:
        """Restores assets and metadata from a previous backup point."""
        backup_path = Path(backup_path)
        if not backup_path.exists():
            logger.error("Backup path does not exist: %s", backup_path)
            return False

        try:
            assets_backup = backup_path / "assets" / "wallpapers"
            metadata_backup = backup_path / "assets" / "metadata"

            target_assets = self.workspace_root / "assets" / "wallpapers"
            target_metadata = self.workspace_root / "assets" / "metadata"

            if assets_backup.exists():
                if target_assets.exists():
                    shutil.rmtree(target_assets)
                shutil.copytree(assets_backup, target_assets)

            if metadata_backup.exists():
                if target_metadata.exists():
                    shutil.rmtree(target_metadata)
                shutil.copytree(metadata_backup, target_metadata)

            logger.info("Successfully restored sync backup from %s", backup_path)
            return True
        except Exception as e:
            logger.error("Failed to restore backup %s: %s", backup_path, e, exc_info=True)
            return False
