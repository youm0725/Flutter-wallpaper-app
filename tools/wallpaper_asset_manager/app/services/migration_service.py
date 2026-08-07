import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from app.utils.path_helper import PathHelper
from app.services.metadata_service import MetadataService
from app.services.sync_backup_service import SyncBackupService
from app.core.logger import get_logger

logger = get_logger("MigrationService")

class MigrationService:
    """Utility migrating legacy dual-folder assets (full/ & thumbnails/) to single WebP structure."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.metadata_service = MetadataService(workspace_root=self.workspace_root)
        self.backup_service = SyncBackupService(workspace_root=self.workspace_root)

    def detect_legacy_assets(self) -> Dict[str, Any]:
        """Detects whether legacy full/ or thumbnails/ wallpaper directories exist."""
        wallpapers_dir = self.workspace_root / "assets" / "wallpapers"
        full_dir = wallpapers_dir / "full"
        thumb_dir = wallpapers_dir / "thumbnails"

        legacy_full_count = 0
        legacy_thumb_count = 0
        total_legacy_bytes = 0

        if full_dir.exists():
            for root, _, files in full_dir.walk():
                for f in files:
                    fp = root / f
                    if fp.is_file() and fp.suffix.lower() == ".webp":
                        legacy_full_count += 1
                        total_legacy_bytes += fp.stat().st_size

        if thumb_dir.exists():
            for root, _, files in thumb_dir.walk():
                for f in files:
                    fp = root / f
                    if fp.is_file() and fp.suffix.lower() == ".webp":
                        legacy_thumb_count += 1
                        total_legacy_bytes += fp.stat().st_size

        needs_migration = legacy_full_count > 0 or legacy_thumb_count > 0

        return {
            "needs_migration": needs_migration,
            "legacy_full_count": legacy_full_count,
            "legacy_thumb_count": legacy_thumb_count,
            "total_legacy_mb": round(total_legacy_bytes / (1024 * 1024), 2),
        }

    def execute_migration(self, create_backup_first: bool = True) -> Dict[str, Any]:
        """Executes migration normalizing legacy assets to single assets/wallpapers/*.webp structure."""
        start_time = time.time()
        wallpapers_dir = self.workspace_root / "assets" / "wallpapers"
        wallpapers_dir.mkdir(parents=True, exist_ok=True)

        backup_path = None
        if create_backup_first:
            backup_path = self.backup_service.create_sync_backup(label="migration")

        wallpapers = self.metadata_service.load_wallpapers_json()

        migrated_count = 0
        skipped_count = 0
        failed_count = 0
        recovered_bytes = 0

        # 1. Process Metadata Records
        for record in wallpapers:
            rel_image = record.get("imagePath", "")
            rel_thumb = record.get("thumbnailPath", "")

            # If already pointing to assets/wallpapers/*.webp without full/ or thumbnails/
            if rel_image and not "/full/" in rel_image and not "/thumbnails/" in rel_image:
                skipped_count += 1
                if "thumbnailPath" in record:
                    del record["thumbnailPath"]
                continue

            # Locate legacy full file
            src_full_path = self.workspace_root / rel_image if rel_image else None
            
            if src_full_path and src_full_path.exists():
                dest_filename = src_full_path.name
                dest_path = wallpapers_dir / dest_filename
                
                # Resolve filename collisions
                counter = 2
                stem = src_full_path.stem
                while dest_path.exists() and dest_path != src_full_path:
                    dest_path = wallpapers_dir / f"{stem}-{counter}.webp"
                    counter += 1

                try:
                    # Move or copy full asset to root wallpapers/ dir
                    if src_full_path != dest_path:
                        shutil.move(str(src_full_path), str(dest_path))

                    # Update metadata record
                    new_rel = f"assets/wallpapers/{dest_path.name}"
                    record["imagePath"] = new_rel
                    if "thumbnailPath" in record:
                        del record["thumbnailPath"]

                    migrated_count += 1

                    # Remove corresponding legacy thumbnail if exists
                    if rel_thumb:
                        thumb_disk = self.workspace_root / rel_thumb
                        if thumb_disk.exists() and thumb_disk != dest_path:
                            recovered_bytes += thumb_disk.stat().st_size
                            try:
                                thumb_disk.unlink()
                            except Exception:
                                pass
                except Exception as e:
                    logger.error("Migration failed for %s: %s", rel_image, e)
                    failed_count += 1
            else:
                failed_count += 1

        # 2. Save Updated Metadata
        self.metadata_service.save_wallpapers_json(wallpapers, create_backup_first=False)

        # 3. Clean up empty legacy directories
        for sub in ("full", "thumbnails"):
            d = wallpapers_dir / sub
            if d.exists():
                try:
                    shutil.rmtree(d, ignore_errors=True)
                except Exception as e:
                    logger.warning("Could not remove legacy dir %s: %s", d, e)

        duration = round(time.time() - start_time, 2)
        space_recovered_mb = round(recovered_bytes / (1024 * 1024), 2)

        summary = (
            f"Migration Completed in {duration}s!\n"
            f"Migrated: {migrated_count}, Skipped: {skipped_count}, Failed: {failed_count}.\n"
            f"Storage Recovered: {space_recovered_mb} MB."
        )

        logger.info(summary.replace("\n", " "))

        return {
            "success": failed_count == 0,
            "migrated_count": migrated_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count,
            "space_recovered_mb": space_recovered_mb,
            "duration_seconds": duration,
            "backup_path": str(backup_path) if backup_path else None,
            "summary": summary
        }
