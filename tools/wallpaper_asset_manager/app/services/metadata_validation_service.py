from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("MetadataValidationService")

class MetadataValidationService:
    """Service providing schema, integrity, and file availability checks for wallpaper metadata."""
    
    @staticmethod
    def validate_metadata(
        wallpapers: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
        collections: List[Dict[str, Any]],
        workspace_root: Path | None = None
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validates entire wallpaper metadata dataset.
        Returns: (is_all_valid, list_of_issues)
        """
        issues: List[Dict[str, Any]] = []
        root = workspace_root or PathHelper.get_workspace_root()

        valid_cat_ids = {c.get("id", "").lower() for c in categories}
        valid_col_ids = {col.get("id", "").lower() for col in collections}

        seen_ids = set()
        seen_titles = set()
        seen_filenames = set()

        for idx, item in enumerate(wallpapers):
            item_id = item.get("id", f"idx_{idx}")
            title = item.get("title", "")
            category = item.get("category", "")
            full_path = item.get("imagePath", "")
            thumb_path = item.get("thumbnailPath", "")

            # 1. Unique ID Check
            if item_id in seen_ids:
                issues.append({"id": item_id, "type": "Error", "message": f"Duplicate Wallpaper ID '{item_id}'"})
            else:
                seen_ids.add(item_id)

            # 2. Unique Title Check (Warning)
            if title:
                title_lower = title.lower().strip()
                if title_lower in seen_titles:
                    issues.append({"id": item_id, "type": "Warning", "message": f"Duplicate wallpaper title '{title}'"})
                else:
                    seen_titles.add(title_lower)
            else:
                issues.append({"id": item_id, "type": "Error", "message": "Wallpaper title is empty."})

            # 3. Category Check
            if category.lower().strip() not in valid_cat_ids:
                issues.append({"id": item_id, "type": "Warning", "message": f"Category '{category}' not defined in categories.json"})

            # 4. File Existence Check on Disk
            if full_path:
                full_disk = root / full_path
                if not full_disk.exists():
                    issues.append({"id": item_id, "type": "Error", "message": f"Wallpaper asset file missing on disk: '{full_path}'"})
                else:
                    fname = full_disk.name.lower()
                    if fname in seen_filenames:
                        issues.append({"id": item_id, "type": "Warning", "message": f"Duplicate wallpaper filename: '{fname}'"})
                    else:
                        seen_filenames.add(fname)
            else:
                issues.append({"id": item_id, "type": "Error", "message": "imagePath is missing."})

            # 5. Thumbnail Path check if present
            if thumb_path:
                thumb_disk = root / thumb_path
                if not thumb_disk.exists():
                    issues.append({"id": item_id, "type": "Warning", "message": f"Legacy thumbnail asset file missing on disk: '{thumb_path}'"})

        is_all_valid = not any(issue["type"] == "Error" for issue in issues)
        logger.info("Metadata validation completed. Found %d issues.", len(issues))
        return is_all_valid, issues
