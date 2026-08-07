import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from app.utils.path_helper import PathHelper
from app.services.sync_backup_service import SyncBackupService
from app.services.flutter_detector_service import FlutterDetectorService
from app.core.logger import get_logger

logger = get_logger("SyncService")

DEFAULT_MAX_APP_SIZE_MB = 200.0

class SyncService:
    """Core synchronization service V2 between Asset Manager output and Flutter workspace."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.backup_service = SyncBackupService(self.workspace_root)
        self.detector_service = FlutterDetectorService(self.workspace_root)
        
        self.output_dir = PathHelper.get_output_dir()
        self.reports_dir = PathHelper.get_tool_root() / "logs" / "sync_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def calculate_dir_size_bytes(self, dir_path: Path) -> int:
        if not dir_path.exists():
            return 0
        total = 0
        for root, _, files in dir_path.walk():
            for f in files:
                p = root / f
                if p.is_file():
                    total += p.stat().st_size
        return total

    def calculate_dry_run(self) -> Dict[str, Any]:
        """Calculates Dry Run preview comparing processed output with target Flutter assets."""
        target_assets = self.workspace_root / "assets" / "wallpapers"
        
        processed_wp_dir = self.output_dir / "wallpapers" if (self.output_dir / "wallpapers").exists() else self.output_dir

        added_files: List[str] = []
        updated_files: List[str] = []
        removed_files: List[str] = []

        # Compare Processed vs Target Assets
        target_files_set = set()
        if target_assets.exists():
            for root, _, files in target_assets.walk():
                for f in files:
                    fp = root / f
                    if fp.is_file() and fp.suffix.lower() == ".webp":
                        rel = fp.relative_to(target_assets)
                        target_files_set.add(str(rel))

        processed_files_set = set()
        if processed_wp_dir.exists():
            for root, _, files in processed_wp_dir.walk():
                for f in files:
                    fp = root / f
                    if fp.is_file() and fp.suffix.lower() == ".webp":
                        rel = fp.relative_to(processed_wp_dir)
                        rel_str = str(rel)
                        processed_files_set.add(rel_str)

                        if rel_str in target_files_set:
                            updated_files.append(rel_str)
                        else:
                            added_files.append(rel_str)

        for tf in target_files_set:
            if tf not in processed_files_set:
                removed_files.append(tf)

        cur_bytes = self.calculate_dir_size_bytes(target_assets)
        cur_mb = cur_bytes / (1024 * 1024)

        proc_bytes = self.calculate_dir_size_bytes(processed_wp_dir)
        projected_mb = proc_bytes / (1024 * 1024)
        delta_mb = projected_mb - cur_mb

        exceeds_limit = projected_mb > DEFAULT_MAX_APP_SIZE_MB

        return {
            "added_count": len(added_files),
            "updated_count": len(updated_files),
            "removed_count": len(removed_files),
            "added_files": added_files,
            "updated_files": updated_files,
            "removed_files": removed_files,
            "current_size_mb": round(cur_mb, 2),
            "projected_size_mb": round(projected_mb, 2),
            "delta_size_mb": round(delta_mb, 2),
            "exceeds_limit": exceeds_limit,
            "max_limit_mb": DEFAULT_MAX_APP_SIZE_MB
        }

    def execute_sync(self, create_backup: bool = True) -> Tuple[bool, str, Path]:
        """Executes full asset & metadata synchronization to Flutter application."""
        start_time = time.time()
        dry_run = self.calculate_dry_run()

        # Step 1: Pre-Sync Backup
        backup_path = None
        if create_backup:
            backup_path = self.backup_service.create_sync_backup(label="sync")

        # Step 2: Target Destination Setup
        target_assets = self.workspace_root / "assets" / "wallpapers"
        target_metadata = self.workspace_root / "assets" / "metadata"
        target_assets.mkdir(parents=True, exist_ok=True)
        target_metadata.mkdir(parents=True, exist_ok=True)

        try:
            # Step 3: Copy WebP Wallpaper Assets directly
            processed_wp_dir = self.output_dir / "wallpapers" if (self.output_dir / "wallpapers").exists() else self.output_dir

            if processed_wp_dir.exists():
                for root, _, files in processed_wp_dir.walk():
                    for f in files:
                        fp = root / f
                        if fp.is_file() and fp.suffix.lower() == ".webp":
                            shutil.copy2(fp, target_assets / fp.name)

            duration = round(time.time() - start_time, 2)

            # Step 4: Generate Sync Report Log
            report_path = self._generate_report(dry_run, duration, backup_path)
            logger.info("Flutter Sync V2 completed in %.2fs. Report: %s", duration, report_path)

            summary_msg = f"Synced successfully in {duration}s! Added: {dry_run['added_count']}, Updated: {dry_run['updated_count']}."
            return True, summary_msg, report_path

        except Exception as e:
            logger.error("Sync execution failed: %s", e, exc_info=True)
            if backup_path:
                logger.info("Attempting automatic rollback from %s...", backup_path)
                self.backup_service.restore_backup(backup_path)
            return False, f"Sync failed: {e}. Rollback executed.", Path()

    def _generate_report(self, dry_run: Dict, duration: float, backup_path: Path | None) -> Path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"sync_report_{timestamp}.txt"

        lines = [
            "==========================================================",
            "FLUTTER WALLPAPER APP — ASSET SYNC REPORT V2",
            "==========================================================",
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {duration:.2f} seconds",
            f"Backup Location: {backup_path if backup_path else 'None'}",
            "",
            "SUMMARY STATS:",
            f"  - Wallpapers Added:   {dry_run['added_count']}",
            f"  - Wallpapers Updated: {dry_run['updated_count']}",
            f"  - Wallpapers Removed: {dry_run['removed_count']}",
            f"  - Current App Assets: {dry_run['current_size_mb']} MB",
            f"  - New App Assets:     {dry_run['projected_size_mb']} MB (Delta: {dry_run['delta_size_mb']:+} MB)",
            "",
            "ADDED ASSETS:",
            "\n".join(f"  + {f}" for f in dry_run['added_files']) if dry_run['added_files'] else "  None",
            "",
            "REMOVED ASSETS:",
            "\n".join(f"  - {f}" for f in dry_run['removed_files']) if dry_run['removed_files'] else "  None",
            "=========================================================="
        ]

        report_file.write_text("\n".join(lines), encoding="utf-8")
        return report_file
