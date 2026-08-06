import json
from pathlib import Path
from typing import List, Dict, Any
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("ChecklistManagerService")

DEFAULT_CHECKLIST = [
    {"id": "app_icon", "title": "App Icon verified & generated", "completed": True},
    {"id": "splash_screen", "title": "Splash screen configured", "completed": True},
    {"id": "version_bump", "title": "Version number updated in pubspec.yaml", "completed": True},
    {"id": "screenshots", "title": "Store screenshots generated (Portrait/Landscape)", "completed": False},
    {"id": "privacy_policy", "title": "Privacy policy URL updated", "completed": True},
    {"id": "release_notes", "title": "Release notes prepared", "completed": False},
    {"id": "store_desc", "title": "Store listing description verified", "completed": True}
]

class ChecklistManagerService:
    """Service managing developer release checklist states."""
    
    def __init__(self):
        self.checklist_path = PathHelper.get_config_dir() / "checklist.json"
        self.items: List[Dict[str, Any]] = self.load_checklist()

    def load_checklist(self) -> List[Dict[str, Any]]:
        if not self.checklist_path.exists():
            self.save_checklist(DEFAULT_CHECKLIST)
            return DEFAULT_CHECKLIST.copy()
        try:
            with open(self.checklist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else DEFAULT_CHECKLIST.copy()
        except Exception:
            return DEFAULT_CHECKLIST.copy()

    def save_checklist(self, items: List[Dict[str, Any]] = None) -> bool:
        to_save = items if items is not None else self.items
        try:
            with open(self.checklist_path, "w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=2)
            return True
        except Exception as e:
            logger.error("Failed saving checklist: %s", e)
            return False

    def toggle_item(self, item_id: str) -> bool:
        for item in self.items:
            if item.get("id") == item_id:
                item["completed"] = not item.get("completed", False)
                self.save_checklist()
                return True
        return False
