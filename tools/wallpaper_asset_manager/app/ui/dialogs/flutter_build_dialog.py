import os
import threading
import customtkinter as ctk
from pathlib import Path
from typing import Optional
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("FlutterBuildDialog")

class FlutterBuildDialog(ctk.CTkToplevel):
    """Modal dialog for triggering Android APK and Apple IPA release builds from Asset Manager."""
    
    def __init__(self, master, app_service):
        super().__init__(master)
        self.service = app_service
        
        self.title("📱 Flutter Application Package Builder (APK & IPA)")
        self.geometry("860x620")
        self.minsize(720, 500)
        
        self.is_building = False
        
        # Make modal window stays on top
        self.transient(master)
        self.grab_set()

        # Configure Grid Layout
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Title Banner
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text="📱 Flutter App Builder — Android (APK) & Apple (IPA)",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Build production binary packages for your Flutter wallpaper app directly from the Asset Manager.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        ).pack(anchor="w", pady=(4, 0))

        # Control Buttons Bar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_apk = ctk.CTkButton(
            btn_frame,
            text="🤖 Build Android APK",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=38,
            command=self._build_apk_click
        )
        self.btn_apk.pack(side="left", padx=(0, 10))

        self.btn_ipa = ctk.CTkButton(
            btn_frame,
            text="🍎 Build Apple IPA",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            height=38,
            command=self._build_ipa_click
        )
        self.btn_ipa.pack(side="left", padx=(0, 10))

        self.btn_both = ctk.CTkButton(
            btn_frame,
            text="🚀 Build Both (APK & IPA)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            height=38,
            command=self._build_both_click
        )
        self.btn_both.pack(side="left", padx=(0, 10))

        self.btn_folder = ctk.CTkButton(
            btn_frame,
            text="📂 Open Output Folder",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            border_width=1,
            height=38,
            command=self._open_output_folder
        )
        self.btn_folder.pack(side="right")

        # Live Console Output Box
        console_frame = ctk.CTkFrame(self)
        console_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        console_frame.grid_rowconfigure(1, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            console_frame,
            text="Build Output Log:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.console_textbox = ctk.CTkTextbox(
            console_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.console_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.console_textbox.insert("1.0", "Ready to build. Click 'Build Android APK', 'Build Apple IPA', or 'Build Both'.\n")

        # Progress Bar & Status Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=3, column=0, padx=20, pady=(0, 15), sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(footer_frame)
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0.0)

        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="Status: Idle",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(anchor="w")

    def _append_log(self, text: str):
        """Thread-safe log appender."""
        def _update():
            self.console_textbox.insert("end", text)
            self.console_textbox.see("end")
        self.after(0, _update)

    def _set_building(self, building: bool, status_msg: str):
        self.is_building = building
        def _update():
            state = "disabled" if building else "normal"
            self.btn_apk.configure(state=state)
            self.btn_ipa.configure(state=state)
            self.btn_both.configure(state=state)
            self.status_label.configure(text=f"Status: {status_msg}")
            if building:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start()
            else:
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")
                self.progress_bar.set(1.0 if "Completed" in status_msg or "Success" in status_msg else 0.0)
        self.after(0, _update)

    def _build_apk_click(self):
        if self.is_building:
            return
        self._set_building(True, "Building Android APK...")
        self.console_textbox.delete("1.0", "end")

        def _worker():
            res = self.service.build_service.build_apk(log_callback=self._append_log)
            status = "Completed Successfully!" if res["success"] else "APK Build Failed"
            self._set_building(False, status)

        threading.Thread(target=_worker, daemon=True).start()

    def _build_ipa_click(self):
        if self.is_building:
            return
        self._set_building(True, "Building Apple iOS IPA...")
        self.console_textbox.delete("1.0", "end")

        def _worker():
            res = self.service.build_service.build_ipa(log_callback=self._append_log)
            status = "Processed!" if res["success"] else "iOS Build Finished"
            self._set_building(False, status)

        threading.Thread(target=_worker, daemon=True).start()

    def _build_both_click(self):
        if self.is_building:
            return
        self._set_building(True, "Building APK and IPA packages...")
        self.console_textbox.delete("1.0", "end")

        def _worker():
            res = self.service.build_service.build_both(log_callback=self._append_log)
            status = "All Builds Completed!"
            self._set_building(False, status)

        threading.Thread(target=_worker, daemon=True).start()

    def _open_output_folder(self):
        rel_dir = PathHelper.get_tool_root() / "output" / "releases"
        rel_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(rel_dir))
        except Exception as e:
            logger.error("Could not open folder %s: %s", rel_dir, e)
