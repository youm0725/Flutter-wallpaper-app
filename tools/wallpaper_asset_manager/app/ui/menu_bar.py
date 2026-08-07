import tkinter as tk
from typing import Callable, Optional

class MenuBar:
    """Native menu bar configuration."""
    
    def __init__(
        self,
        root: tk.Tk,
        on_navigate: Optional[Callable[[str], None]] = None,
        on_theme: Optional[Callable[[str], None]] = None
    ):
        self.root = root
        self.on_navigate = on_navigate or (lambda view: None)
        self.on_theme = on_theme or (lambda theme: None)
        
        self.menubar = tk.Menu(root)
        
        # File Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Dashboard", command=lambda: self.on_navigate("Dashboard"))
        file_menu.add_command(label="Import Folder...", command=lambda: self.on_navigate("Import"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        # View Menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="Dark Theme", command=lambda: self.on_theme("Dark"))
        view_menu.add_command(label="Light Theme", command=lambda: self.on_theme("Light"))
        view_menu.add_command(label="System Theme", command=lambda: self.on_theme("System"))
        view_menu.add_separator()
        view_menu.add_command(label="Logs", command=lambda: self.on_navigate("Logs"))
        self.menubar.add_cascade(label="View", menu=view_menu)

        # Tools Menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        tools_menu.add_command(label="Process Assets", command=lambda: self.on_navigate("Process"))
        tools_menu.add_command(label="Edit Metadata", command=lambda: self.on_navigate("Metadata"))
        tools_menu.add_command(label="Validate Schema", command=lambda: self.on_navigate("Validation"))
        self.menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Settings", command=lambda: self.on_navigate("Settings"))
        help_menu.add_separator()
        help_menu.add_command(label="About", command=lambda: self.on_navigate("About"))
        self.menubar.add_cascade(label="Help", menu=help_menu)

        root.config(menu=self.menubar)
