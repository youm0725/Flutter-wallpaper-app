import customtkinter as ctk
from typing import Callable
from app.models.imported_wallpaper import ImportedWallpaperItem

class ImportGridCard(ctk.CTkFrame):
    """Grid card representing an imported wallpaper item."""
    
    def __init__(
        self,
        master,
        item: ImportedWallpaperItem,
        is_active_preview: bool,
        on_select_click: Callable[[str], None],
        on_checkbox_toggle: Callable[[str, bool], None],
        **kwargs
    ):
        border_color = ("#3B82F6", "#3B82F6") if is_active_preview else ("gray75", "gray30")
        fg_color = ("#EFF6FF", "#1E293B") if is_active_preview else ("gray95", "gray17")
        
        super().__init__(
            master,
            corner_radius=8,
            border_width=2 if is_active_preview else 1,
            border_color=border_color,
            fg_color=fg_color,
            width=150,
            height=240,
            **kwargs
        )
        
        self.item = item
        self.on_select_click = on_select_click
        self.on_checkbox_toggle = on_checkbox_toggle
        
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)

        # Header Row: Checkbox + Validation Badge
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=28)
        header_frame.pack(fill="x", padx=6, pady=(6, 2))
        
        self.checkbox_var = ctk.BooleanVar(value=item.is_selected)
        self.checkbox = ctk.CTkCheckBox(
            header_frame,
            text="",
            variable=self.checkbox_var,
            width=20,
            height=20,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_check
        )
        self.checkbox.pack(side="left")

        # Validation status pill badge
        badge_color = "#10B981" if item.validation_status == "Valid" else ("#F59E0B" if item.validation_status == "Warning" else "#EF4444")
        badge_text = "✓ OK" if item.validation_status == "Valid" else ("⚠ Warn" if item.validation_status == "Warning" else "❌ Err")
        
        badge_label = ctk.CTkLabel(
            header_frame,
            text=badge_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            fg_color=badge_color,
            corner_radius=4,
            width=48,
            height=18
        )
        badge_label.pack(side="right")

        # Thumbnail Image Container
        img_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray14"), corner_radius=6)
        img_frame.pack(fill="both", expand=True, padx=6, pady=2)
        
        if item.thumbnail_ctk:
            img_label = ctk.CTkLabel(img_frame, image=item.thumbnail_ctk, text="")
        else:
            img_label = ctk.CTkLabel(
                img_frame,
                text="🖼️ Loading...",
                font=ctk.CTkFont(size=11),
                text_color="gray50"
            )
        img_label.pack(fill="both", expand=True, padx=2, pady=2)

        # Footer Info: Filename & Resolution / Size
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=6, pady=(2, 6))

        # Truncate filename if needed
        disp_name = item.filename
        if len(disp_name) > 18:
            disp_name = disp_name[:15] + "..."

        name_label = ctk.CTkLabel(
            footer_frame,
            text=disp_name,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x")

        sub_label = ctk.CTkLabel(
            footer_frame,
            text=f"{item.resolution_str} • {item.file_size_formatted}",
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        sub_label.pack(fill="x")

        # Bind Click events to select card
        for widget in (self, img_frame, img_label, footer_frame, name_label, sub_label):
            widget.bind("<Button-1>", lambda e: self.on_select_click(item.id))

    def _on_check(self):
        val = self.checkbox_var.get()
        self.item.is_selected = val
        self.on_checkbox_toggle(self.item.id, val)
