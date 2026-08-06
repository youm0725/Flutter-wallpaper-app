import customtkinter as ctk
from typing import Optional
from app.models.imported_wallpaper import ImportedWallpaperItem
from app.ui.widgets.card_widget import CardWidget

class PreviewPanel(ctk.CTkFrame):
    """Side panel displaying full preview and metadata for active wallpaper."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, width=320, corner_radius=8, fg_color=("gray95", "gray17"), **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header Title
        title_label = ctk.CTkLabel(
            self,
            text="🖼️ Wallpaper Inspector",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        # Main Scrollable Details Container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        self.scroll_frame.columnconfigure(0, weight=1)

        # Large Image Container
        self.image_container = ctk.CTkFrame(self.scroll_frame, fg_color=("gray90", "gray14"), height=240, corner_radius=6)
        self.image_container.pack(fill="x", padx=4, pady=(0, 10))
        
        self.image_label = ctk.CTkLabel(
            self.image_container,
            text="No wallpaper selected",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        self.image_label.pack(fill="both", expand=True, padx=4, pady=4)

        # Metadata Card
        self.meta_card = CardWidget(self.scroll_frame, title="Image Attributes", subtitle="File & Resolution Metadata")
        self.meta_card.pack(fill="x", padx=4, pady=6)
        
        self.meta_labels = {}
        fields = [
            ("Filename", "filename"),
            ("Resolution", "resolution_str"),
            ("Aspect Ratio", "aspect_ratio_str"),
            ("File Size", "file_size_formatted"),
            ("Format", "extension"),
            ("Created Date", "creation_date_str"),
        ]
        
        for label_text, key in fields:
            row = ctk.CTkFrame(self.meta_card.container, fg_color="transparent")
            row.pack(fill="x", pady=3)
            
            lbl = ctk.CTkLabel(row, text=f"{label_text}:", font=ctk.CTkFont(size=11, weight="bold"), width=95, anchor="w")
            lbl.pack(side="left")
            
            val_lbl = ctk.CTkLabel(row, text="-", font=ctk.CTkFont(size=11), text_color=("gray30", "gray70"), anchor="w")
            val_lbl.pack(side="left", fill="x", expand=True)
            self.meta_labels[key] = val_lbl

        # Validation Card
        self.val_card = CardWidget(self.scroll_frame, title="Validation Status", subtitle="Integrity & Resolution Checks")
        self.val_card.pack(fill="x", padx=4, pady=6)
        
        self.val_status_label = ctk.CTkLabel(
            self.val_card.container,
            text="Status: Pending",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.val_status_label.pack(fill="x", pady=(0, 4))
        
        self.val_msg_label = ctk.CTkLabel(
            self.val_card.container,
            text="Select a wallpaper to inspect validation status.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            justify="left",
            anchor="nw",
            wraplength=270
        )
        self.val_msg_label.pack(fill="both", expand=True)

    def set_wallpaper_item(self, item: Optional[ImportedWallpaperItem]):
        if not item:
            self.image_label.configure(image=None, text="No wallpaper selected")
            for lbl in self.meta_labels.values():
                lbl.configure(text="-")
            self.val_status_label.configure(text="Status: Idle", text_color="gray50")
            self.val_msg_label.configure(text="No wallpaper selected.")
            return

        # Large Preview Image
        if item.preview_ctk:
            self.image_label.configure(image=item.preview_ctk, text="")
        elif item.thumbnail_ctk:
            self.image_label.configure(image=item.thumbnail_ctk, text="")
        else:
            self.image_label.configure(image=None, text="🖼️ Generating preview...")

        # Update Metadata Labels
        self.meta_labels["filename"].configure(text=item.filename)
        self.meta_labels["resolution_str"].configure(text=item.resolution_str)
        self.meta_labels["aspect_ratio_str"].configure(text=item.aspect_ratio_str)
        self.meta_labels["file_size_formatted"].configure(text=item.file_size_formatted)
        self.meta_labels["extension"].configure(text=item.extension.upper())
        self.meta_labels["creation_date_str"].configure(text=item.creation_date_str)

        # Update Validation Status
        if item.validation_status == "Valid":
            self.val_status_label.configure(text="✓ Status: Valid", text_color="#10B981")
        elif item.validation_status == "Warning":
            self.val_status_label.configure(text="⚠ Status: Warning", text_color="#F59E0B")
        else:
            self.val_status_label.configure(text="❌ Status: Error / Corrupted", text_color="#EF4444")

        msg_text = "\n".join(f"• {m}" for m in item.validation_messages) if item.validation_messages else "✓ All checks passed cleanly."
        self.val_msg_label.configure(text=msg_text)
