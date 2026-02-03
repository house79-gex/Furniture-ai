"""
Comando Genera Disegni per FurnitureAI
Genera disegni tecnici 2D dai componenti 3D
"""

import adsk.core
import adsk.fusion
import traceback
from . import logging_utils

logger = logging_utils.get_logger()


class DrawingCommand(adsk.core.CommandCreatedEventHandler):
    """Handler per il comando genera disegni"""
    
    def __init__(self):
        super().__init__()
        self._handlers = []
        
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Event handlers
            on_execute = DrawingExecuteHandler()
            cmd.execute.add(on_execute)
            self._handlers.append(on_execute)
            
            on_destroy = DrawingDestroyHandler()
            cmd.destroy.add(on_destroy)
            self._handlers.append(on_destroy)
            
            # Crea inputs
            inputs = cmd.commandInputs
            
            # Gruppo viste
            group_viste = inputs.addGroupCommandInput('gruppo_viste', 'Viste da Generare')
            group_viste.isExpanded = True
            viste_inputs = group_viste.children
            
            viste_inputs.addBoolValueInput('vista_frontale', 'Vista frontale', True, '', True)
            viste_inputs.addBoolValueInput('vista_laterale', 'Vista laterale', True, '', True)
            viste_inputs.addBoolValueInput('vista_alto', 'Vista dall\'alto', True, '', True)
            viste_inputs.addBoolValueInput('vista_isometrica', 'Vista isometrica', True, '', False)
            
            # Gruppo dettagli
            group_dettagli = inputs.addGroupCommandInput('gruppo_dettagli', 'Dettagli')
            group_dettagli.isExpanded = True
            dettagli_inputs = group_dettagli.children
            
            dettagli_inputs.addBoolValueInput('quote_dimensioni', 'Quote dimensioni', True, '', True)
            dettagli_inputs.addBoolValueInput('quote_fori', 'Quote fori', True, '', True)
            dettagli_inputs.addBoolValueInput('callout_ferramenta', 'Callout ferramenta', True, '', True)
            dettagli_inputs.addBoolValueInput('distinta_materiali', 'Distinta materiali', True, '', True)
            
            # Gruppo formato
            group_formato = inputs.addGroupCommandInput('gruppo_formato', 'Formato Output')
            group_formato.isExpanded = True
            formato_inputs = group_formato.children
            
            dropdown_scala = formato_inputs.addDropDownCommandInput(
                'scala',
                'Scala',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown_scala.listItems.add('1:10', True)
            dropdown_scala.listItems.add('1:5', False)
            dropdown_scala.listItems.add('1:2', False)
            dropdown_scala.listItems.add('1:1', False)
            
            dropdown_formato = formato_inputs.addDropDownCommandInput(
                'formato_foglio',
                'Formato foglio',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown_formato.listItems.add('A4 (210x297mm)', True)
            dropdown_formato.listItems.add('A3 (297x420mm)', False)
            dropdown_formato.listItems.add('A2 (420x594mm)', False)
            dropdown_formato.listItems.add('A1 (594x841mm)', False)
            
            dropdown_output = formato_inputs.addDropDownCommandInput(
                'formato_output',
                'Formato output',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown_output.listItems.add('Drawing Fusion 360', True)
            dropdown_output.listItems.add('PDF', False)
            dropdown_output.listItems.add('DWG', False)
            dropdown_output.listItems.add('DXF', False)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore creazione comando disegni:\n{}'.format(traceback.format_exc()))


class DrawingExecuteHandler(adsk.core.CommandEventHandler):
    """Handler per l'esecuzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)
            
            if not design:
                ui.messageBox('Nessun design attivo')
                return
            
            # Ottieni parametri
            inputs = args.command.commandInputs
            
            vista_frontale = inputs.itemById('vista_frontale').value
            vista_laterale = inputs.itemById('vista_laterale').value
            vista_alto = inputs.itemById('vista_alto').value
            vista_iso = inputs.itemById('vista_isometrica').value
            
            quote_dim = inputs.itemById('quote_dimensioni').value
            quote_fori = inputs.itemById('quote_fori').value
            callout_hw = inputs.itemById('callout_ferramenta').value
            distinta = inputs.itemById('distinta_materiali').value
            
            scala = inputs.itemById('scala').selectedItem.name
            formato_foglio = inputs.itemById('formato_foglio').selectedItem.name
            formato_output = inputs.itemById('formato_output').selectedItem.name
            
            # Conta viste selezionate
            viste_count = sum([vista_frontale, vista_laterale, vista_alto, vista_iso])
            
            if viste_count == 0:
                ui.messageBox('Selezionare almeno una vista')
                return
            
            # Placeholder per generazione disegni (da implementare)
            msg = (
                'Genera Disegni Tecnici\n\n'
                'Viste selezionate: {}\n'
                'Scala: {}\n'
                'Formato: {}\n'
                'Output: {}\n\n'
                'Opzioni:\n'
                '- Quote dimensioni: {}\n'
                '- Quote fori: {}\n'
                '- Callout ferramenta: {}\n'
                '- Distinta materiali: {}\n\n'
                'NOTA: Funzionalità in fase di implementazione.\n'
                'Utilizzare il modulo Drawing di Fusion 360 manualmente.'.format(
                    viste_count,
                    scala,
                    formato_foglio,
                    formato_output,
                    'Sì' if quote_dim else 'No',
                    'Sì' if quote_fori else 'No',
                    'Sì' if callout_hw else 'No',
                    'Sì' if distinta else 'No'
                )
            )
            
            ui.messageBox(msg, 'Genera Disegni')
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore generazione disegni:\n{}'.format(traceback.format_exc()))


class DrawingDestroyHandler(adsk.core.CommandEventHandler):
    """Handler per la distruzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        pass
