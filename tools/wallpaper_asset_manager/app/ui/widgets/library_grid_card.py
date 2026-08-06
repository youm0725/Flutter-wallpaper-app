import customtkinter as ctk
from pathlib import Path
from typing import Dict, Any, Callable
from PIL import Image
from app.utils.path_helper import PathHelper

class LibraryGridCard(ctk.CTkFrame):
    """Grid card displaying a single wallpaper item in the Library Manager."""
    
    def __init__(
        self,
        master,
        wallpaper_data: Dict[str, Any],
        is_selected: bool,
        on_click: Callable[[str], None],
        on_toggle_featured: Callable[[str], None],
        **kwargs
    ):
        border_color = ("#3B82F6", "#3B82F6") if is_selected else ("gray75", "gray30")
        fg_color = ("#EFF6FF", "#1E293B") if is_selected else ("gray95", "gray17")
        
        super().__init__(
            master,
            corner_radius=8,
            border_width=2 if is_selected else 1,
            border_color=border_color,
            fg_color=fg_color,
            width=160,
            height=250,
            **kwargs
        )
        
        self.item_data = wallpaper_data
        self.on_click = on_click
        self.on_toggle_featured = on_toggle_featured
        
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)

        # Header Row: Category Badge + Featured Toggle Star Button
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=28)
        header_frame.pack(fill="x", padx=6, pady=(6, 2))
        
        cat_name = wallpaper_data.get("category", "General").capitalize()
        cat_label = ctk.CTkLabel(
            header_frame,
            text=cat_name,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            fg_color="#3B82F6",
            corner_radius=4,
            width=50,
            height=18
        )
        cat_label.pack(side="left")

        is_feat = wallpaper_data.get("isFeatured", wallpaper_data.get("featured", False))
        star_text = "★ Featured" if is_feat else "☆ Feature"
        star_color = "#F59E0B" if is_feat else ("gray40", "gray60")
        
        star_btn = ctk.CTkButton(
            header_frame,
            text=star_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=star_color,
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            width=65,
            height=18,
            command=lambda: self.on_toggle_featured(wallpaper_data.get("id", ""))
        )
        star_btn.pack(side="right")

        # Thumbnail Image Container
        img_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray14"), corner_radius=6)
        img_frame.pack(fill="both", expand=True, padx=6, pady=2)
        
        thumb_path_rel = wallpaper_data.get("thumbnailPath") or wallpaper_data.get("imagePath")
        img_ctk = self._load_thumb_ctk(thumb_path_rel)
        
        if img_ctk:
            img_label = ctk.CTkLabel(img_frame, image=img_ctk, text="")
        else:
            img_label = ctk.CTkLabel(
                img_frame,
                text="🖼️ No Image",
                font=ctk.CTkFont(size=11),
                text_color="gray50"
            )
        img_label.pack(fill="both", expand=True, padx=2, pady=2)

        # Footer Info: Title & Resolution / Size
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=6, pady=(2, 6))

        disp_title = wallpaper_data.get("title", "Untitled")
        if len(disp_title) > 18:
            disp_title = disp_title[:15] + "..."

        title_label = ctk.CTkLabel(
            footer_frame,
            text=disp_title,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x")

        res_sz = f"{wallpaper_data.get('resolution', '1080x1920')} • {wallpaper_data.get('fileSize', '')}"
        sub_label = ctk.CTkLabel(
            footer_frame,
            text=res_sz,
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        sub_label.pack(fill="x")

        # Bind Click Events
        w_id = wallpaper_data.get("id", "")
        for widget in (self, img_frame, img_label, footer_frame, title_label, sub_label):
            widget.bind("<Button-1>", lambda e: self.on_click(w_id))

    def _load_thumb_ctk(self, rel_path: str):
        if not rel_path:
            return None
        full_disk = PathHelper.get_workspace_root() / rel_path
        if not full_disk.exists():
            return None

        try:
            with Image.open(full_disk) as img:
                img_copy = img.copy()
                img_copy.thumbnail((160, 240), Image.Resampling.LANCZOS)
                return ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        except Exception:
            return None
