import customtkinter as ctk
from app.services.app_service import AppService
from app.ui.sidebar import Sidebar
from app.ui.status_bar import StatusBar
from app.ui.menu_bar import MenuBar
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.import_view import ImportView
from app.ui.views.process_view import ProcessView
from app.ui.views.metadata_view import MetadataView
from app.ui.views.validation_view import ValidationView
from app.ui.views.settings_view import SettingsView
from app.ui.views.logs_view import LogsView
from app.ui.views.about_view import AboutView
from app.core.logger import get_logger

logger = get_logger("MainWindow")

class MainWindow(ctk.CTk):
    """Main desktop application window."""
    
    def __init__(self, service: AppService):
        super().__init__()
        
        self.service = service
        self.title("Wallpaper Asset Manager v1.0")
        self.geometry("1150x720")
        self.minsize(900, 600)
        
        # Apply initial saved theme
        saved_theme = self.service.state.theme_mode
        ctk.set_appearance_mode(saved_theme)
        
        # Grid Configuration (1 row for content, 1 row for status bar)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Native Menu Bar
        self.menu_bar = MenuBar(
            self,
            on_navigate=self.navigate_to,
            on_theme=self.change_theme
        )

        # Sidebar (Left)
        self.sidebar = Sidebar(
            self,
            on_navigate_callback=self.navigate_to,
            on_theme_callback=self.change_theme,
            current_theme=saved_theme
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Main Content Container (Center)
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Initialize Views Dictionary
        self.views = {
            "Dashboard": DashboardView(self.content_container, self.service),
            "Import": ImportView(self.content_container, self.service),
            "Process": ProcessView(self.content_container, self.service),
            "Metadata": MetadataView(self.content_container, self.service),
            "Validation": ValidationView(self.content_container, self.service),
            "Settings": SettingsView(self.content_container, self.service),
            "Logs": LogsView(self.content_container, self.service),
            "About": AboutView(self.content_container, self.service),
        }

        # Place all views into content container stack
        for view_frame in self.views.values():
            view_frame.grid(row=0, column=0, sticky="nsew")

        # Status Bar (Bottom)
        self.status_bar = StatusBar(
            self,
            project_path=self.service.state.project_path
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Display initial view
        self.navigate_to("Dashboard")
        logger.info("Main desktop window initialized successfully.")

    def navigate_to(self, view_id: str):
        """Switches the visible main view frame."""
        if view_id in self.views:
            target_view = self.views[view_id]
            target_view.lift()
            self.sidebar.set_active(view_id)
            self.status_bar.set_status(f"Active View: {view_id}")
            
            # Special case refresh for Logs view
            if view_id == "Logs" and hasattr(target_view, "reload_logs"):
                target_view.reload_logs()

            logger.info("Navigated to %s view.", view_id)

    def change_theme(self, theme_name: str):
        """Changes the UI appearance mode dynamically."""
        ctk.set_appearance_mode(theme_name)
        self.service.set_theme(theme_name)
        self.sidebar.theme_option.set(theme_name)
        self.status_bar.set_status(f"Theme set to {theme_name}")
