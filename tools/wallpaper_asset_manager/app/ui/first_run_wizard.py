import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from app.utils.path_helper import PathHelper
from app.services.flutter_detector_service import FlutterDetectorService
from app.core.logger import get_logger

logger = get_logger("FirstRunWizard")

class FirstRunWizard(ctk.CTkToplevel):
    """First Launch Setup Wizard modal guiding setup and workspace validation."""
    
    def __init__(self, master, config_manager):
        super().__init__(master)
        self.config_manager = config_manager
        self.detector = FlutterDetectorService()

        self.title("Wallpaper Asset Manager - Initial Setup Wizard")
        self.geometry("640x480")
        self.resizable(False, False)
        self.grab_set()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header Title
        hdr = ctk.CTkFrame(self, height=60, fg_color="#1E293B", corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")
        
        lbl_hdr = ctk.CTkLabel(
            hdr,
            text="🚀 Welcome to Wallpaper Asset Manager Setup",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        lbl_hdr.pack(side="left", padx=20, pady=15)

        # Wizard Content Box
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.body.columnconfigure(0, weight=1)

        msg_lbl = ctk.CTkLabel(
            self.body,
            text="Configure your Flutter Wallpaper Gallery project workspace paths to complete initial setup.",
            font=ctk.CTkFont(size=13),
            wraplength=580,
            anchor="w",
            justify="left"
        )
        msg_lbl.pack(fill="x", pady=(0, 15))

        # Path Picker Entry
        ctk.CTkLabel(self.body, text="Flutter Project Workspace Root:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", pady=(5, 2))
        
        path_row = ctk.CTkFrame(self.body, fg_color="transparent")
        path_row.pack(fill="x", pady=(0, 15))

        self.path_entry = ctk.CTkEntry(path_row, width=420)
        self.path_entry.insert(0, str(PathHelper.get_workspace_root()))
        self.path_entry.pack(side="left", padx=(0, 10))

        btn_browse = ctk.CTkButton(path_row, text="📁 Browse", width=90, command=self._browse_folder)
        btn_browse.pack(side="left")

        # Verification Status Card
        self.status_box = ctk.CTkFrame(self.body, fg_color=("gray90", "gray18"), corner_radius=6)
        self.status_box.pack(fill="x", pady=10)

        self.status_lbl = ctk.CTkLabel(
            self.status_box,
            text="Ready to validate workspace.",
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        self.status_lbl.pack(padx=12, pady=12)

        # Complete Setup Button
        self.btn_finish = ctk.CTkButton(
            self,
            text="✓ Complete Setup & Launch Manager",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            command=self._complete_setup
        )
        self.btn_finish.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        self._validate_workspace()

    def _browse_folder(self):
        chosen = filedialog.askdirectory(title="Select Wallpaper Gallery Project Root")
        if chosen:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, chosen)
            self._validate_workspace()

    def _validate_workspace(self):
        p = Path(self.path_entry.get().strip())
        self.detector.workspace_root = p
        
        is_ok, msg = self.detector.is_valid_flutter_project()
        if is_ok:
            self.status_lbl.configure(text=f"✓ Valid Flutter workspace: {msg}", text_color="#10B981")
            self.btn_finish.configure(state="normal")
        else:
            self.status_lbl.configure(text=f"⚠️ {msg}", text_color="#EF4444")
            self.btn_finish.configure(state="disabled")

    def _complete_setup(self):
        self.config_manager.set("app", "first_run", False)
        logger.info("Initial setup wizard completed successfully.")
        self.destroy()
