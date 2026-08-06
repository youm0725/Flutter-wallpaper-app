import unittest
import tempfile
from pathlib import Path
from app.core.crash_handler import CrashHandler
from app.utils.path_helper import PathHelper

class TestFinalReleasePolish(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_crash_handler_report(self):
        report_file = CrashHandler.create_crash_report(RuntimeError, RuntimeError("Test crash"), "Dummy traceback")
        self.assertTrue(report_file.exists())
        self.assertIn("CRASH REPORT", report_file.read_text(encoding="utf-8"))

    def test_documentation_files_exist(self):
        tool_root = PathHelper.get_tool_root()
        readme = tool_root / "README.md"
        user_guide = tool_root / "USER_GUIDE.md"
        build_script = tool_root / "build_executable.py"

        self.assertTrue(readme.exists())
        self.assertTrue(user_guide.exists())
        self.assertTrue(build_script.exists())

if __name__ == "__main__":
    unittest.main()
