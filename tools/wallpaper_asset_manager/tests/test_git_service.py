import unittest
import tempfile
from pathlib import Path

from app.services.git_service import GitService

class TestGitService(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.git_service = GitService(workspace_root=self.tmp_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_git_status_initialization(self):
        status = self.git_service.get_git_status()
        self.assertIn("is_clean", status)
        self.assertIn("branch", status)

if __name__ == "__main__":
    unittest.main()
