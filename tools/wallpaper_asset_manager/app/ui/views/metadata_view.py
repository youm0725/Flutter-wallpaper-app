import customtkinter as ctk
from app.ui.widgets.card_widget import CardWidget

class MetadataView(ctk.CTkFrame):
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text="🏷️ Metadata Inspector & Editor",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        card = CardWidget(self, title="wallpapers.json Schema Editor", subtitle="Inspect and update wallpaper titles, tags, and category mappings")
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        info = ctk.CTkLabel(
            card.container,
            text="[Placeholder Module]\n\nMetadata view will provide a tabular grid editor to edit titles, tags, featured flags, and collections.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        info.pack(fill="both", expand=True, pady=40)
