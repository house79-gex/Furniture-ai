"""
Gestore dell'interfaccia utente per FurnitureAI
"""

import adsk.core
import adsk.fusion
import os
from typing import List
from .furniture_wizard import FurnitureWizardCommand


def initialize(ui: adsk.core.UserInterface, handlers: List):
    """Inizializza l'interfaccia utente dell'add-in"""
    try:
        # Usa il tab "Crea" (SolidTab) invece di "Utilità" (ToolsTab)
        create_tab = ui.allToolbarTabs.itemById('SolidTab')
        if not create_tab:
            # Fallback su ToolsTab se SolidTab non trovato
            create_tab = ui.allToolbarTabs.itemById('ToolsTab')
        
        if not create_tab:
            ui.messageBox('Errore: nessun tab disponibile per FurnitureAI')
            return
        
        # Crea pannello FurnitureAI
        furniture_panel = create_tab.toolbarPanels.itemById('FurnitureAIPanel')
        if not furniture_panel:
            furniture_panel = create_tab.toolbarPanels.add('FurnitureAIPanel', 'FurnitureAI')
        # Debug (RIMUOVI dopo aver risolto)
ui.messageBox(f'Resources folder: {resources_folder}\nExists: {os.path.exists(resources_folder)}\nIcon path: {icon_path}')
        # GESTIONE ICONA - Percorso corretto
        # __file__ è il percorso di ui_manager.py (in fusion_addin/lib/)
        # Dobbiamo andare su di 1 livello per arrivare a fusion_addin/, poi entrare in resources/
        current_file = os.path.abspath(__file__)  # Percorso assoluto ui_manager.py
        lib_folder = os.path.dirname(current_file)  # fusion_addin/lib/
        addon_folder = os.path.dirname(lib_folder)  # fusion_addin/
        resources_folder = os.path.join(addon_folder, 'resources')
        
        # Verifica esistenza cartella resources
        icon_path = ''
        if os.path.exists(resources_folder):
            # Fusion cerca automaticamente _16.png, _32.png, _64.png aggiungendo il suffisso
            # Quindi passiamo il path senza estensione: "path/to/furniture_icon"
            icon_base_path = os.path.join(resources_folder, 'furniture_icon')
            
            # Verifica che almeno un'icona esista
            if (os.path.exists(icon_base_path + '_16.png') or 
                os.path.exists(icon_base_path + '_32.png') or
                os.path.exists(icon_base_path + '_64.png')):
                icon_path = icon_base_path
        
        # Aggiungi comando wizard mobili
        cmd_def = ui.commandDefinitions.itemById('FurnitureWizardCmd')
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition(
                'FurnitureWizardCmd',
                'Wizard Mobili',
                'Crea mobili parametrici con wizard guidato',
                icon_path  # Stringa vuota se nessuna icona trovata
            )
        
        # Crea handler per il comando
        wizard_cmd = FurnitureWizardCommand()
        cmd_def.commandCreated.add(wizard_cmd)
        handlers.append(wizard_cmd)
        
        # Aggiungi controllo al pannello
        control = furniture_panel.controls.itemById('FurnitureWizardCmd')
        if not control:
            furniture_panel.controls.addCommand(cmd_def)
        
        # Aggiungi comando configurazione IA
        config_cmd_def = ui.commandDefinitions.itemById('FurnitureAIConfigCmd')
        if not config_cmd_def:
            # Usa icona generica settings se disponibile
            config_icon = ''
            if os.path.exists(resources_folder):
                config_icon_path = os.path.join(resources_folder, 'settings_icon')
                if os.path.exists(config_icon_path + '_16.png'):
                    config_icon = config_icon_path
            
            config_cmd_def = ui.commandDefinitions.addButtonDefinition(
                'FurnitureAIConfigCmd',
                'Configura IA',
                'Configura endpoint IA locale (Ollama/LM Studio)',
                config_icon
            )
        
        config_control = furniture_panel.controls.itemById('FurnitureAIConfigCmd')
        if not config_control:
            furniture_panel.controls.addCommand(config_cmd_def)
        
    except Exception as e:
        if ui:
            ui.messageBox('Errore inizializzazione UI: {}'.format(str(e)))


def cleanup(ui: adsk.core.UserInterface, handlers: List):
    """Pulisce l'interfaccia utente dell'add-in"""
    try:
        # Rimuovi pannello da entrambi i tab possibili
        for tab_id in ['SolidTab', 'ToolsTab']:
            tab = ui.allToolbarTabs.itemById(tab_id)
            if tab:
                furniture_panel = tab.toolbarPanels.itemById('FurnitureAIPanel')
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
