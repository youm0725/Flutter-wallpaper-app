from dataclasses import dataclass, field
from typing import List

@dataclass
class AppState:
    """Holds global application state variables."""
    active_view: str = "Dashboard"
    status_message: str = "Application Ready"
    theme_mode: str = "Dark"
    project_path: str = ""
    processing_status: str = "Idle"
    loaded_items_count: int = 0
