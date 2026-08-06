import json
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Tuple
from app.utils.path_helper import PathHelper
from app.services.master_backup_service import MasterBackupService
from app.services.metadata_service import MetadataService
from app.core.logger import get_logger

logger = get_logger("MasterRestoreService")

class MasterRestoreService:
    """Service handling backup validation, restore diff previewing, emergency snapshots, and restore execution."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.tool_root = PathHelper.get_tool_root()
        self.backup_service = MasterBackupService(workspace_root=self.workspace_root)
        self.metadata_service = MetadataService(workspace_root=self.workspace_root)

    def validate_backup(self, backup_folder: Path) -> Tuple[bool, str]:
        backup_folder = Path(backup_folder)
        if not backup_folder.exists():
            return False, "Backup directory does not exist."

        info_file = backup_folder / "backup_info.json"
        if not info_file.exists():
            return False, "Missing backup_info.json metadata file."

        try:
            with open(info_file, "r", encoding="utf-8") as f:
                info = json.load(f)
            if "wallpaper_count" not in info:
                return False, "Corrupted backup_info.json format."
        except Exception as e:
            return False, f"Unreadable backup_info.json: {e}"

        return True, "Backup structure & metadata verified."

    def preview_restore(self, backup_folder: Path) -> Dict[str, Any]:
        """Calculates restore preview diff comparing current workspace state vs backup state."""
        backup_folder = Path(backup_folder)
        info_file = backup_folder / "backup_info.json"
        
        current_wallpapers = self.metadata_service.load_wallpapers_json()
        cur_count = len(current_wallpapers)

        backup_count = 0
        backup_reason = "Unknown"
        backup_date = "Unknown"
        backup_size = 0.0

        if info_file.exists():
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    info = json.load(f)
                backup_count = info.get("wallpaper_count", 0)
                backup_reason = info.get("reason", "Manual")
                backup_date = f"{info.get('date')} {info.get('time')}"
                backup_size = info.get("storage_size_mb", 0.0)
            except Exception:
                pass

        diff_count = backup_count - cur_count
        diff_str = f"+{diff_count} wallpapers added" if diff_count > 0 else (f"{diff_count} wallpapers removed" if diff_count < 0 else "No wallpaper count change")

        return {
            "current_wallpapers_count": cur_count,
            "backup_wallpapers_count": backup_count,
            "count_difference": diff_count,
            "diff_summary": diff_str,
            "backup_date": backup_date,
            "backup_reason": backup_reason,
            "backup_size_mb": backup_size
        }

    def restore_backup(
        self,
        backup_folder: Path,
        mode: str = "Complete",
        create_emergency_backup: bool = True
    ) -> Tuple[bool, str]:
        """Restores repository state with automatic pre-restore emergency backup."""
        start_time = time.time()
        backup_folder = Path(backup_folder)

        is_valid, val_msg = self.validate_backup(backup_folder)
        if not is_valid:
            logger.error("Restore aborted: %s", val_msg)
            return False, f"Restore failed: {val_msg}"

        # Emergency Backup Creation
        if create_emergency_backup:
            logger.info("Creating pre-restore emergency safety backup...")
            self.backup_service.create_backup(reason="Before Restore Emergency Backup")

        try:
            # Mode 1: Restore Metadata
            if mode in ("Complete", "Metadata Only"):
                meta_src = backup_folder / "metadata"
                if meta_src.exists():
                    meta_dst = self.workspace_root / "assets" / "metadata"
                    if meta_dst.exists():
                        shutil.rmtree(meta_dst)
                    shutil.copytree(meta_src, meta_dst)

            # Mode 2: Restore Assets
            if mode in ("Complete", "Assets Only"):
                assets_src = backup_folder / "assets"
                if assets_src.exists():
                    assets_dst = self.workspace_root / "assets" / "wallpapers"
                    if assets_dst.exists():
                        shutil.rmtree(assets_dst)
                    shutil.copytree(assets_src, assets_dst)

            # Mode 3: Restore Config
            if mode in ("Complete", "Configuration Only"):
                config_src = backup_folder / "config"
                if config_src.exists():
                    config_dst = self.tool_root / "config"
                    shutil.copytree(config_src, config_dst, dirs_exist_ok=True)

            duration = round(time.time() - start_time, 2)
            logger.info("Successfully restored backup (%s mode) in %.2fs", mode, duration)
            return True, f"Successfully restored backup in {duration}s ({mode} mode)."

        except Exception as e:
            logger.error("Restore operation failed: %s", e, exc_info=True)
            return False, f"Restore operation failed: {e}"
