import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("WALLPAPER ASSET MANAGER - DESKTOP EXECUTABLE BUILDER")
    print("=" * 60)

    manager_root = Path(__file__).resolve().parent
    main_py = manager_root / "main.py"
    dist_dir = manager_root / "dist" / "WallpaperAssetManager"

    # Kill any running WallpaperAssetManager processes holding locks
    if sys.platform == "win32":
        try:
            subprocess.run(["taskkill", "/F", "/IM", "WallpaperAssetManager.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # Clean existing dist output
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print("\n[WARNING] Could not delete existing dist folder. Please close any open WallpaperAssetManager app windows or error dialogs before rebuilding.")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=WallpaperAssetManager",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--distpath={manager_root / 'dist'}",
        f"--workpath={manager_root / 'build'}",
        str(main_py)
    ]

    print(f"\nRunning build command:\n{' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=manager_root)
    
    if res.returncode == 0:
        print("\n" + "=" * 60)
        print("[OK] BUILD SUCCESSFUL! Standalone application created in:")
        print(f"{manager_root / 'dist' / 'WallpaperAssetManager'}")
        print("=" * 60)
    else:
        print("\n[ERROR] Build failed with exit code:", res.returncode)
        print("If the error is 'Access is denied', please close all open Wallpaper Asset Manager dialogs/windows and re-run.")

if __name__ == "__main__":
    main()
