"""
Workbench FurnitureAI — FreeCAD 1.0 / 1.1
"""

import inspect
import os
import sys


def _workbench_dir() -> str:
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        for frame_info in inspect.stack():
            fn = frame_info.filename or ""
            if "FurnitureAI" in fn and fn.endswith("InitGui.py") and os.path.isfile(fn):
                return os.path.dirname(os.path.abspath(fn))
        import FreeCAD

        return os.path.join(
            FreeCAD.getUserAppDataDir(),
            "Mod",
            "Furniture-ai",
            "freecad_addon",
            "FurnitureAI",
        )


_wb_dir = _workbench_dir()
_repo_root = os.path.abspath(os.path.join(_wb_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import FreeCADGui as Gui

from . import FurnitureAICommands


def _register_workbench() -> None:
    """Registra il workbench solo nell'ambiente GUI (non in FreeCADCmd)."""

    class FurnitureAIWorkbench(Gui.Workbench):
        """Workbench per mobili parametrici."""

        MenuText = "FurnitureAI"
        ToolTip = "Progettazione mobili parametrici"
        Icon = os.path.join(_wb_dir, "Resources", "icons", "FurnitureAI.svg")

        def Initialize(self):
            FurnitureAICommands.register_commands()
            self.appendToolbar("FurnitureAI", FurnitureAICommands.COMMAND_LIST)
            self.appendMenu("FurnitureAI", FurnitureAICommands.COMMAND_LIST)

        def GetClassName(self):
            return "Gui::PythonWorkbench"

    Gui.addWorkbench(FurnitureAIWorkbench())


if hasattr(Gui, "Workbench") and hasattr(Gui, "addWorkbench"):
    _register_workbench()
