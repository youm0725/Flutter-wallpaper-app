import unittest
import tempfile
from pathlib import Path

from app.services.master_backup_service import MasterBackupService
from app.services.master_restore_service import MasterRestoreService
from app.services.metadata_service import MetadataService

class TestBackupRestoreEngine(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

        # Seed mock repository
        meta_service = MetadataService(workspace_root=self.tmp_path)
        meta_service.save_wallpapers_json([
            {"id": "test_01", "title": "Test Wallpaper", "category": "nature"}
        ], create_backup_first=False)

        (self.tmp_path / "assets" / "wallpapers" / "full").mkdir(parents=True)
        (self.tmp_path / "assets" / "wallpapers" / "full" / "test.webp").write_bytes(b"mock_data")

        self.backup_service = MasterBackupService(workspace_root=self.tmp_path)
        self.restore_service = MasterRestoreService(workspace_root=self.tmp_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_create_and_list_backup(self):
        ok, msg, backup_path = self.backup_service.create_backup(reason="Unit Test")
        self.assertTrue(ok)
        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / "backup_info.json").exists())

        backups = self.backup_service.list_backups()
        self.assertGreaterEqual(len(backups), 1)
        self.assertEqual(backups[0]["reason"], "Unit Test")

    def test_restore_preview_diff(self):
        ok, msg, backup_path = self.backup_service.create_backup(reason="Before Edit")
        preview = self.restore_service.preview_restore(backup_path)
        
        self.assertIn("current_wallpapers_count", preview)
        self.assertIn("diff_summary", preview)
        self.assertEqual(preview["current_wallpapers_count"], 1)

    def test_emergency_backup_and_restore(self):
        ok, msg, backup_path = self.backup_service.create_backup(reason="Original Snapshot")
        
        # Modify workspace metadata
        meta_service = MetadataService(workspace_root=self.tmp_path)
        meta_service.save_wallpapers_json([], create_backup_first=False)
        self.assertEqual(len(meta_service.load_wallpapers_json()), 0)

        # Restore from backup
        res_ok, res_msg = self.restore_service.restore_backup(backup_path, mode="Complete", create_emergency_backup=True)
        self.assertTrue(res_ok)
        self.assertEqual(len(meta_service.load_wallpapers_json()), 1)

if __name__ == "__main__":
    unittest.main()
