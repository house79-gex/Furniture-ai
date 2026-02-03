"""
Comando Lista Taglio per FurnitureAI
Genera lista di taglio dai componenti 3D
"""

import adsk.core
import adsk.fusion
import traceback
from . import cutlist_generator, logging_utils

logger = logging_utils.get_logger()


class CutlistCommand(adsk.core.CommandCreatedEventHandler):
    """Handler per il comando lista taglio"""
    
    def __init__(self):
        super().__init__()
        self._handlers = []
        
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Event handlers
            on_execute = CutlistExecuteHandler()
            cmd.execute.add(on_execute)
            self._handlers.append(on_execute)
            
            on_destroy = CutlistDestroyHandler()
            cmd.destroy.add(on_destroy)
            self._handlers.append(on_destroy)
            
            # Crea inputs
            inputs = cmd.commandInputs
            
            # Gruppo opzioni
            group = inputs.addGroupCommandInput('gruppo_opzioni', 'Opzioni Lista Taglio')
            group.isExpanded = True
            group_inputs = group.children
            
            # Formato output
            dropdown = group_inputs.addDropDownCommandInput(
                'formato_output',
                'Formato output',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown.listItems.add('Tabella UI', True)
            dropdown.listItems.add('Excel (XLSX)', False)
            dropdown.listItems.add('CSV', False)
            dropdown.listItems.add('PDF', False)
            
            # Include dettagli ferramenta
            group_inputs.addBoolValueInput('include_hardware', 'Includi ferramenta', True, '', True)
            
            # Raggruppa per materiale
            group_inputs.addBoolValueInput('group_by_material', 'Raggruppa per materiale', True, '', True)
            
            # Ottimizza orientamento
            group_inputs.addBoolValueInput('optimize_orientation', 'Ottimizza orientamento', True, '', True)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore creazione comando lista taglio:\n{}'.format(traceback.format_exc()))


class CutlistExecuteHandler(adsk.core.CommandEventHandler):
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
            formato = inputs.itemById('formato_output').selectedItem.name
            include_hardware = inputs.itemById('include_hardware').value
            group_by_material = inputs.itemById('group_by_material').value
            optimize_orientation = inputs.itemById('optimize_orientation').value
            
            # Genera lista taglio
            generator = cutlist_generator.CutListGenerator(design)
            cutlist = generator.generate_cutlist(
                include_hardware=include_hardware,
                group_by_material=group_by_material,
                optimize_orientation=optimize_orientation
            )
            
            if not cutlist:
                ui.messageBox('Nessun componente trovato per lista taglio')
                return
            
            # Output in base al formato
            if formato == 'Tabella UI':
                # Mostra in dialog
                msg = self._format_cutlist_message(cutlist)
                ui.messageBox(msg, 'Lista Taglio')
            elif formato == 'Excel (XLSX)':
                # Esporta Excel
                result = generator.export_to_excel(cutlist)
                if result['success']:
                    ui.messageBox('Lista taglio esportata:\n{}'.format(result['file']))
                else:
                    ui.messageBox('Errore export Excel:\n{}'.format(result['error']))
            elif formato == 'CSV':
                # Esporta CSV
                result = generator.export_to_csv(cutlist)
                if result['success']:
                    ui.messageBox('Lista taglio esportata:\n{}'.format(result['file']))
                else:
                    ui.messageBox('Errore export CSV:\n{}'.format(result['error']))
            elif formato == 'PDF':
                ui.messageBox('Export PDF non ancora implementato')
                
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore generazione lista taglio:\n{}'.format(traceback.format_exc()))
    
    def _format_cutlist_message(self, cutlist):
        """Formatta lista taglio per messaggio UI"""
        msg = 'LISTA TAGLIO\n' + '='*60 + '\n\n'
        
        total_items = 0
        for item in cutlist:
            total_items += 1
            msg += '{}. {} - {}x{}x{} mm\n'.format(
                total_items,
                item.get('name', 'Senza nome'),
                int(item.get('length', 0) * 10),
                int(item.get('width', 0) * 10),
                int(item.get('thickness', 0) * 10)
            )
            if item.get('material'):
                msg += '   Materiale: {}\n'.format(item['material'])
            if item.get('quantity', 1) > 1:
                msg += '   Quantità: {}\n'.format(item['quantity'])
            msg += '\n'
        
        msg += '='*60 + '\n'
        msg += 'Totale componenti: {}\n'.format(total_items)
        
        return msg


class CutlistDestroyHandler(adsk.core.CommandEventHandler):
    """Handler per la distruzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        pass
