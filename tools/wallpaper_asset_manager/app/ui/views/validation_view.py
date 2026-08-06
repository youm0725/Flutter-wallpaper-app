import customtkinter as ctk
from app.ui.widgets.card_widget import CardWidget

class ValidationView(ctk.CTkFrame):
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text="✅ Asset & Schema Integrity Validator",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        card = CardWidget(self, title="Validation Suite", subtitle="Detect missing files, broken JSON paths, or orphaned WebP assets")
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        info = ctk.CTkLabel(
            card.container,
            text="[Placeholder Module]\n\nValidation suite will perform automated sanity checks to guarantee 100% offline asset availability.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        info.pack(fill="both", expand=True, pady=40)
