import unittest
import tempfile
from pathlib import Path

from app.services.flutter_build_service import FlutterBuildService

class TestFlutterBuildService(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.build_service = FlutterBuildService(workspace_root=self.tmp_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_initialization(self):
        self.assertIsNotNone(self.build_service.releases_dir)
        self.assertTrue(self.build_service.releases_dir.exists())

    def test_run_flutter_cmd(self):
        logs = []
        code, output = self.build_service._run_flutter_cmd(["--version"], log_callback=lambda l: logs.append(l))
        self.assertIsNotNone(code)
        self.assertTrue(len(logs) > 0)

if __name__ == "__main__":
    unittest.main()
