import customtkinter as ctk
from app.ui.widgets.card_widget import CardWidget

class AboutView(ctk.CTkFrame):
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text="ℹ️ About Wallpaper Asset Manager",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        card = CardWidget(self, title="System Information", subtitle="Developer tooling specifications")
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        about_text = (
            "Wallpaper Asset Manager v1.0.0 (Phase T1 - Batch T1.1)\n\n"
            "• Purpose: Offline Wallpaper Asset Pipeline & Metadata Generator\n"
            "• GUI Framework: CustomTkinter (Python 3.12+)\n"
            "• Architecture: Clean MVC Modular Architecture\n"
            "• Configuration: TOML (config/config.toml)\n"
            "• Logging: Structured File & Console Logging (logs/app.log)\n"
            "• Target Application: Wallpaper Gallery Offline Flutter App\n\n"
            "Designed and built for high-performance offline mobile wallpaper curation."
        )
        
        info = ctk.CTkLabel(
            card.container,
            text=about_text,
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="nw"
        )
        info.pack(fill="both", expand=True, pady=10)
