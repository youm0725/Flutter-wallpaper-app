import customtkinter as ctk
from pathlib import Path
from typing import Dict, Any, List, Optional
from tkinter import messagebox
from PIL import Image

from app.services.metadata_service import MetadataService
from app.services.history_service import HistoryService
from app.services.metadata_validation_service import MetadataValidationService
from app.services.library_service import LibraryService
from app.ui.widgets.card_widget import CardWidget
from app.ui.widgets.library_grid_card import LibraryGridCard
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("MetadataView")

class MetadataView(ctk.CTkFrame):
    """Complete Wallpaper Library Manager & Metadata Editor Screen View."""
    
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.metadata_service = MetadataService()
        self.history_service = HistoryService()
        self.library_service = LibraryService(self.metadata_service, self.history_service)
        
        self.selected_wallpaper_id: Optional[str] = None
        self.featured_only_filter: bool = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)  # Inspector Panel Fixed Width
        self.grid_rowconfigure(1, weight=1)

        # ----------------------------------------------------
        # TOP TOOLBAR
        # ----------------------------------------------------
        self.toolbar = ctk.CTkFrame(self, height=48, corner_radius=6)
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))

        # Action Buttons Left
        self.btn_save = ctk.CTkButton(
            self.toolbar,
            text="💾 Save All Metadata",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self._on_save_all
        )
        self.btn_save.pack(side="left", padx=(10, 5), pady=8)

        self.btn_undo = ctk.CTkButton(
            self.toolbar,
            text="↩️ Undo",
            width=75,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._on_undo
        )
        self.btn_undo.pack(side="left", padx=5, pady=8)

        self.btn_redo = ctk.CTkButton(
            self.toolbar,
            text="↪️ Redo",
            width=75,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._on_redo
        )
        self.btn_redo.pack(side="left", padx=5, pady=8)

        self.btn_cat_mgr = ctk.CTkButton(
            self.toolbar,
            text="📂 Categories",
            width=100,
            fg_color=("gray75", "gray30"),
            command=self._open_category_manager
        )
        self.btn_cat_mgr.pack(side="left", padx=5, pady=8)

        self.btn_feat_toggle = ctk.CTkButton(
            self.toolbar,
            text="★ Featured Only",
            width=110,
            fg_color="transparent",
            border_width=1,
            text_color="#F59E0B",
            command=self._on_toggle_featured_filter
        )
        self.btn_feat_toggle.pack(side="left", padx=5, pady=8)

        # Right Filters & Search
        self.sort_option = ctk.CTkOptionMenu(
            self.toolbar,
            values=["Title", "Category", "Featured", "ID"],
            width=110,
            command=lambda v: self.refresh_library_grid()
        )
        self.sort_option.pack(side="right", padx=(5, 10), pady=8)

        cat_ids = [c.get("id", "") for c in self.library_service.categories]
        self.category_filter_option = ctk.CTkOptionMenu(
            self.toolbar,
            values=["All"] + cat_ids,
            width=120,
            command=lambda v: self.refresh_library_grid()
        )
        self.category_filter_option.set("All")
        self.category_filter_option.pack(side="right", padx=5, pady=8)

        self.search_entry = ctk.CTkEntry(
            self.toolbar,
            placeholder_text="🔍 Filter title, tag...",
            width=160
        )
        self.search_entry.pack(side="right", padx=5, pady=8)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_library_grid())

        # ----------------------------------------------------
        # CENTER LIBRARY GRID
        # ----------------------------------------------------
        self.grid_scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_scrollable.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=4)

        # ----------------------------------------------------
        # RIGHT INSPECTOR DETAILS PANEL
        # ----------------------------------------------------
        self.inspector_panel = ctk.CTkFrame(self, width=320, corner_radius=8, fg_color=("gray95", "gray17"))
        self.inspector_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=4)
        self.inspector_panel.columnconfigure(0, weight=1)
        self.inspector_panel.rowconfigure(1, weight=1)

        inspector_title = ctk.CTkLabel(
            self.inspector_panel,
            text="✏️ Edit Wallpaper Metadata",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        inspector_title.grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        self.inspector_scroll = ctk.CTkScrollableFrame(self.inspector_panel, fg_color="transparent")
        self.inspector_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        self.inspector_scroll.columnconfigure(0, weight=1)

        self._build_inspector_fields()

        # Display initial wallpapers
        self.refresh_library_grid()

    def _build_inspector_fields(self):
        # Preview Image Box
        self.insp_img_container = ctk.CTkFrame(self.inspector_scroll, fg_color=("gray90", "gray14"), height=220, corner_radius=6)
        self.insp_img_container.pack(fill="x", padx=4, pady=(0, 10))
        self.insp_img_label = ctk.CTkLabel(self.insp_img_container, text="Select a wallpaper", font=ctk.CTkFont(size=12), text_color="gray50")
        self.insp_img_label.pack(fill="both", expand=True, padx=4, pady=4)

        # Title Field
        ctk.CTkLabel(self.inspector_scroll, text="Title:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=4, pady=(4, 2))
        self.insp_title_entry = ctk.CTkEntry(self.inspector_scroll)
        self.insp_title_entry.pack(fill="x", padx=4, pady=(0, 8))
        self.insp_title_entry.bind("<FocusOut>", lambda e: self._on_field_edited())

        # Category Field
        ctk.CTkLabel(self.inspector_scroll, text="Category:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=4, pady=(4, 2))
        cat_names = [c.get("id", "") for c in self.library_service.categories]
        self.insp_cat_option = ctk.CTkOptionMenu(
            self.inspector_scroll,
            values=cat_names if cat_names else ["general"],
            command=lambda v: self._on_field_edited()
        )
        self.insp_cat_option.pack(fill="x", padx=4, pady=(0, 8))

        # Collections Field
        ctk.CTkLabel(self.inspector_scroll, text="Collections (comma-separated):", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=4, pady=(4, 2))
        self.insp_cols_entry = ctk.CTkEntry(self.inspector_scroll)
        self.insp_cols_entry.pack(fill="x", padx=4, pady=(0, 8))
        self.insp_cols_entry.bind("<FocusOut>", lambda e: self._on_field_edited())

        # Tags Field
        ctk.CTkLabel(self.inspector_scroll, text="Tags (comma-separated):", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=4, pady=(4, 2))
        self.insp_tags_entry = ctk.CTkEntry(self.inspector_scroll)
        self.insp_tags_entry.pack(fill="x", padx=4, pady=(0, 8))
        self.insp_tags_entry.bind("<FocusOut>", lambda e: self._on_field_edited())

        # Description Field
        ctk.CTkLabel(self.inspector_scroll, text="Description:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=4, pady=(4, 2))
        self.insp_desc_text = ctk.CTkTextbox(self.inspector_scroll, height=70)
        self.insp_desc_text.pack(fill="x", padx=4, pady=(0, 8))
        self.insp_desc_text.bind("<FocusOut>", lambda e: self._on_field_edited())

        # Featured Checkbox
        self.insp_featured_var = ctk.BooleanVar(value=False)
        self.insp_featured_check = ctk.CTkCheckBox(
            self.inspector_scroll,
            text="Mark as Featured Wallpaper",
            variable=self.insp_featured_var,
            font=ctk.CTkFont(weight="bold"),
            command=self._on_field_edited
        )
        self.insp_featured_check.pack(fill="x", padx=4, pady=8)

        # Action Buttons: Delete Record
        btn_del = ctk.CTkButton(
            self.inspector_scroll,
            text="🗑️ Delete Metadata Record",
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._on_delete_selected_wallpaper
        )
        btn_del.pack(fill="x", padx=4, pady=(15, 10))

    # ----------------------------------------------------
    # EVENT HANDLERS
    # ----------------------------------------------------
    def _on_save_all(self):
        saved = self.library_service.save_all_to_disk()
        if saved:
            self.service.update_status("✓ Saved metadata and created backup in assets/metadata/backups/")
            messagebox.showinfo("Success", "Metadata saved to wallpapers.json, categories.json, collections.json successfully!")
        else:
            messagebox.showerror("Error", "Failed saving metadata files.")

    def _on_undo(self):
        if self.library_service.undo():
            self.refresh_library_grid()
            self.service.update_status("Undo executed")

    def _on_redo(self):
        if self.library_service.redo():
            self.refresh_library_grid()
            self.service.update_status("Redo executed")

    def _on_toggle_featured_filter(self):
        self.featured_only_filter = not self.featured_only_filter
        btn_text = "★ Featured Only" if self.featured_only_filter else "☆ Featured Filter"
        fg = ("#F59E0B", "#F59E0B") if self.featured_only_filter else "transparent"
        self.btn_feat_toggle.configure(text=btn_text, fg_color=fg)
        self.refresh_library_grid()

    def _on_card_clicked(self, wallpaper_id: str):
        self.selected_wallpaper_id = wallpaper_id
        self.populate_inspector(wallpaper_id)
        self.refresh_library_grid()

    def _on_card_toggle_featured(self, wallpaper_id: str):
        self.library_service.toggle_featured(wallpaper_id)
        self.populate_inspector(wallpaper_id)
        self.refresh_library_grid()

    def _on_field_edited(self):
        if not self.selected_wallpaper_id:
            return

        w = self.library_service.get_wallpaper_by_id(self.selected_wallpaper_id)
        if not w:
            return

        title = self.insp_title_entry.get().strip()
        cat = self.insp_cat_option.get().strip()
        cols_raw = self.insp_cols_entry.get().strip()
        tags_raw = self.insp_tags_entry.get().strip()
        desc = self.insp_desc_text.get("1.0", "end-1c").strip()
        is_feat = self.insp_featured_var.get()

        cols = [c.strip() for c in cols_raw.split(",") if c.strip()]
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

        updates = {
            "title": title,
            "category": cat,
            "collections": cols,
            "tags": tags,
            "description": desc,
            "isFeatured": is_feat,
            "featured": is_feat,
        }
        self.library_service.update_wallpaper(self.selected_wallpaper_id, updates)
        self.refresh_library_grid()

    def _on_delete_selected_wallpaper(self):
        if not self.selected_wallpaper_id:
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete metadata for '{self.selected_wallpaper_id}'?"):
            self.library_service.delete_wallpaper(self.selected_wallpaper_id)
            self.selected_wallpaper_id = None
            self.populate_inspector(None)
            self.refresh_library_grid()

    def _open_category_manager(self):
        dialog = ctk.CTkInputDialog(text="Enter new category ID (e.g. cyber, nature):", title="Create Category")
        new_cat = dialog.get_input()
        if new_cat:
            cat_id = new_cat.lower().strip()
            if self.library_service.add_category(cat_id, new_cat.capitalize()):
                # Refresh categories dropdowns
                cat_names = [c.get("id", "") for c in self.library_service.categories]
                self.insp_cat_option.configure(values=cat_names)
                self.category_filter_option.configure(values=["All"] + cat_names)
                messagebox.showinfo("Category Added", f"Category '{cat_id}' created successfully.")

    # ----------------------------------------------------
    # GRID & INSPECTOR REFRESH
    # ----------------------------------------------------
    def refresh_library_grid(self):
        self.library_service.reload_all()

        # Dynamic category list refresh
        cat_ids = [c.get("id", "") for c in self.library_service.categories]
        cur_cat = self.category_filter_option.get()
        self.category_filter_option.configure(values=["All"] + cat_ids)
        if cur_cat in ["All"] + cat_ids:
            self.category_filter_option.set(cur_cat)
        else:
            self.category_filter_option.set("All")

        self.insp_cat_option.configure(values=cat_ids if cat_ids else ["general"])

        query = self.search_entry.get()
        cat_filter = self.category_filter_option.get()
        feat_filter = True if self.featured_only_filter else None
        sort_k = self.sort_option.get()

        wallpapers = self.library_service.filter_and_sort(
            query=query,
            category_filter=cat_filter,
            featured_filter=feat_filter,
            sort_key=sort_k
        )

        for widget in self.grid_scrollable.winfo_children():
            widget.destroy()

        if not wallpapers:
            empty_lbl = ctk.CTkLabel(
                self.grid_scrollable,
                text="No wallpapers match active filter criteria.",
                font=ctk.CTkFont(size=14),
                text_color="gray50"
            )
            empty_lbl.pack(pady=40)
            return

        # Select first wallpaper if none selected
        if not self.selected_wallpaper_id or not any(w.get("id") == self.selected_wallpaper_id for w in wallpapers):
            self.selected_wallpaper_id = wallpapers[0].get("id")
            self.populate_inspector(self.selected_wallpaper_id)

        cols_count = 4
        for index, item in enumerate(wallpapers):
            row = index // cols_count
            col = index % cols_count
            
            w_id = item.get("id", "")
            card = LibraryGridCard(
                self.grid_scrollable,
                wallpaper_data=item,
                is_selected=(w_id == self.selected_wallpaper_id),
                on_click=self._on_card_clicked,
                on_toggle_featured=self._on_card_toggle_featured
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def populate_inspector(self, wallpaper_id: Optional[str]):
        if not wallpaper_id:
            self.insp_img_label.configure(image=None, text="Select a wallpaper")
            self.insp_title_entry.delete(0, "end")
            self.insp_cols_entry.delete(0, "end")
            self.insp_tags_entry.delete(0, "end")
            self.insp_desc_text.delete("1.0", "end")
            self.insp_featured_var.set(False)
            return

        w = self.library_service.get_wallpaper_by_id(wallpaper_id)
        if not w:
            return

        # Load Preview Image
        rel_path = w.get("thumbnailPath") or w.get("imagePath")
        if rel_path:
            filename = Path(rel_path).name
            category = w.get("category", "general").lower()
            candidates = [
                PathHelper.get_workspace_root() / rel_path,
                PathHelper.get_output_dir() / "thumbnails" / category / filename,
                PathHelper.get_output_dir() / "full" / category / filename,
                PathHelper.get_workspace_root() / "assets" / "wallpapers" / "thumbnails" / category / filename,
                PathHelper.get_workspace_root() / "assets" / "wallpapers" / "full" / category / filename,
            ]
            full_disk = next((c for c in candidates if c.exists()), None)
            if full_disk:
                try:
                    with Image.open(full_disk) as img:
                        img_copy = img.copy()
                        img_copy.thumbnail((260, 380), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
                        self.insp_img_label.configure(image=ctk_img, text="")
                except Exception:
                    self.insp_img_label.configure(image=None, text="🖼️ Preview error")
            else:
                self.insp_img_label.configure(image=None, text="⚠️ File missing")

        # Fill Fields
        self.insp_title_entry.delete(0, "end")
        self.insp_title_entry.insert(0, w.get("title", ""))

        self.insp_cat_option.set(w.get("category", "general"))

        self.insp_cols_entry.delete(0, "end")
        self.insp_cols_entry.insert(0, ", ".join(w.get("collections", [])))

        self.insp_tags_entry.delete(0, "end")
        self.insp_tags_entry.insert(0, ", ".join(w.get("tags", [])))

        self.insp_desc_text.delete("1.0", "end")
        self.insp_desc_text.insert("1.0", w.get("description", ""))

        is_feat = w.get("isFeatured", w.get("featured", False))
        self.insp_featured_var.set(is_feat)
