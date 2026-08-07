# Wallpaper Gallery — Production Asset Compression Policy

This document details the production compression rules, resolution constraints, WebP quality presets, file size targets, and library size budget for the Wallpaper Gallery application.

---

## 1. Primary Compression Principles

- **Single Asset Architecture**: Every wallpaper exists as exactly **one** production WebP asset (`.webp`) inside `assets/wallpapers/`.
- **Proportional Lanczos Scaling**: Images exceeding maximum display dimensions are resized using Lanczos resampling while preserving 100% of the original aspect ratio (`height > width`). Wallpapers are **never** stretched or cropped.
- **Lossy WebP Preset**: Default preset is `Balanced` (`quality=82`, `method=6`). Provides optimal visual fidelity on high-density smartphone screens while keeping average file size ~150–250 KB.
- **No Metadata Overhead**: The app directly discovers `.webp` wallpapers from Flutter's `AssetManifest`. JSON metadata is no longer required.

---

## 2. Technical Parameters

| Configuration | Default Setting | Rationale |
| :--- | :--- | :--- |
| **Max Dimensions** | `1440x3200` | Supports modern QHD+/4K smartphone viewports cleanly without bloated pixel counts. |
| **Aspect Ratio Policy** | Vertical Portrait (`height > width`) | Rejects horizontal/landscape images to guarantee seamless wallpaper rendering. |
| **WebP Quality Preset** | `Balanced` (`Q=82`) | Optimal visual quality with zero perceptible compression artifacts. |
| **Warning Threshold** | `500 KB` | Triggers a warning if an uncommonly complex image exceeds 500 KB. |
| **Hard Size Threshold** | `1000 KB (1 MB)` | Requires manual review for any single wallpaper exceeding 1 MB. |
| **Library Target Budget**| `< 200 MB` | Keeps a 500-wallpaper offline library well within Play Store & App Store size limits. |

---

## 3. Library Size Projections (250–500 Wallpapers)

Based on an average production WebP size of **~200 KB**:

| Wallpaper Count | Projected Total Library Size | Safety Margin vs 200 MB Target |
| :--- | :--- | :--- |
| **250 Wallpapers** | ~50.0 MB | **+150.0 MB (75% Under Target)** |
| **300 Wallpapers** | ~60.0 MB | **+140.0 MB (70% Under Target)** |
| **350 Wallpapers** | ~70.0 MB | **+130.0 MB (65% Under Target)** |
| **400 Wallpapers** | ~80.0 MB | **+120.0 MB (60% Under Target)** |
| **450 Wallpapers** | ~90.0 MB | **+110.0 MB (55% Under Target)** |
| **500 Wallpapers** | ~100.0 MB | **+100.0 MB (50% Under Target)** |

---

## 4. Asset Manager Tool Workflow

1. Place raw source images into `tools/wallpaper_asset_manager/input/`.
2. Run Asset Manager or launch GUI tool:
   ```powershell
   python tools/wallpaper_asset_manager/main.py
   ```
3. Process wallpapers using `Balanced` preset. Optimized WebP assets are output into `assets/wallpapers/`.
4. Flutter automatically discovers and renders all WebP wallpapers dynamically at launch.
