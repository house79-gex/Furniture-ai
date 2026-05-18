"""
Test unitari furniture_core (senza FreeCAD / Fusion).
"""

import os
import sys
import tempfile
import unittest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from furniture_core.models import default_params_for_type, normalize_params
from furniture_core.validation import validate_cabinet_params
from furniture_core.parser_nl import parse_description
from furniture_core.panel_specs import build_panel_specs
from furniture_core.cutlist import export_csv, panels_to_cutlist


class TestFurnitureCore(unittest.TestCase):
    def test_defaults_pensile(self):
        p = default_params_for_type("Pensile")
        self.assertEqual(p["profondita"], 35.0)
        self.assertFalse(p["con_zoccolo"])

    def test_validation_ok(self):
        p = normalize_params({"larghezza": 80, "altezza": 90, "profondita": 60})
        self.assertEqual(validate_cabinet_params(p), [])

    def test_validation_fail(self):
        p = normalize_params({"larghezza": 5})
        self.assertTrue(len(validate_cabinet_params(p)) > 0)

    def test_parse_description(self):
        p = parse_description("mobile cucina largo 80cm alto 90cm con 2 ripiani e 2 ante")
        self.assertEqual(p["larghezza"], 80.0)
        self.assertEqual(p["altezza"], 90.0)
        self.assertEqual(p["num_ripiani"], 2)
        self.assertEqual(p["num_ante"], 2)

    def test_panel_specs_count(self):
        p = normalize_params({"num_ripiani": 2, "con_zoccolo": True})
        panels = build_panel_specs(p)
        # 4 base + 2 ripiani + schienale + zoccolo = 8
        self.assertEqual(len(panels), 8)

    def test_cutlist_export(self):
        panels = build_panel_specs(normalize_params({}))
        cutlist = panels_to_cutlist(panels)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            path = tmp.name
        try:
            export_csv(cutlist, path)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Fianco_SX", content)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
