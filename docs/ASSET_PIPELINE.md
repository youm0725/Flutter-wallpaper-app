# Wallpaper Gallery — Production Asset Pipeline Guide

This document defines the production asset processing, validation, WebP optimization, and metadata generation pipeline for the Wallpaper Gallery project.

---

## 1. Directory Architecture

The asset pipeline maintains a strict separation between source wallpapers and production app assets:

```text
wallpaper_app/
├── assets/
│   ├── metadata/
│   │   ├── categories.json
│   │   ├── collections.json
│   │   └── wallpapers.json
│   └── wallpapers/           <-- Production WebP files only (consumed by Flutter)
│
└── tools/wallpaper_asset_manager/
    ├── app/                  <-- Desktop PyCustomTkinter Application
    │   ├── services/         <-- Validation, Library, Import, Image Engine
    │   ├── ui/               <-- Metadata, Import, Delete, Settings Views
    │   └── utils/
    ├── config/               <-- App configuration (config.toml)
    ├── dist/                 <-- Standalone executable (WallpaperAssetManager.exe)
    ├── logs/                 <-- Validation & Size audit reports
    └── output/               <-- Temporary staging output
```

---

## 2. Production Asset Processing Steps

### Step 1: Placing Source Wallpapers
- Place incoming source images (JPG, PNG, WebP) into a temporary folder or import directly via the **Asset Manager Desktop Tool**.

### Step 2: Running Asset Manager
- Launch the standalone GUI tool:
  ```powershell
  tools/wallpaper_asset_manager/dist/WallpaperAssetManager/WallpaperAssetManager.exe
  ```
  Or run via Python:
  ```powershell
  cd tools/wallpaper_asset_manager
  python main.py
  ```

### Step 3: Image Validation Rules
The Asset Manager automatically enforces strict validation:
1. **Vertical Aspect Ratio Enforcement**:
   - Only vertical portrait images (`height > width`) are accepted.
   - Any horizontal image (`width >= height`) is automatically rejected and logged.
2. **Format & Integrity Check**:
   - Corrupt files, 0-byte images, and unsupported formats are rejected.
3. **Duplicate Detection**:
   - Identical image content is detected via SHA-256 hashing to prevent duplicate wallpapers.

### Step 4: Production WebP Conversion
- Every approved image is converted into a high-quality, size-optimized WebP file (`.webp`).
- No duplicate format files (PNG/JPG) are placed into production assets.

### Step 5: ID & Metadata Generation
- Wallpapers are assigned stable, deterministic IDs (e.g., `nature_001`, `abstract_002`).
- Minimal offline metadata is written to `assets/metadata/wallpapers.json`:
  - `id`: Unique wallpaper string.
  - `title`: Human-readable title.
  - `category`: Assigned category ID.
  - `imagePath`: Relative Flutter asset path (`assets/wallpapers/<id>.webp`).

### Step 6: Size Budget & Health Reporting
- Target total library size budget for 250–500 wallpapers: **Under 200 MB**.
- Configurable per-file warning threshold: `500 KB`.

---

## 3. Validation & Verification Commands

- To validate Flutter assets:
  ```powershell
  flutter analyze
  ```
- To build release binaries:
  ```powershell
  flutter build apk --release ; flutter build appbundle --release
  ```
