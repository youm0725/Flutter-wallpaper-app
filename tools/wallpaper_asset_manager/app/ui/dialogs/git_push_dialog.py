import threading
import customtkinter as ctk
from typing import Optional
from app.core.logger import get_logger

logger = get_logger("GitPushDialog")

class GitPushDialog(ctk.CTkToplevel):
    """Modal dialog for committing and pushing workspace changes directly to GitHub remote repository."""
    
    def __init__(self, master, app_service):
        super().__init__(master)
        self.service = app_service
        
        self.title("🚀 GitHub Sync & Repository Push")
        self.geometry("780x560")
        self.minsize(680, 460)
        self.is_running = False
        
        self.transient(master)
        self.grab_set()

        # Configure Grid Layout
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Title Banner
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(16, 8), sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text="🚀 Push App & Asset Changes to GitHub Repository",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Sync all your wallpaper gallery updates, categories, metadata, and code directly to remote GitHub main branch.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        ).pack(anchor="w", pady=(2, 0))

        # Commit Message Input Frame
        msg_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray17"), corner_radius=8)
        msg_frame.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        msg_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            msg_frame,
            text="Commit Message:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

        self.commit_entry = ctk.CTkEntry(
            msg_frame,
            placeholder_text="Updated wallpaper gallery assets, categories & metadata"
        )
        self.commit_entry.insert(0, "Updated wallpaper gallery assets, categories & metadata via Asset Manager")
        self.commit_entry.grid(row=0, column=1, padx=(4, 12), pady=12, sticky="ew")

        # Action Button Row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.btn_push = ctk.CTkButton(
            btn_frame,
            text="🚀 Commit & Push to GitHub",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=38,
            command=self._start_push
        )
        self.btn_push.pack(side="left", padx=(0, 10))

        self.btn_close = ctk.CTkButton(
            btn_frame,
            text="Close",
            font=ctk.CTkFont(size=12),
            fg_color="gray50",
            hover_color="gray40",
            height=38,
            command=self.destroy
        )
        self.btn_close.pack(side="right")

        # Live Console Output Box
        console_frame = ctk.CTkFrame(self)
        console_frame.grid(row=3, column=0, padx=20, pady=8, sticky="nsew")
        console_frame.grid_rowconfigure(1, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            console_frame,
            text="Git Terminal Log:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 4), sticky="w")

        self.console_textbox = ctk.CTkTextbox(
            console_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.console_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Load initial Git status
        self._load_git_status()

    def _append_log(self, text: str):
        """Thread-safe log appender."""
        def _update():
            self.console_textbox.insert("end", text)
            self.console_textbox.see("end")
        self.after(0, _update)

    def _load_git_status(self):
        status = self.service.git_service.get_git_status()
        self.console_textbox.delete("1.0", "end")
        self.console_textbox.insert("1.0", f"Active Branch: {status['branch']}\n")
        self.console_textbox.insert("end", f"Uncommitted Changes: {status['uncommitted_count']} files\n")
        if status['changed_files']:
            self.console_textbox.insert("end", "\nChanged Files List:\n")
            for f in status['changed_files'][:15]:
                self.console_textbox.insert("end", f"  • {f}\n")
            if len(status['changed_files']) > 15:
                self.console_textbox.insert("end", f"  ... and {len(status['changed_files']) - 15} more files.\n")
        else:
            self.console_textbox.insert("end", "\nWorking tree is clean. Ready to push latest commits to remote repository.\n")

    def _start_push(self):
        if self.is_running:
            return

        self.is_running = True
        self.btn_push.configure(state="disabled")
        msg = self.commit_entry.get().strip()

        def _worker():
            res = self.service.git_service.commit_and_push(commit_message=msg, log_callback=self._append_log)
            def _finish():
                self.is_running = False
                self.btn_push.configure(state="normal")
                status = "Pushed to GitHub Successfully!" if res["success"] else "Push Failed"
                self.service.update_status(f"✓ {res['message']}")
            self.after(0, _finish)

        threading.Thread(target=_worker, daemon=True).start()
