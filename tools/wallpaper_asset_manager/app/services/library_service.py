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
        self.purge_horizontal_wallpapers()

        self.history_service.clear()
        self._push_undo_snapshot()
        logger.info("Library Service initialized with %d wallpapers, %d categories, %d collections.",
                    len(self.wallpapers), len(self.categories), len(self.collections))

    def purge_horizontal_wallpapers(self) -> int:
        """Scans all wallpapers on disk & metadata, purging any horizontal/landscape wallpapers (width >= height)."""
        from PIL import Image
        removed_count = 0
        valid_wallpapers = []

        for w in self.wallpapers:
            rel_path = w.get("imagePath", "")
            full_path = self.metadata_service.workspace_root / rel_path
            
            is_horizontal = False
            if full_path.exists():
                try:
                    with Image.open(full_path) as img:
                        w_px, h_px = img.size
                        if w_px >= h_px:
                            is_horizontal = True
                except Exception as e:
                    logger.warning("Could not inspect image %s: %s", full_path, e)
            
            if is_horizontal:
                removed_count += 1
                logger.info("Purging horizontal wallpaper: %s (%s)", w.get("id"), rel_path)
                try:
                    if full_path.exists():
                        full_path.unlink()
                except Exception as e:
                    logger.warning("Could not delete file %s: %s", full_path, e)
            else:
                valid_wallpapers.append(w)

        if removed_count > 0:
            self.wallpapers = valid_wallpapers
            self.metadata_service.save_wallpapers_json(self.wallpapers)
            logger.info("Purged %d horizontal wallpapers from library and disk.", removed_count)

        return removed_count

    def _auto_discover_disk_wallpapers(self):
        """Scans assets/wallpapers on disk, registers valid vertical WebP records, and purges dead missing file records."""
        from PIL import Image
        import time

        # 1. Purge dead metadata entries whose asset file does not exist
        valid_entries = []
        dead_found = False
        for w in self.wallpapers:
            rel_path = w.get("imagePath", "")
            if rel_path:
                full_path = self.metadata_service.workspace_root / rel_path
                if full_path.exists():
                    valid_entries.append(w)
                else:
                    dead_found = True
                    logger.info("Purging dead ghost metadata entry (file missing): %s (%s)", w.get("id"), rel_path)
            else:
                dead_found = True

        if dead_found:
            self.wallpapers = valid_entries
            self.metadata_service.save_wallpapers_json(self.wallpapers)

        # 2. Discover missing vertical WebP files in assets/wallpapers (recursively)
        wp_dir = self.metadata_service.workspace_root / "assets" / "wallpapers"
        if not wp_dir.exists():
            return

        new_found = False
        discovered_categories = set(c.get("id", "").lower() for c in self.categories)

        for webp_file in wp_dir.rglob("*.webp"):
            if webp_file.is_dir():
                continue

            # Check if vertical wallpaper (height > width)
            is_vertical = True
            try:
                with Image.open(webp_file) as img:
                    w_px, h_px = img.size
                    if w_px >= h_px:
                        is_vertical = False
            except Exception as e:
                logger.warning("Could not read image dimensions for %s: %s. Registering asset.", webp_file, e)

            if not is_vertical:
                logger.warning("Auto-discovery skipping horizontal image: %s", webp_file.name)
                continue

            filename = webp_file.name
            rel_full = str(webp_file.relative_to(self.metadata_service.workspace_root)).replace("\\", "/")

            already_exists = any(
                w.get("imagePath", "").endswith(filename) or
                w.get("id", "") == webp_file.stem
                for w in self.wallpapers
            )
            
            # Derive category from filename prefix e.g. "avatar_1.webp" -> "avatar"
            stem = webp_file.stem
            parts = re.split(r'[_\-]', stem)
            if parts and parts[0] and not parts[0].isdigit():
                cat_id = parts[0].lower()
            elif webp_file.parent != wp_dir:
                cat_id = webp_file.parent.name.lower()
            else:
                cat_id = "general"

            if cat_id not in discovered_categories:
                self.categories.append({
                    "id": cat_id,
                    "name": cat_id.capitalize(),
                    "description": f"{cat_id.capitalize()} wallpapers",
                    "icon": "folder"
                })
                discovered_categories.add(cat_id)

            if already_exists:
                # Update existing wallpaper category if missing
                for w in self.wallpapers:
                    if w.get("id", "") == webp_file.stem or w.get("imagePath", "").endswith(filename):
                        w["category"] = cat_id
                        w["imagePath"] = rel_full
                continue

            raw_title = stem.replace("_", " ").replace("-", " ").title()
            w_id = stem

            new_entry = {
                "id": w_id,
                "title": raw_title,
                "category": cat_id,
                "imagePath": rel_full,
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
        """Deletes wallpaper asset file from disk, removes metadata from wallpapers.json and collections.json while preserving category."""
        w = self.get_wallpaper_by_id(wallpaper_id)
        if not w:
            return False

        self._push_undo_snapshot()

        # 1. Remove asset file from disk
        rel_path = w.get("imagePath", "")
        if rel_path:
            full_path = self.metadata_service.workspace_root / rel_path
            try:
                if full_path.exists():
                    full_path.unlink()
                    logger.info("Deleted wallpaper file asset: %s", full_path)
            except Exception as e:
                logger.warning("Could not delete wallpaper file asset %s: %s", full_path, e)

        # 2. Remove entry from wallpapers list
        self.wallpapers = [item for item in self.wallpapers if item.get("id") != wallpaper_id]

        # 3. Remove wallpaper_id from collections metadata
        for col in self.collections:
            if "wallpaperIds" in col and isinstance(col["wallpaperIds"], list):
                col["wallpaperIds"] = [id_item for id_item in col["wallpaperIds"] if id_item != wallpaper_id]

        # 4. Save metadata to disk
        self.metadata_service.save_wallpapers_json(self.wallpapers)
        self.metadata_service.save_collections_json(self.collections)

        logger.info("Deleted wallpaper %s and all associated data. Category preserved.", wallpaper_id)
        return True

    def delete_wallpapers_bulk(self, wallpaper_ids: List[str]) -> int:
        """Bulk deletes multiple wallpapers, asset files, and collection entries while keeping categories untouched."""
        if not wallpaper_ids:
            return 0

        self._push_undo_snapshot()
        deleted_count = 0
        ids_to_delete = set(wallpaper_ids)

        # Delete asset files
        for w in self.wallpapers:
            if w.get("id") in ids_to_delete:
                rel_path = w.get("imagePath", "")
                if rel_path:
                    full_path = self.metadata_service.workspace_root / rel_path
                    try:
                        if full_path.exists():
                            full_path.unlink()
                    except Exception as e:
                        logger.warning("Could not delete file %s: %s", full_path, e)
                deleted_count += 1

        # Filter wallpapers list
        self.wallpapers = [w for w in self.wallpapers if w.get("id") not in ids_to_delete]

        # Filter collection links
        for col in self.collections:
            if "wallpaperIds" in col and isinstance(col["wallpaperIds"], list):
                col["wallpaperIds"] = [id_item for id_item in col["wallpaperIds"] if id_item not in ids_to_delete]

        # Save metadata to disk
        if deleted_count > 0:
            self.metadata_service.save_wallpapers_json(self.wallpapers)
            self.metadata_service.save_collections_json(self.collections)
            logger.info("Bulk deleted %d wallpapers. Categories preserved.", deleted_count)

        return deleted_count

    # ----------------------------------------------------
    # CATEGORY OPERATIONS
    # ----------------------------------------------------
    def add_category(self, cat_id: str, name: str, description: str = "", icon: str = "folder") -> bool:
        cat_id = cat_id.lower().strip()
        if any(c.get("id", "").lower() == cat_id for c in self.categories):
            logger.warning("Category '%s' already exists.", cat_id)
            return False

        self._push_undo_snapshot()
        self.categories.append({
            "id": cat_id,
            "name": name.strip(),
            "description": description.strip(),
            "icon": icon.strip() or "folder"
        })
        logger.info("Added new category: %s (%s)", name, cat_id)
        return True

    def update_category(
        self,
        old_id: str,
        new_name: str,
        new_description: str = "",
        new_icon: str = "folder",
        new_id: Optional[str] = None
    ) -> bool:
        old_id = old_id.lower().strip()
        target_category = None
        for c in self.categories:
            if c.get("id", "").lower() == old_id:
                target_category = c
                break

        if not target_category:
            logger.warning("Category '%s' not found for update.", old_id)
            return False

        self._push_undo_snapshot()
        target_category["name"] = new_name.strip()
        target_category["description"] = new_description.strip()
        target_category["icon"] = new_icon.strip() or "folder"

        if new_id and new_id.lower().strip() != old_id:
            clean_new_id = new_id.lower().strip()
            if any(c.get("id", "").lower() == clean_new_id for c in self.categories if c is not target_category):
                logger.warning("Cannot rename category ID to existing '%s'", clean_new_id)
            else:
                target_category["id"] = clean_new_id
                for w in self.wallpapers:
                    if w.get("category", "").lower() == old_id:
                        w["category"] = clean_new_id

        logger.info("Updated category %s: %s", old_id, new_name)
        return True

    def rename_category(self, cat_id: str, new_name: str) -> bool:
        return self.update_category(cat_id, new_name)

    def delete_category(self, cat_id: str, reassign_category: str = "general") -> bool:
        self._push_undo_snapshot()
        self.categories = [c for c in self.categories if c.get("id", "").lower() != cat_id.lower()]
        
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
