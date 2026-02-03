"""
Comando per configurare l'integrazione IA (LM Studio/Ollama)
"""

import adsk.core
import adsk.fusion
import traceback
from typing import List
from . import config_manager, ai_client


class ConfigAICommand(adsk.core.CommandCreatedEventHandler):
    """Handler per il comando configurazione IA"""
    
    def __init__(self):
        super().__init__()
        self._handlers = []
        
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Dimensioni dialog
            cmd.setDialogInitialSize(400, 300)
            
            # Event handlers
            on_execute = ConfigAIExecuteHandler()
            cmd.execute.add(on_execute)
            self._handlers.append(on_execute)
            
            on_destroy = ConfigAIDestroyHandler()
            cmd.destroy.add(on_destroy)
            self._handlers.append(on_destroy)
            
            # Carica config attuale
            config = config_manager.load_config()
            
            # Crea inputs
            inputs = cmd.commandInputs
            
            # Gruppo Configurazione IA
            group_config = inputs.addGroupCommandInput('gruppo_config', 'Configurazione IA')
            group_config.isExpanded = True
            config_inputs = group_config.children
            
            # Endpoint
            config_inputs.addStringValueInput('ai_endpoint', 'Endpoint IA', 
                                             config.get('ai_endpoint', 'http://localhost:1234'))
            
            # Modello
            config_inputs.addStringValueInput('ai_model', 'Modello', 
                                             config.get('ai_model', 'llama-3.2-3b-instruct'))
            
            # Info
            info_text = config_inputs.addTextBoxCommandInput('info', '', 
                                                             'Configurazione per LM Studio (default: http://localhost:1234)\n'
                                                             'o Ollama (http://localhost:11434)\n\n'
                                                             'Modelli consigliati:\n'
                                                             '- LM Studio: llama-3.2-3b-instruct\n'
                                                             '- Ollama: llama3, llama2',
                                                             6, True)
            info_text.isReadOnly = True
            
            # Test connessione
            group_test = inputs.addGroupCommandInput('gruppo_test', 'Test Connessione')
            group_test.isExpanded = True
            test_inputs = group_test.children
            
            test_inputs.addBoolValueInput('btn_test', 'Testa Connessione', False, '', False)
            
            # Status
            status_input = test_inputs.addTextBoxCommandInput('status', '', 
                                                              'Premere "Testa Connessione" per verificare',
                                                              3, True)
            status_input.isReadOnly = True
            # Handler per cambiamenti input
            on_input_changed = ConfigAIInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            self._handlers.append(on_input_changed)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore creazione dialog configurazione IA:\n{}'.format(traceback.format_exc()))


class ConfigAIExecuteHandler(adsk.core.CommandEventHandler):
    """Handler per l'esecuzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            # Ottieni parametri da inputs
            inputs = args.command.commandInputs
            
            endpoint = inputs.itemById('ai_endpoint').value
            model = inputs.itemById('ai_model').value
            
            # Salva configurazione
            config_manager.update_config({
                'ai_endpoint': endpoint,
                'ai_model': model
            })
            
            # Testa connessione
            ai = ai_client.AIClient(endpoint, model=model, enable_fallback=False)
            
            if ai.is_available():
                ui.messageBox('Configurazione salvata con successo!\n\n'
                            'Endpoint: {}\n'
                            'Modello: {}\n\n'
                            'IA disponibile e funzionante.'.format(endpoint, model))
            else:
                ui.messageBox('Configurazione salvata.\n\n'
                            'Endpoint: {}\n'
                            'Modello: {}\n\n'
                            'ATTENZIONE: IA non raggiungibile.\n'
                            'Verifica che il server sia avviato.'.format(endpoint, model))
                
        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore salvataggio configurazione:\n{}'.format(str(e)))


class ConfigAIInputChangedHandler(adsk.core.InputChangedEventHandler):
    """Handler per i cambiamenti negli input"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.InputChangedEventArgs):
        try:
            changed_input = args.input
            inputs = args.inputs
            
            # Test connessione quando si preme il pulsante
            if changed_input.id == 'btn_test':
                endpoint_input = inputs.itemById('ai_endpoint')
                model_input = inputs.itemById('ai_model')
                status_input = inputs.itemById('status')
                
                if endpoint_input and model_input and status_input:
                    endpoint = endpoint_input.value
                    model = model_input.value
                    
                    # Testa connessione
                    ai = ai_client.AIClient(endpoint, model=model, enable_fallback=False)
                    
                    if ai.is_available():
                        status_input.text = '✓ Connessione riuscita!\n'\
                                          'IA disponibile su {}'.format(endpoint)
                    else:
                        status_input.text = '✗ Connessione fallita\n'\
                                          'Verifica che il server sia avviato su {}'.format(endpoint)
                    
        except:
            pass


class ConfigAIDestroyHandler(adsk.core.CommandEventHandler):
    """Handler per la distruzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        pass
