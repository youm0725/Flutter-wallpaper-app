import sys
import traceback
import time
from pathlib import Path
from tkinter import messagebox
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("CrashHandler")

class CrashHandler:
    """Global crash handler catching unhandled exceptions and generating crash reports."""
    
    @staticmethod
    def setup_crash_handler(app_instance=None):
        def _handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.critical("Unhandled Exception caught by CrashHandler:\n%s", err_msg)
            
            report_file = CrashHandler.create_crash_report(exc_type, exc_value, err_msg)
            
            try:
                messagebox.showerror(
                    "Wallpaper Asset Manager - Unexpected Error",
                    f"An unexpected error occurred.\n\nA crash report has been saved to:\n{report_file}\n\nError: {exc_value}"
                )
            except Exception:
                pass

        sys.excepthook = _handle_exception

    @staticmethod
    def create_crash_report(exc_type, exc_value, traceback_str: str) -> Path:
        reports_dir = PathHelper.get_logs_dir() / "crash_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"crash_{timestamp}.txt"
        
        content = [
            "==========================================================",
            "WALLPAPER ASSET MANAGER — CRASH REPORT",
            "==========================================================",
            f"Date & Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Python Version: {sys.version.split()[0]} ({sys.platform})",
            f"Exception Type: {exc_type.__name__}",
            f"Exception Message: {exc_value}",
            "",
            "STACK TRACE:",
            traceback_str,
            "=========================================================="
        ]
        
        report_file.write_text("\n".join(content), encoding="utf-8")
        return report_file
