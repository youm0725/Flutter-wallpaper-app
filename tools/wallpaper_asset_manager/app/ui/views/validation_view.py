import os
import customtkinter as ctk
from typing import Dict, List, Optional
from tkinter import messagebox

from app.services.release_validator_service import ReleaseValidatorService
from app.services.checklist_manager_service import ChecklistManagerService
from app.ui.widgets.card_widget import CardWidget
from app.core.logger import get_logger

logger = get_logger("ValidationView")

class ValidationView(ctk.CTkFrame):
    """Release Validation & Quality Checker Dashboard View."""
    
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.service = service
        self.validator_service = ReleaseValidatorService()
        self.checklist_service = ChecklistManagerService()

        self.last_results: Optional[Dict] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ----------------------------------------------------
        # HEADER & SCAN BUTTONS
        # ----------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🛡️ Release Validation & Quality Checker",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left")

        btn_export = ctk.CTkButton(
            header_frame,
            text="📄 Export Reports",
            width=110,
            fg_color=("gray75", "gray30"),
            command=self._export_reports
        )
        btn_export.pack(side="right", padx=5)

        btn_run = ctk.CTkButton(
            header_frame,
            text="🛡️ Run Validation Scan",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._run_scan
        )
        btn_run.pack(side="right", padx=5)

        # ----------------------------------------------------
        # DASHBOARD SUMMARY CARDS
        # ----------------------------------------------------
        self.summary_card = CardWidget(self, title="Validation Scan Dashboard", subtitle="Audited security, asset integrity, and metadata status")
        self.summary_card.grid(row=1, column=0, sticky="ew", padx=20, pady=8)

        dash_grid = ctk.CTkFrame(self.summary_card.container, fg_color="transparent")
        dash_grid.pack(fill="x", pady=4)
        dash_grid.columnconfigure((0,1,2,3,4), weight=1)

        self.stat_checks = self._create_stat_box(dash_grid, 0, "Total Checks", "0", "gray50")
        self.stat_passed = self._create_stat_box(dash_grid, 1, "Passed", "0", "#10B981")
        self.stat_warnings = self._create_stat_box(dash_grid, 2, "Warnings", "0", "#F59E0B")
        self.stat_errors = self._create_stat_box(dash_grid, 3, "Errors", "0", "#EF4444")
        self.stat_size = self._create_stat_box(dash_grid, 4, "App Asset Size", "0.0 MB", "#38BDF8")

        # ----------------------------------------------------
        # TABVIEW (ISSUES & FIX SUGGESTIONS vs RELEASE CHECKLIST)
        # ----------------------------------------------------
        self.tabview = ctk.CTkTabview(self, corner_radius=8)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=20, pady=(8, 20))
        
        self.tab_issues = self.tabview.add("Audit Issues & Actionable Fixes")
        self.tab_checklist = self.tabview.add("Release Checklist")

        self.tab_issues.columnconfigure(0, weight=1)
        self.tab_issues.rowconfigure(0, weight=1)
        
        self.issues_scroll = ctk.CTkScrollableFrame(self.tab_issues, fg_color="transparent")
        self.issues_scroll.grid(row=0, column=0, sticky="nsew")

        # Release Checklist Tab Setup
        self.tab_checklist.columnconfigure(0, weight=1)
        self.tab_checklist.rowconfigure(0, weight=1)
        self.checklist_scroll = ctk.CTkScrollableFrame(self.tab_checklist, fg_color="transparent")
        self.checklist_scroll.grid(row=0, column=0, sticky="nsew")

        self.refresh_checklist_tab()
        
        # Run initial scan
        self._run_scan()

    def _create_stat_box(self, master, col: int, title: str, value: str, color: str):
        box = ctk.CTkFrame(master, fg_color=("gray90", "gray18"), corner_radius=6)
        box.grid(row=0, column=col, padx=5, pady=4, sticky="nsew")
        
        lbl_title = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=11), text_color=("gray40", "gray60"))
        lbl_title.pack(padx=6, pady=(6, 2))

        lbl_val = ctk.CTkLabel(box, text=value, font=ctk.CTkFont(size=16, weight="bold"), text_color=color)
        lbl_val.pack(padx=6, pady=(0, 6))
        return lbl_val

    def _run_scan(self):
        self.last_results = self.validator_service.run_full_validation()
        
        r = self.last_results
        self.stat_checks.configure(text=str(r["total_checks"]))
        self.stat_passed.configure(text=str(r["pass_count"]))
        self.stat_warnings.configure(text=str(r["warning_count"]))
        self.stat_errors.configure(text=str(r["error_count"]))
        self.stat_size.configure(text=f"{r['storage_stats']['total_size_mb']} MB")

        self.refresh_issues_tab()
        self.service.update_status(f"Validation scan complete: {r['error_count']} errors, {r['warning_count']} warnings.")

    def refresh_issues_tab(self):
        for widget in self.issues_scroll.winfo_children():
            widget.destroy()

        if not self.last_results or not self.last_results["issues"]:
            pass_card = ctk.CTkFrame(self.issues_scroll, fg_color=("gray95", "gray18"), corner_radius=8)
            pass_card.pack(fill="x", padx=10, pady=20)
            
            lbl = ctk.CTkLabel(
                pass_card,
                text="✓ All 100% release quality validation checks passed cleanly! App is ready for production release.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#10B981"
            )
            lbl.pack(pady=30)
            return

        for issue in self.last_results["issues"]:
            card = ctk.CTkFrame(self.issues_scroll, fg_color=("gray95", "gray18"), corner_radius=8)
            card.pack(fill="x", padx=6, pady=4)

            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.pack(fill="x", padx=10, pady=(8, 2))

            sev = issue["severity"]
            badge_color = "#EF4444" if sev == "Error" else "#F59E0B"
            badge = ctk.CTkLabel(hdr, text=sev.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="white", fg_color=badge_color, corner_radius=4, width=60, height=20)
            badge.pack(side="left", padx=(0, 8))

            cat_lbl = ctk.CTkLabel(hdr, text=issue["category"], font=ctk.CTkFont(size=12, weight="bold"))
            cat_lbl.pack(side="left")

            loc_lbl = ctk.CTkLabel(hdr, text=f"Location: {issue['location']}", font=ctk.CTkFont(size=11), text_color=("gray40", "gray60"))
            loc_lbl.pack(side="right")

            prob_lbl = ctk.CTkLabel(card, text=f"Problem: {issue['problem']}", font=ctk.CTkFont(size=12), text_color=("gray20", "gray80"), anchor="w", justify="left")
            prob_lbl.pack(fill="x", padx=10, pady=(2, 2))

            fix_lbl = ctk.CTkLabel(card, text=f"Suggested Fix: {issue['fix']}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#10B981", anchor="w", justify="left")
            fix_lbl.pack(fill="x", padx=10, pady=(0, 8))

    def refresh_checklist_tab(self):
        for widget in self.checklist_scroll.winfo_children():
            widget.destroy()

        for item in self.checklist_service.items:
            row = ctk.CTkFrame(self.checklist_scroll, fg_color=("gray95", "gray18"), corner_radius=6)
            row.pack(fill="x", padx=6, pady=4)

            var = ctk.BooleanVar(value=item.get("completed", False))
            chk = ctk.CTkCheckBox(
                row,
                text=item.get("title", ""),
                variable=var,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda item_id=item.get("id"): self.checklist_service.toggle_item(item_id)
            )
            chk.pack(side="left", padx=12, pady=10)

    def _export_reports(self):
        if not self.last_results:
            return
        
        rep_dir = self.validator_service.reports_dir
        messagebox.showinfo(
            "Reports Exported",
            f"Release validation reports (HTML, JSON, TXT) generated successfully in:\n\n{rep_dir}"
        )
