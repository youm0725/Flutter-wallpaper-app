from app.core.config_manager import ConfigManager
from app.core.logger import get_logger
from app.models.app_state import AppState
from app.utils.path_helper import PathHelper
from app.services.metadata_service import MetadataService
from app.services.history_service import HistoryService
from app.services.library_service import LibraryService
from app.services.migration_service import MigrationService
from app.services.cleanup_service import CleanupService
from app.services.flutter_build_service import FlutterBuildService
from app.services.git_service import GitService

logger = get_logger("AppService")

class AppService:
    """Service layer managing application state, configuration, builds, git sync, migration, and events."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        saved_theme = self.config_manager.get("app", "theme", "Dark")
        self.state = AppState(
            theme_mode=saved_theme,
            project_path=str(PathHelper.get_workspace_root())
        )
        self.metadata_service = MetadataService()
        self.history_service = HistoryService()
        self.library_service = LibraryService(self.metadata_service, self.history_service)
        self.migration_service = MigrationService()
        self.cleanup_service = CleanupService()
        self.build_service = FlutterBuildService()
        self.git_service = GitService()

    def set_theme(self, theme_name: str) -> None:
        """Updates active theme and persists setting in config.toml."""
        self.state.theme_mode = theme_name
        self.config_manager.set("app", "theme", theme_name)
        logger.info("Application theme set to: %s", theme_name)

    def update_status(self, message: str) -> None:
        """Updates global status bar message."""
        self.state.status_message = message
        logger.info("Status updated: %s", message)
