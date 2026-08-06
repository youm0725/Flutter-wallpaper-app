import unittest
import tempfile
from pathlib import Path
from PIL import Image

from app.services.validation_service import ValidationService
from app.services.thumbnail_service import ThumbnailService
from app.services.import_service import ImportService

class TestImportService(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        
        # Create a valid test image (1080x1920)
        self.valid_img_path = self.tmp_path / "valid_wallpaper.jpg"
        img = Image.new("RGB", (1080, 1920), color=(100, 150, 200))
        img.save(self.valid_img_path, "JPEG")

        # Create a low res test image (500x500)
        self.lowres_img_path = self.tmp_path / "lowres_wallpaper.png"
        img2 = Image.new("RGB", (500, 500), color=(200, 50, 50))
        img2.save(self.lowres_img_path, "PNG")

        self.thumb_service = ThumbnailService()
        self.import_service = ImportService(thumbnail_service=self.thumb_service)

    def tearDown(self):
        self.thumb_service.shutdown()
        try:
            self.tmpdir.cleanup()
        except Exception:
            pass

    def test_validation_service(self):
        is_valid, status, msgs, w, h, res_str, aspect_str, creation_str = ValidationService.validate_file(self.valid_img_path)
        self.assertTrue(is_valid)
        self.assertEqual(status, "Valid")
        self.assertEqual(w, 1080)
        self.assertEqual(h, 1920)
        self.assertEqual(res_str, "1080x1920")
        self.assertIn("9:16", aspect_str)

    def test_low_res_warning(self):
        is_valid, status, msgs, w, h, res_str, aspect_str, creation_str = ValidationService.validate_file(self.lowres_img_path)
        self.assertTrue(is_valid)
        self.assertEqual(status, "Warning")
        self.assertTrue(any("Low resolution" in m for m in msgs))

    def test_import_service_workflow(self):
        items = self.import_service.import_files([self.valid_img_path, self.lowres_img_path])
        self.assertEqual(len(items), 2)
        
        stats = self.import_service.get_stats()
        self.assertEqual(stats["total_count"], "2")
        self.assertEqual(stats["selected_count"], "0")
        
        self.import_service.select_all()
        stats = self.import_service.get_stats()
        self.assertEqual(stats["selected_count"], "2")

        # Delete selected
        self.import_service.delete_selected()
        self.assertEqual(len(self.import_service.items), 0)

if __name__ == "__main__":
    unittest.main()
