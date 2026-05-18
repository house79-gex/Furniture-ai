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


class CmdExportXilog:
    """Esporta programma Xilog Plus per CNC SCM."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "Export Xilog",
            "ToolTip": "Genera file .xilog (Xilog Plus) dai parametri wizard",
        }

    def IsActive(self):
        return True

    def Activated(self):
        try:
            from PySide2 import QtWidgets
        except ImportError:
            from PySide import QtGui as QtWidgets  # type: ignore

        dlg = FurnitureWizardDialog(Gui.getMainWindow())
        dlg.setWindowTitle("FurnitureAI — Export Xilog")
        if dlg.exec_() != 1:
            return
        params = dlg.get_params()
        if not params:
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            Gui.getMainWindow(),
            "Salva programma Xilog",
            App.getUserAppDataDir(),
            "Xilog (*.xilog);;Tutti (*.*)",
        )
        if not path:
            return
        if not path.lower().endswith(".xilog"):
            path += ".xilog"

        from furniture_core.xilog_export import save_xilog_for_cabinet

        if save_xilog_for_cabinet(params, path):
            App.Console.PrintMessage("FurnitureAI: Xilog salvato in {}\n".format(path))
        else:
            App.Console.PrintError("FurnitureAI: errore salvataggio Xilog\n")

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


COMMAND_LIST = [
    "FurnitureAI_Wizard",
    "FurnitureAI_Cutlist",
    "FurnitureAI_Xilog",
]

Gui.addCommand("FurnitureAI_Wizard", CmdFurnitureWizard())
Gui.addCommand("FurnitureAI_Cutlist", CmdExportCutlist())
Gui.addCommand("FurnitureAI_Xilog", CmdExportXilog())
