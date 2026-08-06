import json
import shutil
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.utils.path_helper import PathHelper
from app.services.metadata_service import MetadataService
from app.core.logger import get_logger

logger = get_logger("MasterBackupService")

class MasterBackupService:
    """Service orchestrating full local repository backups, indexing, and auto-pruning."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.tool_root = PathHelper.get_tool_root()
        self.backups_dir = self.tool_root / "backups" / "repository_backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_service = MetadataService(workspace_root=self.workspace_root)

    def create_backup(self, reason: str = "Manual Backup", description: str = "") -> Tuple[bool, str, Path]:
        """Creates complete local backup snapshot of assets, metadata, config, and reports."""
        start_time = time.time()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        candidate_name = f"backup_{timestamp}"
        backup_folder = self.backups_dir / candidate_name
        
        counter = 1
        while backup_folder.exists():
            backup_folder = self.backups_dir / f"{candidate_name}_{counter}"
            counter += 1
        
        try:
            backup_folder.mkdir(parents=True, exist_ok=True)

            # Copy Assets
            assets_src = self.workspace_root / "assets" / "wallpapers"
            if assets_src.exists():
                shutil.copytree(assets_src, backup_folder / "assets", dirs_exist_ok=True)

            # Copy Metadata
            meta_src = self.workspace_root / "assets" / "metadata"
            if meta_src.exists():
                shutil.copytree(meta_src, backup_folder / "metadata", dirs_exist_ok=True)

            # Copy Config
            config_src = self.tool_root / "config"
            if config_src.exists():
                shutil.copytree(config_src, backup_folder / "config", dirs_exist_ok=True)

            # Copy Reports & Logs
            reports_src = self.tool_root / "logs"
            if reports_src.exists():
                shutil.copytree(reports_src, backup_folder / "reports", dirs_exist_ok=True)

            # Compute Backup Meta Info
            wallpapers = self.metadata_service.load_wallpapers_json()
            
            total_bytes = 0
            for root, _, files in backup_folder.walk():
                for f in files:
                    fp = root / f
                    if fp.is_file():
                        total_bytes += fp.stat().st_size

            size_mb = round(total_bytes / (1024 * 1024), 2)
            
            info = {
                "backup_id": f"backup_{timestamp}",
                "date": time.strftime("%Y-%m-%d"),
                "time": time.strftime("%H:%M:%S"),
                "wallpaper_count": len(wallpapers),
                "storage_size_mb": size_mb,
                "app_version": "1.0.0",
                "reason": reason,
                "description": description or "Full local wallpaper repository backup snapshot.",
                "duration_seconds": round(time.time() - start_time, 2)
            }

            info_file = backup_folder / "backup_info.json"
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(info, f, indent=2)

            logger.info("Successfully created backup %s (%d MB) in %.2fs", info["backup_id"], size_mb, info["duration_seconds"])
            return True, f"Backup created successfully: {info['backup_id']} ({size_mb} MB)", backup_folder

        except Exception as e:
            logger.error("Failed to create backup: %s", e, exc_info=True)
            if backup_folder.exists():
                shutil.rmtree(backup_folder, ignore_errors=True)
            return False, f"Backup failed: {e}", Path()

    def list_backups(self) -> List[Dict[str, Any]]:
        results = []
        if not self.backups_dir.exists():
            return results

        for sub in sorted(self.backups_dir.iterdir(), reverse=True):
            if sub.is_dir() and sub.name.startswith("backup_"):
                info_file = sub / "backup_info.json"
                if info_file.exists():
                    try:
                        with open(info_file, "r", encoding="utf-8") as f:
                            info = json.load(f)
                        info["folder_path"] = str(sub)
                        results.append(info)
                    except Exception:
                        pass
        return results

    def delete_backup(self, backup_folder_name: str) -> bool:
        target = self.backups_dir / backup_folder_name
        if target.exists() and target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
            logger.info("Deleted backup folder: %s", backup_folder_name)
            return True
        return False

    def prune_old_backups(self, max_keep: int = 10) -> int:
        backups = self.list_backups()
        pruned_count = 0
        if len(backups) > max_keep:
            for old_b in backups[max_keep:]:
                folder_name = Path(old_b["folder_path"]).name
                if self.delete_backup(folder_name):
                    pruned_count += 1
        logger.info("Pruned %d old backups. Retained latest %d.", pruned_count, max_keep)
        return pruned_count
