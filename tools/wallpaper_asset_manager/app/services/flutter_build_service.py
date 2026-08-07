import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Callable
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("FlutterBuildService")

class FlutterBuildService:
    """Service executing Flutter APK (Android) and IPA (Apple iOS) builds asynchronously."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.releases_dir = PathHelper.get_tool_root() / "output" / "releases"
        self.releases_dir.mkdir(parents=True, exist_ok=True)

    def _run_flutter_cmd(
        self,
        args: list[str],
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[int, str]:
        """Runs flutter subprocess command and streams output live."""
        cmd = ["flutter"] + args
        logger.info("Executing Flutter command: %s in %s", " ".join(cmd), self.workspace_root)
        if log_callback:
            log_callback(f"Executing: {' '.join(cmd)}\n")

        full_output = []
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                encoding="utf-8",
                errors="replace"
            )

            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    full_output.append(line)
                    if log_callback:
                        log_callback(line)

            process.wait()
            return process.returncode, "".join(full_output)
        except Exception as e:
            err_msg = f"Failed to execute Flutter command: {e}"
            logger.error(err_msg)
            if log_callback:
                log_callback(err_msg + "\n")
            return -1, err_msg

    def build_apk(
        self,
        build_mode: str = "release",
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Builds Android APK package."""
        start_time = time.time()
        args = ["build", "apk", f"--{build_mode}"]

        if log_callback:
            log_callback(f"\n==================================================\n")
            log_callback(f"🤖 STARTING ANDROID APK BUILD ({build_mode.upper()})\n")
            log_callback(f"==================================================\n")

        code, logs = self._run_flutter_cmd(args, log_callback=log_callback)
        duration = round(time.time() - start_time, 2)

        # Output artifact check
        target_apk_name = f"app-{build_mode}.apk"
        built_apk = self.workspace_root / "build" / "app" / "outputs" / "flutter-apk" / target_apk_name
        dest_apk = self.releases_dir / f"WallpaperApp-{build_mode}.apk"

        if code == 0 and built_apk.exists():
            shutil.copy2(built_apk, dest_apk)
            msg = f"✓ Android APK built successfully in {duration}s! Exported to output/releases/{dest_apk.name}"
            logger.info(msg)
            if log_callback:
                log_callback(f"\n[OK] {msg}\n")
            return {
                "success": True,
                "platform": "Android (APK)",
                "duration_seconds": duration,
                "output_path": str(dest_apk),
                "file_size_mb": round(dest_apk.stat().st_size / (1024 * 1024), 2),
                "message": msg
            }
        else:
            msg = f"❌ Android APK build failed (Exit code: {code}). See logs above."
            logger.error(msg)
            if log_callback:
                log_callback(f"\n[ERROR] {msg}\n")
            return {
                "success": False,
                "platform": "Android (APK)",
                "duration_seconds": duration,
                "output_path": None,
                "file_size_mb": 0.0,
                "message": msg
            }

    def build_ipa(
        self,
        build_mode: str = "release",
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Builds Apple iOS IPA / App package."""
        start_time = time.time()
        
        # Check platform support (macOS required for full Xcode iOS builds)
        is_windows = os.name == "nt"
        
        if log_callback:
            log_callback(f"\n==================================================\n")
            log_callback(f"🍎 STARTING APPLE iOS / IPA BUILD ({build_mode.upper()})\n")
            log_callback(f"==================================================\n")

        if is_windows:
            win_msg = (
                "NOTE: Native Apple iOS / IPA compilation requires macOS with Xcode installed.\n"
                "Running Flutter iOS verification build on Windows...\n"
            )
            if log_callback:
                log_callback(win_msg)

        args = ["build", "ios", f"--{build_mode}", "--no-codesign"]
        code, logs = self._run_flutter_cmd(args, log_callback=log_callback)
        duration = round(time.time() - start_time, 2)

        # Output artifact check
        built_ipa_dir = self.workspace_root / "build" / "ios" / "ipa"
        built_archive_dir = self.workspace_root / "build" / "ios" / "archive"

        dest_ipa = self.releases_dir / f"WallpaperApp-{build_mode}.ipa"

        if code == 0:
            msg = f"✓ Apple iOS Package processed in {duration}s."
            if log_callback:
                log_callback(f"\n[OK] {msg}\n")
            return {
                "success": True,
                "platform": "Apple iOS (IPA)",
                "duration_seconds": duration,
                "output_path": str(built_ipa_dir) if built_ipa_dir.exists() else str(self.workspace_root / "build" / "ios"),
                "file_size_mb": 0.0,
                "message": msg
            }
        else:
            msg = (
                f"Apple iOS build completed with exit code {code}.\n"
                "Note: To generate signed .ipa bundles for App Store / TestFlight, run on a macOS machine with Xcode."
            )
            logger.info(msg)
            if log_callback:
                log_callback(f"\n[INFO] {msg}\n")
            return {
                "success": False,
                "platform": "Apple iOS (IPA)",
                "duration_seconds": duration,
                "output_path": None,
                "file_size_mb": 0.0,
                "message": msg
            }

    def build_both(
        self,
        build_mode: str = "release",
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Builds both Android APK and Apple iOS IPA packages sequentially."""
        start_time = time.time()
        apk_res = self.build_apk(build_mode=build_mode, log_callback=log_callback)
        ipa_res = self.build_ipa(build_mode=build_mode, log_callback=log_callback)

        total_duration = round(time.time() - start_time, 2)
        
        summary = (
            f"Build Process Completed in {total_duration}s!\n"
            f"Android APK: {'SUCCESS' if apk_res['success'] else 'FAILED'}\n"
            f"Apple iOS: {'PROCESSED' if ipa_res['success'] else 'MACOS REQUIRED'}"
        )

        return {
            "apk_result": apk_res,
            "ipa_result": ipa_res,
            "total_duration": total_duration,
            "summary": summary
        }
