import customtkinter as ctk
from pathlib import Path
from typing import Dict, List, Optional
from tkinter import messagebox, filedialog

from app.services.flutter_detector_service import FlutterDetectorService
from app.services.sync_backup_service import SyncBackupService
from app.services.sync_service import SyncService
from app.ui.widgets.card_widget import CardWidget
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("SyncView")

class SyncView(ctk.CTkFrame):
    """Flutter Sync Engine Screen View."""
    
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.detector_service = FlutterDetectorService()
        self.backup_service = SyncBackupService()
        self.sync_service = SyncService()

        self.grid_columnconfigure(0, weight=1)

        # Title Header
        title_label = ctk.CTkLabel(
            self,
            text="🔄 Flutter App Synchronization Engine",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # ----------------------------------------------------
        # FLUTTER WORKSPACE DETECTOR CARD
        # ----------------------------------------------------
        self.workspace_card = CardWidget(self, title="Target Flutter Application Workspace", subtitle="Verified project path & pubspec.yaml assets configuration")
        self.workspace_card.grid(row=1, column=0, sticky="ew", padx=20, pady=8)

        ws_frame = ctk.CTkFrame(self.workspace_card.container, fg_color="transparent")
        ws_frame.pack(fill="x", pady=6)

        is_valid, msg = self.detector_service.is_valid_flutter_project()
        badge_text = "✓ Flutter Project Verified" if is_valid else "❌ Invalid Project"
        badge_bg = "#10B981" if is_valid else "#EF4444"

        badge_lbl = ctk.CTkLabel(
            ws_frame,
            text=badge_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
            fg_color=badge_bg,
            corner_radius=4,
            width=160,
            height=24
        )
        badge_lbl.pack(side="left", padx=(0, 10))

        path_lbl = ctk.CTkLabel(
            ws_frame,
            text=f"Path: {PathHelper.get_workspace_root()}",
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70"),
            anchor="w"
        )
        path_lbl.pack(side="left", fill="x", expand=True)

        pubspec_ok, warnings = self.detector_service.verify_pubspec_assets()
        pubspec_text = "pubspec.yaml assets OK" if pubspec_ok else f"⚠ {len(warnings)} pubspec warnings"
        pubspec_lbl = ctk.CTkLabel(
            self.workspace_card.container,
            text=pubspec_text,
            font=ctk.CTkFont(size=11),
            text_color="#10B981" if pubspec_ok else "#F59E0B",
            anchor="w"
        )
        pubspec_lbl.pack(fill="x", pady=(2, 4))

        # ----------------------------------------------------
        # DRY RUN PREVIEW & APP SIZE METER CARD
        # ----------------------------------------------------
        self.meter_card = CardWidget(self, title="Dry Run Sync Preview & Size Meter", subtitle="Asset size delta & change diff summary")
        self.meter_card.grid(row=2, column=0, sticky="ew", padx=20, pady=8)

        # Meter Stats Grid
        stats_frame = ctk.CTkFrame(self.meter_card.container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=6)
        stats_frame.columnconfigure((0,1,2,3), weight=1)

        self.stat_added = self._create_stat_box(stats_frame, 0, "Added Assets", "0 files", "#10B981")
        self.stat_updated = self._create_stat_box(stats_frame, 1, "Updated Assets", "0 files", "#3B82F6")
        self.stat_removed = self._create_stat_box(stats_frame, 2, "Removed Assets", "0 files", "#EF4444")
        self.stat_size = self._create_stat_box(stats_frame, 3, "Size Delta", "0.0 MB", "#F59E0B")

        # Size Bar
        size_bar_frame = ctk.CTkFrame(self.meter_card.container, fg_color="transparent")
        size_bar_frame.pack(fill="x", pady=(10, 4))

        self.size_progress = ctk.CTkProgressBar(size_bar_frame)
        self.size_progress.set(0.2)
        self.size_progress.pack(fill="x", side="top", pady=(0, 4))

        self.size_label = ctk.CTkLabel(
            size_bar_frame,
            text="Current App Assets: 0 MB | Projected: 0 MB | 200 MB Warning Limit",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        self.size_label.pack(side="left")

        # ----------------------------------------------------
        # ACTION BUTTONS & RESTORE BACKUP CARD
        # ----------------------------------------------------
        self.actions_card = CardWidget(self, title="Sync Controls & Backup Restoration", subtitle="Safely synchronize or restore previous snapshot")
        self.actions_card.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 20))

        btn_row = ctk.CTkFrame(self.actions_card.container, fg_color="transparent")
        btn_row.pack(fill="x", pady=6)

        btn_sync = ctk.CTkButton(
            btn_row,
            text="⚡ Sync to Flutter App",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            command=self._on_start_sync
        )
        btn_sync.pack(side="left", padx=(0, 10))

        btn_git_push = ctk.CTkButton(
            btn_row,
            text="🚀 Push to GitHub",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            height=36,
            command=self._open_git_push_dialog
        )
        btn_git_push.pack(side="left", padx=10)

        btn_preview = ctk.CTkButton(
            btn_row,
            text="🔍 Preview Sync (Dry Run)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "gray30"),
            height=36,
            command=self.refresh_dry_run
        )
        btn_preview.pack(side="left", padx=10)

        btn_restore = ctk.CTkButton(
            btn_row,
            text="↺ Restore Previous Backup",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            height=36,
            command=self._on_restore_backup
        )
        btn_restore.pack(side="left", padx=10)

        # Run initial dry run calculation
        self.refresh_dry_run()

    def _create_stat_box(self, master, col: int, title: str, value: str, color: str):
        box = ctk.CTkFrame(master, fg_color=("gray90", "gray18"), corner_radius=6)
        box.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
        
        lbl_title = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=11), text_color=("gray40", "gray60"))
        lbl_title.pack(padx=8, pady=(6, 2))

        lbl_val = ctk.CTkLabel(box, text=value, font=ctk.CTkFont(size=15, weight="bold"), text_color=color)
        lbl_val.pack(padx=8, pady=(0, 6))
        return lbl_val

    def refresh_dry_run(self):
        dry_run = self.sync_service.calculate_dry_run()

        self.stat_added.configure(text=f"+{dry_run['added_count']} files")
        self.stat_updated.configure(text=f"{dry_run['updated_count']} files")
        self.stat_removed.configure(text=f"-{dry_run['removed_count']} files")
        self.stat_size.configure(text=f"{dry_run['delta_size_mb']:+} MB")

        cur_mb = dry_run['current_size_mb']
        proj_mb = dry_run['projected_size_mb']
        limit_mb = dry_run['max_limit_mb']

        pct = min(proj_mb / limit_mb, 1.0)
        self.size_progress.set(pct)
        
        self.size_label.configure(
            text=f"Current App Assets: {cur_mb} MB | Projected: {proj_mb} MB | {limit_mb} MB Warning Limit"
        )
        self.service.update_status(f"Dry run preview updated: Projected size {proj_mb} MB")

    def _on_start_sync(self):
        dry_run = self.sync_service.calculate_dry_run()

        if dry_run["removed_count"] > 0:
            msg = f"⚠ Note: {dry_run['removed_count']} wallpapers will be removed from the Flutter app assets.\n\nProceed with Sync?"
        else:
            msg = f"Sync processed WebP wallpapers and metadata to the Flutter application?\n\nAdded: {dry_run['added_count']} | Updated: {dry_run['updated_count']}."

        if messagebox.askyesno("Confirm Sync to Flutter App", msg):
            success, summary, report_path = self.sync_service.execute_sync(create_backup=True)
            if success:
                self.refresh_dry_run()
                self.service.update_status(f"✓ {summary}")
                if messagebox.askyesno("Sync Successful", f"{summary}\n\nWould you like to commit and push these updates to GitHub now?"):
                    self._open_git_push_dialog()
            else:
                messagebox.showerror("Sync Failed", summary)

    def _on_restore_backup(self):
        backups = self.backup_service.list_backups()
        if not backups:
            messagebox.showinfo("Restore Backup", "No pre-sync backups available yet.")
            return

        latest_backup = backups[0]
        msg = f"Restore Flutter assets and metadata to previous backup point?\n\nBackup: {latest_backup['name']}\nCreated: {latest_backup['created_at']}"
        if messagebox.askyesno("Confirm Restore", msg):
            ok = self.backup_service.restore_backup(Path(latest_backup["path"]))
            if ok:
                self.refresh_dry_run()
                self.service.update_status("✓ Restored previous sync backup successfully")
                messagebox.showinfo("Restore Complete", "Flutter assets & metadata restored to previous backup state.")
            else:
                messagebox.showerror("Restore Failed", "Failed restoring backup.")

    def _open_git_push_dialog(self):
        from app.ui.dialogs.git_push_dialog import GitPushDialog
        GitPushDialog(self.winfo_toplevel(), self.service)
