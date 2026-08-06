import customtkinter as ctk
from app.ui.widgets.card_widget import CardWidget

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.config_manager = service.config_manager
        
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text="⚙️ Preferences & Configuration",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Appearance Card
        theme_card = CardWidget(self, title="Appearance & UI Theme", subtitle="Choose application color scheme")
        theme_card.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        theme_row = ctk.CTkFrame(theme_card.container, fg_color="transparent")
        theme_row.pack(fill="x", pady=10)
        
        ctk.CTkLabel(theme_row, text="Theme Mode:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 15))
        
        current_theme = self.config_manager.get("app", "theme", "Dark")
        self.theme_menu = ctk.CTkOptionMenu(
            theme_row,
            values=["Dark", "Light", "System"],
            command=self._on_theme_changed
        )
        self.theme_menu.set(current_theme)
        self.theme_menu.pack(side="left")

        # Processing Settings Card
        proc_card = CardWidget(self, title="Compression & Image Quality Defaults", subtitle="Configure default WebP quality parameters")
        proc_card.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        q_full = str(self.config_manager.get("processing", "quality_full", 85))
        q_thumb = str(self.config_manager.get("processing", "quality_thumb", 75))
        
        proc_row1 = ctk.CTkFrame(proc_card.container, fg_color="transparent")
        proc_row1.pack(fill="x", pady=6)
        ctk.CTkLabel(proc_row1, text="Full Image WebP Quality (1-100):", width=220, anchor="w").pack(side="left")
        self.q_full_entry = ctk.CTkEntry(proc_row1, width=100)
        self.q_full_entry.insert(0, q_full)
        self.q_full_entry.pack(side="left", padx=10)

        proc_row2 = ctk.CTkFrame(proc_card.container, fg_color="transparent")
        proc_row2.pack(fill="x", pady=6)
        ctk.CTkLabel(proc_row2, text="Thumbnail WebP Quality (1-100):", width=220, anchor="w").pack(side="left")
        self.q_thumb_entry = ctk.CTkEntry(proc_row2, width=100)
        self.q_thumb_entry.insert(0, q_thumb)
        self.q_thumb_entry.pack(side="left", padx=10)
        
        # Save Button & Message
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="w", padx=20, pady=15)
        
        save_btn = ctk.CTkButton(
            btn_row,
            text="💾 Save Configuration",
            font=ctk.CTkFont(weight="bold"),
            command=self._save_settings
        )
        save_btn.pack(side="left")

        self.msg_label = ctk.CTkLabel(btn_row, text="", text_color="green", font=ctk.CTkFont(size=12))
        self.msg_label.pack(side="left", padx=15)

    def _on_theme_changed(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)
        self.service.set_theme(new_theme)

    def _save_settings(self):
        try:
            q_f = int(self.q_full_entry.get().strip())
            q_t = int(self.q_thumb_entry.get().strip())
            
            self.config_manager.set("processing", "quality_full", q_f)
            self.config_manager.set("processing", "quality_thumb", q_t)
            self.config_manager.save_config()
            
            self.msg_label.configure(text="✓ Settings saved to config.toml", text_color="green")
            self.service.update_status("Configuration saved successfully")
        except Exception as e:
            self.msg_label.configure(text=f"Error: {e}", text_color="red")
