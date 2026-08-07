import json
import shutil
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("MetadataService")

DEFAULT_CATEGORIES = []
DEFAULT_COLLECTIONS = []

class MetadataService:
    """Service managing metadata files, JSON serialization, and automated backups."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.metadata_dir = self.workspace_root / "assets" / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = self.metadata_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def get_wallpapers_path(self) -> Path:
        return self.metadata_dir / "wallpapers.json"

    def get_categories_path(self) -> Path:
        return self.metadata_dir / "categories.json"

    def get_collections_path(self) -> Path:
        return self.metadata_dir / "collections.json"

    def create_backup(self, label: str = "auto") -> Path:
        """Creates timestamped backup copy of all metadata files."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_subfolder = self.backup_dir / f"backup_{timestamp}_{label}"
        backup_subfolder.mkdir(parents=True, exist_ok=True)

        for json_file in ("wallpapers.json", "categories.json", "collections.json"):
            src = self.metadata_dir / json_file
            if src.exists():
                shutil.copy2(src, backup_subfolder / json_file)

        logger.info("Created metadata backup at %s", backup_subfolder)
        return backup_subfolder

    def load_wallpapers_json(self) -> List[Dict[str, Any]]:
        path = self.get_wallpapers_path()
        if not path.exists():
            logger.info("wallpapers.json not found. Returning empty list.")
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error("Error reading wallpapers.json: %s", e)
            return []

    def load_categories_json(self) -> List[Dict[str, Any]]:
        path = self.get_categories_path()
        if not path.exists():
            self.save_categories_json(DEFAULT_CATEGORIES, create_backup_first=False)
            return DEFAULT_CATEGORIES.copy()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else DEFAULT_CATEGORIES.copy()
        except Exception as e:
            logger.error("Error reading categories.json: %s", e)
            return DEFAULT_CATEGORIES.copy()

    def load_collections_json(self) -> List[Dict[str, Any]]:
        path = self.get_collections_path()
        if not path.exists():
            self.save_collections_json(DEFAULT_COLLECTIONS, create_backup_first=False)
            return DEFAULT_COLLECTIONS.copy()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else DEFAULT_COLLECTIONS.copy()
        except Exception as e:
            logger.error("Error reading collections.json: %s", e)
            return DEFAULT_COLLECTIONS.copy()

    def save_wallpapers_json(self, wallpapers: List[Dict[str, Any]], create_backup_first: bool = True) -> bool:
        if create_backup_first:
            self.create_backup(label="wallpapers_save")

        path = self.get_wallpapers_path()
        try:
            # Sort keys for stable formatting
            formatted_list = []
            for item in wallpapers:
                ordered_item = {
                    "id": item.get("id", ""),
                    "title": item.get("title", ""),
                    "category": item.get("category", ""),
                    "thumbnailPath": item.get("thumbnailPath", ""),
                    "imagePath": item.get("imagePath", ""),
                    "resolution": item.get("resolution", "1080x1920"),
                    "fileSize": item.get("fileSize", ""),
                    "tags": item.get("tags", []),
                    "isFeatured": item.get("isFeatured", item.get("featured", False)),
                    "collections": item.get("collections", []),
                    "description": item.get("description", ""),
                }
                formatted_list.append(ordered_item)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(formatted_list, f, indent=2, ensure_ascii=False)
            
            logger.info("Saved %d wallpaper records to wallpapers.json", len(formatted_list))
            return True
        except Exception as e:
            logger.error("Failed saving wallpapers.json: %s", e)
            return False

    def save_categories_json(self, categories: List[Dict[str, Any]], create_backup_first: bool = True) -> bool:
        if create_backup_first:
            self.create_backup(label="categories_save")

        path = self.get_categories_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)
            logger.info("Saved %d category records to categories.json", len(categories))
            return True
        except Exception as e:
            logger.error("Failed saving categories.json: %s", e)
            return False

    def save_collections_json(self, collections: List[Dict[str, Any]], create_backup_first: bool = True) -> bool:
        if create_backup_first:
            self.create_backup(label="collections_save")

        path = self.get_collections_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(collections, f, indent=2, ensure_ascii=False)
            logger.info("Saved %d collection records to collections.json", len(collections))
            return True
        except Exception as e:
            logger.error("Failed saving collections.json: %s", e)
            return False
