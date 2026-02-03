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
        # LISTA DEI TAB DOVE APPARIRE (Design e Utilità)
        tab_ids = ['SolidTab', 'ToolsTab']
        
        panels_created = []
        
        for tab_id in tab_ids:
            tab = ui.allToolbarTabs.itemById(tab_id)
            if not tab:
                continue
            
            # Crea pannello per questo tab (NOME CORTO)
            panel_id = 'FurnitureAIPanel_{}'.format(tab_id)
            furniture_panel = tab.toolbarPanels.itemById(panel_id)
            if not furniture_panel:
                furniture_panel = tab.toolbarPanels.add(panel_id, 'Mobili')  # NOME CORTO
            
            panels_created.append((tab_id, furniture_panel))
        
        # Se nessun pannello creato, errore
        if not panels_created:
            ui.messageBox('Errore: nessun tab disponibile per FurnitureAI')
            return
        
        # Crea DEFINIZIONE comando UNA SOLA VOLTA
        cmd_def = ui.commandDefinitions.itemById('FurnitureWizardCmd')
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition(
                'FurnitureWizardCmd',
                'Wizard Mobili',
                'Crea mobili parametrici con wizard guidato',
                ''  # Nessuna icona
            )
        
        # Handler comando
        wizard_cmd = FurnitureWizardCommand()
        cmd_def.commandCreated.add(wizard_cmd)
        handlers.append(wizard_cmd)
        
        # AGGIUNGI CONTROLLO A TUTTI I PANNELLI CREATI
        for tab_id, panel in panels_created:
            control = panel.controls.itemById('FurnitureWizardCmd')
            if not control:
                panel.controls.addCommand(cmd_def)
        
        # Comando configurazione IA
        config_cmd_def = ui.commandDefinitions.itemById('FurnitureAIConfigCmd')
        if not config_cmd_def:
            config_cmd_def = ui.commandDefinitions.addButtonDefinition(
                'FurnitureAIConfigCmd',
                'Config IA',
                'Configura endpoint IA locale (Ollama/LM Studio)',
                ''  # Nessuna icona
            )
        
        # Aggiungi config a tutti i pannelli
        for tab_id, panel in panels_created:
            config_control = panel.controls.itemById('FurnitureAIConfigCmd')
            if not config_control:
                panel.controls.addCommand(config_cmd_def)
        
    except Exception as e:
        if ui:
            ui.messageBox('Errore inizializzazione UI: {}'.format(str(e)))


def cleanup(ui: adsk.core.UserInterface, handlers: List):
    """Pulisce l'interfaccia utente dell'add-in"""
    try:
        # Rimuovi pannelli da tutti i tab
        tab_ids = ['SolidTab', 'ToolsTab']
        
        for tab_id in tab_ids:
            tab = ui.allToolbarTabs.itemById(tab_id)
            if tab:
                panel_id = 'FurnitureAIPanel_{}'.format(tab_id)
                furniture_panel = tab.toolbarPanels.itemById(panel_id)
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
