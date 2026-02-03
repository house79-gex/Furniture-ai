"""
Comando Ottimizzazione Taglio (Nesting) per FurnitureAI
Ottimizza il taglio dei pannelli su lastre standard
"""

import adsk.core
import adsk.fusion
import traceback
from . import logging_utils

logger = logging_utils.get_logger()


class NestingCommand(adsk.core.CommandCreatedEventHandler):
    """Handler per il comando ottimizzazione taglio"""
    
    def __init__(self):
        super().__init__()
        self._handlers = []
        
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Event handlers
            on_execute = NestingExecuteHandler()
            cmd.execute.add(on_execute)
            self._handlers.append(on_execute)
            
            on_destroy = NestingDestroyHandler()
            cmd.destroy.add(on_destroy)
            self._handlers.append(on_destroy)
            
            # Crea inputs
            inputs = cmd.commandInputs
            
            # Gruppo dimensioni lastra
            group_lastra = inputs.addGroupCommandInput('gruppo_lastra', 'Dimensioni Lastra Standard')
            group_lastra.isExpanded = True
            lastra_inputs = group_lastra.children
            
            # Preset lastre comuni
            dropdown = lastra_inputs.addDropDownCommandInput(
                'preset_lastra',
                'Preset lastra',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown.listItems.add('2800x2070 mm (standard)', True)
            dropdown.listItems.add('3050x1220 mm', False)
            dropdown.listItems.add('2440x1220 mm (4x8 ft)', False)
            dropdown.listItems.add('Custom', False)
            
            lastra_inputs.addValueInput('lastra_larghezza', 'Larghezza lastra', 'mm',
                                       adsk.core.ValueInput.createByReal(280.0))
            lastra_inputs.addValueInput('lastra_altezza', 'Altezza lastra', 'mm',
                                       adsk.core.ValueInput.createByReal(207.0))
            
            # Gruppo parametri ottimizzazione
            group_opt = inputs.addGroupCommandInput('gruppo_ottimizzazione', 'Parametri Ottimizzazione')
            group_opt.isExpanded = True
            opt_inputs = group_opt.children
            
            opt_inputs.addValueInput('spessore_lama', 'Spessore lama', 'mm',
                                    adsk.core.ValueInput.createByReal(0.4))
            opt_inputs.addValueInput('margine_lastra', 'Margine lastra', 'mm',
                                    adsk.core.ValueInput.createByReal(1.0))
            
            # Algoritmo
            dropdown_algo = opt_inputs.addDropDownCommandInput(
                'algoritmo',
                'Algoritmo',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            dropdown_algo.listItems.add('Guillotine (veloce)', True)
            dropdown_algo.listItems.add('MaxRects (ottimale)', False)
            dropdown_algo.listItems.add('Skyline (bilanciato)', False)
            
            # Opzioni
            opt_inputs.addBoolValueInput('allow_rotation', 'Permetti rotazione pezzi', True, '', True)
            opt_inputs.addBoolValueInput('minimize_waste', 'Minimizza scarto', True, '', True)
            
            # Output
            group_output = inputs.addGroupCommandInput('gruppo_output', 'Output')
            group_output.isExpanded = True
            output_inputs = group_output.children
            
            output_inputs.addBoolValueInput('show_visualization', 'Mostra visualizzazione', True, '', True)
            output_inputs.addBoolValueInput('export_dxf', 'Esporta DXF', True, '', False)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore creazione comando nesting:\n{}'.format(traceback.format_exc()))


class NestingExecuteHandler(adsk.core.CommandEventHandler):
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
            
            lastra_w = inputs.itemById('lastra_larghezza').value
            lastra_h = inputs.itemById('lastra_altezza').value
            spessore_lama = inputs.itemById('spessore_lama').value
            margine = inputs.itemById('margine_lastra').value
            algoritmo = inputs.itemById('algoritmo').selectedItem.name
            allow_rotation = inputs.itemById('allow_rotation').value
            minimize_waste = inputs.itemById('minimize_waste').value
            show_viz = inputs.itemById('show_visualization').value
            export_dxf = inputs.itemById('export_dxf').value
            
            # Placeholder per logica nesting (da implementare con WoodWorkingWizard)
            ui.messageBox(
                'Ottimizzazione Taglio\n\n'
                'Parametri:\n'
                '- Lastra: {}x{} mm\n'
                '- Spessore lama: {} mm\n'
                '- Margine: {} mm\n'
                '- Algoritmo: {}\n'
                '- Rotazione: {}\n'
                '- Minimizza scarto: {}\n\n'
                'NOTA: Funzionalità in fase di implementazione.\n'
                'Utilizzare WoodWorkingWizard per ottimizzazione completa.'.format(
                    int(lastra_w * 10), int(lastra_h * 10),
                    spessore_lama * 10, margine * 10,
                    algoritmo,
                    'Sì' if allow_rotation else 'No',
                    'Sì' if minimize_waste else 'No'
                ),
                'Ottimizzazione Taglio'
            )
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore ottimizzazione taglio:\n{}'.format(traceback.format_exc()))


class NestingDestroyHandler(adsk.core.CommandEventHandler):
    """Handler per la distruzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        pass
