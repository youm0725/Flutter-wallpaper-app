import os
import re
import gc
import time
from pathlib import Path
from typing import Tuple, Dict
from PIL import Image, ImageOps
from app.models.processing_task import ProcessingTask
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("ImageProcessingEngine")

QUALITY_PRESETS: Dict[str, int] = {
    "High": 90,
    "Balanced": 82,
    "Compact": 75
}

class ImageProcessingEngine:
    """Core image processing pipeline converting wallpapers to optimized WebP assets."""
    
    @staticmethod
    def clean_filename(raw_filename: str) -> str:
        """Converts filename to clean snake_case WebP name."""
        stem = Path(raw_filename).stem
        # Lowercase, replace spaces and dashes with underscores
        clean = stem.lower().strip()
        clean = re.sub(r'[\s\-]+', '_', clean)
        # Remove non-alphanumeric except underscores
        clean = re.sub(r'[^a-z0-9_]', '', clean)
        # Collapse multiple underscores
        clean = re.sub(r'_+', '_', clean).strip('_')
        if not clean:
            clean = "wallpaper"
        return f"{clean}.webp"

    @staticmethod
    def resolve_unique_path(target_dir: Path, filename: str) -> Path:
        """Appends -2, -3, -4 suffix if file already exists to prevent overwriting."""
        target_dir.mkdir(parents=True, exist_ok=True)
        candidate = target_dir / filename
        if not candidate.exists():
            return candidate

        stem = candidate.stem
        suffix = candidate.suffix
        counter = 2
        while True:
            new_candidate = target_dir / f"{stem}-{counter}{suffix}"
            if not new_candidate.exists():
                return new_candidate
            counter += 1

    @classmethod
    def process_wallpaper(
        cls,
        task: ProcessingTask,
        preset: str = "Balanced",
        max_width: int = 1440,
        max_height: int = 3200,
        thumb_width: int = 360,
        output_root: Path | None = None
    ) -> bool:
        """Executes full wallpaper processing pipeline on a candidate task."""
        start_time = time.time()
        task.status = "Processing"
        
        quality = QUALITY_PRESETS.get(preset, 82)
        base_output_dir = output_root or PathHelper.get_output_dir()
        
        category = task.category.lower().strip() if task.category else "general"
        full_dir = base_output_dir / "full" / category
        thumb_dir = base_output_dir / "thumbnails" / category

        input_path = task.imported_item.file_path
        clean_name = cls.clean_filename(task.imported_item.filename)

        full_output_path = cls.resolve_unique_path(full_dir, clean_name)
        thumb_output_path = cls.resolve_unique_path(thumb_dir, full_output_path.name)

        try:
            logger.info("Processing wallpaper: %s -> %s (Preset: %s, Q: %d)", input_path.name, full_output_path.name, preset, quality)

            # Open image copy (never touch original file in input/)
            with Image.open(input_path) as orig_img:
                # 1. Correct EXIF Orientation
                img = ImageOps.exif_transpose(orig_img)

                # 2. Color Mode Standardisation (RGB for WebP)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")

                # 3. Resize Full Wallpaper (Max 1440x3200, aspect ratio preserved, no stretch)
                orig_w, orig_h = img.size
                if orig_w > max_width or orig_h > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                # 4. Save Full WebP Wallpaper
                img.save(full_output_path, "WEBP", quality=quality, method=6)
                task.full_size_bytes = full_output_path.stat().st_size

                # 5. Generate Thumbnail (Width: 360px, aspect ratio preserved)
                cur_w, cur_h = img.size
                calc_h = int(cur_h * (thumb_width / cur_w)) if cur_w > 0 else 640
                
                thumb_img = img.copy()
                thumb_img.thumbnail((thumb_width, calc_h), Image.Resampling.LANCZOS)
                thumb_img.save(thumb_output_path, "WEBP", quality=min(quality, 80), method=6)
                task.thumb_size_bytes = thumb_output_path.stat().st_size

            # Update Task Record
            task.output_full_path = full_output_path
            task.output_thumb_path = thumb_output_path
            task.duration_seconds = round(time.time() - start_time, 2)
            task.status = "Completed"
            
            logger.info("Successfully processed %s in %.2fs. Full: %s (%d KB), Thumb: %s (%d KB)",
                        input_path.name, task.duration_seconds,
                        full_output_path.name, round(task.full_size_bytes / 1024),
                        thumb_output_path.name, round(task.thumb_size_bytes / 1024))

            return True

        except Exception as e:
            task.duration_seconds = round(time.time() - start_time, 2)
            task.status = "Failed"
            task.error_message = str(e)
            logger.error("Error processing wallpaper %s: %s", input_path, e, exc_info=True)
            return False
        finally:
            gc.collect()  # Release memory after processing each image
