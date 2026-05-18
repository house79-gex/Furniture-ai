"""
Comandi workbench FurnitureAI.
"""

from __future__ import annotations

import os

import FreeCAD as App
import FreeCADGui as Gui

from .freecad_geometry import build_cabinet_in_document
from .wizard_dialog import FurnitureWizardDialog

_wb_dir = os.path.dirname(os.path.abspath(__file__))
_ICON = os.path.join(_wb_dir, "Resources", "icons", "FurnitureAI.svg")


class CmdFurnitureWizard:
    """Apre il wizard e genera il mobile nel documento attivo."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "Wizard mobili",
            "ToolTip": "Crea un mobile parametrico (fianchi, ripiani, schienale)",
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        doc = App.ActiveDocument
        if doc is None:
            return
        dlg = FurnitureWizardDialog(Gui.getMainWindow())
        if dlg.exec_() != 1:
            return
        params = dlg.get_params()
        if not params:
            return
        try:
            part, names = build_cabinet_in_document(doc, params)
            doc.recompute()
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(doc.Name, part.Name)
            App.Console.PrintMessage(
                "FurnitureAI: creati {} pannelli in '{}'\n".format(len(names), part.Label)
            )
        except Exception as exc:
            App.Console.PrintError("FurnitureAI: {}\n".format(exc))

    def GetClassName(self):
        return "Gui::Command"


class CmdExportCutlist:
    """Esporta lista taglio CSV dal wizard (ultima generazione manuale)."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "Lista taglio",
            "ToolTip": "Esporta lista taglio CSV dai parametri wizard",
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        from PySide2 import QtWidgets

        dlg = FurnitureWizardDialog(Gui.getMainWindow())
        dlg.setWindowTitle("FurnitureAI — Lista taglio")
        if dlg.exec_() != 1:
            return
        params = dlg.get_params()
        if not params:
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            Gui.getMainWindow(),
            "Salva lista taglio",
            App.getUserAppDataDir(),
            "CSV (*.csv)",
        )
        if not path:
            return

        from furniture_core.panel_specs import build_panel_specs
        from furniture_core.cutlist import export_csv, panels_to_cutlist

        panels = build_panel_specs(params)
        cutlist = panels_to_cutlist(panels)
        export_csv(cutlist, path)
        App.Console.PrintMessage("FurnitureAI: lista taglio salvata in {}\n".format(path))

    def GetClassName(self):
        return "Gui::Command"


COMMAND_LIST = ["FurnitureAI_Wizard", "FurnitureAI_Cutlist"]

Gui.addCommand("FurnitureAI_Wizard", CmdFurnitureWizard())
Gui.addCommand("FurnitureAI_Cutlist", CmdExportCutlist())
