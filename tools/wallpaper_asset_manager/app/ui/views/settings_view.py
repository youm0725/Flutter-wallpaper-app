import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from app.ui.widgets.card_widget import CardWidget
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("SettingsView")

class SettingsView(ctk.CTkFrame):
    """Application Settings & Configuration Management View."""
    
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.cfg = self.service.config_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title Header
        title_label = ctk.CTkLabel(
            self,
            text="⚙️ Application Settings & Preferences",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Main Scrollable Form Container
        self.form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.form_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.form_scroll.columnconfigure(0, weight=1)

        self._build_settings_form()

    def _build_settings_form(self):
        # 1. UI Appearance Card
        card_ui = CardWidget(self.form_scroll, title="UI & Appearance", subtitle="Visual theme and window layout settings")
        card_ui.pack(fill="x", pady=8)

        row_theme = ctk.CTkFrame(card_ui.container, fg_color="transparent")
        row_theme.pack(fill="x", pady=6)
        ctk.CTkLabel(row_theme, text="Color Theme Mode:", font=ctk.CTkFont(weight="bold"), width=160, anchor="w").pack(side="left")
        
        cur_theme = self.cfg.get("app", "theme", "System")
        self.theme_option = ctk.CTkOptionMenu(
            row_theme,
            values=["System", "Dark", "Light"],
            command=self._on_theme_changed
        )
        self.theme_option.set(cur_theme)
        self.theme_option.pack(side="left")

        # 2. Workspace & Paths Card
        card_paths = CardWidget(self.form_scroll, title="Workspace & Repository Paths", subtitle="Target Flutter application location")
        card_paths.pack(fill="x", pady=8)

        row_path = ctk.CTkFrame(card_paths.container, fg_color="transparent")
        row_path.pack(fill="x", pady=6)
        ctk.CTkLabel(row_path, text="Repository Root Path:", font=ctk.CTkFont(weight="bold"), width=160, anchor="w").pack(side="left")
        
        self.path_entry = ctk.CTkEntry(row_path, width=380)
        self.path_entry.insert(0, str(PathHelper.get_workspace_root()))
        self.path_entry.pack(side="left", padx=5)

        # 3. Processing Defaults Card
        card_proc = CardWidget(self.form_scroll, title="Image Processing Defaults", subtitle="Default WebP quality & downscaling bounds")
        card_proc.pack(fill="x", pady=8)

        row_preset = ctk.CTkFrame(card_proc.container, fg_color="transparent")
        row_preset.pack(fill="x", pady=6)
        ctk.CTkLabel(row_preset, text="Default WebP Preset:", font=ctk.CTkFont(weight="bold"), width=160, anchor="w").pack(side="left")
        
        cur_preset = self.cfg.get("processing", "preset", "Balanced")
        self.preset_option = ctk.CTkOptionMenu(
            row_preset,
            values=["High (90)", "Balanced (82)", "Compact (75)"]
        )
        if cur_preset == "High": self.preset_option.set("High (90)")
        elif cur_preset == "Compact": self.preset_option.set("Compact (75)")
        else: self.preset_option.set("Balanced (82)")
        self.preset_option.pack(side="left")

        row_limit = ctk.CTkFrame(card_proc.container, fg_color="transparent")
        row_limit.pack(fill="x", pady=6)
        ctk.CTkLabel(row_limit, text="Size Warning Limit (MB):", font=ctk.CTkFont(weight="bold"), width=160, anchor="w").pack(side="left")
        
        self.limit_entry = ctk.CTkEntry(row_limit, width=120)
        self.limit_entry.insert(0, str(self.cfg.get("processing", "warning_limit_mb", 200.0)))
        self.limit_entry.pack(side="left")

        # Save Button
        btn_save = ctk.CTkButton(
            self.form_scroll,
            text="💾 Save Application Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            command=self._on_save_settings
        )
        btn_save.pack(anchor="w", pady=15)

    def _on_theme_changed(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)
        self.cfg.set("app", "theme", new_theme)

    def _on_save_settings(self):
        try:
            val_limit = float(self.limit_entry.get().strip())
            self.cfg.set("processing", "warning_limit_mb", val_limit)

            preset_str = self.preset_option.get()
            preset = "High" if "High" in preset_str else ("Compact" if "Compact" in preset_str else "Balanced")
            self.cfg.set("processing", "preset", preset)

            self.service.update_status("✓ Saved application configuration settings")
            messagebox.showinfo("Settings Saved", "Application configuration saved to config.toml successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed saving settings: {e}")
