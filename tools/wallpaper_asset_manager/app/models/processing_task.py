from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from app.models.imported_wallpaper import ImportedWallpaperItem

@dataclass
class ProcessingTask:
    """Model representing a single image processing job in the queue."""
    id: str
    imported_item: ImportedWallpaperItem
    category: str = "general"
    status: str = "Waiting"  # "Waiting", "Processing", "Completed", "Failed", "Paused"
    output_full_path: Optional[Path] = None
    output_thumb_path: Optional[Path] = None
    original_size_bytes: int = 0
    full_size_bytes: int = 0
    thumb_size_bytes: int = 0
    duration_seconds: float = 0.0
    error_message: str = ""
