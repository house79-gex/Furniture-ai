"""
Gestore UI FurnitureAI - Versione Professionale
"""

import adsk.core
import adsk.fusion
import os
import tempfile
import shutil
from typing import List
from .furniture_wizard import FurnitureWizardCommand

_panel = None
_controls = []


def initialize(ui: adsk.core.UserInterface, handlers: List):
    """Inizializza l'interfaccia utente dell'add-in"""
    global _panel, _controls
    
    try:
        # Setup icone temp
        addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icons_temp = os.path.join(tempfile.gettempdir(), 'FurnitureAI_Icons')
        os.makedirs(icons_temp, exist_ok=True)
        
        resources_src = os.path.join(addon_path, 'resources')
        for size in ['16', '32', '64']:
            src = os.path.join(resources_src, 'furniture_icon_{0}.png'.format(size))
            dest = os.path.join(icons_temp, '{0}x{0}.png'.format(size))
            if os.path.exists(src):
                shutil.copyfile(src, dest)
        
        # Workspace + Panel CORRETTO (metodo professionale)
        workspaces = ui.workspaces
        design_ws = workspaces.itemById('FusionSolidEnvironment')
        if not design_ws:
            ui.messageBox('Errore: workspace FusionSolidEnvironment non disponibile')
            return
        
        _panel = design_ws.toolbarPanels.itemById('SolidCreatePanel')
        if not _panel:
            ui.messageBox('Errore: pannello SolidCreatePanel non disponibile')
            return
        
        cmd_defs = ui.commandDefinitions
        
        # Comando Wizard
        wizard_id = 'FurnitureAI_Wizard'
        wizard_def = cmd_defs.itemById(wizard_id)
        if not wizard_def:
            wizard_def = cmd_defs.addButtonDefinition(
                wizard_id, 'Wizard Mobili',
                'Crea mobili parametrici con IA', icons_temp)
        
        wizard_handler = FurnitureWizardCommand()
        wizard_def.commandCreated.add(wizard_handler)
        handlers.append(wizard_handler)
        
        if not _panel.controls.itemById(wizard_id):
            ctrl = _panel.controls.addCommand(wizard_def)
            ctrl.isPromoted = True  # CHIAVE: bottone sempre visibile
            _controls.append(ctrl)
        
    except Exception as e:
        if ui:
            ui.messageBox('Errore inizializzazione UI: {}'.format(str(e)))


def cleanup(ui: adsk.core.UserInterface, handlers: List):
    """Pulisce l'interfaccia utente dell'add-in"""
    global _controls
    
    try:
        # Rimuovi controlli dal pannello
        for ctrl in _controls:
            if ctrl and ctrl.isValid:
                ctrl.deleteMe()
        _controls.clear()
        
        # Rimuovi definizioni comandi
        cmd_defs = ui.commandDefinitions
        cmd_def = cmd_defs.itemById('FurnitureAI_Wizard')
        if cmd_def:
            cmd_def.deleteMe()
        
        # Pulisci handlers
        handlers.clear()
        
    except Exception as e:
        if ui:
            ui.messageBox('Errore pulizia UI: {}'.format(str(e)))
