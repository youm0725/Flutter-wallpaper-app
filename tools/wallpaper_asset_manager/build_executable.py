import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("WALLPAPER ASSET MANAGER - DESKTOP EXECUTABLE BUILDER")
    print("=" * 60)

    manager_root = Path(__file__).resolve().parent
    main_py = manager_root / "main.py"
    
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

    print(f"Running build command:\n{' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=manager_root)
    
    if res.returncode == 0:
        print("\n" + "=" * 60)
        print("✓ BUILD SUCCESSFUL! Standalone application created in:")
        print(f"{manager_root / 'dist' / 'WallpaperAssetManager'}")
        print("=" * 60)
    else:
        print("\nBuild failed with exit code:", res.returncode)

if __name__ == "__main__":
    main()
