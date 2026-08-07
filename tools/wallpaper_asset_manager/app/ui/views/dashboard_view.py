import json
import time
import customtkinter as ctk
from pathlib import Path
from typing import Dict, Any
from tkinter import messagebox

from app.services.statistics_service import StatisticsService
from app.ui.widgets.card_widget import CardWidget
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("DashboardView")

class DashboardView(ctk.CTkFrame):
    """Main Application Dashboard & Analytics View."""
    
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.stats_service = StatisticsService()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------------------------------------------
        # TOP HEADER & CONTROLS
        # ----------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title_lbl = ctk.CTkLabel(
            header,
            text="📊 Dashboard & Wallpaper Library Analytics",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_lbl.pack(side="left")

        btn_export = ctk.CTkButton(
            header,
            text="📄 Export Report",
            width=110,
            fg_color=("gray75", "gray30"),
            command=self._export_report
        )
        btn_export.pack(side="right", padx=5)

        btn_build = ctk.CTkButton(
            header,
            text="📱 Build APK & IPA",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            command=self._open_flutter_builder
        )
        btn_build.pack(side="right", padx=5)

        btn_refresh = ctk.CTkButton(
            header,
            text="🔄 Refresh Data",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.refresh_analytics
        )
        btn_refresh.pack(side="right", padx=5)

        # Main Scrollable Dashboard Content Container
        self.scroll_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scroll_content.columnconfigure(0, weight=1)

        self._build_dashboard_layout()
        self.refresh_analytics(force=False)

    def _build_dashboard_layout(self):
        # 1. Summary Cards Row
        self.summary_card = CardWidget(self.scroll_content, title="Library Overview", subtitle="Wallpaper counts, categories, and storage metrics")
        self.summary_card.pack(fill="x", pady=8)

        grid1 = ctk.CTkFrame(self.summary_card.container, fg_color="transparent")
        grid1.pack(fill="x", pady=4)
        grid1.columnconfigure((0,1,2,3,4,5), weight=1)

        self.box_wallpapers = self._create_stat_box(grid1, 0, "Wallpapers", "0", "#38BDF8")
        self.box_categories = self._create_stat_box(grid1, 1, "Categories", "0", "#3B82F6")
        self.box_collections = self._create_stat_box(grid1, 2, "Collections", "0", "#8B5CF6")
        self.box_featured = self._create_stat_box(grid1, 3, "Featured", "0", "#F59E0B")
        self.box_storage = self._create_stat_box(grid1, 4, "Storage Used", "0 MB", "#10B981")
        self.box_app_size = self._create_stat_box(grid1, 5, "App Asset Size", "0 MB", "#06B6D4")

        # 2. Storage & Image Analytics Row
        self.row2_frame = ctk.CTkFrame(self.scroll_content, fg_color="transparent")
        self.row2_frame.pack(fill="x", pady=8)
        self.row2_frame.columnconfigure((0, 1), weight=1)

        self.card_storage = CardWidget(self.row2_frame, title="Storage Breakdown", subtitle="Asset size distribution across layers")
        self.card_storage.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.lbl_storage_full = ctk.CTkLabel(self.card_storage.container, text="Full Wallpapers: 0 MB", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_storage_full.pack(fill="x", pady=2)
        
        self.lbl_storage_thumb = ctk.CTkLabel(self.card_storage.container, text="Thumbnails: 0 MB", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_storage_thumb.pack(fill="x", pady=2)

        self.lbl_storage_meta = ctk.CTkLabel(self.card_storage.container, text="Metadata: 0 MB", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_storage_meta.pack(fill="x", pady=2)

        self.lbl_storage_backups = ctk.CTkLabel(self.card_storage.container, text="Backups: 0 MB", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_storage_backups.pack(fill="x", pady=2)

        self.card_image_stats = CardWidget(self.row2_frame, title="Image Analytics", subtitle="Resolution and file size benchmarks")
        self.card_image_stats.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.lbl_avg_size = ctk.CTkLabel(self.card_image_stats.container, text="Average File Size: 0 KB", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_avg_size.pack(fill="x", pady=2)

        self.lbl_largest = ctk.CTkLabel(self.card_image_stats.container, text="Largest File: 0 KB", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_largest.pack(fill="x", pady=2)

        self.lbl_smallest = ctk.CTkLabel(self.card_image_stats.container, text="Smallest File: 0 KB", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_smallest.pack(fill="x", pady=2)

        self.lbl_common_res = ctk.CTkLabel(self.card_image_stats.container, text="Most Common Resolution: 1080x1920", font=ctk.CTkFont(size=12), anchor="w")
        self.lbl_common_res.pack(fill="x", pady=2)

        # 3. Quick Actions & Health Row
        self.card_actions = CardWidget(self.scroll_content, title="Quick Action Shortcuts", subtitle="Jump directly to core management tools")
        self.card_actions.pack(fill="x", pady=8)

        act_frame = ctk.CTkFrame(self.card_actions.container, fg_color="transparent")
        act_frame.pack(fill="x", pady=6)

        actions = [
            ("🖼️ Import Wallpapers", "Import"),
            ("⚡ Process Images", "Process"),
            ("✏️ Manage Library", "Metadata"),
            ("🔄 Sync Flutter", "Sync"),
            ("🛡️ Run Validation", "Validation"),
        ]

        for text, tab_name in actions:
            btn = ctk.CTkButton(
                act_frame,
                text=text,
                font=ctk.CTkFont(weight="bold"),
                fg_color=("gray75", "gray30"),
                command=lambda t=tab_name: self._navigate_tab(t)
            )
            btn.pack(side="left", padx=6, fill="x", expand=True)

    def _create_stat_box(self, master, col: int, title: str, value: str, color: str):
        box = ctk.CTkFrame(master, fg_color=("gray90", "gray18"), corner_radius=6)
        box.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")
        
        lbl_title = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=11), text_color=("gray40", "gray60"))
        lbl_title.pack(padx=6, pady=(6, 2))

        lbl_val = ctk.CTkLabel(box, text=value, font=ctk.CTkFont(size=16, weight="bold"), text_color=color)
        lbl_val.pack(padx=6, pady=(0, 6))
        return lbl_val

    def refresh_analytics(self, force: bool = True):
        data = self.stats_service.get_dashboard_analytics(force_refresh=force)

        self.box_wallpapers.configure(text=str(data["total_wallpapers"]))
        self.box_categories.configure(text=str(data["total_categories"]))
        self.box_collections.configure(text=str(data["total_collections"]))
        self.box_featured.configure(text=str(data["featured_count"]))
        self.box_storage.configure(text=f"{data['total_storage_mb']} MB")
        self.box_app_size.configure(text=f"{data['projected_app_mb']} MB")

        self.lbl_storage_full.configure(text=f"Full Wallpapers: {data['full_size_mb']} MB")
        self.lbl_storage_thumb.configure(text=f"Thumbnails: {data['thumb_size_mb']} MB")
        self.lbl_storage_meta.configure(text=f"Metadata: {data['metadata_size_mb']} MB")
        self.lbl_storage_backups.configure(text=f"Backups: {data['backups_size_mb']} MB")

        self.lbl_avg_size.configure(text=f"Average File Size: {data['avg_size_kb']} KB")
        self.lbl_largest.configure(text=f"Largest File: {data['largest_kb']} KB")
        self.lbl_smallest.configure(text=f"Smallest File: {data['smallest_kb']} KB")
        self.lbl_common_res.configure(text=f"Most Common Resolution: {data['common_resolution']}")

        self.service.update_status(f"Dashboard analytics refreshed ({data['total_wallpapers']} wallpapers)")

    def _navigate_tab(self, tab_name: str):
        # Switch main sidebar view
        main_win = self.master.master
        if hasattr(main_win, "sidebar"):
            main_win.sidebar._on_nav_click(tab_name)

    def _export_report(self):
        data = self.stats_service.get_dashboard_analytics()
        rep_dir = PathHelper.get_tool_root() / "logs" / "analytics_reports"
        rep_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        json_file = rep_dir / f"analytics_report_{timestamp}.json"
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Report Exported", f"Dashboard analytics report exported to:\n\n{json_file}")

    def _open_flutter_builder(self):
        from app.ui.dialogs.flutter_build_dialog import FlutterBuildDialog
        FlutterBuildDialog(self.winfo_toplevel(), self.service)
