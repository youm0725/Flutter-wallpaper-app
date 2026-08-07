import unittest
import tempfile
from pathlib import Path
from PIL import Image

from app.models.imported_wallpaper import ImportedWallpaperItem
from app.models.processing_task import ProcessingTask
from app.services.image_processing_engine import ImageProcessingEngine, QUALITY_PRESETS
from app.services.migration_service import MigrationService
from app.services.cleanup_service import CleanupService

class TestImageProcessingEngine(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

        self.input_dir = self.tmp_path / "input"
        self.input_dir.mkdir()
        self.output_dir = self.tmp_path / "output"

        # Create test raw input image (2000x3000)
        self.raw_img_path = self.input_dir / "Dark Mountain Peak (2026).JPG"
        img = Image.new("RGB", (2000, 3000), color=(50, 100, 150))
        img.save(self.raw_img_path, "JPEG")
        self.original_mtime = self.raw_img_path.stat().st_mtime

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_clean_filename(self):
        raw = "Dark Mountain Peak (2026).JPG"
        clean = ImageProcessingEngine.clean_filename(raw)
        self.assertEqual(clean, "dark_mountain_peak_2026.webp")

    def test_unique_path_resolution(self):
        target_dir = self.tmp_path / "test_unique"
        target_dir.mkdir()
        
        path1 = ImageProcessingEngine.resolve_unique_path(target_dir, "test.webp")
        self.assertEqual(path1.name, "test.webp")
        path1.touch()

        path2 = ImageProcessingEngine.resolve_unique_path(target_dir, "test.webp")
        self.assertEqual(path2.name, "test-2.webp")

    def test_image_processing_pipeline(self):
        item = ImportedWallpaperItem(
            id="test1",
            file_path=self.raw_img_path,
            filename=self.raw_img_path.name,
            extension=".jpg",
            file_size_bytes=self.raw_img_path.stat().st_size,
            file_size_formatted="2.5 MB"
        )
        task = ProcessingTask(id="task_test1", imported_item=item, category="nature")

        # Process with High preset
        success = ImageProcessingEngine.process_wallpaper(
            task,
            preset="High",
            max_width=1440,
            max_height=3200,
            output_root=self.output_dir
        )

        self.assertTrue(success)
        self.assertEqual(task.status, "Completed")
        self.assertIsNotNone(task.output_full_path)
        self.assertTrue(task.output_full_path.exists())

        # Verify output format is WebP
        self.assertEqual(task.output_full_path.suffix, ".webp")

        # Verify image dimensions bounded by 1440x3200
        with Image.open(task.output_full_path) as full_img:
            w, h = full_img.size
            self.assertLessEqual(w, 1440)
            self.assertLessEqual(h, 3200)

        # Verify Original File Remains UNTOUCHED
        self.assertTrue(self.raw_img_path.exists())
        self.assertEqual(self.raw_img_path.stat().st_mtime, self.original_mtime)

    def test_migration_and_cleanup_services(self):
        migration_service = MigrationService(workspace_root=self.tmp_path)
        cleanup_service = CleanupService(workspace_root=self.tmp_path)

        detect = migration_service.detect_legacy_assets()
        self.assertFalse(detect["needs_migration"])

        orphans = cleanup_service.find_orphaned_assets()
        self.assertEqual(orphans["orphan_count"], 0)

if __name__ == "__main__":
    unittest.main()
