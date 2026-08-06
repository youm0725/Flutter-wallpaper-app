import unittest
import tempfile
from pathlib import Path
from app.core.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def test_default_config_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.toml"
            manager = ConfigManager(config_path=config_path)
            
            self.assertTrue(config_path.exists())
            self.assertEqual(manager.get("app", "name"), "Wallpaper Asset Manager")
            self.assertEqual(manager.get("app", "theme"), "Dark")

    def test_config_update_and_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.toml"
            manager = ConfigManager(config_path=config_path)
            
            manager.set("app", "theme", "Light")
            self.assertEqual(manager.get("app", "theme"), "Light")
            
            # Reload from disk to verify persistence
            reloaded_manager = ConfigManager(config_path=config_path)
            self.assertEqual(reloaded_manager.get("app", "theme"), "Light")

if __name__ == "__main__":
    unittest.main()
