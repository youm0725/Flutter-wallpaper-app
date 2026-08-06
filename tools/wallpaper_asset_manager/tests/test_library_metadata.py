import unittest
import tempfile
from pathlib import Path
from app.services.metadata_service import MetadataService
from app.services.history_service import HistoryService
from app.services.library_service import LibraryService
from app.services.metadata_validation_service import MetadataValidationService

class TestLibraryMetadata(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

        self.metadata_service = MetadataService(workspace_root=self.tmp_path)
        self.history_service = HistoryService()

        # Seed initial test wallpapers
        initial_wallpapers = [
            {
                "id": "nature_01",
                "title": "Misty Alpine Forest",
                "category": "nature",
                "thumbnailPath": "assets/wallpapers/thumbnails/nature/misty_alpine_forest.webp",
                "imagePath": "assets/wallpapers/full/nature/misty_alpine_forest.webp",
                "resolution": "1080x1920",
                "fileSize": "11 KB",
                "tags": ["fog", "trees", "mountains"],
                "isFeatured": True,
                "collections": ["Editor's Choice"],
                "description": "A foggy forest landscape."
            },
            {
                "id": "cars_01",
                "title": "Supercar Midnight Drift",
                "category": "cars",
                "thumbnailPath": "assets/wallpapers/thumbnails/cars/supercar_midnight_drift.webp",
                "imagePath": "assets/wallpapers/full/cars/supercar_midnight_drift.webp",
                "resolution": "1080x1920",
                "fileSize": "15 KB",
                "tags": ["supercar", "drift", "night"],
                "isFeatured": False,
                "collections": [],
                "description": "Retro supercar drift."
            }
        ]
        self.metadata_service.save_wallpapers_json(initial_wallpapers, create_backup_first=False)

        self.library_service = LibraryService(self.metadata_service, self.history_service)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_unique_id_generation(self):
        new_id = self.library_service.generate_next_id("nature")
        self.assertEqual(new_id, "nature_02")
        self.assertNotIn(new_id, [w["id"] for w in self.library_service.wallpapers])

    def test_update_and_undo(self):
        orig_title = self.library_service.wallpapers[0]["title"]
        self.library_service.update_wallpaper("nature_01", {"title": "Updated Misty Forest"})
        self.assertEqual(self.library_service.wallpapers[0]["title"], "Updated Misty Forest")

        # Perform Undo
        undone = self.library_service.undo()
        self.assertTrue(undone)
        self.assertEqual(self.library_service.wallpapers[0]["title"], orig_title)

    def test_bulk_update(self):
        updated_count = self.library_service.bulk_update(
            target_ids=["nature_01", "cars_01"],
            add_tags=["premium", "hd"],
            set_featured=True
        )
        self.assertEqual(updated_count, 2)
        self.assertTrue(all(w["isFeatured"] for w in self.library_service.wallpapers))
        self.assertTrue(all("premium" in w["tags"] for w in self.library_service.wallpapers))

    def test_category_crud(self):
        self.library_service.add_category("cyber", "Cyberpunk Aesthetics")
        self.assertTrue(any(c["id"] == "cyber" for c in self.library_service.categories))

        self.library_service.delete_category("cars", reassign_category="general")
        self.assertFalse(any(c["id"] == "cars" for c in self.library_service.categories))
        cars_item = self.library_service.get_wallpaper_by_id("cars_01")
        self.assertEqual(cars_item["category"], "general")

    def test_metadata_backup_creation(self):
        backup_path = self.metadata_service.create_backup(label="unit_test")
        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / "wallpapers.json").exists())

    def test_metadata_validation(self):
        is_valid, issues = MetadataValidationService.validate_metadata(
            self.library_service.wallpapers,
            self.library_service.categories,
            self.library_service.collections,
            workspace_root=self.tmp_path
        )
        # Disk files do not exist in temp dir, so errors should be flagged
        self.assertFalse(is_all_valid if 'is_all_valid' in locals() else is_valid)
        self.assertTrue(len(issues) > 0)

if __name__ == "__main__":
    unittest.main()
