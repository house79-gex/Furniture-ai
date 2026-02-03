"""
Gestore UI FurnitureAI - Versione Professionale Completa
Gestisce tutti i comandi dell'add-in
"""

import adsk.core
import adsk.fusion
import os
import tempfile
import shutil
from typing import List
from .furniture_wizard import FurnitureWizardCommand
from .cutlist_command import CutlistCommand
from .nesting_command import NestingCommand
from .drawing_command import DrawingCommand
from .door_designer_command import DoorDesignerCommand

_panel = None
_controls = []


def initialize(ui: adsk.core.UserInterface, handlers: List):
    """Inizializza l'interfaccia utente dell'add-in con tutti i comandi"""
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
        
        # Workspace + Panel - Supporta sia Design che Assembly
        workspaces = ui.workspaces
        
        # Lista workspace supportati
        workspace_ids = [
            'FusionSolidEnvironment',  # Design/Part mode
            'AssemblyEnvironment'       # Assembly mode
        ]
        
        for ws_id in workspace_ids:
            workspace = workspaces.itemById(ws_id)
            if not workspace:
                continue
            
            # Pannello CREA
            panel = workspace.toolbarPanels.itemById('SolidCreatePanel')
            if not panel:
                continue
            
            # Salva riferimento al pannello principale (Design)
            if ws_id == 'FusionSolidEnvironment':
                _panel = panel
            
            cmd_defs = ui.commandDefinitions
            
            # 1. COMANDO WIZARD MOBILI
            wizard_id = 'FurnitureAI_Wizard'
            wizard_def = cmd_defs.itemById(wizard_id)
            if not wizard_def:
                wizard_def = cmd_defs.addButtonDefinition(
                    wizard_id, 'Wizard Mobili',
                    'Crea mobili parametrici con IA', icons_temp)
            
            wizard_handler = FurnitureWizardCommand()
            wizard_def.commandCreated.add(wizard_handler)
            handlers.append(wizard_handler)
            
            if not panel.controls.itemById(wizard_id):
                ctrl = panel.controls.addCommand(wizard_def)
                ctrl.isPromoted = True  # Bottone sempre visibile
                _controls.append(ctrl)
            
            # 2. COMANDO LISTA TAGLIO
            cutlist_id = 'FurnitureAI_Cutlist'
            cutlist_def = cmd_defs.itemById(cutlist_id)
            if not cutlist_def:
                cutlist_def = cmd_defs.addButtonDefinition(
                    cutlist_id, 'Lista Taglio',
                    'Genera lista di taglio automatica', icons_temp)
            
            cutlist_handler = CutlistCommand()
            cutlist_def.commandCreated.add(cutlist_handler)
            handlers.append(cutlist_handler)
            
            if not panel.controls.itemById(cutlist_id):
                ctrl = panel.controls.addCommand(cutlist_def)
                ctrl.isPromoted = False
                _controls.append(ctrl)
            
            # 3. COMANDO OTTIMIZZA TAGLIO
            nesting_id = 'FurnitureAI_Nesting'
            nesting_def = cmd_defs.itemById(nesting_id)
            if not nesting_def:
                nesting_def = cmd_defs.addButtonDefinition(
                    nesting_id, 'Ottimizza Taglio',
                    'Ottimizza disposizione pannelli su lastre', icons_temp)
            
            nesting_handler = NestingCommand()
            nesting_def.commandCreated.add(nesting_handler)
            handlers.append(nesting_handler)
            
            if not panel.controls.itemById(nesting_id):
                ctrl = panel.controls.addCommand(nesting_def)
                ctrl.isPromoted = False
                _controls.append(ctrl)
            
            # 4. COMANDO GENERA DISEGNI
            drawing_id = 'FurnitureAI_Drawing'
            drawing_def = cmd_defs.itemById(drawing_id)
            if not drawing_def:
                drawing_def = cmd_defs.addButtonDefinition(
                    drawing_id, 'Genera Disegni',
                    'Crea disegni tecnici 2D', icons_temp)
            
            drawing_handler = DrawingCommand()
            drawing_def.commandCreated.add(drawing_handler)
            handlers.append(drawing_handler)
            
            if not panel.controls.itemById(drawing_id):
                ctrl = panel.controls.addCommand(drawing_def)
                ctrl.isPromoted = False
                _controls.append(ctrl)
            
            # 5. COMANDO DESIGNER ANTE
            door_id = 'FurnitureAI_DoorDesigner'
            door_def = cmd_defs.itemById(door_id)
            if not door_def:
                door_def = cmd_defs.addButtonDefinition(
                    door_id, 'Designer Ante',
                    'Crea ante custom (piatta, bugna, cornice, vetro)', icons_temp)
            
            door_handler = DoorDesignerCommand()
            door_def.commandCreated.add(door_handler)
            handlers.append(door_handler)
            
            if not panel.controls.itemById(door_id):
                ctrl = panel.controls.addCommand(door_def)
                ctrl.isPromoted = False
                _controls.append(ctrl)
            
            # 6. COMANDO GESTIONE MATERIALI (placeholder per futuro)
            # Per ora materiali sono gestiti nel wizard
            
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
        command_ids = [
            'FurnitureAI_Wizard',
            'FurnitureAI_Cutlist',
            'FurnitureAI_Nesting',
            'FurnitureAI_Drawing',
            'FurnitureAI_DoorDesigner'
        ]
        
        for cmd_id in command_ids:
            cmd_def = cmd_defs.itemById(cmd_id)
            if cmd_def:
                cmd_def.deleteMe()
        
        # Pulisci handlers
        handlers.clear()
        
    except Exception as e:
        if ui:
            ui.messageBox('Errore pulizia UI: {}'.format(str(e)))
