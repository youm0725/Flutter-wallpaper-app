import unittest
import tempfile
from pathlib import Path
from app.services.cache_service import CacheService
from app.services.statistics_service import StatisticsService
from app.services.metadata_service import MetadataService

class TestDashboardAnalytics(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

        # Seed test metadata files
        meta_service = MetadataService(workspace_root=self.tmp_path)
        meta_service.save_wallpapers_json([
            {
                "id": "nature_01",
                "title": "Forest",
                "category": "nature",
                "resolution": "1080x1920",
                "fileSize": "12 KB",
                "tags": ["trees"],
                "isFeatured": True
            }
        ], create_backup_first=False)

        self.cache_service = CacheService()
        self.stats_service = StatisticsService(workspace_root=self.tmp_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_cache_service(self):
        sample = {"test": 123}
        self.cache_service.save_cache(sample)
        loaded = self.cache_service.load_cache()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["test"], 123)

        self.cache_service.invalidate_cache()
        self.assertIsNone(self.cache_service.load_cache())

    def test_statistics_calculation(self):
        stats = self.stats_service.get_dashboard_analytics(force_refresh=True)
        self.assertEqual(stats["total_wallpapers"], 1)
        self.assertEqual(stats["featured_count"], 1)
        self.assertIn("category_breakdown", stats)
        self.assertIn("common_resolution", stats)
        self.assertEqual(stats["common_resolution"], "1080x1920")

if __name__ == "__main__":
    unittest.main()
