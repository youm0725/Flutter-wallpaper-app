import customtkinter as ctk
from app.ui.widgets.card_widget import CardWidget
from app.utils.path_helper import PathHelper

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Page Title Header
        title_label = ctk.CTkLabel(
            self,
            text="📊 Asset Manager Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 10))
        
        # Summary Cards Grid
        card1 = CardWidget(self, title="Wallpaper Library", subtitle="Current offline asset counts")
        card1.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        
        c1_content = ctk.CTkLabel(
            card1.container,
            text="• Total Wallpapers: 20 WebP files\n• Categories: 9 Categories\n• Architecture: Scalable 2-Tier (Full + Thumb)\n• Target Scalability: 5,000+ Wallpapers",
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="nw"
        )
        c1_content.pack(fill="both", expand=True, pady=10)

        card2 = CardWidget(self, title="Workspace Overview", subtitle="Target Flutter Project Location")
        card2.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        
        c2_content = ctk.CTkLabel(
            card2.container,
            text=f"• Root Directory:\n  {PathHelper.get_workspace_root()}\n\n• Metadata Location:\n  assets/metadata/wallpapers.json\n\n• Assets Directory:\n  assets/wallpapers/",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="nw"
        )
        c2_content.pack(fill="both", expand=True, pady=10)
        
        # Quick Actions Card
        card3 = CardWidget(self, title="System Pipeline Status", subtitle="Foundation Phase T1.1 Active")
        card3.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=(10, 20))
        
        status_info = ctk.CTkLabel(
            card3.container,
            text="✓ Project foundation initialized cleanly with CustomTkinter GUI & MVC Architecture.\n✓ Configuration manager initialized (config/config.toml).\n✓ Logging system active (logs/app.log).\n✓ Ready for image processing and metadata generation modules.",
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w"
        )
        status_info.pack(fill="both", expand=True, pady=8)
