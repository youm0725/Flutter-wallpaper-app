# Wallpaper Asset Manager — User Guide & Developer Manual

**Version 1.0.0**  
*Internal Developer Desktop Application for Flutter Wallpaper Gallery*

---

## Table of Contents
1. [Overview & Requirements](#1-overview--requirements)
2. [Installation & Launch](#2-installation--launch)
3. [Wallpaper Import Workflow (Batch T1.2)](#3-wallpaper-import-workflow)
4. [Image Processing Engine (Batch T1.3)](#4-image-processing-engine)
5. [Metadata & Wallpaper Library Manager (Batch T1.4)](#5-metadata--wallpaper-library-manager)
6. [Flutter Sync Engine (Batch T1.5)](#6-flutter-sync-engine)
7. [Release Validation & Quality Checker (Batch T1.6)](#7-release-validation--quality-checker)
8. [Dashboard & Analytics (Batch T1.7)](#8-dashboard--analytics)
9. [Backup & Restore System (Batch T1.8)](#9-backup--restore-system)
10. [Keyboard Shortcuts](#10-keyboard-shortcuts)
11. [Troubleshooting & Support](#11-troubleshooting--support)

---

## 1. Overview & Requirements
The **Wallpaper Asset Manager** is an offline desktop developer application built with Python 3.12+ and CustomTkinter. It lives inside the main repository under `tools/wallpaper_asset_manager/`.

- **Supported OS**: Windows 10/11, macOS, Linux
- **Python Dependencies**: `customtkinter`, `pillow`, `tomli-w`, `tkinterdnd2`

---

## 2. Installation & Launch

### Running from Python Source:
```bash
cd tools/wallpaper_asset_manager
python -m pip install -r requirements.txt
python main.py
```

### Building Windows Executable:
```bash
python build_executable.py
```
The standalone executable will be generated inside `tools/wallpaper_asset_manager/dist/`.

---

## 3. Wallpaper Import Workflow
- Click **Import Images** or **Import Folder**, or drag & drop `.jpg`, `.jpeg`, `.png`, or `.webp` files into the Drop Zone.
- The inspector side panel immediately verifies resolution, file readability, aspect ratio (9:16 mobile portrait), and duplicate filenames.

---

## 4. Image Processing Engine
- Converts raw source wallpapers into optimized `.webp` assets.
- Automatically handles **EXIF rotation** correction (`ImageOps.exif_transpose`).
- **Full Wallpaper**: Bounded to max `1440x3200` resolution (no stretching/cropping).
- **Thumbnail**: Scaled to `360px` proportional width.
- **Compression Presets**:
  - `High`: Quality 90
  - `Balanced`: Quality 82
  - `Compact`: Quality 75

---

## 5. Metadata & Wallpaper Library Manager
- Manages `wallpapers.json`, `categories.json`, and `collections.json` without requiring manual JSON editing.
- Automatic non-duplicating ID generator (e.g. `nature_01`, `cars_02`).
- Integrated **Undo / Redo** (`Ctrl+Z` / `↩️ Undo` / `↪️ Redo`) stack.
- Automated timestamped backup saved to `assets/metadata/backups/` before every JSON save.

---

## 6. Flutter Sync Engine
- Synchronizes processed WebP wallpapers and metadata JSON files into the main Flutter application (`assets/wallpapers/` & `assets/metadata/`).
- Performs a **Dry Run** preview calculation showing added, updated, and removed file counts and size delta MB.
- Creates pre-sync snapshots in `backups/sync_backups/`.

---

## 7. Release Validation & Quality Checker
- Audits wallpaper resolution, WebP readability, missing thumbnails, duplicate IDs, missing categories, and `pubspec.yaml` asset entries.
- Exports HTML, JSON, and Text reports in `logs/validation_reports/`.

---

## 8. Dashboard & Analytics
- Provides real-time metrics for total wallpapers, categories, collections, featured items, and total storage MB.
- Uses offline caching (`config/stats_cache.json`) for instant dashboard opening.

---

## 9. Backup & Restore System
- Stores full local repository snapshots under `backups/repository_backups/backup_[timestamp]`.
- Supports **Complete**, **Metadata Only**, **Assets Only**, and **Configuration Only** restore modes with automatic pre-restore emergency backups.

---

## 10. Keyboard Shortcuts
| Shortcut | Action |
|---|---|
| `Ctrl + I` | Jump to Import Manager View |
| `Ctrl + S` | Jump to Flutter Sync Engine View |
| `Ctrl + B` | Jump to Backup & Restore System |
| `Ctrl + R` | Jump to Release Validation View |
| `Ctrl + F` | Focus Search Input |

---

## 11. Troubleshooting & Support
- **Uncaught Exceptions**: Recorded in `logs/crash_reports/crash_[timestamp].txt`.
- **Application Logs**: Recorded in `logs/app.log`.
