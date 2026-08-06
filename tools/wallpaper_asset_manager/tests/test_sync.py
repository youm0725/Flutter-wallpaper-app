import unittest
import tempfile
from pathlib import Path
from app.services.flutter_detector_service import FlutterDetectorService
from app.services.sync_backup_service import SyncBackupService
from app.services.sync_service import SyncService

class TestFlutterSyncEngine(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

        # Mock Flutter workspace structure
        (self.tmp_path / "lib").mkdir()
        pubspec = self.tmp_path / "pubspec.yaml"
        pubspec.write_text(
            "name: wallpaper_app\nassets:\n  - assets/wallpapers/full/\n  - assets/wallpapers/thumbnails/\n  - assets/metadata/\n",
            encoding="utf-8"
        )

        (self.tmp_path / "assets" / "wallpapers" / "full" / "nature").mkdir(parents=True)
        (self.tmp_path / "assets" / "wallpapers" / "thumbnails" / "nature").mkdir(parents=True)
        (self.tmp_path / "assets" / "metadata").mkdir(parents=True)

        self.detector = FlutterDetectorService(workspace_root=self.tmp_path)
        self.backup_service = SyncBackupService(workspace_root=self.tmp_path)
        self.sync_service = SyncService(workspace_root=self.tmp_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_flutter_workspace_detector(self):
        is_valid, msg = self.detector.is_valid_flutter_project()
        self.assertTrue(is_valid)

        pubspec_ok, warnings = self.detector.verify_pubspec_assets()
        self.assertTrue(pubspec_ok)
        self.assertEqual(len(warnings), 0)

    def test_pre_sync_backup_and_restore(self):
        # Create a test asset file in mock workspace
        test_asset = self.tmp_path / "assets" / "wallpapers" / "full" / "nature" / "test.webp"
        test_asset.write_bytes(b"mock_webp_data")

        backup_path = self.backup_service.create_sync_backup(label="test_backup")
        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / "assets" / "wallpapers" / "full" / "nature" / "test.webp").exists())

        # Delete asset from workspace
        test_asset.unlink()
        self.assertFalse(test_asset.exists())

        # Restore from backup
        restored = self.backup_service.restore_backup(backup_path)
        self.assertTrue(restored)
        self.assertTrue(test_asset.exists())

    def test_dry_run_calculation(self):
        dry_run = self.sync_service.calculate_dry_run()
        self.assertIn("added_count", dry_run)
        self.assertIn("projected_size_mb", dry_run)
        self.assertFalse(dry_run["exceeds_limit"])

if __name__ == "__main__":
    unittest.main()
