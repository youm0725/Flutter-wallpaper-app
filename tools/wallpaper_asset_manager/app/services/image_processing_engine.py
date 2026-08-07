import os
import re
import gc
import time
from pathlib import Path
from typing import Tuple, Dict, Optional
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
    """Core image processing pipeline V2 generating single optimized WebP assets per wallpaper."""
    
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
        output_root: Optional[Path] = None,
        single_asset_mode: bool = True,
        **kwargs
    ) -> bool:
        """Executes wallpaper processing pipeline generating optimized WebP asset."""
        start_time = time.time()
        task.status = "Processing"
        
        quality = QUALITY_PRESETS.get(preset, 82)
        base_output_dir = output_root or PathHelper.get_output_dir()
        
        # If output_root doesn't end with 'wallpapers', route into wallpapers subfolder
        if base_output_dir.name != "wallpapers":
            target_dir = base_output_dir / "wallpapers"
        else:
            target_dir = base_output_dir

        input_path = task.imported_item.file_path
        clean_name = cls.clean_filename(task.imported_item.filename)

        output_path = cls.resolve_unique_path(target_dir, clean_name)

        try:
            logger.info(
                "Processing wallpaper V2: %s -> %s (Preset: %s, Q: %d, Max: %dx%d)",
                input_path.name, output_path.name, preset, quality, max_width, max_height
            )

            # Open image copy (never touch original file in input/)
            with Image.open(input_path) as orig_img:
                # 1. Correct EXIF Orientation
                img = ImageOps.exif_transpose(orig_img)

                # 2. Color Mode Standardisation (RGB/RGBA for WebP)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")

                # 3. Enforce Vertical Wallpapers Requirement (height > width)
                orig_w, orig_h = img.size
                if orig_w >= orig_h:
                    raise ValueError(f"Horizontal image rejected ({orig_w}x{orig_h}). Only vertical (portrait) wallpapers (height > width) are allowed.")

                # 4. Image Quality Enhancement Pipeline (Upscaling, Detail Sharpening & Color Vibrance)
                from PIL import ImageFilter, ImageEnhance

                # A. Upscale lower-resolution images up to target QHD resolution (1440x3200) using Lanczos
                if orig_w < max_width and orig_h < max_height:
                    scale = min(max_width / orig_w, max_height / orig_h)
                    if scale > 1.0 and scale <= 2.5:
                        new_w = int(orig_w * scale)
                        new_h = int(orig_h * scale)
                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                elif orig_w > max_width or orig_h > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                # B. Unsharp Masking for crisp detail sharpening
                img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=2))

                # C. Selective Contrast Boost (+5%)
                contrast_enhancer = ImageEnhance.Contrast(img)
                img = contrast_enhancer.enhance(1.05)

                # D. Color Saturation Vibrance Boost (+8%)
                color_enhancer = ImageEnhance.Color(img)
                img = color_enhancer.enhance(1.08)

                # E. Sharpness Fine-Tuning (+15%)
                sharp_enhancer = ImageEnhance.Sharpness(img)
                img = sharp_enhancer.enhance(1.15)

                # 5. Save WebP format without lossy compression (100% quality)
                img.save(output_path, "WEBP", quality=100, lossless=True, method=6)
                task.full_size_bytes = output_path.stat().st_size
                task.thumb_size_bytes = task.full_size_bytes

            # Update Task Record
            task.output_full_path = output_path
            task.output_thumb_path = output_path
            task.duration_seconds = round(time.time() - start_time, 2)
            task.status = "Completed"
            
            orig_bytes = input_path.stat().st_size
            opt_bytes = task.full_size_bytes
            saved_bytes = max(0, orig_bytes - opt_bytes)
            saved_percent = round((saved_bytes / orig_bytes * 100), 1) if orig_bytes > 0 else 0.0

            logger.info(
                "Successfully processed %s in %.2fs. Original: %d KB, Optimized: %d KB (Saved %s%%)",
                input_path.name, task.duration_seconds,
                round(orig_bytes / 1024), round(opt_bytes / 1024), saved_percent
            )

            return True

        except Exception as e:
            task.duration_seconds = round(time.time() - start_time, 2)
            task.status = "Failed"
            task.error_message = str(e)
            logger.error("Error processing wallpaper %s: %s", input_path, e, exc_info=True)
            return False
        finally:
            gc.collect()  # Release memory after processing each image
