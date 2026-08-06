from app.core.config_manager import ConfigManager
from app.core.logger import get_logger
from app.models.app_state import AppState
from app.utils.path_helper import PathHelper

logger = get_logger("AppService")

class AppService:
    """Service layer managing application state, configuration, and background events."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        saved_theme = self.config_manager.get("app", "theme", "Dark")
        self.state = AppState(
            theme_mode=saved_theme,
            project_path=str(PathHelper.get_workspace_root())
        )

    def set_theme(self, theme_name: str) -> None:
        """Updates active theme and persists setting in config.toml."""
        self.state.theme_mode = theme_name
        self.config_manager.set("app", "theme", theme_name)
        logger.info("Application theme set to: %s", theme_name)

    def update_status(self, message: str) -> None:
        """Updates global status bar message."""
        self.state.status_message = message
        logger.info("Status updated: %s", message)
