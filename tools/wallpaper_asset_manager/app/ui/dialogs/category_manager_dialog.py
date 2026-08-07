import customtkinter as ctk
from typing import Callable, Optional
from tkinter import messagebox

class CategoryManagerDialog(ctk.CTkToplevel):
    """Modal dialog for creating, editing, and deleting wallpaper categories."""
    
    def __init__(self, master, library_service, on_refresh_callback: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.library_service = library_service
        self.on_refresh_callback = on_refresh_callback
        
        self.title("📂 Category Manager")
        self.geometry("620x520")
        self.minsize(560, 450)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        
        title_lbl = ctk.CTkLabel(
            hdr,
            text="📂 Wallpaper Categories Manager",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        title_lbl.pack(side="left")
        
        # Add New Category Frame (Top Form)
        add_card = ctk.CTkFrame(self, corner_radius=8, fg_color=("gray90", "gray17"))
        add_card.grid(row=1, column=0, sticky="ew", padx=20, pady=8)
        add_card.columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(add_card, text="Add New Category", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))
        
        # Form Fields
        self.entry_id = ctk.CTkEntry(add_card, placeholder_text="ID (e.g. amoled, nature)")
        self.entry_id.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        
        self.entry_name = ctk.CTkEntry(add_card, placeholder_text="Display Name (e.g. AMOLED)")
        self.entry_name.grid(row=1, column=1, padx=8, pady=4, sticky="ew")
        
        self.entry_icon = ctk.CTkEntry(add_card, placeholder_text="Icon (e.g. dark_mode)")
        self.entry_icon.grid(row=1, column=2, padx=8, pady=4, sticky="ew")
        
        btn_add = ctk.CTkButton(
            add_card,
            text="➕ Add",
            width=80,
            fg_color="#10B981",
            hover_color="#059669",
            command=self._on_add_category
        )
        btn_add.grid(row=1, column=3, padx=8, pady=4)
        
        self.entry_desc = ctk.CTkEntry(add_card, placeholder_text="Category description (optional)")
        self.entry_desc.grid(row=2, column=0, columnspan=3, padx=8, pady=(4, 10), sticky="ew")
        
        # Existing Categories List (Scrollable)
        list_lbl = ctk.CTkLabel(self, text="Existing Categories:", font=ctk.CTkFont(weight="bold"), anchor="w")
        list_lbl.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 4))
        
        self.list_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_scroll.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self.list_scroll.columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        self._refresh_categories_list()

    def _refresh_categories_list(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()

        categories = self.library_service.categories
        if not categories:
            empty_lbl = ctk.CTkLabel(
                self.list_scroll,
                text="No categories created yet. Add your first category above!",
                font=ctk.CTkFont(size=13),
                text_color="gray50"
            )
            empty_lbl.pack(pady=30)
            return

        for cat in categories:
            cat_id = cat.get("id", "")
            cat_name = cat.get("name", cat_id.capitalize())
            cat_icon = cat.get("icon", "folder")
            cat_desc = cat.get("description", "")

            row_frame = ctk.CTkFrame(self.list_scroll, fg_color=("gray95", "gray18"), corner_radius=6, height=44)
            row_frame.pack(fill="x", pady=3)
            
            info_lbl = ctk.CTkLabel(
                row_frame,
                text=f"📂  {cat_name} ({cat_id})",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            info_lbl.pack(side="left", padx=12, pady=8)
            
            if cat_desc:
                desc_lbl = ctk.CTkLabel(
                    row_frame,
                    text=f"•  {cat_desc}",
                    font=ctk.CTkFont(size=11),
                    text_color=("gray40", "gray60"),
                    anchor="w"
                )
                desc_lbl.pack(side="left", padx=8)

            btn_del = ctk.CTkButton(
                row_frame,
                text="🗑️ Delete",
                width=75,
                height=26,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=lambda c_id=cat_id: self._on_delete_category(c_id)
            )
            btn_del.pack(side="right", padx=10, pady=8)

    def _on_add_category(self):
        raw_id = self.entry_id.get().strip().lower()
        name = self.entry_name.get().strip()
        icon = self.entry_icon.get().strip() or "folder"
        desc = self.entry_desc.get().strip()

        if not raw_id:
            messagebox.showwarning("Input Error", "Please enter a valid Category ID (e.g. amoled, cars).", parent=self)
            return

        if not name:
            name = raw_id.capitalize()

        if self.library_service.add_category(raw_id, name, desc):
            # Also update icon field in last added category
            for c in self.library_service.categories:
                if c.get("id") == raw_id:
                    c["icon"] = icon
                    break

            self.library_service.save_all_to_disk()

            self.entry_id.delete(0, "end")
            self.entry_name.delete(0, "end")
            self.entry_icon.delete(0, "end")
            self.entry_desc.delete(0, "end")

            self._refresh_categories_list()

            if self.on_refresh_callback:
                self.on_refresh_callback()

            messagebox.showinfo("Success", f"Category '{name}' ({raw_id}) created successfully!", parent=self)
        else:
            messagebox.showerror("Error", f"Category ID '{raw_id}' already exists.", parent=self)

    def _on_delete_category(self, cat_id: str):
        if messagebox.askyesno("Confirm Delete", f"Delete category '{cat_id}'? Wallpapers under this category will be reassigned.", parent=self):
            self.library_service.delete_category(cat_id)
            self.library_service.save_all_to_disk()
            self._refresh_categories_list()

            if self.on_refresh_callback:
                self.on_refresh_callback()
