"""
Comandi workbench FurnitureAI — comportamento allineato all'add-in Fusion.
"""

from __future__ import annotations

import os
from typing import List, Tuple

import FreeCAD as App
import FreeCADGui as Gui

from furniture_core.assembly_spec import cabinet_assembly_label, suggest_module_name

from .freecad_geometry import (
    add_cabinet_module_to_document,
    build_cabinet_assembly_in_document,
)
from .wizard_dialog import FurnitureWizardDialog

_wb_dir = os.path.dirname(os.path.abspath(__file__))
_ICON = os.path.join(_wb_dir, "Resources", "icons", "FurnitureAI.svg")


def _ensure_document() -> App.Document:
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("FurnitureAI")
    return doc


def _report_success(assembly_label: str, panel_names: List[str]) -> None:
    msg = (
        "Mobile creato con successo.\n\n"
        "Assieme: {}\n"
        "Componenti: {}\n\n"
        "Ogni pannello è un sotto-assieme (come in Fusion)."
    ).format(assembly_label, ", ".join(panel_names))
    App.Console.PrintMessage("FurnitureAI: {}\n".format(msg.replace("\n\n", " — ")))
    try:
        from PySide2 import QtWidgets
    except ImportError:
        from PySide import QtGui as QtWidgets  # type: ignore
    QtWidgets.QMessageBox.information(Gui.getMainWindow(), "FurnitureAI", msg)


def _last_module_layout_x(doc: App.Document) -> float:
    """Posizione X per il prossimo modulo in fila (cm), stile layout lineare Fusion."""
    x = 0.0
    for obj in doc.Objects:
        if obj.TypeId == "App::Part" and obj.Name.startswith("Modulo_"):
            placement = obj.Placement.Base
            # Approssima fine modulo: origine + larghezza non nota → usa solo offset cumulativo
            x = max(x, placement.x / 10.0 + 80.0)
    return x


class CmdFurnitureWizard:
    """Crea un assieme mobile (equivalente generate_furniture su Fusion)."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "🪑 Wizard mobili",
            "ToolTip": "Crea carcassa + ante (Fondo/Cielo tra fianchi, ripiani arretrati)",
        }

    def IsActive(self):
        return True

    def Activated(self):
        dlg = FurnitureWizardDialog(Gui.getMainWindow())
        if dlg.exec_() != 1:
            return
        params = dlg.get_params()
        if not params:
            return
        doc = _ensure_document()
        try:
            asm_name = cabinet_assembly_label(params)
            mobile, names = build_cabinet_assembly_in_document(doc, params, assembly_name=asm_name)
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(doc.Name, mobile.Name)
            _report_success(mobile.Label, names)
        except Exception as exc:
            App.Console.PrintError("FurnitureAI: {}\n".format(exc))

    def GetClassName(self):
        return "Gui::Command"


class CmdAddModule:
    """Aggiunge un modulo mobile posizionato (equivalente ModularProject.add_cabinet_module)."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "📦 Aggiungi modulo",
            "ToolTip": "Aggiunge un altro mobile come assieme posizionato (layout modulare)",
        }

    def IsActive(self):
        return True

    def Activated(self):
        dlg = FurnitureWizardDialog(Gui.getMainWindow())
        dlg.setWindowTitle("FurnitureAI — Nuovo modulo")
        if dlg.exec_() != 1:
            return
        params = dlg.get_params()
        if not params:
            return
        doc = _ensure_document()
        try:
            existing = [o.Name for o in doc.Objects]
            mod_name = suggest_module_name(existing)
            pos_x = _last_module_layout_x(doc)
            position: Tuple[float, float, float] = (pos_x, 0.0, 0.0)
            mobile, names = add_cabinet_module_to_document(
                doc, params, position_cm=position, module_name=mod_name
            )
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(doc.Name, mobile.Name)
            _report_success(mobile.Label, names)
        except Exception as exc:
            App.Console.PrintError("FurnitureAI: {}\n".format(exc))

    def GetClassName(self):
        return "Gui::Command"


class CmdExportXilog:
    """Esporta programma Xilog Plus per CNC SCM."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "⚙ Export Xilog",
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
    """Esporta lista taglio CSV dai parametri wizard."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "📋 Lista taglio",
            "ToolTip": "Esporta lista taglio CSV dai parametri wizard",
        }

    def IsActive(self):
        return True

    def Activated(self):
        try:
            from PySide2 import QtWidgets
        except ImportError:
            from PySide import QtGui as QtWidgets  # type: ignore

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
    "FurnitureAI_AddModule",
    "FurnitureAI_Cutlist",
    "FurnitureAI_Xilog",
]

_commands_registered = False


def register_commands() -> None:
    """Registra comandi GUI (chiamare da Workbench.Initialize)."""
    global _commands_registered
    if _commands_registered:
        return
    Gui.addCommand("FurnitureAI_Wizard", CmdFurnitureWizard())
    Gui.addCommand("FurnitureAI_AddModule", CmdAddModule())
    Gui.addCommand("FurnitureAI_Cutlist", CmdExportCutlist())
    Gui.addCommand("FurnitureAI_Xilog", CmdExportXilog())
    _commands_registered = True
