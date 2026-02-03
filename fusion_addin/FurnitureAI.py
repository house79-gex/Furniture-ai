"""
FurnitureAI Add-in per Fusion 360
Add-in per la progettazione parametrica di mobili in legno con integrazione IA locale
e post-processore Xilog Plus per CNC SCM Record 130TV (NUM 1050)
"""

import adsk.core
import adsk.fusion
import traceback
from typing import Optional

from .lib import ui_manager, furniture_generator, ai_client, config_manager

# Variabili globali
_app: Optional[adsk.core.Application] = None
_ui: Optional[adsk.core.UserInterface] = None
_handlers = []


def run(context):
    """Entry point dell'add-in quando viene avviato"""
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Carica/crea configurazione (questo assicura che config.json esista)
        config = config_manager.load_config()
        
        # Inizializza il gestore UI
        ui_manager.initialize(_ui, _handlers)
        
        # Verifica disponibilità IA
        ai = ai_client.AIClient(
            config.get('ai_endpoint', 'http://localhost:1234'),
            model=config.get('ai_model', 'llama-3.2-3b-instruct'),
            enable_fallback=False
        )
        
        ai_status = '(IA disponibile)' if ai.is_available() else '(IA non disponibile - usa "Configura IA")'
        
        _ui.messageBox('FurnitureAI add-in avviato con successo! {}\n\n'
                      'Usa il pannello "Crea" per accedere ai comandi di progettazione mobili.'.format(ai_status))
        
    except:
        if _ui:
            _ui.messageBox('Errore durante l\'avvio di FurnitureAI:\n{}'.format(traceback.format_exc()))


def stop(context):
    """Entry point dell'add-in quando viene fermato"""
    try:
        # Pulisce UI e handlers
        ui_manager.cleanup(_ui, _handlers)
        
        if _ui:
            _ui.messageBox('FurnitureAI add-in arrestato.')
            
    except:
        if _ui:
            _ui.messageBox('Errore durante l\'arresto di FurnitureAI:\n{}'.format(traceback.format_exc()))
