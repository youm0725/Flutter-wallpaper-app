import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    """Bottom status bar displaying system status and workspace path."""
    
    def __init__(self, master, project_path: str = "", **kwargs):
        super().__init__(master, height=28, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Status Message (Left)
        self.status_label = ctk.CTkLabel(
            self,
            text="● Application Ready",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70")
        )
        self.status_label.grid(row=0, column=0, padx=12, pady=4, sticky="w")
        
        # Workspace Path (Center)
        self.path_label = ctk.CTkLabel(
            self,
            text=f"Workspace: {project_path}",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        self.path_label.grid(row=0, column=1, padx=12, pady=4, sticky="w")
        
        # Processing Status (Right)
        self.proc_label = ctk.CTkLabel(
            self,
            text="Idle | Phase T1.1",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        self.proc_label.grid(row=0, column=2, padx=12, pady=4, sticky="e")

    def set_status(self, message: str):
        self.status_label.configure(text=f"● {message}")

    def set_proc_status(self, proc_text: str):
        self.proc_label.configure(text=proc_text)
