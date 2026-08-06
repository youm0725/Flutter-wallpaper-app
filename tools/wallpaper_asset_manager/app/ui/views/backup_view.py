import customtkinter as ctk
from pathlib import Path
from typing import Dict, List, Optional
from tkinter import messagebox

from app.services.master_backup_service import MasterBackupService
from app.services.master_restore_service import MasterRestoreService
from app.ui.widgets.card_widget import CardWidget
from app.core.logger import get_logger

logger = get_logger("BackupView")

class BackupView(ctk.CTkFrame):
    """Local Repository Backup & Restore Manager Screen View."""
    
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.backup_service = MasterBackupService()
        self.restore_service = MasterRestoreService()

        self.selected_backup_folder: Optional[str] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ----------------------------------------------------
        # TOP CONTROLS & HEADER
        # ----------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="🛡️ Local Repository Backup & Restore System",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_lbl.pack(side="left")

        btn_manual_backup = ctk.CTkButton(
            header_frame,
            text="📦 Create Manual Backup",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self._on_create_manual_backup
        )
        btn_manual_backup.pack(side="right", padx=5)

        btn_prune = ctk.CTkButton(
            header_frame,
            text="🧹 Prune Old Backups",
            width=130,
            fg_color=("gray75", "gray30"),
            command=self._on_prune_backups
        )
        btn_prune.pack(side="right", padx=5)

        # ----------------------------------------------------
        # RESTORE MODE & SETTINGS CARD
        # ----------------------------------------------------
        self.settings_card = CardWidget(self, title="Restore Configuration & Settings", subtitle="Select restore mode scope & backup retention policy")
        self.settings_card.grid(row=1, column=0, sticky="ew", padx=20, pady=8)

        cfg_frame = ctk.CTkFrame(self.settings_card.container, fg_color="transparent")
        cfg_frame.pack(fill="x", pady=4)

        ctk.CTkLabel(cfg_frame, text="Restore Scope Mode:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 6))
        self.restore_mode_option = ctk.CTkOptionMenu(
            cfg_frame,
            values=["Complete", "Metadata Only", "Assets Only", "Configuration Only"],
            width=160
        )
        self.restore_mode_option.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(cfg_frame, text="Retain Latest:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 6))
        self.keep_option = ctk.CTkOptionMenu(
            cfg_frame,
            values=["5 Backups", "10 Backups", "20 Backups"],
            width=110
        )
        self.keep_option.set("10 Backups")
        self.keep_option.pack(side="left", padx=(0, 15))

        # Restore Action Buttons Right
        btn_preview = ctk.CTkButton(
            cfg_frame,
            text="🔍 Preview Restore",
            fg_color=("gray75", "gray30"),
            command=self._on_preview_restore
        )
        btn_preview.pack(side="right", padx=5)

        btn_restore = ctk.CTkButton(
            cfg_frame,
            text="↺ Restore Selected Backup",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._on_restore_selected
        )
        btn_restore.pack(side="right", padx=5)

        # ----------------------------------------------------
        # BACKUP HISTORY TABLE
        # ----------------------------------------------------
        self.table_card = CardWidget(self, title="Available Local Backups", subtitle="Pre-sync snapshots, metadata backups, and manual safety points")
        self.table_card.grid(row=2, column=0, sticky="nsew", padx=20, pady=(8, 20))

        # Table Header
        tbl_hdr = ctk.CTkFrame(self.table_card.container, height=28, fg_color=("gray85", "gray25"))
        tbl_hdr.pack(fill="x", pady=(0, 6))
        
        ctk.CTkLabel(tbl_hdr, text="Date & Time", width=160, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(tbl_hdr, text="Reason / Trigger", width=220, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Wallpapers", width=100, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Size (MB)", width=100, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_hdr, text="Folder ID", width=180, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left")

        self.table_scroll = ctk.CTkScrollableFrame(self.table_card.container, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True)

        self.refresh_backups_table()

    def _on_create_manual_backup(self):
        dialog = ctk.CTkInputDialog(text="Enter backup note / reason (optional):", title="Manual Backup")
        reason = dialog.get_input() or "User Manual Backup"
        
        ok, msg, path = self.backup_service.create_backup(reason=reason)
        if ok:
            self.refresh_backups_table()
            self.service.update_status(f"✓ {msg}")
            messagebox.showinfo("Backup Complete", msg)
        else:
            messagebox.showerror("Backup Error", msg)

    def _on_prune_backups(self):
        keep_str = self.keep_option.get()
        keep_n = 10
        if "5" in keep_str: keep_n = 5
        elif "20" in keep_str: keep_n = 20
        
        pruned = self.backup_service.prune_old_backups(max_keep=keep_n)
        self.refresh_backups_table()
        messagebox.showinfo("Prune Backups", f"Pruned {pruned} old backups. Retained latest {keep_n} backups.")

    def _on_preview_restore(self):
        if not self.selected_backup_folder:
            messagebox.showwarning("Select Backup", "Please select a backup from the table first.")
            return

        target_path = Path(self.selected_backup_folder)
        preview = self.restore_service.preview_restore(target_path)
        
        msg = f"--- RESTORE PREVIEW DIFF ---\n\n" \
              f"Backup Date: {preview['backup_date']}\n" \
              f"Backup Reason: {preview['backup_reason']}\n" \
              f"Backup Size: {preview['backup_size_mb']} MB\n\n" \
              f"Current Wallpapers: {preview['current_wallpapers_count']}\n" \
              f"Backup Wallpapers: {preview['backup_wallpapers_count']}\n\n" \
              f"Difference: {preview['diff_summary']}"
        
        messagebox.showinfo("Restore Preview", msg)

    def _on_restore_selected(self):
        if not self.selected_backup_folder:
            messagebox.showwarning("Select Backup", "Please select a backup from the table first.")
            return

        target_path = Path(self.selected_backup_folder)
        mode = self.restore_mode_option.get()
        
        preview = self.restore_service.preview_restore(target_path)
        msg = f"Restore repository using '{mode}' mode?\n\n" \
              f"Backup: {target_path.name}\n" \
              f"Impact: {preview['diff_summary']}\n\n" \
              f"Note: An emergency safety backup will be automatically created prior to restoring."

        if messagebox.askyesno("Confirm Restore", msg):
            ok, res_msg = self.restore_service.restore_backup(target_path, mode=mode, create_emergency_backup=True)
            if ok:
                self.refresh_backups_table()
                self.service.update_status(f"✓ {res_msg}")
                messagebox.showinfo("Restore Complete", res_msg)
            else:
                messagebox.showerror("Restore Failed", res_msg)

    def _on_select_row(self, folder_path: str):
        self.selected_backup_folder = folder_path
        self.refresh_table_row_styles()

    def refresh_backups_table(self):
        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        backups = self.backup_service.list_backups()
        if not backups:
            empty_lbl = ctk.CTkLabel(
                self.table_scroll,
                text="No repository backups available yet. Click 'Create Manual Backup' to generate one.",
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            )
            empty_lbl.pack(pady=30)
            return

        if not self.selected_backup_folder or not any(b["folder_path"] == self.selected_backup_folder for b in backups):
            self.selected_backup_folder = backups[0]["folder_path"]

        for b in backups:
            fpath = b["folder_path"]
            is_sel = (fpath == self.selected_backup_folder)
            bg = ("#EFF6FF", "#1E293B") if is_sel else ("gray95", "gray18")
            
            row = ctk.CTkFrame(self.table_scroll, fg_color=bg, height=32, corner_radius=4)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            dt_str = f"{b.get('date')} {b.get('time')}"
            ctk.CTkLabel(row, text=dt_str, width=160, font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(side="left", padx=10)
            
            reason_str = b.get("reason", "Manual")
            ctk.CTkLabel(row, text=reason_str, width=220, font=ctk.CTkFont(size=11), text_color="#38BDF8", anchor="w").pack(side="left")

            ctk.CTkLabel(row, text=str(b.get("wallpaper_count", 0)), width=100, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=f"{b.get('storage_size_mb', 0.0)} MB", width=100, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=Path(fpath).name, width=180, font=ctk.CTkFont(size=11), text_color=("gray40", "gray60"), anchor="w").pack(side="left")

            for widget in (row, row.winfo_children()):
                row.bind("<Button-1>", lambda e, p=fpath: self._on_select_row(p))

    def refresh_table_row_styles(self):
        self.refresh_backups_table()
