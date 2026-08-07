import customtkinter as ctk
from typing import Dict, List
from app.models.processing_task import ProcessingTask
from app.services.processing_queue_manager import ProcessingQueueManager
from app.services.image_processing_engine import QUALITY_PRESETS
from app.ui.widgets.card_widget import CardWidget
from app.core.logger import get_logger

logger = get_logger("ProcessView")

class ProcessView(ctk.CTkFrame):
    """Image Processing Engine Screen View."""
    
    CATEGORIES = [
        "nature", "abstract", "amoled", "anime",
        "architecture", "cars", "gaming", "minimal", "space", "general"
    ]

    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.queue_manager = ProcessingQueueManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ----------------------------------------------------
        # PAGE HEADER & CONTROLS
        # ----------------------------------------------------
        title_label = ctk.CTkLabel(
            self,
            text="⚡ Image Processing Engine & WebP Compression",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Toolbar Frame
        self.toolbar_card = CardWidget(self, title="Batch Processing Controls", subtitle="Configure compression preset & category mapping")
        self.toolbar_card.grid(row=1, column=0, sticky="ew", padx=20, pady=8)

        ctrl_frame = ctk.CTkFrame(self.toolbar_card.container, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=6)

        # Preset Selector
        ctk.CTkLabel(ctrl_frame, text="Quality Preset:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 6))
        
        saved_preset = self.service.config_manager.get("processing", "preset", "Balanced")
        self.preset_option = ctk.CTkOptionMenu(
            ctrl_frame,
            values=["High (Q: 90)", "Balanced (Q: 82)", "Compact (Q: 75)"],
            width=150,
            command=self._on_preset_selected
        )
        if saved_preset == "High":
            self.preset_option.set("High (Q: 90)")
        elif saved_preset == "Compact":
            self.preset_option.set("Compact (Q: 75)")
        else:
            self.preset_option.set("Balanced (Q: 82)")
        self.preset_option.pack(side="left", padx=(0, 15))

        # Category Selector
        ctk.CTkLabel(ctrl_frame, text="Target Category:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 6))
        
        initial_cats = [c.get("id", "") for c in self.service.library_service.categories]
        if not initial_cats:
            initial_cats = ["general"]

        self.category_option = ctk.CTkOptionMenu(
            ctrl_frame,
            values=initial_cats,
            width=130
        )
        self.category_option.set(initial_cats[0])
        self.category_option.pack(side="left", padx=(0, 15))

        # Action Buttons
        self.btn_start = ctk.CTkButton(
            ctrl_frame,
            text="⚡ Start Processing",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self._start_processing
        )
        self.btn_start.pack(side="left", padx=5)

        self.btn_pause = ctk.CTkButton(
            ctrl_frame,
            text="⏸️ Pause",
            width=80,
            fg_color=("gray75", "gray30"),
            command=self._toggle_pause
        )
        self.btn_pause.pack(side="left", padx=5)

        self.btn_cancel = ctk.CTkButton(
            ctrl_frame,
            text="🛑 Cancel",
            width=80,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._cancel_processing
        )
        self.btn_cancel.pack(side="left", padx=5)

        # Progress Indicator Row
        progress_row = ctk.CTkFrame(self.toolbar_card.container, fg_color="transparent")
        progress_row.pack(fill="x", pady=(10, 4))

        self.progress_bar = ctk.CTkProgressBar(progress_row)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", side="top", pady=(0, 6))

        self.progress_label = ctk.CTkLabel(
            progress_row,
            text="Queue Ready • 0 items in processing queue",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        self.progress_label.pack(side="left")

        # ----------------------------------------------------
        # QUEUE LIST TABLE (Scrollable)
        # ----------------------------------------------------
        self.queue_card = CardWidget(self, title="Processing Queue & WebP Assets", subtitle="Live task status and file size reduction")
        self.queue_card.grid(row=2, column=0, sticky="nsew", padx=20, pady=(8, 20))

        # Table Header
        tbl_hdr = ctk.CTkFrame(self.queue_card.container, height=28, fg_color=("gray85", "gray25"))
        tbl_hdr.pack(fill="x", pady=(0, 6))
        
        ctk.CTkLabel(tbl_hdr, text="Status", width=100, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(tbl_hdr, text="Input Filename", width=220, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Category", width=110, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Output WebP", width=200, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Full Size", width=100, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Thumb Size", width=100, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Duration", width=80, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")

        self.queue_scrollable = ctk.CTkScrollableFrame(self.queue_card.container, fg_color="transparent")
        self.queue_scrollable.pack(fill="both", expand=True)

    def _on_preset_selected(self, choice: str):
        preset_name = "Balanced"
        if "High" in choice:
            preset_name = "High"
        elif "Compact" in choice:
            preset_name = "Compact"

        self.service.config_manager.set("processing", "preset", preset_name)

    def populate_queue_from_imports(self, imported_items: List):
        """Populates processing queue from imported items."""
        cat = self.category_option.get().lower()
        self.queue_manager.add_imported_items(imported_items, category=cat)
        self.refresh_queue_table()

    def _start_processing(self):
        # Auto sync tasks from active import view if queue empty
        if not self.queue_manager.tasks:
            # Check if import view has items
            import_view = self.master.master.views.get("Import")
            if import_view and import_view.import_service.items:
                cat = self.category_option.get().lower()
                self.queue_manager.add_imported_items(import_view.import_service.items, category=cat)

        if not self.queue_manager.tasks:
            self.progress_label.configure(text="⚠ Queue is empty. Import images first in the Import tab!")
            return

        choice = self.preset_option.get()
        preset_name = "High" if "High" in choice else ("Compact" if "Compact" in choice else "Balanced")

        self.btn_start.configure(state="disabled")
        self.queue_manager.start_processing(
            preset=preset_name,
            on_progress=self._on_queue_progress,
            on_completed=self._on_queue_completed
        )

    def _toggle_pause(self):
        if self.queue_manager.is_paused:
            self.queue_manager.resume_processing()
            self.btn_pause.configure(text="⏸️ Pause")
        else:
            self.queue_manager.pause_processing()
            self.btn_pause.configure(text="▶️ Resume")

    def _cancel_processing(self):
        self.queue_manager.cancel_processing()
        self.btn_start.configure(state="normal")
        self.progress_label.configure(text="Processing cancelled by user.")

    def _on_queue_progress(self, stats: Dict):
        pct = stats["percentage"] / 100.0
        self.progress_bar.set(pct)
        
        msg = f"Processing: {stats['completed']}/{stats['total']} ({stats['percentage']}%) • Elapsed: {stats['elapsed_seconds']}s • Est. Rem: {stats['est_remaining_seconds']}s"
        self.progress_label.configure(text=msg)
        self.service.update_status(msg)
        
        self.after(0, self.refresh_queue_table)

    def _on_queue_completed(self):
        self.btn_start.configure(state="normal")
        self.progress_bar.set(1.0)
        self.progress_label.configure(text="✓ Batch processing complete! All WebP assets generated.")
        self.service.update_status("Batch wallpaper processing complete")
        self.after(0, self.refresh_queue_table)

    def refresh_queue_table(self):
        for widget in self.queue_scrollable.winfo_children():
            widget.destroy()

        if not self.queue_manager.tasks:
            empty_lbl = ctk.CTkLabel(
                self.queue_scrollable,
                text="No items in processing queue. Import wallpapers from the Import tab to begin.",
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            )
            empty_lbl.pack(pady=30)
            return

        for task in self.queue_manager.tasks:
            row_frame = ctk.CTkFrame(self.queue_scrollable, fg_color=("gray95", "gray18"), height=32)
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)

            # Status Badge
            st = task.status
            st_color = "#10B981" if st == "Completed" else ("#3B82F6" if st == "Processing" else ("#EF4444" if st == "Failed" else "gray50"))
            st_lbl = ctk.CTkLabel(row_frame, text=st, width=90, font=ctk.CTkFont(size=11, weight="bold"), text_color="white", fg_color=st_color, corner_radius=4)
            st_lbl.pack(side="left", padx=5, pady=4)

            # Input Filename
            in_name = task.imported_item.filename
            if len(in_name) > 28: in_name = in_name[:25] + "..."
            ctk.CTkLabel(row_frame, text=in_name, width=220, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")

            # Category
            ctk.CTkLabel(row_frame, text=task.category, width=110, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")

            # Output WebP
            out_name = task.output_full_path.name if task.output_full_path else "-"
            ctk.CTkLabel(row_frame, text=out_name, width=200, font=ctk.CTkFont(size=11), text_color=("gray20", "gray80"), anchor="w").pack(side="left")

            # Full Size
            full_sz = f"{round(task.full_size_bytes / 1024)} KB" if task.full_size_bytes else "-"
            ctk.CTkLabel(row_frame, text=full_sz, width=100, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")

            # Thumb Size
            thumb_sz = f"{round(task.thumb_size_bytes / 1024)} KB" if task.thumb_size_bytes else "-"
            ctk.CTkLabel(row_frame, text=thumb_sz, width=100, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")

            # Duration
            dur_str = f"{task.duration_seconds:.2f}s" if task.duration_seconds > 0 else "-"
            ctk.CTkLabel(row_frame, text=dur_str, width=80, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")

    def refresh_data(self):
        cat_ids = [c.get("id", "") for c in self.service.library_service.categories]
        if not cat_ids:
            cat_ids = ["general"]
        cur = self.category_option.get()
        self.category_option.configure(values=cat_ids)
        if cur in cat_ids:
            self.category_option.set(cur)
        else:
            self.category_option.set(cat_ids[0])
