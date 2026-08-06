import os
from pathlib import Path
from typing import List, Optional
from tkinter import filedialog
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

from app.models.imported_wallpaper import ImportedWallpaperItem
from app.services.import_service import ImportService
from app.services.thumbnail_service import ThumbnailService
from app.ui.widgets.import_grid_card import ImportGridCard
from app.ui.widgets.preview_panel import PreviewPanel
from app.core.logger import get_logger

logger = get_logger("ImportView")

class ImportView(ctk.CTkFrame):
    """Main Wallpaper Import Manager Screen View."""
    
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.import_service = ImportService(thumbnail_service=ThumbnailService())
        self.card_widgets: List[ImportGridCard] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)  # Fixed preview panel width
        self.grid_rowconfigure(1, weight=1)

        # ----------------------------------------------------
        # TOP TOOLBAR
        # ----------------------------------------------------
        self.toolbar_frame = ctk.CTkFrame(self, height=48, corner_radius=6)
        self.toolbar_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))

        # Import Buttons Group
        btn_import_file = ctk.CTkButton(
            self.toolbar_frame,
            text="🖼️ Import Images",
            width=120,
            font=ctk.CTkFont(weight="bold"),
            command=self._on_import_files
        )
        btn_import_file.pack(side="left", padx=(10, 5), pady=8)

        btn_import_folder = ctk.CTkButton(
            self.toolbar_frame,
            text="📂 Import Folder",
            width=120,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self._on_import_folder
        )
        btn_import_folder.pack(side="left", padx=5, pady=8)

        # Selection Control Group
        btn_select_all = ctk.CTkButton(
            self.toolbar_frame,
            text="☑️ Select All",
            width=90,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._on_select_all
        )
        btn_select_all.pack(side="left", padx=5, pady=8)

        btn_deselect_all = ctk.CTkButton(
            self.toolbar_frame,
            text="⬜ Deselect All",
            width=95,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._on_deselect_all
        )
        btn_deselect_all.pack(side="left", padx=5, pady=8)

        btn_delete_selected = ctk.CTkButton(
            self.toolbar_frame,
            text="❌ Delete Selected",
            width=110,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._on_delete_selected
        )
        btn_delete_selected.pack(side="left", padx=5, pady=8)

        btn_clear = ctk.CTkButton(
            self.toolbar_frame,
            text="🗑️ Clear All",
            width=90,
            fg_color="transparent",
            text_color="#EF4444",
            hover_color=("gray85", "gray25"),
            command=self._on_clear_all
        )
        btn_clear.pack(side="left", padx=5, pady=8)

        # Sort Dropdown & Search Bar (Right side of toolbar)
        self.sort_option = ctk.CTkOptionMenu(
            self.toolbar_frame,
            values=["Import Time", "Filename", "Resolution", "File Size"],
            width=120,
            command=self._on_sort_changed
        )
        self.sort_option.pack(side="right", padx=(5, 10), pady=8)

        self.search_entry = ctk.CTkEntry(
            self.toolbar_frame,
            placeholder_text="🔍 Search wallpapers...",
            width=160
        )
        self.search_entry.pack(side="right", padx=5, pady=8)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_grid())

        # ----------------------------------------------------
        # CENTER CONTENT AREA (Grid View + Drop Zone)
        # ----------------------------------------------------
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=4)
        self.grid_container.columnconfigure(0, weight=1)
        self.grid_container.rowconfigure(0, weight=1)

        # Scrollable Grid Frame
        self.grid_scrollable = ctk.CTkScrollableFrame(self.grid_container, fg_color="transparent")
        self.grid_scrollable.grid(row=0, column=0, sticky="nsew")

        # Empty State Placeholder Frame
        self.empty_state_frame = ctk.CTkFrame(self.grid_container, fg_color=("gray95", "gray17"), corner_radius=8)
        self.empty_state_frame.grid(row=0, column=0, sticky="nsew")
        
        empty_title = ctk.CTkLabel(
            self.empty_state_frame,
            text="📥 Drag & Drop Images or Folders Here",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray30", "gray70")
        )
        empty_title.pack(expand=True, pady=(60, 5))

        empty_sub = ctk.CTkLabel(
            self.empty_state_frame,
            text="Supports JPG, JPEG, PNG, and WEBP formats.\nOr click 'Import Images' / 'Import Folder' from top toolbar.",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray50"),
            justify="center"
        )
        empty_sub.pack(expand=True, pady=(0, 60))

        # Setup Drag & Drop Binding
        if HAS_DND:
            try:
                self.empty_state_frame.drop_target_register(DND_FILES)
                self.empty_state_frame.dnd_bind("<<Drop>>", self._on_drag_drop)
                self.grid_scrollable.drop_target_register(DND_FILES)
                self.grid_scrollable.dnd_bind("<<Drop>>", self._on_drag_drop)
            except Exception as e:
                logger.info("TkinterDnD registration note: %s", e)

        # ----------------------------------------------------
        # RIGHT PREVIEW PANEL
        # ----------------------------------------------------
        self.preview_panel = PreviewPanel(self)
        self.preview_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=4)

        # ----------------------------------------------------
        # BOTTOM IMPORT STATUS BAR
        # ----------------------------------------------------
        self.import_status_bar = ctk.CTkFrame(self, height=28, corner_radius=4, fg_color=("gray90", "gray14"))
        self.import_status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(4, 12))

        self.stats_label = ctk.CTkLabel(
            self.import_status_bar,
            text="Imported: 0 | Selected: 0 | Total Size: 0 KB | Validation Issues: 0",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        self.stats_label.pack(side="left", padx=12, pady=4)

    # ----------------------------------------------------
    # EVENT HANDLERS
    # ----------------------------------------------------
    def _on_import_files(self):
        paths = filedialog.askopenfilenames(
            title="Select Wallpaper Images",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp"), ("All Files", "*.*")]
        )
        if paths:
            file_paths = [Path(p) for p in paths]
            self.import_service.import_files(file_paths, on_thumbnail_ready=self._on_thumbnail_updated)
            self.refresh_grid()

    def _on_import_folder(self):
        folder_path = filedialog.askdirectory(title="Select Wallpaper Folder")
        if folder_path:
            self.import_service.import_directory(Path(folder_path), on_thumbnail_ready=self._on_thumbnail_updated)
            self.refresh_grid()

    def _on_drag_drop(self, event):
        raw_data = event.data
        if not raw_data:
            return

        # Parse dragged file paths
        paths: List[Path] = []
        if raw_data.startswith("{"):
            # Windows space enclosed paths
            import re
            matches = re.findall(r"\{([^}]+)\}", raw_data)
            paths = [Path(m) for m in matches]
        else:
            paths = [Path(p.strip()) for p in raw_data.split()]

        file_candidates: List[Path] = []
        for p in paths:
            if p.is_dir():
                self.import_service.import_directory(p, on_thumbnail_ready=self._on_thumbnail_updated)
            elif p.is_file():
                file_candidates.append(p)

        if file_candidates:
            self.import_service.import_files(file_candidates, on_thumbnail_ready=self._on_thumbnail_updated)

        self.refresh_grid()

    def _on_clear_all(self):
        self.import_service.clear_all()
        self.refresh_grid()

    def _on_delete_selected(self):
        self.import_service.delete_selected()
        self.refresh_grid()

    def _on_select_all(self):
        self.import_service.select_all()
        self.refresh_grid()

    def _on_deselect_all(self):
        self.import_service.deselect_all()
        self.refresh_grid()

    def _on_sort_changed(self, sort_val: str):
        self.import_service.sort_key = sort_val
        self.refresh_grid()

    def _on_card_click(self, item_id: str):
        item = self.import_service.set_active_preview(item_id)
        self.preview_panel.set_wallpaper_item(item)
        self.refresh_grid_selection_states()

    def _on_card_check_toggle(self, item_id: str, is_checked: bool):
        self.update_stats_bar()

    def _on_thumbnail_updated(self, item_id: str):
        # Update preview panel if active item got thumbnail
        active_item = self.import_service.get_selected_preview_item()
        if active_item and active_item.id == item_id:
            self.preview_panel.set_wallpaper_item(active_item)
        self.after(0, self.refresh_grid)

    # ----------------------------------------------------
    # GRID RENDERING & REFRESH
    # ----------------------------------------------------
    def refresh_grid(self):
        # Update Search Query
        self.import_service.search_query = self.search_entry.get()

        # Get Display Items
        items = self.import_service.get_display_items()

        # Toggle Empty State vs Grid Frame
        if not items and not self.import_service.items:
            self.empty_state_frame.lift()
            self.preview_panel.set_wallpaper_item(None)
            self.update_stats_bar()
            return
        else:
            self.grid_scrollable.lift()

        # Clear existing card widgets safely
        for widget in self.grid_scrollable.winfo_children():
            widget.destroy()

        self.card_widgets.clear()

        # Grid Layout Calculation (Columns count based on scrollable width)
        cols_count = 4
        active_item = self.import_service.get_selected_preview_item()
        active_id = active_item.id if active_item else None

        for index, item in enumerate(items):
            row = index // cols_count
            col = index % cols_count

            card = ImportGridCard(
                self.grid_scrollable,
                item=item,
                is_active_preview=(item.id == active_id),
                on_select_click=self._on_card_click,
                on_checkbox_toggle=self._on_card_check_toggle
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.card_widgets.append(card)

        # Update Preview Panel
        self.preview_panel.set_wallpaper_item(active_item)
        self.update_stats_bar()

    def refresh_grid_selection_states(self):
        active_item = self.import_service.get_selected_preview_item()
        active_id = active_item.id if active_item else None
        
        for card in self.card_widgets:
            is_active = (card.item.id == active_id)
            border_color = ("#3B82F6", "#3B82F6") if is_active else ("gray75", "gray30")
            fg_color = ("#EFF6FF", "#1E293B") if is_active else ("gray95", "gray17")
            card.configure(
                border_width=2 if is_active else 1,
                border_color=border_color,
                fg_color=fg_color
            )

    def update_stats_bar(self):
        stats = self.import_service.get_stats()
        self.stats_label.configure(
            text=f"Imported: {stats['total_count']} | Selected: {stats['selected_count']} | Total Size: {stats['total_size']} | Validation Issues: {stats['issues_count']}"
        )
        self.service.update_status(f"Imported {stats['total_count']} wallpapers")
