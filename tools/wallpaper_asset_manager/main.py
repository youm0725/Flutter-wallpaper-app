import sys
from pathlib import Path

# Add manager root directory to python sys.path
MANAGER_ROOT = Path(__file__).resolve().parent
if str(MANAGER_ROOT) not in sys.path:
    sys.path.insert(0, str(MANAGER_ROOT))

from PIL import Image, WebPImagePlugin, PngImagePlugin, JpegImagePlugin
from app.core.logger import setup_logging
from app.core.config_manager import ConfigManager
from app.services.app_service import AppService
from app.ui.main_window import MainWindow

def main():
    # Initialize logging system
    logger = setup_logging()
    logger.info("Starting Wallpaper Asset Manager v1.0.0...")

    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Initialize application service
    app_service = AppService(config_manager)

    # Launch GUI main window
    app = MainWindow(app_service)
    app.mainloop()
    
    logger.info("Wallpaper Asset Manager shut down cleanly.")

if __name__ == "__main__":
    main()
