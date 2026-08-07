import customtkinter as ctk
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from tkinter import messagebox
from PIL import Image

from app.services.metadata_service import MetadataService
from app.services.history_service import HistoryService
from app.services.library_service import LibraryService
from app.ui.widgets.card_widget import CardWidget
from app.core.logger import get_logger

logger = get_logger("DeleteWallpapersView")

class DeleteWallpapersView(ctk.CTkFrame):
    """Dedicated Wallpaper Deletion View allowing single or bulk wallpaper removal without modifying categories."""

    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.service = service
        self.metadata_service = getattr(service, "metadata_service", None) or MetadataService()
        self.history_service = getattr(service, "history_service", None) or HistoryService()
        self.library_service = getattr(service, "library_service", None) or LibraryService(self.metadata_service, self.history_service)

        self.selected_ids: Set[str] = set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------------------------------------------
        # TOP TOOLBAR & HEADER
        # ----------------------------------------------------
        self.toolbar = ctk.CTkFrame(self, height=54, corner_radius=6)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        # Title & Count
        self.lbl_title = ctk.CTkLabel(
            self.toolbar,
            text="🗑️ Delete Wallpapers",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.lbl_title.pack(side="left", padx=12, pady=10)

        # Action Buttons
        self.btn_delete_selected = ctk.CTkButton(
            self.toolbar,
            text="🗑️ Delete Selected (0)",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._on_delete_selected
        )
        self.btn_delete_selected.pack(side="left", padx=10, pady=10)

        self.btn_select_all = ctk.CTkButton(
            self.toolbar,
            text="☑️ Select All",
            width=90,
            fg_color=("gray75", "gray30"),
            command=self._on_select_all
        )
        self.btn_select_all.pack(side="left", padx=4, pady=10)

        self.btn_clear_sel = ctk.CTkButton(
            self.toolbar,
            text="☐ Clear",
            width=70,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._on_clear_selection
        )
        self.btn_clear_sel.pack(side="left", padx=4, pady=10)

        # Right Controls: Category Filter & Search
        self.search_entry = ctk.CTkEntry(
            self.toolbar,
            placeholder_text="🔍 Search wallpapers...",
            width=200
        )
        self.search_entry.pack(side="right", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        self.cat_filter_option = ctk.CTkOptionMenu(
            self.toolbar,
            values=["All"],
            width=130,
            command=lambda v: self.refresh_data()
        )
        self.cat_filter_option.pack(side="right", padx=4, pady=10)

        # ----------------------------------------------------
        # MAIN GRID AREA
        # ----------------------------------------------------
        self.scroll_grid = ctk.CTkScrollableFrame(self, corner_radius=6)
        self.scroll_grid.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.scroll_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def refresh_data(self):
        """Reloads wallpaper library and updates category dropdown and grid cards."""
        self.library_service.reload_all()

        cat_ids = [c.get("id", "") for c in self.library_service.categories]
        cur_cat = self.cat_filter_option.get()
        self.cat_filter_option.configure(values=["All"] + cat_ids)
        if cur_cat in ["All"] + cat_ids:
            self.cat_filter_option.set(cur_cat)
        else:
            self.cat_filter_option.set("All")

        # Clear existing grid widgets
        for widget in self.scroll_grid.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip()
        cat_filter = self.cat_filter_option.get()

        wallpapers = self.library_service.filter_and_sort(
            query=query,
            category=cat_filter if cat_filter != "All" else None
        )

        if not wallpapers:
            empty_lbl = ctk.CTkLabel(
                self.scroll_grid,
                text="No wallpapers found to delete.",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray50")
            )
            empty_lbl.grid(row=0, column=0, columnspan=4, pady=60)
            self._update_delete_button_text()
            return

        for idx, w in enumerate(wallpapers):
            row = idx // 4
            col = idx % 4

            w_id = w.get("id", "")
            title = w.get("title", w_id)
            cat = w.get("category", "")
            rel_path = w.get("imagePath", "")
            full_path = self.metadata_service.workspace_root / rel_path

            card = ctk.CTkFrame(self.scroll_grid, corner_radius=8, border_width=1, border_color=("gray80", "gray30"))
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Selection Checkbox
            chk_var = ctk.BooleanVar(value=(w_id in self.selected_ids))
            chk = ctk.CTkCheckBox(
                card,
                text="",
                variable=chk_var,
                width=24,
                command=lambda wid=w_id, var=chk_var: self._toggle_selection(wid, var.get())
            )
            chk.pack(anchor="nw", padx=8, pady=(8, 4))

            # Thumbnail placeholder or image
            img_lbl = ctk.CTkLabel(card, text="[No Image]", width=160, height=120)
            if full_path.exists():
                try:
                    with Image.open(full_path) as pil_img:
                        pil_img.thumbnail((160, 120))
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                        img_lbl.configure(image=ctk_img, text="")
                except Exception:
                    pass
            img_lbl.pack(padx=8, pady=4)

            # Details
            lbl_info = ctk.CTkLabel(
                card,
                text=f"{title}\nCategory: {cat}",
                font=ctk.CTkFont(size=11),
                justify="center"
            )
            lbl_info.pack(padx=8, pady=2)

            # Individual Delete Button
            btn_del = ctk.CTkButton(
                card,
                text="🗑️ Delete",
                height=26,
                fg_color="#EF4444",
                hover_color="#DC2626",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda wid=w_id, t=title: self._on_delete_single(wid, t)
            )
            btn_del.pack(padx=8, pady=(4, 8), fill="x")

        self._update_delete_button_text()

    def _toggle_selection(self, wallpaper_id: str, is_selected: bool):
        if is_selected:
            self.selected_ids.add(wallpaper_id)
        else:
            self.selected_ids.discard(wallpaper_id)
        self._update_delete_button_text()

    def _on_select_all(self):
        query = self.search_entry.get().strip()
        cat_filter = self.cat_filter_option.get()
        wallpapers = self.library_service.filter_and_sort(
            query=query,
            category=cat_filter if cat_filter != "All" else None
        )
        for w in wallpapers:
            if w.get("id"):
                self.selected_ids.add(w["id"])
        self.refresh_data()

    def _on_clear_selection(self):
        self.selected_ids.clear()
        self.refresh_data()

    def _update_delete_button_text(self):
        count = len(self.selected_ids)
        self.btn_delete_selected.configure(text=f"🗑️ Delete Selected ({count})")

    def _on_delete_single(self, wallpaper_id: str, title: str):
        if messagebox.askyesno("Confirm Deletion", f"Permanently delete wallpaper '{title}' ({wallpaper_id})?\n\nThis will remove the wallpaper image file asset and app metadata. Category will NOT be deleted."):
            self.library_service.delete_wallpaper(wallpaper_id)
            self.selected_ids.discard(wallpaper_id)
            self.refresh_data()

    def _on_delete_selected(self):
        if not self.selected_ids:
            messagebox.showinfo("No Selection", "Please select at least one wallpaper to delete.")
            return

        count = len(self.selected_ids)
        if messagebox.askyesno("Confirm Bulk Deletion", f"Permanently delete {count} selected wallpapers?\n\nThis will remove all associated image files and app metadata entries. Categories will remain intact."):
            deleted = self.library_service.delete_wallpapers_bulk(list(self.selected_ids))
            self.selected_ids.clear()
            self.refresh_data()
            messagebox.showinfo("Deletion Complete", f"Successfully deleted {deleted} wallpapers from the app.")
