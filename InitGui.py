"""
Shim workbench FreeCAD — carica il workbench da freecad_addon/FurnitureAI.
Installare l'intera repository in: %APPDATA%/FreeCAD/Mod/Furniture-ai
"""

import importlib.util
import os
import sys

_repo_root = os.path.dirname(os.path.abspath(__file__))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

_addon_initgui = os.path.join(_repo_root, "freecad_addon", "FurnitureAI", "InitGui.py")
_spec = importlib.util.spec_from_file_location("furnitureai_initgui", _addon_initgui)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
