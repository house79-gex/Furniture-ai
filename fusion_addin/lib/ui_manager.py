"""
Gestore dell'interfaccia utente per FurnitureAI
"""

import adsk.core
import adsk.fusion
from typing import List
from .furniture_wizard import FurnitureWizardCommand


def initialize(ui: adsk.core.UserInterface, handlers: List):
    """Inizializza l'interfaccia utente dell'add-in"""
    try:
        # Crea il pannello nella scheda "Crea" (SolidTab)
        create_tab = ui.allToolbarTabs.itemById('SolidTab')
        if not create_tab:
            create_tab = ui.allToolbarTabs.itemById('ToolsTab')  # Fallback
        
        # Crea pannello FurnitureAI
        furniture_panel = create_tab.toolbarPanels.itemById('FurnitureAIPanel')
        if not furniture_panel:
            furniture_panel = create_tab.toolbarPanels.add('FurnitureAIPanel', 'FurnitureAI')
        
        # Percorso icona
        import os
        icon_folder = os.path.join(os.path.dirname(__file__), '..', 'resources')
        icon_path = os.path.join(icon_folder, 'furniture_icon')
        
        # Aggiungi comando wizard mobili
        cmd_def = ui.commandDefinitions.itemById('FurnitureWizardCmd')
        if not cmd_def:
            # Se esiste cartella resources con icona, usala
            if os.path.exists(icon_folder) and os.path.exists(icon_path + '_16.png'):
                cmd_def = ui.commandDefinitions.addButtonDefinition(
                    'FurnitureWizardCmd',
                    'Wizard Mobili',
                    'Crea mobili parametrici con wizard guidato',
                    icon_path  # Senza estensione, Fusion cerca 16/32/64px
                )
            else:
                # Altrimenti usa solo testo
                cmd_def = ui.commandDefinitions.addButtonDefinition(
                    'FurnitureWizardCmd',
                    'Wizard Mobili',
                    'Crea mobili parametrici con wizard guidato',
                    ''
                )
        
        # Crea handler per il comando
        wizard_cmd = FurnitureWizardCommand()
        cmd_def.commandCreated.add(wizard_cmd)
        handlers.append(wizard_cmd)
        
        # Aggiungi controllo al pannello
        furniture_panel.controls.addCommand(cmd_def)
        
        # Aggiungi comando configurazione IA
        config_cmd_def = ui.commandDefinitions.itemById('FurnitureAIConfigCmd')
        if not config_cmd_def:
            config_cmd_def = ui.commandDefinitions.addButtonDefinition(
                'FurnitureAIConfigCmd',
                'Configura IA',
                'Configura endpoint IA locale',
                ''
            )
        
        furniture_panel.controls.addCommand(config_cmd_def)
        
    except Exception as e:
        ui.messageBox('Errore inizializzazione UI: {}'.format(str(e)))


def cleanup(ui: adsk.core.UserInterface, handlers: List):
    """Pulisce l'interfaccia utente dell'add-in"""
    try:
        # Rimuovi pannello - prova prima SolidTab, poi ToolsTab
        create_tab = ui.allToolbarTabs.itemById('SolidTab')
        if not create_tab:
            create_tab = ui.allToolbarTabs.itemById('ToolsTab')
            
        if create_tab:
            furniture_panel = create_tab.toolbarPanels.itemById('FurnitureAIPanel')
            if furniture_panel:
                furniture_panel.deleteMe()
        
        # Rimuovi definizioni comandi
        cmd_def = ui.commandDefinitions.itemById('FurnitureWizardCmd')
        if cmd_def:
            cmd_def.deleteMe()
            
        config_cmd_def = ui.commandDefinitions.itemById('FurnitureAIConfigCmd')
        if config_cmd_def:
            config_cmd_def.deleteMe()
        
        # Pulisci handlers
        handlers.clear()
        
    except Exception as e:
        if ui:
            ui.messageBox('Errore pulizia UI: {}'.format(str(e)))
