import unittest
import tempfile
from pathlib import Path
from PIL import Image

from app.services.asset_validator_service import AssetValidatorService
from app.services.size_analyzer_service import SizeAnalyzerService
from app.services.checklist_manager_service import ChecklistManagerService
from app.services.release_validator_service import ReleaseValidatorService

class TestReleaseValidationEngine(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

        # Mock asset directory structure
        self.full_dir = self.tmp_path / "assets" / "wallpapers" / "full" / "nature"
        self.thumb_dir = self.tmp_path / "assets" / "wallpapers" / "thumbnails" / "nature"
        self.full_dir.mkdir(parents=True)
        self.thumb_dir.mkdir(parents=True)

        # Save valid WebP image
        img = Image.new("RGB", (1080, 1920), color=(100, 200, 100))
        img.save(self.full_dir / "test_wallpaper.webp", "WEBP")
        img.save(self.thumb_dir / "test_wallpaper.webp", "WEBP")

        # Mock metadata directory
        meta_dir = self.tmp_path / "assets" / "metadata"
        meta_dir.mkdir(parents=True)
        (meta_dir / "wallpapers.json").write_text("[]", encoding="utf-8")
        (meta_dir / "categories.json").write_text("[]", encoding="utf-8")
        (meta_dir / "collections.json").write_text("[]", encoding="utf-8")

        # Mock pubspec.yaml
        (self.tmp_path / "pubspec.yaml").write_text("name: app\nassets:\n  - assets/wallpapers/full/\n", encoding="utf-8")
        (self.tmp_path / "lib").mkdir()

        self.validator = ReleaseValidatorService(workspace_root=self.tmp_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_asset_validator_audit(self):
        issues = AssetValidatorService.audit_assets(workspace_root=self.tmp_path)
        # Valid 1080x1920 WebP image should pass cleanly
        self.assertEqual(len(issues), 0)

    def test_storage_size_analyzer(self):
        res = SizeAnalyzerService.analyze_storage_size(workspace_root=self.tmp_path)
        self.assertIn("total_size_mb", res)
        self.assertGreaterEqual(res["total_size_mb"], 0.0)

    def test_checklist_manager(self):
        svc = ChecklistManagerService()
        self.assertTrue(len(svc.items) > 0)
        first_id = svc.items[0]["id"]
        init_state = svc.items[0]["completed"]
        svc.toggle_item(first_id)
        self.assertNotEqual(svc.items[0]["completed"], init_state)

    def test_full_release_validation_run(self):
        results = self.validator.run_full_validation()
        self.assertIn("total_checks", results)
        self.assertIn("pass_count", results)
        self.assertIn("issues", results)

        # Verify Report File Exports exist
        html_reports = list(self.validator.reports_dir.glob("*.html"))
        json_reports = list(self.validator.reports_dir.glob("*.json"))
        txt_reports = list(self.validator.reports_dir.glob("*.txt"))

        self.assertTrue(len(html_reports) > 0)
        self.assertTrue(len(json_reports) > 0)
        self.assertTrue(len(txt_reports) > 0)

if __name__ == "__main__":
    unittest.main()
