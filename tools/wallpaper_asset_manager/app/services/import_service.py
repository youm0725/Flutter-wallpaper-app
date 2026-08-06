import uuid
from pathlib import Path
from typing import List, Dict, Optional, Callable, Set
from app.models.imported_wallpaper import ImportedWallpaperItem
from app.services.validation_service import ValidationService, SUPPORTED_EXTENSIONS
from app.services.thumbnail_service import ThumbnailService
from app.core.logger import get_logger

logger = get_logger("ImportService")

class ImportService:
    """Service managing wallpaper import session, file validation, filtering, and sorting."""
    
    def __init__(self, thumbnail_service: ThumbnailService):
        self.thumbnail_service = thumbnail_service
        self.items: List[ImportedWallpaperItem] = []
        self.selected_item_id: Optional[str] = None
        self.search_query: str = ""
        self.sort_key: str = "Import Time"
        self.sort_reverse: bool = False

    def import_files(
        self,
        file_paths: List[Path],
        on_thumbnail_ready: Optional[Callable[[str], None]] = None
    ) -> List[ImportedWallpaperItem]:
        """Imports a list of image files, validates them, and queues thumbnail generation."""
        new_items: List[ImportedWallpaperItem] = []
        existing_filenames = {item.filename for item in self.items}

        for path in file_paths:
            path = Path(path).resolve()
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            # Skip exact duplicate path already in list
            if any(item.file_path == path for item in self.items):
                logger.info("File already imported: %s", path)
                continue

            # Validate file
            is_valid, status, msgs, w, h, res_str, aspect_str, creation_str = ValidationService.validate_file(
                path, existing_filenames=existing_filenames
            )
            existing_filenames.add(path.name)

            size_bytes = path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            size_fmt = f"{size_mb:.1f} MB" if size_mb >= 1.0 else f"{round(size_bytes / 1024)} KB"

            item_id = str(uuid.uuid4())[:8]
            item = ImportedWallpaperItem(
                id=item_id,
                file_path=path,
                filename=path.name,
                extension=path.suffix.lower(),
                file_size_bytes=size_bytes,
                file_size_formatted=size_fmt,
                width=w,
                height=h,
                resolution_str=res_str,
                aspect_ratio_str=aspect_str,
                creation_date_str=creation_str,
                is_valid=is_valid,
                validation_status=status,
                validation_messages=msgs
            )

            self.items.append(item)
            new_items.append(item)

            # Select first imported item if none selected
            if not self.selected_item_id:
                self.selected_item_id = item.id

            # Queue Async Thumbnail Generation
            def _cb(fp: Path, t_img, p_img, target_item=item):
                target_item.thumbnail_ctk = t_img
                target_item.preview_ctk = p_img
                if on_thumbnail_ready:
                    on_thumbnail_ready(target_item.id)

            self.thumbnail_service.generate_thumbnails_async(path, _cb)

        logger.info("Imported %d new wallpapers. Total count: %d", len(new_items), len(self.items))
        return new_items

    def import_directory(
        self,
        dir_path: Path,
        on_thumbnail_ready: Optional[Callable[[str], None]] = None
    ) -> List[ImportedWallpaperItem]:
        """Scans directory recursively for supported images and imports them."""
        dir_path = Path(dir_path).resolve()
        if not dir_path.is_dir():
            logger.error("Invalid import directory: %s", dir_path)
            return []

        candidates: List[Path] = []
        for root, _, files in dir_path.walk():
            for f in files:
                p = root / f
                if p.suffix.lower() in SUPPORTED_EXTENSIONS:
                    candidates.append(p)

        logger.info("Scanned directory %s: Found %d candidates.", dir_path, len(candidates))
        return self.import_files(candidates, on_thumbnail_ready=on_thumbnail_ready)

    def clear_all(self) -> None:
        """Clears all imported items in current session."""
        self.items.clear()
        self.selected_item_id = None
        logger.info("Import session cleared.")

    def delete_selected(self) -> None:
        """Removes all checked items from session."""
        self.items = [item for item in self.items if not item.is_selected]
        if self.selected_item_id and not any(item.id == self.selected_item_id for item in self.items):
            self.selected_item_id = self.items[0].id if self.items else None
        logger.info("Selected items deleted. Remaining: %d", len(self.items))

    def select_all(self) -> None:
        for item in self.items:
            item.is_selected = True

    def deselect_all(self) -> None:
        for item in self.items:
            item.is_selected = False

    def set_active_preview(self, item_id: str) -> Optional[ImportedWallpaperItem]:
        self.selected_item_id = item_id
        return self.get_selected_preview_item()

    def get_selected_preview_item(self) -> Optional[ImportedWallpaperItem]:
        if not self.selected_item_id and self.items:
            self.selected_item_id = self.items[0].id
        for item in self.items:
            if item.id == self.selected_item_id:
                return item
        return None

    def get_filtered_sorted_items(self) -> List[ImportedWallpaperItem]:
        pass

    def get_display_items(self) -> List[ImportedWallpaperItem]:
        """Returns items matching active search query and sorting key."""
        result = self.items.copy()
        
        # Search Filter
        if self.search_query.strip():
            q = self.search_query.lower().strip()
            result = [item for item in result if q in item.filename.lower()]

        # Sorting
        if self.sort_key == "Filename":
            result.sort(key=lambda x: x.filename.lower(), reverse=self.sort_reverse)
        elif self.sort_key == "Resolution":
            result.sort(key=lambda x: x.width * x.height, reverse=self.sort_reverse)
        elif self.sort_key == "File Size":
            result.sort(key=lambda x: x.file_size_bytes, reverse=self.sort_reverse)
        elif self.sort_key == "Import Time":
            # Retain insertion order
            if self.sort_reverse:
                result.reverse()

        return result

    def get_stats(self) -> Dict[str, str]:
        total_count = len(self.items)
        selected_count = sum(1 for item in self.items if item.is_selected)
        total_bytes = sum(item.file_size_bytes for item in self.items)
        
        total_mb = total_bytes / (1024 * 1024)
        total_size_str = f"{total_mb:.1f} MB" if total_mb >= 1.0 else f"{round(total_bytes / 1024)} KB"
        
        issues_count = sum(1 for item in self.items if item.validation_status in ("Warning", "Error"))
        
        return {
            "total_count": str(total_count),
            "selected_count": str(selected_count),
            "total_size": total_size_str,
            "issues_count": str(issues_count)
        }
