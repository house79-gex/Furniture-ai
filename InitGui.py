"""
Shim workbench FreeCAD — installare l'intera repository in Mod/Furniture-ai.

FreeCAD a volte esegue InitGui.py senza definire __file__; si usa inspect come fallback.
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys


def _repo_root() -> str:
    """Root del repository (cartella con furniture_core/)."""
    try:
        root = os.path.dirname(os.path.abspath(__file__))
        if os.path.isdir(os.path.join(root, "furniture_core")):
            return root
    except NameError:
        pass

    for frame_info in inspect.stack():
        fn = frame_info.filename or ""
        if not fn.endswith("InitGui.py") or not os.path.isfile(fn):
            continue
        root = os.path.dirname(os.path.abspath(fn))
        if os.path.isdir(os.path.join(root, "furniture_core")):
            return root

    import FreeCAD

    return os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Furniture-ai")


_repo_root = _repo_root()
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

_addon_parent = os.path.join(_repo_root, "freecad_addon")
if _addon_parent not in sys.path:
    sys.path.insert(0, _addon_parent)

importlib.import_module("FurnitureAI.InitGui")
