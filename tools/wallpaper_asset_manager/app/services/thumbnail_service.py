import concurrent.futures
from pathlib import Path
from typing import Dict, Tuple, Callable, Optional
from PIL import Image
import customtkinter as ctk
from app.core.logger import get_logger

logger = get_logger("ThumbnailService")

class ThumbnailService:
    """Service for asynchronous thumbnail and preview image generation."""
    
    def __init__(self, max_workers: int = 4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.cache: Dict[str, Tuple[ctk.CTkImage, ctk.CTkImage]] = {}

    def generate_thumbnails_async(
        self,
        file_path: Path,
        callback: Callable[[Path, Optional[ctk.CTkImage], Optional[ctk.CTkImage]], None]
    ) -> None:
        """Submits thumbnail generation task to background worker pool."""
        self.executor.submit(self._process_image, file_path, callback)

    def _process_image(
        self,
        file_path: Path,
        callback: Callable[[Path, Optional[ctk.CTkImage], Optional[ctk.CTkImage]], None]
    ) -> None:
        try:
            path_key = str(file_path)
            if path_key in self.cache:
                thumb_ctk, preview_ctk = self.cache[path_key]
                callback(file_path, thumb_ctk, preview_ctk)
                return

            with Image.open(file_path) as img:
                # Convert RGBA to RGB for JPEG/WEBP safety if needed
                if img.mode in ("RGBA", "P"):
                    img_rgb = img.convert("RGBA")
                else:
                    img_rgb = img.convert("RGB")

                # Generate Grid Thumbnail (120x180 thumbnail aspect ratio)
                thumb_img = img_rgb.copy()
                thumb_img.thumbnail((160, 240), Image.Resampling.LANCZOS)
                thumb_ctk = ctk.CTkImage(light_image=thumb_img, dark_image=thumb_img, size=thumb_img.size)

                # Generate Preview Panel Image (300x480)
                preview_img = img_rgb.copy()
                preview_img.thumbnail((320, 480), Image.Resampling.LANCZOS)
                preview_ctk = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=preview_img.size)

                self.cache[path_key] = (thumb_ctk, preview_ctk)
                callback(file_path, thumb_ctk, preview_ctk)
        except Exception as e:
            logger.warning("Failed to generate thumbnail for %s: %s", file_path, e)
            callback(file_path, None, None)

    def shutdown(self):
        self.executor.shutdown(wait=False)
