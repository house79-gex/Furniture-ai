"""
Comando Designer Ante per FurnitureAI
Crea ante custom con diversi stili
"""

import adsk.core
import adsk.fusion
import traceback
from . import door_designer, logging_utils

logger = logging_utils.get_logger()


class DoorDesignerCommand(adsk.core.CommandCreatedEventHandler):
    """Handler per il comando designer ante"""
    
    def __init__(self):
        super().__init__()
        self._handlers = []
        
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Imposta dimensioni dialog
            cmd.setDialogInitialSize(400, 550)
            
            # Event handlers
            on_execute = DoorDesignerExecuteHandler()
            cmd.execute.add(on_execute)
            self._handlers.append(on_execute)
            
            on_input_changed = DoorDesignerInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            self._handlers.append(on_input_changed)
            
            on_destroy = DoorDesignerDestroyHandler()
            cmd.destroy.add(on_destroy)
            self._handlers.append(on_destroy)
            
            # Crea inputs
            inputs = cmd.commandInputs
            
            # Gruppo tipo anta
            group_tipo = inputs.addGroupCommandInput('gruppo_tipo', 'Tipo Anta')
            group_tipo.isExpanded = True
            tipo_inputs = group_tipo.children
            
            dropdown_tipo = tipo_inputs.addDropDownCommandInput(
                'tipo_anta',
                'Stile anta',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle
            )
            door_types = door_designer.DoorDesigner.get_door_types()
            is_first = True
            for tipo, desc in door_types.items():
                dropdown_tipo.listItems.add('{} - {}'.format(tipo.capitalize(), desc), is_first)
                is_first = False
            
            # Gruppo dimensioni
            group_dim = inputs.addGroupCommandInput('gruppo_dimensioni', 'Dimensioni Anta')
            group_dim.isExpanded = True
            dim_inputs = group_dim.children
            
            dim_inputs.addValueInput('larghezza', 'Larghezza', 'cm',
                                    adsk.core.ValueInput.createByReal(40.0))
            dim_inputs.addValueInput('altezza', 'Altezza', 'cm',
                                    adsk.core.ValueInput.createByReal(70.0))
            dim_inputs.addValueInput('spessore', 'Spessore', 'cm',
                                    adsk.core.ValueInput.createByReal(1.8))
            
            # Gruppo parametri specifici (variano per tipo)
            group_params = inputs.addGroupCommandInput('gruppo_parametri', 'Parametri Specifici')
            group_params.isExpanded = True
            group_params.isVisible = False  # Nascosto inizialmente
            params_inputs = group_params.children
            
            # Parametri per bugna
            params_inputs.addValueInput('border_width', 'Larghezza bordo', 'cm',
                                       adsk.core.ValueInput.createByReal(5.0))
            params_inputs.addValueInput('raise_height', 'Altezza rialzo', 'cm',
                                       adsk.core.ValueInput.createByReal(0.5))
            
            # Parametri per cornice
            params_inputs.addValueInput('frame_width', 'Larghezza cornice', 'cm',
                                       adsk.core.ValueInput.createByReal(6.0))
            params_inputs.addValueInput('frame_depth', 'Profondità cornice', 'cm',
                                       adsk.core.ValueInput.createByReal(1.0))
            
            # Parametri per vetro
            params_inputs.addValueInput('glass_frame_width', 'Larghezza telaio', 'cm',
                                       adsk.core.ValueInput.createByReal(4.0))
            params_inputs.addValueInput('glass_thickness', 'Spessore vetro', 'cm',
                                       adsk.core.ValueInput.createByReal(0.4))
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore creazione comando designer ante:\n{}'.format(traceback.format_exc()))


class DoorDesignerExecuteHandler(adsk.core.CommandEventHandler):
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
            
            tipo_raw = inputs.itemById('tipo_anta').selectedItem.name
            tipo = tipo_raw.split(' - ')[0].lower()
            
            width = inputs.itemById('larghezza').value
            height = inputs.itemById('altezza').value
            thickness = inputs.itemById('spessore').value
            
            # Parametri specifici
            params = {}
            if tipo == 'bugna':
                params['border_width'] = inputs.itemById('border_width').value
                params['raise_height'] = inputs.itemById('raise_height').value
            elif tipo == 'cornice':
                params['frame_width'] = inputs.itemById('frame_width').value
                params['frame_depth'] = inputs.itemById('frame_depth').value
            elif tipo == 'vetro':
                params['frame_width'] = inputs.itemById('glass_frame_width').value
                params['glass_thickness'] = inputs.itemById('glass_thickness').value
            
            # Crea anta
            component = design.rootComponent
            designer = door_designer.DoorDesigner(component)
            
            body = designer.create_door(tipo, width, height, thickness, params)
            
            if body:
                ui.messageBox('Anta {} creata con successo!'.format(tipo.capitalize()))
            else:
                ui.messageBox('Errore creazione anta')
                
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Errore esecuzione designer ante:\n{}'.format(traceback.format_exc()))


class DoorDesignerInputChangedHandler(adsk.core.InputChangedEventHandler):
    """Handler per i cambiamenti negli input"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.InputChangedEventArgs):
        try:
            changed_input = args.input
            inputs = args.inputs
            
            # Mostra/nascondi parametri specifici in base al tipo
            if changed_input.id == 'tipo_anta':
                tipo_raw = changed_input.selectedItem.name
                tipo = tipo_raw.split(' - ')[0].lower()
                
                # Parametri gruppo
                params_group = inputs.itemById('gruppo_parametri')
                border_width = inputs.itemById('border_width')
                raise_height = inputs.itemById('raise_height')
                frame_width = inputs.itemById('frame_width')
                frame_depth = inputs.itemById('frame_depth')
                glass_frame_width = inputs.itemById('glass_frame_width')
                glass_thickness = inputs.itemById('glass_thickness')
                
                # Nascondi tutti
                border_width.isVisible = False
                raise_height.isVisible = False
                frame_width.isVisible = False
                frame_depth.isVisible = False
                glass_frame_width.isVisible = False
                glass_thickness.isVisible = False
                
                # Mostra gruppo e parametri appropriati
                if tipo == 'piatta':
                    params_group.isVisible = False
                elif tipo == 'bugna':
                    params_group.isVisible = True
                    border_width.isVisible = True
                    raise_height.isVisible = True
                elif tipo == 'cornice':
                    params_group.isVisible = True
                    frame_width.isVisible = True
                    frame_depth.isVisible = True
                elif tipo == 'vetro':
                    params_group.isVisible = True
                    glass_frame_width.isVisible = True
                    glass_thickness.isVisible = True
                elif tipo == 'custom':
                    params_group.isVisible = False
                    
        except:
            pass


class DoorDesignerDestroyHandler(adsk.core.CommandEventHandler):
    """Handler per la distruzione del comando"""
    
    def __init__(self):
        super().__init__()
        
    def notify(self, args: adsk.core.CommandEventArgs):
        pass
