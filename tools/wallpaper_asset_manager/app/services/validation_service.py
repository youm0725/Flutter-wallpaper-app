import os
import time
from pathlib import Path
from typing import Tuple, List, Dict
from PIL import Image
from app.core.logger import get_logger

logger = get_logger("ValidationService")

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

class ValidationService:
    """Service providing image validation, resolution checking, and duplicate detection."""
    
    @staticmethod
    def validate_file(file_path: Path, existing_filenames: set = None) -> Tuple[bool, str, List[str], int, int, str, str, str]:
        """
        Validates an image file.
        Returns: (is_valid, validation_status, validation_messages, width, height, resolution_str, aspect_ratio_str, creation_date_str)
        """
        messages: List[str] = []
        status = "Valid"
        is_valid = True
        width, height = 0, 0
        res_str = "Unknown"
        aspect_str = "Unknown"
        creation_str = "Unknown"

        if not file_path.exists():
            return False, "Error", ["File does not exist on disk."], 0, 0, "Unknown", "Unknown", "Unknown"

        # Check creation date
        try:
            stat = file_path.stat()
            creation_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
        except Exception:
            creation_str = "Unknown"

        # Extension Check
        ext = file_path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return False, "Error", [f"Unsupported file format '{ext}'."], 0, 0, "Unknown", "Unknown", creation_str

        # Duplicate Filename Check
        if existing_filenames and file_path.name in existing_filenames:
            status = "Warning"
            messages.append(f"Duplicate filename '{file_path.name}' detected in import list.")

        # PIL Image Inspection
        try:
            with Image.open(file_path) as img:
                img.verify()  # Check for truncation or corruption

            with Image.open(file_path) as img:
                width, height = img.size
                res_str = f"{width}x{height}"
                
                # Aspect Ratio Calculation
                if height > 0:
                    ratio = width / height
                    if abs(ratio - (9/16)) < 0.05:
                        aspect_str = "9:16 (Mobile Portrait)"
                    elif abs(ratio - (16/9)) < 0.05:
                        aspect_str = "16:9 (Landscape)"
                    else:
                        aspect_str = f"{ratio:.2f}:1"
                
                # Minimum Resolution Warning (Standard 1080x1920 mobile portrait)
                if width < 720 or height < 1280:
                    status = "Warning" if status != "Error" else "Error"
                    messages.append(f"Low resolution ({res_str}). Recommended minimum is 1080x1920.")
                
                # File Size Warning (> 15 MB)
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > 15.0:
                    status = "Warning" if status != "Error" else "Error"
                    messages.append(f"Large uncompressed file size ({size_mb:.1f} MB). Optimization recommended.")

        except Exception as e:
            logger.warning("Corrupted or unreadable image file %s: %s", file_path, e)
            return False, "Error", [f"Corrupted or unreadable image file: {e}"], 0, 0, "Corrupted", "Unknown", creation_str

        if not messages:
            messages.append("Image structure and resolution passed validation.")

        return is_valid, status, messages, width, height, res_str, aspect_str, creation_str
