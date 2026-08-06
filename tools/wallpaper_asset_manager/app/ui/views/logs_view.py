import customtkinter as ctk
from app.ui.widgets.card_widget import CardWidget
from app.utils.path_helper import PathHelper

class LogsView(ctk.CTkFrame):
    def __init__(self, master, service, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text="📜 System Execution Logs",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        card = CardWidget(self, title="Runtime Log File", subtitle="Live contents of logs/app.log")
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        btn_bar = ctk.CTkFrame(card.container, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            btn_bar,
            text="🔄 Refresh Logs",
            width=120,
            command=self.reload_logs
        )
        refresh_btn.pack(side="left")

        log_path = PathHelper.get_logs_dir() / "app.log"
        ctk.CTkLabel(
            btn_bar,
            text=f"Log path: {log_path}",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).pack(side="left", padx=15)

        self.log_textbox = ctk.CTkTextbox(
            card.container,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none"
        )
        self.log_textbox.pack(fill="both", expand=True)

        self.reload_logs()

    def reload_logs(self):
        log_file = PathHelper.get_logs_dir() / "app.log"
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")

        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_textbox.insert("1.0", content)
            except Exception as e:
                self.log_textbox.insert("1.0", f"Error reading log file: {e}")
        else:
            self.log_textbox.insert("1.0", "No log file found yet.")

        self.log_textbox.configure(state="disabled")
