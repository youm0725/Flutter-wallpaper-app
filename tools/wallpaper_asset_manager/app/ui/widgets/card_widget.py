import customtkinter as ctk

class CardWidget(ctk.CTkFrame):
    """Reusable card container widget with modern styling."""
    
    def __init__(self, master, title: str, subtitle: str = "", **kwargs):
        super().__init__(master, corner_radius=8, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(fill="x")
        
        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self.header_frame,
                text=subtitle,
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray60"),
                anchor="w"
            )
            self.subtitle_label.pack(fill="x", pady=(2, 0))
            
        # Content container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 14))
        self.grid_rowconfigure(1, weight=1)
