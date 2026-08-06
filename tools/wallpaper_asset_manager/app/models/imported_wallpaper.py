from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from PIL import Image
import customtkinter as ctk

@dataclass
class ImportedWallpaperItem:
    """Model representing an imported wallpaper candidate before processing."""
    id: str
    file_path: Path
    filename: str
    extension: str
    file_size_bytes: int
    file_size_formatted: str
    width: int = 0
    height: int = 0
    resolution_str: str = "Unknown"
    aspect_ratio_str: str = "Unknown"
    creation_date_str: str = "Unknown"
    is_valid: bool = True
    validation_status: str = "Valid"  # "Valid", "Warning", "Error"
    validation_messages: List[str] = field(default_factory=list)
    is_selected: bool = False
    thumbnail_ctk: Optional[ctk.CTkImage] = None
    preview_ctk: Optional[ctk.CTkImage] = None
