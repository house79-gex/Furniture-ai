"""
Workbench FurnitureAI — FreeCAD 1.1
"""

import os
import sys

# Aggiunge la root del repository al path per importare furniture_core
_wb_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.abspath(os.path.join(_wb_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import FreeCADGui as Gui

from . import FurnitureAICommands


class FurnitureAIWorkbench(Gui.Workbench):
    """Workbench per mobili parametrici."""

    MenuText = "FurnitureAI"
    ToolTip = "Progettazione mobili parametrici"
    Icon = os.path.join(_wb_dir, "Resources", "icons", "FurnitureAI.svg")

    def Initialize(self):
        self.appendToolbar("FurnitureAI", FurnitureAICommands.COMMAND_LIST)
        self.appendMenu("FurnitureAI", FurnitureAICommands.COMMAND_LIST)

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(FurnitureAIWorkbench())
