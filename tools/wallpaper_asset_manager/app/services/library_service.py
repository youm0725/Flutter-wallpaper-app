import copy
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.services.metadata_service import MetadataService
from app.services.history_service import HistoryService
from app.services.metadata_validation_service import MetadataValidationService
from app.core.logger import get_logger

logger = get_logger("LibraryService")

class LibraryService:
    """Service managing wallpaper library data, CRUD operations, bulk edits, and state history."""
    
    def __init__(self, metadata_service: MetadataService, history_service: HistoryService):
        self.metadata_service = metadata_service
        self.history_service = history_service
        
        self.wallpapers: List[Dict[str, Any]] = []
        self.categories: List[Dict[str, Any]] = []
        self.collections: List[Dict[str, Any]] = []
        
        self.used_id_history: set = set()
        self.reload_all()

    def reload_all(self):
        """Reloads metadata from disk and auto-discovers processed WebP wallpapers."""
        self.wallpapers = self.metadata_service.load_wallpapers_json()
        self.categories = self.metadata_service.load_categories_json()
        self.collections = self.metadata_service.load_collections_json()
        
        for w in self.wallpapers:
            if w.get("id"):
                self.used_id_history.add(w["id"])

        self._auto_discover_disk_wallpapers()

        self.history_service.clear()
        self._push_undo_snapshot()
        logger.info("Library Service initialized with %d wallpapers, %d categories, %d collections.",
                    len(self.wallpapers), len(self.categories), len(self.collections))

    def _auto_discover_disk_wallpapers(self):
        """Scans output/full and assets/wallpapers/full on disk and registers missing WebP records."""
        from app.utils.path_helper import PathHelper
        import time

        search_dirs = [
            self.metadata_service.workspace_root / "assets" / "wallpapers" / "full",
        ]
        if self.metadata_service.workspace_root == PathHelper.get_workspace_root():
            search_dirs.append(PathHelper.get_output_dir() / "full")

        new_found = False
        for full_dir in search_dirs:
            if not full_dir.exists():
                continue

            for cat_dir in full_dir.iterdir():
                if not cat_dir.is_dir():
                    continue
                cat_id = cat_dir.name.lower()

                for webp_file in cat_dir.glob("*.webp"):
                    filename = webp_file.name
                    rel_full = f"assets/wallpapers/full/{cat_id}/{filename}"
                    rel_thumb = f"assets/wallpapers/thumbnails/{cat_id}/{filename}"

                    already_exists = any(
                        w.get("imagePath", "").endswith(filename) or
                        w.get("thumbnailPath", "").endswith(filename) or
                        w.get("id", "") == webp_file.stem
                        for w in self.wallpapers
                    )
                    if already_exists:
                        continue

                    raw_title = webp_file.stem.replace("_", " ").replace("-", " ").title()
                    w_id = self.generate_next_id(cat_id)

                    new_entry = {
                        "id": w_id,
                        "title": raw_title,
                        "category": cat_id,
                        "imagePath": rel_full,
                        "thumbnailPath": rel_thumb,
                        "collections": [],
                        "tags": [cat_id, "wallpaper"],
                        "description": f"{raw_title} wallpaper in {cat_id.capitalize()} category.",
                        "isFeatured": False,
                        "featured": False,
                        "createdAt": time.strftime("%Y-%m-%d")
                    }
                    self.wallpapers.append(new_entry)
                    new_found = True
                    logger.info("Auto-discovered and registered wallpaper record: %s (%s)", w_id, filename)

        if new_found:
            self.metadata_service.save_wallpapers_json(self.wallpapers)

    def _push_undo_snapshot(self):
        snapshot = {
            "wallpapers": copy.deepcopy(self.wallpapers),
            "categories": copy.deepcopy(self.categories),
            "collections": copy.deepcopy(self.collections),
        }
        self.history_service.push_state(snapshot)

    def undo(self) -> bool:
        current_state = {
            "wallpapers": copy.deepcopy(self.wallpapers),
            "categories": copy.deepcopy(self.categories),
            "collections": copy.deepcopy(self.collections),
        }
        prev = self.history_service.undo(current_state)
        if prev:
            self.wallpapers = prev["wallpapers"]
            self.categories = prev["categories"]
            self.collections = prev["collections"]
            logger.info("Undo executed successfully.")
            return True
        return False

    def redo(self) -> bool:
        current_state = {
            "wallpapers": copy.deepcopy(self.wallpapers),
            "categories": copy.deepcopy(self.categories),
            "collections": copy.deepcopy(self.collections),
        }
        next_st = self.history_service.redo(current_state)
        if next_st:
            self.wallpapers = next_st["wallpapers"]
            self.categories = next_st["categories"]
            self.collections = next_st["collections"]
            logger.info("Redo executed successfully.")
            return True
        return False

    def save_all_to_disk(self) -> bool:
        """Saves current state to JSON files with automated backup."""
        w_ok = self.metadata_service.save_wallpapers_json(self.wallpapers)
        c_ok = self.metadata_service.save_categories_json(self.categories)
        col_ok = self.metadata_service.save_collections_json(self.collections)
        return w_ok and c_ok and col_ok

    def generate_next_id(self, category: str = "general") -> str:
        """Generates unique numeric wallpaper ID avoiding duplicate or previously used IDs."""
        prefix = category.lower().strip()
        prefix = re.sub(r'[^a-z0-9]', '', prefix) or "wallpaper"
        
        counter = 1
        while True:
            candidate = f"{prefix}_{counter:02d}"
            if candidate not in self.used_id_history and not any(w.get("id") == candidate for w in self.wallpapers):
                self.used_id_history.add(candidate)
                return candidate
            counter += 1

    def get_wallpaper_by_id(self, wallpaper_id: str) -> Optional[Dict[str, Any]]:
        for w in self.wallpapers:
            if w.get("id") == wallpaper_id:
                return w
        return None

    def update_wallpaper(self, wallpaper_id: str, updates: Dict[str, Any]) -> bool:
        w = self.get_wallpaper_by_id(wallpaper_id)
        if not w:
            return False

        self._push_undo_snapshot()
        w.update(updates)
        logger.info("Updated wallpaper %s: %s", wallpaper_id, list(updates.keys()))
        return True

    def toggle_featured(self, wallpaper_id: str) -> bool:
        w = self.get_wallpaper_by_id(wallpaper_id)
        if not w:
            return False
        
        self._push_undo_snapshot()
        cur = w.get("isFeatured", w.get("featured", False))
        w["isFeatured"] = not cur
        w["featured"] = not cur
        logger.info("Toggled featured for %s: %s -> %s", wallpaper_id, cur, not cur)
        return True

    def delete_wallpaper(self, wallpaper_id: str) -> bool:
        self._push_undo_snapshot()
        orig_len = len(self.wallpapers)
        self.wallpapers = [w for w in self.wallpapers if w.get("id") != wallpaper_id]
        deleted = len(self.wallpapers) < orig_len
        if deleted:
            logger.info("Deleted wallpaper metadata: %s", wallpaper_id)
        return deleted

    # ----------------------------------------------------
    # CATEGORY OPERATIONS
    # ----------------------------------------------------
    def add_category(self, cat_id: str, name: str, description: str = "") -> bool:
        cat_id = cat_id.lower().strip()
        if any(c.get("id", "").lower() == cat_id for c in self.categories):
            logger.warning("Category '%s' already exists.", cat_id)
            return False

        self._push_undo_snapshot()
        self.categories.append({
            "id": cat_id,
            "name": name.strip(),
            "description": description.strip()
        })
        logger.info("Added new category: %s", name)
        return True

    def rename_category(self, cat_id: str, new_name: str) -> bool:
        for c in self.categories:
            if c.get("id") == cat_id:
                self._push_undo_snapshot()
                c["name"] = new_name.strip()
                logger.info("Renamed category %s to %s", cat_id, new_name)
                return True
        return False

    def delete_category(self, cat_id: str, reassign_category: str = "general") -> bool:
        self._push_undo_snapshot()
        self.categories = [c for c in self.categories if c.get("id") != cat_id]
        
        # Reassign wallpapers under deleted category to reassign_category
        for w in self.wallpapers:
            if w.get("category", "").lower() == cat_id.lower():
                w["category"] = reassign_category
        logger.info("Deleted category %s and reassigned wallpapers to %s", cat_id, reassign_category)
        return True

    # ----------------------------------------------------
    # COLLECTION OPERATIONS
    # ----------------------------------------------------
    def add_collection(self, col_id: str, name: str, description: str = "") -> bool:
        col_id = col_id.lower().strip()
        if any(col.get("id", "").lower() == col_id for col in self.collections):
            logger.warning("Collection '%s' already exists.", col_id)
            return False

        self._push_undo_snapshot()
        self.collections.append({
            "id": col_id,
            "name": name.strip(),
            "description": description.strip()
        })
        logger.info("Added new collection: %s", name)
        return True

    # ----------------------------------------------------
    # BULK OPERATIONS
    # ----------------------------------------------------
    def bulk_update(
        self,
        target_ids: List[str],
        category: Optional[str] = None,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
        add_collection: Optional[str] = None,
        remove_collection: Optional[str] = None,
        set_featured: Optional[bool] = None
    ) -> int:
        if not target_ids:
            return 0

        self._push_undo_snapshot()
        target_set = set(target_ids)
        count = 0

        for w in self.wallpapers:
            if w.get("id") in target_set:
                count += 1
                if category:
                    w["category"] = category
                
                # Tags Update
                cur_tags = list(w.get("tags", []))
                if add_tags:
                    for t in add_tags:
                        if t and t not in cur_tags:
                            cur_tags.append(t)
                if remove_tags:
                    cur_tags = [t for t in cur_tags if t not in remove_tags]
                w["tags"] = cur_tags

                # Collections Update
                cur_cols = list(w.get("collections", []))
                if add_collection and add_collection not in cur_cols:
                    cur_cols.append(add_collection)
                if remove_collection and remove_collection in cur_cols:
                    cur_cols.remove(remove_collection)
                w["collections"] = cur_cols

                # Featured Update
                if set_featured is not None:
                    w["isFeatured"] = set_featured
                    w["featured"] = set_featured

        logger.info("Bulk updated %d wallpapers.", count)
        return count

    # ----------------------------------------------------
    # SEARCH & SORTING
    # ----------------------------------------------------
    def filter_and_sort(
        self,
        query: str = "",
        category_filter: str = "All",
        collection_filter: str = "All",
        featured_filter: Optional[bool] = None,
        sort_key: str = "Title",
        sort_reverse: bool = False
    ) -> List[Dict[str, Any]]:
        result = self.wallpapers.copy()

        # Query Search (Title, Filename, Category, Collection, Tags)
        if query.strip():
            q = query.lower().strip()
            filtered = []
            for w in result:
                title = w.get("title", "").lower()
                cat = w.get("category", "").lower()
                cols = " ".join(w.get("collections", [])).lower()
                tags = " ".join(w.get("tags", [])).lower()
                fn = Path(w.get("imagePath", "")).name.lower()
                
                if q in title or q in cat or q in cols or q in tags or q in fn:
                    filtered.append(w)
            result = filtered

        # Category Filter
        if category_filter and category_filter != "All":
            result = [w for w in result if w.get("category", "").lower() == category_filter.lower()]

        # Collection Filter
        if collection_filter and collection_filter != "All":
            result = [w for w in result if any(c.lower() == collection_filter.lower() for c in w.get("collections", []))]

        # Featured Filter
        if featured_filter is not None:
            result = [w for w in result if w.get("isFeatured", w.get("featured", False)) == featured_filter]

        # Sorting
        if sort_key == "Title":
            result.sort(key=lambda x: x.get("title", "").lower(), reverse=sort_reverse)
        elif sort_key == "Category":
            result.sort(key=lambda x: x.get("category", "").lower(), reverse=sort_reverse)
        elif sort_key == "Featured":
            result.sort(key=lambda x: x.get("isFeatured", False), reverse=not sort_reverse)
        elif sort_key == "ID":
            result.sort(key=lambda x: x.get("id", ""), reverse=sort_reverse)

        return result
