# Wallpaper Asset Manager

A production-quality desktop application built with Python 3.12+ and CustomTkinter to manage, process, validate, and organize offline wallpaper assets for the Wallpaper Gallery application.

---

## 📌 Purpose
The **Wallpaper Asset Manager** is a specialized developer tool designed to automate asset management tasks before scaling the wallpaper library to 5,000+ items. It ensures clean category organization, WebP compression, thumbnail generation, and metadata validation without altering the Flutter codebase.

---

## 🛠️ Requirements
- Python **3.12+**
- `customtkinter` (Modern UI toolkit)
- `tomli-w` (TOML configuration serializer)

---

## 🚀 Installation & Running

1. **Navigate to the tool directory**:
   ```bash
   cd tools/wallpaper_asset_manager
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**:
   ```bash
   python main.py
   ```

---

## 📂 Project Architecture

```
tools/wallpaper_asset_manager/
├── app/
│   ├── core/           # Configuration manager and Logging setup
│   ├── models/         # App state models
│   ├── services/       # Core business logic services
│   ├── ui/             # Main window, sidebar, status bar, and menu bar
│   │   ├── views/      # Individual screen views (Dashboard, Import, Process, Settings, etc.)
│   │   └── widgets/    # Reusable custom UI components
│   └── utils/          # Path helpers and system utilities
├── config/             # TOML configuration file (config.toml)
├── assets/             # GUI icons and visual resources
├── logs/               # Application runtime log files
├── input/              # Source images to process
├── output/             # Processed WebP assets and thumbnails
├── main.py             # Application entry point
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

---

## 🗺️ Roadmap
- **Phase T1.1**: Project Foundation (MVC Structure, CustomTkinter UI, TOML Config, Logging)
- **Phase T1.2**: Image Import & Category Pipeline
- **Phase T1.3**: Automated WebP Compression & Thumbnail Generation
- **Phase T1.4**: Metadata Inspector & JSON Validator
