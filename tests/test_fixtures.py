"""Execute synthetic application checks; these do not measure model skill selection."""
import importlib.util
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


class ReuseFixtures(unittest.TestCase):
    def run_fixture(self, name, command):
        result = subprocess.run(command, cwd=FIXTURES / name, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node 22.6+ unavailable")
    def test_typescript_application_boundaries(self):
        self.run_fixture("genui", ["node", "--experimental-strip-types", "--test", "test/flow.test.ts"])

    @unittest.skipUnless(importlib.util.find_spec("fastapi") and importlib.util.find_spec("httpx"), "install Python fixture requirements in an isolated environment")
    def test_python_fastapi_boundaries(self):
        self.run_fixture("python-service", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])

    def test_static_publishing_without_ai(self):
        self.run_fixture("writing-site", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
