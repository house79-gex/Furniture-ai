"""
Test export Xilog da furniture_core.
"""

import os
import sys
import tempfile
import unittest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from furniture_core.models import normalize_params
from furniture_core.xilog_export import generate_xilog_for_cabinet, save_xilog_for_cabinet


class TestXilogExport(unittest.TestCase):
    def test_generate_contains_panels(self):
        code = generate_xilog_for_cabinet(normalize_params({"num_ripiani": 1}))
        self.assertIn("Fianco_SX", code)
        self.assertIn("M30", code)
        self.assertIn("G90", code)

    def test_save_file(self):
        with tempfile.NamedTemporaryFile(suffix=".xilog", delete=False) as tmp:
            path = tmp.name
        try:
            ok = save_xilog_for_cabinet(normalize_params({}), path)
            self.assertTrue(ok)
            with open(path, encoding="utf-8") as f:
                self.assertIn("FurnitureAI", f.read())
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
