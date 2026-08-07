import customtkinter as ctk
from pathlib import Path
from app.ui.sidebar import Sidebar
from app.ui.status_bar import StatusBar
from app.ui.menu_bar import MenuBar
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.import_view import ImportView
from app.ui.views.process_view import ProcessView
from app.ui.views.delete_wallpapers_view import DeleteWallpapersView
from app.ui.views.validation_view import ValidationView
from app.ui.views.sync_view import SyncView
from app.ui.views.backup_view import BackupView
from app.ui.views.settings_view import SettingsView
from app.ui.views.logs_view import LogsView
from app.ui.views.about_view import AboutView
from app.core.crash_handler import CrashHandler
from app.core.logger import get_logger

logger = get_logger("MainWindow")

class MainWindow(ctk.CTk):
    """Main desktop application window container."""
    
    def __init__(self, app_service):
        super().__init__()
        self.service = app_service
        
        # Setup Global Crash Handler
        CrashHandler.setup_crash_handler(self)

        # Apply Window Branding Title & Size
        self.title("Wallpaper Asset Manager - Desktop Developer Tool v1.0.0")
        
        geom = self.service.config_manager.get("ui", "window_geometry", "1280x820")
        self.geometry(geom)
        self.minsize(1080, 700)

        # Theme Initialization
        theme_mode = self.service.config_manager.get("app", "theme", "System")
        if theme_mode in ("Dark", "Light"):
            ctk.set_appearance_mode(theme_mode)

        # Configure Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Native Menu Bar Setup
        self.menu_bar = MenuBar(self, on_navigate=self.show_view, on_theme=self._change_theme)

        # Sidebar Component
        self.sidebar = Sidebar(self, on_navigate_callback=self.show_view, on_theme_callback=self._change_theme)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # View Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Status Bar Component
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Initialize Views
        self.views = {
            "Dashboard": DashboardView(self.container, self.service),
            "Import": ImportView(self.container, self.service),
            "Process": ProcessView(self.container, self.service),
            "DeleteWallpapers": DeleteWallpapersView(self.container, self.service),
            "Validation": ValidationView(self.container, self.service),
            "Sync": SyncView(self.container, self.service),
            "Backups": BackupView(self.container, self.service),
            "Settings": SettingsView(self.container, self.service),
            "Logs": LogsView(self.container, self.service),
            "About": AboutView(self.container, self.service),
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        # Bind Global Keyboard Shortcuts
        self._bind_keyboard_shortcuts()

        # Load last active view
        last_view = self.service.config_manager.get("ui", "last_active_view", "Dashboard")
        self.show_view(last_view if last_view in self.views else "Dashboard")
        
        # Save geometry on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _bind_keyboard_shortcuts(self):
        self.bind("<Control-i>", lambda e: self.sidebar._on_nav_click("Import"))
        self.bind("<Control-s>", lambda e: self.sidebar._on_nav_click("Sync"))
        self.bind("<Control-b>", lambda e: self.sidebar._on_nav_click("Backups"))
        self.bind("<Control-r>", lambda e: self.sidebar._on_nav_click("Validation"))
        self.bind("<Control-f>", lambda e: self._focus_search_shortcut())

    def _focus_search_shortcut(self):
        active_name = self.sidebar.active_view_name
        if active_name == "Import" and hasattr(self.views["Import"], "search_entry"):
            self.views["Import"].search_entry.focus_set()

    def _change_theme(self, mode: str):
        ctk.set_appearance_mode(mode)
        self.service.config_manager.set("app", "theme", mode)

    def show_view(self, view_name: str):
        if view_name in self.views:
            view = self.views[view_name]
            view.lift()
            if hasattr(view, "refresh_library_grid"):
                view.refresh_library_grid()
            elif hasattr(view, "refresh_data"):
                view.refresh_data()
            self.status_bar.set_status(f"Active View: {view_name}")
            self.sidebar.set_active(view_name)
            self.service.config_manager.set("ui", "last_active_view", view_name)

    def _on_close(self):
        try:
            geom = self.geometry()
            self.service.config_manager.set("ui", "window_geometry", geom)
        except Exception:
            pass
        self.destroy()
