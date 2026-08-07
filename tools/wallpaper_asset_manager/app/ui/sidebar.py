import customtkinter as ctk
from typing import Callable, Optional

class Sidebar(ctk.CTkFrame):
    """Sidebar navigation panel."""
    
    NAV_ITEMS = [
        ("Dashboard", "📊  Dashboard"),
        ("Import", "📥  Import"),
        ("Process", "⚡  Process"),
        ("Metadata", "🏷️  Metadata"),
        ("Validation", "✅  Validation"),
        ("Sync", "🔄  Sync"),
        ("Backups", "📦  Backups"),
        ("Settings", "⚙️  Settings"),
        ("Logs", "📜  Logs"),
        ("About", "ℹ️  About"),
    ]
    
    def __init__(
        self,
        master,
        on_navigate_callback: Optional[Callable[[str], None]] = None,
        on_theme_callback: Optional[Callable[[str], None]] = None,
        current_theme: str = "Dark",
        on_nav_change: Optional[Callable[[str], None]] = None,
        on_theme_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(master, width=210, corner_radius=0, **kwargs)
        
        self.on_navigate_callback = on_navigate_callback or on_nav_change or (lambda v: None)
        self.on_theme_callback = on_theme_callback or on_theme_change or (lambda t: None)
        self.buttons = {}
        self.active_nav = "Dashboard"
        
        self.grid_rowconfigure(len(self.NAV_ITEMS) + 1, weight=1)
        
        # App Title Logo Header
        title_label = ctk.CTkLabel(
            self,
            text="WALLPAPER\nASSET MANAGER",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            justify="left"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 20), sticky="ew")
        
        # Navigation Buttons
        for idx, (view_id, display_text) in enumerate(self.NAV_ITEMS, start=1):
            btn = ctk.CTkButton(
                self,
                text=display_text,
                font=ctk.CTkFont(size=13, weight="medium"),
                height=36,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda v=view_id: self._handle_click(v)
            )
            btn.grid(row=idx, column=0, padx=12, pady=3, sticky="ew")
            self.buttons[view_id] = btn

        # Theme Selector at Bottom
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.grid(row=len(self.NAV_ITEMS) + 2, column=0, padx=15, pady=20, sticky="ew")
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Appearance Mode:",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        theme_label.pack(anchor="w", pady=(0, 4))
        
        self.theme_option = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self._handle_theme_change,
            height=28
        )
        self.theme_option.set(current_theme)
        self.theme_option.pack(fill="x")

        # Set initial active state
        self.set_active("Dashboard")

    def _handle_click(self, view_id: str):
        self.set_active(view_id)
        self.on_navigate_callback(view_id)

    def _handle_theme_change(self, new_theme: str):
        self.on_theme_callback(new_theme)

    def _on_nav_click(self, view_id: str):
        self._handle_click(view_id)

    @property
    def active_view_name(self) -> str:
        return self.active_nav

    def set_active(self, view_id: str):
        self.active_nav = view_id
        for key, btn in self.buttons.items():
            if key == view_id:
                btn.configure(
                    fg_color=("gray75", "gray30"),
                    font=ctk.CTkFont(size=13, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    font=ctk.CTkFont(size=13, weight="medium")
                )
